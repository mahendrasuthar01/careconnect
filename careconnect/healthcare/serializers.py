from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework import serializers
from django.conf import settings
from .utils import get_entity_reviews, get_hospital_specialists
from core.serializers import LocationSerializer


class CategorySerializer(DocumentSerializer):
    files = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Category
        fields = '__all__'

    def get_files(self, obj):
        """
        A function that retrieves the files URL for a given object.
        
        Parameters:
            self: The serializer instance.
            obj: The object from which to retrieve the files URL.
        
        Returns:
            The absolute URI of the files URL if it exists, otherwise None.
        """
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            if files_url.startswith('media/'):
                files_url = files_url[len('media/'):]
            
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + files_url)
            else:
                return settings.MEDIA_URL + files_url
        return None

class WorkingTimeSerializer(DocumentSerializer):
    class Meta:
        model = WorkingTime
        fields = '__all__'


class HospitalSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()
    category = CategorySerializer(source='category_id', read_only=True)
    working_time = WorkingTimeSerializer(source='working_time_id', read_only=True)
    location = LocationSerializer(source='location_id', read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    speciaists = serializers.SerializerMethodField()
    entity_type = serializers.SerializerMethodField()
    working_time = WorkingTimeSerializer(source='working_time_id', read_only=True)

    class Meta:
        model = Hospital
        fields = '__all__'

    def get_review_count(self, obj):
        """
        Retrieves the review count from the provided object.
        
        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the review count.
        
        Returns:
            int: The review count if available, otherwise 0.
        """
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        """
        Get the average rating of an object.

        Args:
            obj (object): The object to get the average rating from.

        Returns:
            float: The average rating of the object. If the object does not have an attribute called 'average_rating', 0.0 is returned.
        """
        return getattr(obj, 'average_rating', 0.0)

    def get_reviews(self, obj):
        """
        Retrieves the reviews for a hospital entity.

        Parameters:
            self: The object itself.
            obj: The hospital object for which to retrieve the reviews.

        Returns:
            list: A list of serialized reviews for the hospital.
        """
        hospital_id = str(obj.id)
        return get_entity_reviews(hospital_id, 2)
    
    def get_speciaists(self, obj):
        """
        Retrieves the specialists for a hospital entity.

        Args:
            self: The object itself.
            obj: The hospital object for which to retrieve the specialists.

        Returns:
            list: A list of serialized specialists for the hospital.
        """
        hospital_id = str(obj.id)
        return get_hospital_specialists(hospital_id)
    
    def get_entity_type(self, obj):
        """
        Retrieves the entity type from the provided object.

        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the entity type.

        Returns:
            int: The entity type if available, otherwise 2.
        """
        return getattr(obj, 'entity_type', 2)

    def get_files(self, obj):
        """
        Retrieves the files URL for a given object.

        Parameters:
            obj (dict or object): The object from which to retrieve the files URL.

        Returns:
            str or None: The absolute URI of the files URL if it exists, otherwise None.
        """
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            if files_url.startswith('media/'):
                files_url = files_url[len('media/'):]
            
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + files_url)
            else:
                return settings.MEDIA_URL + files_url
        return None
    

class DoctorSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()
    speciality = CategorySerializer(source='speciality_id', read_only=True)
    location = LocationSerializer(source='location_id', read_only=True)
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    entity_type = serializers.SerializerMethodField()
    working_time = WorkingTimeSerializer(source='working_time_id', read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'

    def get_files(self, obj):
        """
        Retrieves the absolute URL of the files associated with the given object.

        Parameters:
            obj (dict or object): The object from which to retrieve the files.

        Returns:
            str or None: The absolute URL of the files if they exist, otherwise None.
        """
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            if files_url.startswith('media/'):
                files_url = files_url[len('media/'):]
            
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + files_url)
            else:
                return settings.MEDIA_URL + files_url
        return None

    def get_review_count(self, obj):
        """
        Retrieves the review count from the provided object.
        
        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the review count.
        
        Returns:
            int: The review count if available, otherwise 0.
        """
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        """
        Retrieves the average rating from the provided object.
        
        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the average rating.
        
        Returns:
            float: The average rating if available, otherwise 0.0.
        """
        return getattr(obj, 'average_rating', 0.0)

    def get_reviews(self, obj):
        """
        Retrieves the reviews for a given doctor object.

        Args:
            self: The object itself.
            obj: The doctor object for which to retrieve the reviews.

        Returns:
            list: A list of serialized reviews for the doctor.
        """
        doctor_id = str(obj.id)
        return get_entity_reviews(doctor_id, 1)
    
    def get_entity_type(self, obj):
        """
        Retrieves the entity type from the provided object.

        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the entity type.

        Returns:
            int: The entity type if available, otherwise 1.
        """
        return getattr(obj, 'entity_type', 1)



class HospitalCardSerializer(DocumentSerializer):
    hospital_id = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    entity_type = serializers.SerializerMethodField()
    speciality = CategorySerializer(source='category_id', read_only=True)

    class Meta:
        model = Hospital
        fields = ['hospital_id', 'name', 'files', 'location_id', 'is_favorite', 'average_rating', 'review_count', 'entity_type', 'location_id', 'speciality']

    def get_average_rating(self, obj):
        """
        Retrieves the average rating from the provided object.
        
        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the average rating.
        
        Returns:
            float: The average rating if available, otherwise 0.0.
        """
        return getattr(obj, 'average_rating', 0.0)

    def get_review_count(self, obj):
        """
        Retrieves the review count from the provided object.

        Parameters:
            self (object): The object itself.
            obj (object): The object from which to retrieve the review count.

        Returns:
            int: The review count if available, otherwise 0.
        """
        return getattr(obj, 'review_count', 0)
    
    def get_hospital_id(self, obj):
        """
        Retrieves the hospital ID from the provided object.

        Parameters:
            self (object): The object itself.
            obj (object): The object from which to retrieve the hospital ID.

        Returns:
            The hospital ID if available, otherwise None.
        """
        return getattr(obj, 'hospital_id', None)
    
    def get_entity_type(self, obj):
        """
        Retrieves the entity type from the provided object.

        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the entity type.

        Returns:
            int: The entity type if available, otherwise 2.
        """
        return getattr(obj, 'entity_type', 2)
    
    def get_speciality(self, obj):
        return getattr(obj, 'category_id', None)

class DoctorCardSerializer(DocumentSerializer):
    doctor_id = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    speciality = CategorySerializer(source='speciality_id')
    entity_type = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['doctor_id', 'name', 'speciality_id', 'files', 'is_favorite', 
                  'location_id', 'review_count', 'average_rating', 'speciality', 'entity_type']

    def get_review_count(self, obj):
        """
        Get the review count from the provided object.

        Args:
            obj (object): The object from which to retrieve the review count.

        Returns:
            int: The review count if available, otherwise 0.
        """
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        """
        Retrieves the average rating from the provided object.
        
        Parameters:
            self: The object itself.
            obj: The object from which to retrieve the average rating.
        
        Returns:
            float: The average rating if available, otherwise 0.0.
        """
        return getattr(obj, 'average_rating', 0.0)
    
    def get_doctor_id(self, obj):
        """
        Retrieves the doctor ID from the given object.

        Args:
            obj (object): The object from which to retrieve the doctor ID.

        Returns:
            Union[str, None]: The doctor ID if available, otherwise None.
        """
        return getattr(obj, 'doctor_id', None)
    
    def get_entity_type(self, obj):
        """
        Retrieves the entity type from the provided object.

        Args:
            self: The object itself.
            obj: The object from which to retrieve the entity type.

        Returns:
            int: The entity type if available, otherwise 1.
        """
        return getattr(obj, 'entity_type', 1)