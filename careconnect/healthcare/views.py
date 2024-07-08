from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer, DoctorSerializer, DoctorCardSerializer, HospitalCardSerializer
from rest_framework.permissions import AllowAny
from django.conf import settings
import os
from core.models import Review
from rest_framework.decorators import action
from appointments.models import Appointment
from constant import DOCTOR, HOSPITAL
from rest_framework.views import APIView
from .utils import get_reviews_data
from rest_framework.exceptions import NotFound

class CategoryViewSet(viewsets.ModelViewSet):
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
                file_url = None

            Category.objects.create(
                name=name,
                description=description,
                files=file_url
            )

            response_data = serializer.data
            response_data['files'] = None

            if file_url is not None:
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

    def get_queryset(self):
        return WorkingTime.objects.all()
    
    def get_entity_details(self, working_time):
        entity_type = working_time.entity_type
        entity_id = working_time.entity_id

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
        for working_time_instance in queryset:
            serializer = self.get_serializer(working_time_instance)
            working_time_data = serializer.data
            working_time_data['entity_details'] = self.get_entity_details(working_time_instance)
            serialized_data.append(working_time_data)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data['entity_details'] = self.get_entity_details(instance)
        return Response(serializer_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            working_time = self.get_object()
            working_time.delete()
            return Response({"message": "Working-Time deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Working-Time not found"}, status=status.HTTP_404_NOT_FOUND)


class HospitalViewSet(viewsets.ModelViewSet):
    serializer_class = HospitalSerializer
    permission_classes = [AllowAny]
    queryset = Hospital.objects.all()

    def get_queryset(self):
        queryset = self.queryset       
        category_id = self.request.query_params.get('category_id')
        working_time_id = self.request.query_params.get('working_time_id')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if working_time_id:
            queryset = queryset.filter(working_time_id=working_time_id)

        hospital_ids = [str(hospital.id) for hospital in queryset]
        reviews_data = get_reviews_data(hospital_ids, 0)

        for hospital in queryset:
            hospital_id = str(hospital.id)
            hospital.hospital_id = hospital_id
            hospital.review_count = reviews_data.get(hospital_id, {}).get('review_count', 0)
            hospital.average_rating = reviews_data.get(hospital_id, {}).get('average_rating', 0.0)
        
        return queryset
    
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
            image_url = self.save_file(files) if files else None

            hospital = serializer.save(files=image_url)

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
        
    @action(detail=False, methods=['get'])
    def total_review_count(self, request):
        hospitals = self.get_queryset()
        data = []
        for hospital in hospitals:
            review_count = Review.objects.filter(entity_id=str(hospital.id), entity_type=HOSPITAL[0]).count()
            data.append({
                'hospital_id': str(hospital.id),
                'hospital_name': hospital.name,
                'review_count': review_count
            })
        return Response(data)

    
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Doctor.objects.all()


    def get_queryset(self):
        queryset = self.queryset
        hospital_id = self.request.query_params.get('hospital_id')
        speciality_id = self.request.query_params.get('speciality_id')

        if hospital_id:
            queryset = queryset.filter(hospital_id=hospital_id)
        if speciality_id:
            queryset = queryset.filter(speciality_id=speciality_id)

        doctor_ids = [str(doctor.id) for doctor in queryset]
        reviews_data = get_reviews_data(doctor_ids, 1)

        for doctor in queryset:
            doctor_id = str(doctor.id)
            doctor.doctor_id = doctor_id
            doctor.review_count = reviews_data.get(doctor_id, {}).get('review_count', 0)
            doctor.average_rating = reviews_data.get(doctor_id, {}).get('average_rating', 0.0)
            
        return queryset
    
        
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
            file_url = self.save_file(files) if files else None

            doctor = serializer.save(files=file_url, is_active=True)

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
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        speciality_data = {
            'id': str(instance.speciality_id.id), 
            'name': instance.speciality_id.name,
            'description': instance.speciality_id.description
        }
        
        serializer = self.serializer_class(instance)
        serializer_data = serializer.data
        
        serializer_data['speciality'] = speciality_data
        
        return Response(serializer_data, status=status.HTTP_200_OK)
        

    @action(detail=False, methods=['get'])
    def total_review_count(self, request):
        doctors = self.get_queryset()
        data = []

        for doctor in doctors:
            doctor_id = str(doctor.id)
            
            try:
                review_count = Review.objects.filter(entity_id=doctor_id, entity_type=DOCTOR[0]).count()
                data.append({
                    'doctor_id': doctor_id,
                    'doctor_name': doctor.name,
                    'review_count': review_count
                })
            except Exception as e:
                return Response({'error': str(e)}, status=500)

        return Response(data)
    

    @action(detail=False, methods=['get'])
    def total_patients_count(self, request):
        doctors = self.get_queryset()
        data = []
        for doctor in doctors:
            patient_count = Appointment.objects.filter(doctor_id=str(doctor.id)).count()
            data.append({
                'doctor_id': str(doctor.id),
                'doctor_name': doctor.name,
                'patient_count': patient_count
            })
        return Response(data)


class CombinedDoctorsHospitalsListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        hospitals = list(Hospital.objects.all())
        doctors = list(Doctor.objects.all())

        
        doctor_ids = [str(doctor.id) for doctor in doctors]
        hospital_ids = [str(hospital.id) for hospital in hospitals]

        doctor_reviews_data = get_reviews_data(doctor_ids, 1)
        hospital_reviews_data = get_reviews_data(hospital_ids, 2)

        for doctor in doctors:
            doctor_id = str(doctor.id)
            doctor.doctor_id = doctor_id
            doctor.review_count = doctor_reviews_data.get(doctor_id, {}).get('review_count', 0)
            doctor.average_rating = doctor_reviews_data.get(doctor_id, {}).get('average_rating', 0.0)

        for hospital in hospitals:
            hospital_id = str(hospital.id)
            hospital.hospital_id = hospital_id
            hospital.review_count = hospital_reviews_data.get(hospital_id, {}).get('review_count', 0)
            hospital.average_rating = hospital_reviews_data.get(hospital_id, {}).get('average_rating', 0.0)

        hospital_serializer = HospitalCardSerializer(hospitals, many=True)
        doctor_serializer = DoctorCardSerializer(doctors, many=True)

        combined_data = {
            'hospitals': hospital_serializer.data,
            'doctors': doctor_serializer.data
        }

        return Response(combined_data, status=status.HTTP_200_OK)