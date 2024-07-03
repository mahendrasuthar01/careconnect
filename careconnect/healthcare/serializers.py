from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework import serializers
from django.conf import settings
from .utils import get_entity_reviews, get_hospital_specialists


class CategorySerializer(DocumentSerializer):
    files = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Category
        fields = '__all__'

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else getattr(obj, 'files', None)
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'{settings.MEDIA_URL}category_files/{files_url}')
        return None

class WorkingTimeSerializer(DocumentSerializer):
    class Meta:
        model = WorkingTime
        fields = '__all__'


class HospitalSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()
    calegory = CategorySerializer(source='category_id')
    working_time = WorkingTimeSerializer(source='working_time_id')
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    speciaists = serializers.SerializerMethodField()

    def get_review_count(self, obj):
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)

    def get_reviews(self, obj):
        hospital_id = str(obj.id)
        return get_entity_reviews(hospital_id, 2)
    
    def get_speciaists(self, obj):
        hospital_id = str(obj.id)
        return get_hospital_specialists(hospital_id)

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + 'uploaded_files/' + files_url)
            else:
                return settings.MEDIA_URL + 'uploaded_files/' + files_url
        return None
      
    class Meta:
        model = Hospital
        fields = '__all__'

class DoctorSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()
    speciality = CategorySerializer(source='speciality_id')
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = '__all__'

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + 'uploaded_files/' + files_url)
            else:
                return settings.MEDIA_URL + 'uploaded_files/' + files_url
        return None

    def get_review_count(self, obj):
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)

    def get_reviews(self, obj):
        doctor_id = str(obj.id)
        return get_entity_reviews(doctor_id, 1)  # Assuming 1 represents the doctor entity type


class HospitalCardSerializer(DocumentSerializer):
    hospital_id = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ['hospital_id', 'name', 'files', 'location_id', 'is_favorite', 'average_rating', 'review_count']

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)

    def get_review_count(self, obj):
        return getattr(obj, 'review_count', 0)
    
    def get_hospital_id(self, obj):
        return getattr(obj, 'hospital_id', None)

class DoctorCardSerializer(DocumentSerializer):
    doctor_id = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    speciality = CategorySerializer(source='speciality_id')

    class Meta:
        model = Doctor
        fields = ['doctor_id', 'name', 'speciality_id', 'files', 'is_favorite', 
                  'location_id', 'review_count', 'average_rating', 'speciality']

    def get_review_count(self, obj):
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)
    
    def get_doctor_id(self, obj):
        return getattr(obj, 'doctor_id', None)

