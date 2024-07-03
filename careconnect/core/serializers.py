from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Favorite, Location, Review
from rest_framework import serializers
from django.conf import settings


class FavoriteSerializer(DocumentSerializer):
    class Meta:
        model = Favorite
        fields = ['entity_id', 'entity_type']

class LocationSerializer(DocumentSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ReviewSerializer(DocumentSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Review
        exclude = ['user_id']

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else getattr(obj, 'files', None)
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'{settings.MEDIA_URL}review_files/{files_url}')
        return None