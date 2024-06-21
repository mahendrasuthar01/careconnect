from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category

class CategorySerializer(DocumentSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        return Category.objects.create(**validated_data)