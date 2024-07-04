from rest_framework import viewsets, status
from .serializers import FavoriteSerializer, LocationSerializer, ReviewSerializer
from rest_framework.permissions import AllowAny
from .models import Favorite, Location, Review
from rest_framework.response import Response
import os
from django.conf import settings
from healthcare.models import Doctor, Hospital
from healthcare.serializers import HospitalSerializer, DoctorSerializer
from accounts.authentication import JWTAuthentication
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    queryset = Favorite.objects.all()

    def update_mongodb(self, entity_type, entity_id, is_favorite):
        if entity_type == 1:
            Doctor.objects.filter(id=entity_id).update(is_favorite=is_favorite)
        elif entity_type == 2: 
            Hospital.objects.filter(id=entity_id).update(is_favorite=is_favorite)

    def create(self, request, *args, **kwargs):
        entity_id = request.data.get('entity_id')
        entity_type = request.data.get('entity_type')
        user = JWTAuthentication.get_current_user(self, request)
        user_id = str(user.id)

        # Check if the favorite already exists
        favorite = Favorite.objects.filter(user_id=user_id, entity_id=entity_id, entity_type=entity_type).first()
        if favorite:
            # Toggle is_favorite field for the corresponding entity
            if entity_type == 1:
                doctor = Doctor.objects.filter(id=entity_id).first()
                if doctor:
                    doctor.is_favorite = not doctor.is_favorite
                    doctor.save()
                    if not doctor.is_favorite:
                        favorite.delete()
                        return Response({"message": "Favorite item removed successfully"}, status=status.HTTP_200_OK)
            elif entity_type == 2:
                hospital = Hospital.objects.filter(id=entity_id).first()
                if hospital:
                    hospital.is_favorite = not hospital.is_favorite
                    hospital.save()
                    if not hospital.is_favorite:
                        favorite.delete()
                        return Response({"message": "Favorite item removed successfully"}, status=status.HTTP_200_OK)
        
        else:
            # Create new favorite and set is_favorite field
            favorite = Favorite(user_id=user_id, entity_id=entity_id, entity_type=entity_type)
            favorite.save()

            if entity_type == 1:
                doctor = Doctor.objects.filter(id=entity_id).first()
                if doctor:
                    doctor.is_favorite = True
                    doctor.save()
                    serializer = DoctorSerializer(doctor)
                    return Response({"message": "Favorite item added successfully", "Doctor data": serializer.data, "user_id": user_id, "entity_id": entity_id, "entity_type": entity_type}, status=status.HTTP_201_CREATED)
            elif entity_type == 2:
                hospital = Hospital.objects.filter(id=entity_id).first()
                if hospital:
                    hospital.is_favorite = True
                    hospital.save()
                    serializer = HospitalSerializer(hospital)
                    return Response({"message": "Favorite item added successfully", "Hospital data": serializer.data, "user_id": user_id, "entity_id": entity_id, "entity_type": entity_type}, status=status.HTTP_201_CREATED)

        return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_entity_details(self, favorite):
        entity_type = favorite.entity_type
        entity_id = favorite.entity_id

        try:
            if entity_type == 1:
                entity = Doctor.objects.get(id=entity_id)
                serializer = DoctorSerializer(entity)
            elif entity_type == 2:
                entity = Hospital.objects.get(id=entity_id)
                serializer = HospitalSerializer(entity)
            else:
                raise NotFound("Entity type not supported")

            return serializer.data
        except (Doctor.DoesNotExist, Hospital.DoesNotExist):
            raise NotFound("Entity not found")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serialized_data = []
        for favorite_instance in queryset:
            serializer = self.get_serializer(favorite_instance)
            favorite_data = serializer.data
            favorite_data['entity_details'] = self.get_entity_details(favorite_instance)
            serialized_data.append(favorite_data)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data['entity_details'] = self.get_entity_details(instance)
        return Response(serializer_data, status=status.HTTP_200_OK)
          
class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]
    queryset = Location.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            location = self.get_object()
            location.delete()
            return Response({"message":"Location deleted sucessfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error":"Location not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = Review.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        entity_id = self.request.query_params.get('entity_id')
        if entity_id:
            queryset = queryset.filter(entity_type=entity_id)
        return queryset
    
    def save_file(self, file):
        file_path = os.path.join(settings.MEDIA_ROOT, 'review_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/review_files/' + file.name
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get('files', None)
            file_url = self.save_file(file) if file else None

            review = serializer.save(files=file_url)

            response_data = serializer.data
            response_data['files'] =  None

            if file_url is not None:
                response_data['file_path'] = request.build_absolute_uri('/' + file_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def destroy(self, request, *args, **kwargs):
        try:
            review = self.get_object()
            review.delete()
            return Response({"message": "Review deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        

    def get_entity_details(self, review):
        entity_type = review.entity_type
        entity_id = review.entity_id

        try:
            if entity_type == 1:
                entity = Doctor.objects.get(id=entity_id)
                serializer = DoctorSerializer(entity)
            elif entity_type == 2:
                entity = Hospital.objects.get(id=entity_id)
                serializer = HospitalSerializer(entity)
            else:
                raise NotFound("Entity type not supported")

            return serializer.data
        except (Doctor.DoesNotExist, Hospital.DoesNotExist):
            raise NotFound("Entity not found")
        

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for review in serializer.data:
            review['entity_details'] = self.get_entity_details(Review.objects.get(id=review['id']))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data['entity_details'] = self.get_entity_details(instance)
        return Response(serializer_data, status=status.HTTP_200_OK)