from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer, DoctorSerializer
from rest_framework.permissions import AllowAny
from django.conf import settings
import os
from django.utils import timezone


# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WorkingTimeViewSet(viewsets.ModelViewSet):
    queryset = WorkingTime.objects.all()
    serializer_class = WorkingTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

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
                image_url = ""

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
                files=image_url
            )
            hospital.save()

            response_data = serializer.data
            response_data['file_path'] = request.build_absolute_uri('/' + image_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            files = request.FILES.get('files', None)
            if files:
                image_url = self.save_file(files)
            else:
                image_url = instance.files 

            instance.category_id = serializer.validated_data.get('category_id', instance.category_id)
            instance.name = serializer.validated_data.get('name', instance.name)
            instance.review_id = serializer.validated_data.get('review', instance.review_id)
            instance.website = serializer.validated_data.get('website', instance.website)
            instance.phone_number = serializer.validated_data.get('phone_number', instance.phone_number)
            instance.email = serializer.validated_data.get('email', instance.email)
            instance.location_id = serializer.validated_data.get('location_id', instance.location_id)
            instance.working_time_id = serializer.validated_data.get('working_time_id', instance.working_time_id)
            instance.address = serializer.validated_data.get('address', instance.address)
            instance.specialist=serializer.validated_data.get('specialist', instance.specialist)
            instance.files = image_url
            instance.save()

            response_data = serializer.data
            response_data['file_path'] = request.build_absolute_uri('/' + image_url)

            return Response(response_data, status=status.HTTP_200_OK)
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
                file_url = ""

            doctor = Doctor(
                user_id=serializer.validated_data.get('user_id'),
                name=serializer.validated_data.get('name'),
                speciality_id=serializer.validated_data.get('speciality_id'),
                working_time_id=serializer.validated_data.get('working_time_id'),
                about=serializer.validated_data.get('about'),
                location_id=serializer.validated_data.get('location_id'),
                is_favorite=serializer.validated_data.get('is_favorite', False),
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
            response_data['file_path'] = request.build_absolute_uri('/' + file_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            files = request.FILES.get('files', None)
            if files:
                file_url = self.save_file(files)
            else:
                file_url = instance.files

            instance.user_id = serializer.validated_data.get('user_id', instance.user_id)
            instance.name = serializer.validated_data.get('name', instance.name)
            instance.speciality_id = serializer.validated_data.get('speciality_id', instance.speciality_id)
            instance.working_time_id = serializer.validated_data.get('working_time_id', instance.working_time_id)
            instance.about = serializer.validated_data.get('about', instance.about)
            instance.location_id = serializer.validated_data.get('location_id', instance.location_id)
            instance.total_experience = serializer.validated_data.get('total_experience', instance.total_experience)
            instance.total_patients = serializer.validated_data.get('total_patients', instance.total_patients)
            instance.review_id = serializer.validated_data.get('review_id', instance.review_id)
            instance.hospital_id = serializer.validated_data.get('hospital_id', instance.hospital_id)
            instance.files = file_url
            instance.save()

            response_data = serializer.data
            response_data['file_path'] = request.build_absolute_uri('/' + file_url)

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

     
    def destroy(self, request, *args, **kwargs):
        try:
            doctor = self.get_object()
            doctor.delete()
            return Response({"message": "Doctor deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)