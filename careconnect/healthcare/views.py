from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer, DoctorSerializer
from rest_framework.permissions import AllowAny
from django.conf import settings
import os
from django.utils import timezone


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get_queryset(self):
        return Category.objects.all()

    def save_file(self, file):
        file_path = os.path.join(settings.MEDIA_ROOT, 'category_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/category_files/' + file.name
        

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            description = serializer.validated_data.get('description')
            files = request.FILES.get('files', None)

            if files:
                file_url = self.save_file(files)
            else:
                file_url = ""

            Category.objects.create(
                name=name,
                description=description,
                files=file_url
            )

            response_data = serializer.data
            response_data['files'] = request.build_absolute_uri(f'/{file_url}')

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            category = self.get_object()
            serializer = self.get_serializer(category, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)  

class WorkingTimeViewSet(viewsets.ModelViewSet):
    queryset = WorkingTime.objects.all()
    serializer_class = WorkingTimeSerializer
    permission_classes = [AllowAny]

    def destroy(self, request, *args, **kwargs):
        try:
            working_time = self.get_object()
            working_time.delete()
            return Response({"message": "Working-Time deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Working-Time not found"}, status=status.HTTP_404_NOT_FOUND)


class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [AllowAny]

    def save_file(self, file):
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/uploaded_files/' + file.name

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            files = request.FILES.get('files', None)
            if files:
                image_url = self.save_file(files)
            else:
                image_url = None

            hospital = Hospital(
                category_id=serializer.validated_data.get('category_id'),
                name=serializer.validated_data.get('name'),
                review_id=serializer.validated_data.get('review'),
                website=serializer.validated_data.get('website'),
                phone_number=serializer.validated_data.get('phone_number'),
                email=serializer.validated_data.get('email'),
                location_id=serializer.validated_data.get('location_id'),
                working_time_id=serializer.validated_data.get('working_time_id'),
                address=serializer.validated_data.get('address'),
                specialist=serializer.validated_data.get('specialist'),
                is_favorite=serializer.validated_data.get('is_favorite'),
                files=image_url
            )
            hospital.save()

            response_data = serializer.data
            response_data['files'] = None

            if image_url is not None:
                response_data['file_path'] = request.build_absolute_uri('/' + image_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def destroy(self, request, *args, **kwargs):
        try:
            hospital = self.get_object()
            hospital.delete()
            return Response({"message": "Hospital deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Hospital not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]

    def save_file(self, file):
        file_path = os.path.join(settings.MEDIA_ROOT, 'doctors_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/doctors_files/' + file.name
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            files = request.FILES.get('files', None)
            if files:
                file_url = self.save_file(files)
            else:
                file_url = None

            doctor = Doctor(
                user_id=serializer.validated_data.get('user_id'),
                name=serializer.validated_data.get('name'),
                speciality_id=serializer.validated_data.get('speciality_id'),
                working_time_id=serializer.validated_data.get('working_time_id'),
                about=serializer.validated_data.get('about'),
                location_id=serializer.validated_data.get('location_id'),
                is_favorite=serializer.validated_data.get('is_favorite'),
                is_active=True,
                total_experience=serializer.validated_data.get('total_experience'),
                total_patients=serializer.validated_data.get('total_patients'),
                review_id=serializer.validated_data.get('review_id'),
                hospital_id=serializer.validated_data.get('hospital_id'),
                files=file_url
            )
            doctor.sign_up_date = timezone.now()

            doctor.save()

            response_data = serializer.data
            response_data['files'] = None

            if file_url is not None:
                response_data['file_path'] = request.build_absolute_uri('/' + file_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def destroy(self, request, *args, **kwargs):
        try:
            doctor = self.get_object()
            doctor.delete()
            return Response({"message": "Doctor deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)