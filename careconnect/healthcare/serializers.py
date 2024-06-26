from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework import serializers
import os
from django.conf import settings

class CategorySerializer(DocumentSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    

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