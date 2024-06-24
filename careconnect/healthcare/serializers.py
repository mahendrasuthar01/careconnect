from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital

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
    class Meta:
        model = Hospital
        fields = '__all__'