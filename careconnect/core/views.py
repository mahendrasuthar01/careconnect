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
from healthcare.utils import get_reviews_data

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        return Favorite.objects.all()
    
    def update_mongodb(self, entity_type, entity_id, is_favorite):
        """
        Updates the MongoDB database based on the entity type and ID by setting the 'is_favorite' field to the provided value.

        Args:
            self: The FavoriteViewSet instance.
            entity_type (int): The type of the entity (1 for Doctor, 2 for Hospital).
            entity_id (int): The ID of the entity.
            is_favorite (bool): The value to set the 'is_favorite' field to.
        """
        if entity_type == 1:
            Doctor.objects.filter(id=entity_id).update(is_favorite=is_favorite)
        elif entity_type == 2: 
            Hospital.objects.filter(id=entity_id).update(is_favorite=is_favorite)

    def is_valid_entity_id(self, entity_type, entity_id):
        """
        Checks if the provided entity type and ID correspond to a valid entity.
        
        Args:
            self: The FavoriteViewSet instance.
            entity_type (int): The type of the entity (1 for Doctor, 2 for Hospital).
            entity_id (int): The ID of the entity.
        
        Returns:
            bool: True if the entity is valid, False otherwise.
        """
        if entity_type == 1:
            doctor = Doctor.objects.filter(id=entity_id).first()
            return doctor is not None
        elif entity_type == 2:
            hospital = Hospital.objects.filter(id=entity_id).first()
            return hospital is not None
        return False

    def create(self, request, *args, **kwargs):
        """
        A function to create a new favorite item based on the provided entity_id and entity_type.
        
        Args:
            self: The FavoriteViewSet instance.
            request: The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Response: A response indicating the success or failure of the favorite creation process.
        """
        entity_id = request.data.get('entity_id')
        entity_type = request.data.get('entity_type')
        user = JWTAuthentication.get_current_user(self, request)
        user_id = str(user.id)

        if not entity_id or not entity_type:
            return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.is_valid_entity_id(entity_type, entity_id):
            return Response({"error": "Invalid entity_id provided"}, status=status.HTTP_400_BAD_REQUEST)

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
                    return Response({"message": "Favorite item added successfully", "doctor_data": serializer.data, "user_id": user_id, "entity_id": entity_id, "entity_type": entity_type}, status=status.HTTP_201_CREATED)
            elif entity_type == 2:
                hospital = Hospital.objects.filter(id=entity_id).first()
                if hospital:
                    hospital.is_favorite = True
                    hospital.save()
                    serializer = HospitalSerializer(hospital)
                    return Response({"message": "Favorite item added successfully", "hospital_data": serializer.data, "user_id": user_id, "entity_id": entity_id, "entity_type": entity_type}, status=status.HTTP_201_CREATED)

        return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_entity_details(self, favorite):
        """
        Retrieves the details of an entity based on the provided favorite object.

        Args:
            self: The instance of the class.
            favorite (Favorite): The favorite object containing the entity type and ID.

        Returns:
            dict: A dictionary containing the details of the entity. The dictionary has the following keys:
                - 'review_count' (int): The number of reviews for the entity.
                - 'average_rating' (float): The average rating of the reviews for the entity.

        Raises:
            NotFound: If the entity type is not supported or if the entity is not found.
        """
        entity_type = favorite.entity_type
        entity_id = favorite.entity_id

        try:
            if entity_type == 1:
                entity = Doctor.objects.get(id=entity_id)
                review_data = get_reviews_data([entity_id], entity_type)
                entity_data = DoctorSerializer(entity).data
            elif entity_type == 2:
                entity = Hospital.objects.get(id=entity_id)
                review_data = get_reviews_data([entity_id], entity_type)
                entity_data = HospitalSerializer(entity).data
            else:
                raise NotFound("Entity type not supported")
            
            entity_data['review_count'] = review_data[entity_id]['review_count']
            entity_data['average_rating'] = review_data[entity_id]['average_rating']

            return entity_data
        except (Doctor.DoesNotExist, Hospital.DoesNotExist):
            raise NotFound("Entity not found")

    def list(self, request, *args, **kwargs):
        """
        Retrieves a queryset of favorite instances, serializes each instance, adds entity details to the serialized data, and returns a response with the serialized data.
        
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
        for favorite_instance in queryset:
            serializer = self.get_serializer(favorite_instance)
            favorite_data = serializer.data
            favorite_data['entity_details'] = self.get_entity_details(favorite_instance)
            serialized_data.append(favorite_data)

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
          
class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]
    queryset = Location.objects.all()

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a location object from the database.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the location is deleted successfully,
                     otherwise an error response.
        """
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
        """
        Retrieves the queryset for the current viewset based on the provided query parameters.

        Returns:
            QuerySet: The filtered queryset based on the 'entity_id' query parameter.
        """
        queryset = self.queryset
        entity_id = self.request.query_params.get('entity_id')
        if entity_id:
            queryset = queryset.filter(entity_type=entity_id)
        return queryset
    
    def save_file(self, file):
        """
        Saves a file to the 'review_files' directory in the media root.

        Args:
            file (File): The file to be saved.

        Returns:
            str: The path to the saved file in the format 'media/review_files/filename'.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, 'review_files', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return 'media/review_files/' + file.name
    
    def create(self, request, *args, **kwargs):
        """
        Creates a new instance of the model using the provided data and saves it to the database.
        
        Args:
            request (HttpRequest): The HTTP request object containing the data to be validated.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Response: The HTTP response containing the serialized data of the created instance.
                If the data is valid, the response will have a status code of 201 (Created) and
                include the serialized data of the created instance. If the data is invalid, the
                response will have a status code of 400 (Bad Request) and include the serializer
                errors.
        
        Raises:
            None
        
        Steps:
            1. Authenticates the user using the JWTAuthentication class and retrieves the user's ID.
            2. Retrieves the data from the request object.
            3. Adds the user ID to the data dictionary.
            4. Validates the data using the serializer class.
            5. If the data is valid, retrieves the file from the request object and saves it to the
               'review_files' directory in the media root using the 'save_file' method.
            6. Saves the instance using the serializer and the file URL.
            7. Creates a response data dictionary with the serialized data of the created instance.
            8. Sets the 'files' field in the response data to None.
            9. If the file URL is not None, sets the 'file_path' field in the response data to the
               absolute URI of the file.
            10. Returns a HTTP 201 Created response with the serialized response data.
            11. If the data is invalid, returns a HTTP 400 Bad Request response with the serializer
                errors.
        """
        user = JWTAuthentication.get_current_user(self, request)
        user_id = str(user.id)
        
        data = request.data

        data['user_id'] = user_id

        serializer = self.serializer_class(data=request.data)
    
        try:    
            if serializer.is_valid():
                file = request.FILES.get('files', None)
                file_url = self.save_file(file) if file else None

                serializer.save(files=file_url)

                response_data = serializer.data
                response_data['files'] =  None

                if file_url is not None:
                    response_data['file_path'] = request.build_absolute_uri('/' + file_url)

                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValueError:
            return Response({"message": "All fields are required"})
            
    def destroy(self, request, *args, **kwargs):
        """
        Deletes a review object from the database.

        Args:
            self: The ReviewViewSet instance.
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the review is deleted successfully,
                     otherwise an error response.
        """
        try:
            review = self.get_object()
            review.delete()
            return Response({"message": "Review deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
        

    def get_entity_details(self, review):
        """
        Retrieves the details of an entity based on the provided review object.
        
        Args:
            self: The instance of the class.
            review: The review object containing the entity type and ID.
        
        Returns:
            dict: A dictionary containing the details of the entity. The dictionary has keys based on the entity's data.
        
        Raises:
            NotFound: If the entity type is not supported or if the entity is not found.
        """
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
        """
        Retrieves a queryset of items, serializes each item, adds entity details to the serialized data, and returns a response with the serialized data.
        
        Parameters:
            self: reference to the current instance of the class
            request: the request object
            *args: variable length argument list
            **kwargs: variable length keyword argument list
        
        Returns:
            Response object with serialized data and HTTP 200 status
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        for review in serializer.data:
            review['entity_details'] = self.get_entity_details(Review.objects.get(id=review['id']))
        return Response(serializer.data, status=status.HTTP_200_OK)

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