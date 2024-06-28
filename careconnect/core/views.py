from django.shortcuts import render
from rest_framework import viewsets, status
from .serializers import FavoriteSerializer, LocationSerializer, ReviewSerializer
from rest_framework.permissions import AllowAny
from .models import Favorite, Location, Review
from rest_framework.response import Response
import os
from django.conf import settings
from healthcare.models import Doctor, Hospital

# Create your views here.
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]
    queryset = Favorite.objects.all()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        entity_id = request.data.get('entity_id')
        entity_type = request.data.get('entity_type')

        # Check if the favorite already exists
        favorite = Favorite.objects.filter(user_id=user_id, entity_id=entity_id, entity_type=entity_type).first()
        if favorite:
            # Toggle is_favorite field for the corresponding entity
            if entity_type == 1:  # Doctor
                doctor = Doctor.objects.filter(id=entity_id).first()
                if doctor:
                    doctor.is_favorite = not doctor.is_favorite
                    doctor.save()
            elif entity_type == 2:  # Hospital
                hospital = Hospital.objects.filter(id=entity_id).first()
                if hospital:
                    hospital.is_favorite = not hospital.is_favorite
                    hospital.save()
            
            favorite.delete()
            return Response({"message": "Favorite item removed successfully"}, status=status.HTTP_200_OK)
        
        # Create new favorite and set is_favorite field
        favorite = Favorite(user_id=user_id, entity_id=entity_id, entity_type=entity_type)
        favorite.save()

        if entity_type == 1:  # Doctor
            doctor = Doctor.objects.filter(id=entity_id).first()
            if doctor:
                doctor.is_favorite = True
                doctor.save()
        elif entity_type == 2:  # Hospital
            hospital = Hospital.objects.filter(id=entity_id).first()
            if hospital:
                hospital.is_favorite = True
                hospital.save()

        return Response({"message": "Favorite item added successfully"}, status=status.HTTP_201_CREATED)

          
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
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Review.objects.all()
    
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