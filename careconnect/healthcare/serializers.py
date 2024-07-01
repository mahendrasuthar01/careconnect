from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework import serializers
from django.conf import settings
from core.models import Review
from django.db.models import Avg


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

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + 'uploaded_files/' + files_url)
            else:
                # Handle case where request is not available
                return settings.MEDIA_URL + 'uploaded_files/' + files_url
        return None
      
    class Meta:
        model = Hospital
        fields = '__all__'

class DoctorSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else obj.files
        
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(settings.MEDIA_URL + 'uploaded_files/' + files_url)
            else:
                # Handle case where request is not available
                return settings.MEDIA_URL + 'uploaded_files/' + files_url
        return None

    class Meta:
        model = Doctor
        fields = '__all__'

from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers

class HospitalCardSerializer(DocumentSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ['name', 'files', 'location_id', 'average_rating']

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)
    

class DoctorCardSerializer(DocumentSerializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['name', 'speciality_id', 'files', 'is_favorite', 'location_id', 'review_count', 'average_rating']

    def get_review_count(self, obj):
        return getattr(obj, 'review_count', 0)

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)
