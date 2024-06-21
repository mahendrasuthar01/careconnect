from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import Category, WorkingTime

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
