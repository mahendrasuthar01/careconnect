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

        """
        Saves the uploaded file to the 'category_files' directory in the media root.
        
        Parameters:
            file: The uploaded file object.
        
        Returns:
            The path to the saved file in the format 'media/category_files/filename'.
        """

        file_path = os.path.join(settings.MEDIA_ROOT, 'category_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/category_files/' + file.name
        

    def create(self, request, *args, **kwargs) -> Response:

        """
        Creates a new Category object with the provided data.

        Args:
            request (HttpRequest): The HTTP request object containing the data to be validated.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the serialized data of the created Category object.

        Raises:
            ValidationError: If the provided data is invalid.

        Steps:
            1. Validates the provided data using the serializer.
            2. If the data is valid, extracts the 'name' and 'description' fields from the validated data.
            3. Retrieves the 'files' field from the request data.
            4. If 'files' is provided, saves the file using the 'save_file' method and retrieves the file URL.
            5. If 'files' is not provided, sets the file URL to None.
            6. Creates a new Category object with the extracted 'name', 'description', and 'file_url' fields.
            7. Serializes the created Category object and sets the 'files' field to None in the response data.
            8. If 'file_url' is not None, sets the 'files' field in the response data to the absolute URI of the file.
            9. Returns a HTTP 201 Created response with the serialized response data.
            10. If the data is invalid, returns a HTTP 400 Bad Request response with the serializer errors.
        """

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            files = request.FILES.get('files', None)
            file_url = self.save_file(files) if files else None

            category = serializer.save(files=file_url)

            response_data = serializer.data
            response_data['files'] = None

            if file_url is not None:
                response_data['file_path'] = request.build_absolute_uri('/' + file_url)

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):

        """
        Deletes a category object from the database.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the category is deleted successfully,
                     otherwise an error response.

        Raises:
            Exception: If the category is not found in the database.
        """
        
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):

        """
    	Updates an object based on the provided request data, handling exceptions with a response.
    	"""
        
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

        """
        A function to get details of an entity based on the provided working time object.
        It takes a working time object as input.
        Returns the serialized data of the entity based on the entity type and ID from the working time object.
        """

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

        """
    	List view for working time instances. Retrieves a queryset of working time instances, serializes each instance, adds entity details to the serialized data, and returns a response with the serialized data.
    	
    	Parameters:
    	    self: reference to the current instance of the class
    	    request: the request object
    	    *args: variable length argument list
    	    **kwargs: variable length keyword argument list
    	
    	Returns:
    	    Response object with serialized data and HTTP 200 status
    	"""

        queryset = self.get_queryset()

        serialized_data = []
        for working_time_instance in queryset:
            serializer = self.get_serializer(working_time_instance)
            working_time_data = serializer.data
            working_time_data['entity_details'] = self.get_entity_details(working_time_instance)
            serialized_data.append(working_time_data)

        return Response(serialized_data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):

        """
        Retrieves an object, serializes it, adds entity details to the serialized data, and returns a response with the serialized data.

        Parameters:
            self: reference to the current instance of the class
            request: the request object
            *args: variable length argument list
            **kwargs: variable length keyword argument list

        Returns:
            Response object with serialized data and HTTP 200 status
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data['entity_details'] = self.get_entity_details(instance)
        return Response(serializer_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):

        """
        Deletes a working time object from the database.

        Parameters:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the working time is deleted successfully,
                     otherwise an error response.

        Raises:
            Exception: If the working time is not found in the database.
        """

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

        """
        Retrieves the queryset for the current viewset based on the provided query parameters.

        This method filters the queryset based on the 'category_id' and 'working_time_id' query parameters. 
        If the 'category_id' parameter is provided, the queryset is filtered to include only hospitals with 
        the specified category ID. If the 'working_time_id' parameter is provided, the queryset is filtered 
        to include only hospitals with the specified working time ID.

        The method then retrieves the reviews data for the hospitals in the queryset by calling the 
        'get_reviews_data' function with the hospital IDs and a flag indicating that the data is for hospitals.

        Finally, the method updates each hospital in the queryset by adding the 'hospital_id', 'review_count', 
        and 'average_rating' attributes using the reviews data.

        Returns:
            QuerySet: The filtered queryset of hospitals.
        """

        queryset = self.queryset       
        category_id = self.request.query_params.get('category_id')
        working_time_id = self.request.query_params.get('working_time_id')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if working_time_id:
            queryset = queryset.filter(working_time_id=working_time_id)

        hospital_ids = [str(hospital.id) for hospital in queryset]
        reviews_data = get_reviews_data(hospital_ids, 2)

        for hospital in queryset:
            hospital_id = str(hospital.id)
            hospital.hospital_id = hospital_id
            hospital.review_count = reviews_data.get(hospital_id, {}).get('review_count', 0)
            hospital.average_rating = reviews_data.get(hospital_id, {}).get('average_rating', 0.0)
        
        return queryset
    
    def save_file(self, file):
        """
        Save a file to the 'uploaded_files' directory in the media root.

        Args:
            file (File): The file to be saved.

        Returns:
            str: The path to the saved file in the format 'media/uploaded_files/filename'.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/uploaded_files/' + file.name


    def create(self, request, *args, **kwargs):
        """
        Creates a new hospital object with the provided data.

        Args:
            request (HttpRequest): The HTTP request object containing the data to be validated.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the serialized data of the created hospital object.

        Steps:
            1. Validates the provided data using the serializer.
            2. If the data is valid, extracts the 'files' field from the request data.
            3. If 'files' is provided, saves the file using the 'save_file' method and retrieves the file URL.
            4. If 'files' is not provided, sets the file URL to None.
            5. Creates a new hospital object with the provided data and the file URL.
            6. Serializes the created hospital object and sets the 'files' field to None in the response data.
            7. If 'file_url' is not None, sets the 'file_path' field in the response data to the absolute URI of the file.
            8. Returns a HTTP 201 Created response with the serialized response data.
            9. If the data is invalid, returns a HTTP 400 Bad Request response with the serializer errors.
        """
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
        """
        Deletes a hospital object from the database.

        Args:
            self: The HospitalViewSet instance.
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the hospital is deleted successfully,
                     otherwise an error response.
        """
        try:
            hospital = self.get_object()
            hospital.delete()
            return Response({"message": "Hospital deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Hospital not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'])
    def total_review_count(self, request):
        """
        Retrieves the total review count for hospitals.

        Args:
            self: The HospitalViewSet instance.
            request: The HTTP request object.

        Returns:
            Response: The response containing the total review count data for hospitals.
        """
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

    def get_queryset(self):
        """
        Retrieves the queryset for the current viewset based on the provided query parameters.

        This method filters the queryset based on the 'hospital_id' and 'speciality_id' query parameters. 
        If the 'hospital_id' parameter is provided, the queryset is filtered to include only doctors 
        with the specified hospital ID. If the 'speciality_id' parameter is provided, the queryset is 
        filtered to include only doctors with the specified speciality ID.

        The method then retrieves the reviews data for the doctors in the queryset by calling the 
        'get_reviews_data' function with the doctor IDs and a flag indicating that the data is for doctors.

        Finally, the method updates each doctor in the queryset by adding the 'doctor_id', 'review_count', 
        and 'average_rating' attributes using the reviews data.

        Returns:
            QuerySet: The filtered queryset of doctors.
        """
        queryset = Doctor.objects.all()

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
        """
        Save the uploaded file to the 'doctors_files' directory in the media root.
        
        Parameters:
            file: The uploaded file object.
            
        Returns:
            The path to the saved file in the format 'media/doctors_files/filename'.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, 'doctors_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/doctors_files/' + file.name
    
    
    def create(self, request, *args, **kwargs):
        """
        Creates a new doctor object with the provided data and saves any associated files.
        
        Parameters:
            request (HttpRequest): The HTTP request object containing the data to be validated.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: The HTTP response containing the serialized data of the created doctor object.
        """
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
        """
        Deletes a doctor object from the database.

        Args:
            self: The DoctorViewSet instance.
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the doctor is deleted successfully,
                     otherwise an error response.
        """
        try:
            doctor = self.get_object()
            doctor.delete()
            return Response({"message": "Doctor deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves an instance object, creates speciality data, and returns a response with serialized data.
        
        Args:
            self: The DoctorViewSet instance.
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Response: The HTTP response object with serialized data and status code.
        """
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
        """
        Retrieves the total review count for doctors.

        Args:
            self (DoctorViewSet): The DoctorViewSet instance.
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object with the total review count data for doctors.

        Raises:
            Exception: If an error occurs during the retrieval of the review count.

        """
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
        """
        Retrieves the total number of patients for each doctor and returns the data in a list format.

        Args:
            self (DoctorViewSet): The DoctorViewSet instance.
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object with the total patient count data for each doctor.
        """
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
        """
        Retrieves all hospitals and doctors from the database and adds additional information to each doctor and hospital.
        
        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Response: An HTTP response object containing a dictionary with 'hospitals' and 'doctors' keys.
                      The values are lists of serialized hospital and doctor objects respectively.
        """
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