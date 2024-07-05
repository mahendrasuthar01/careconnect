from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Favorite, Location, Review
from accounts.models import User
from rest_framework import serializers
from django.conf import settings
from accounts.serializers import UserSerializer


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
    user = UserSerializer(source='user_id', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    created_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Review
        include = '__all__'

    def get_created_at_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%d %b, %Y')
        return None

    def get_files(self, obj):
        files_url = obj.get('files') if isinstance(obj, dict) else getattr(obj, 'files', None)
        if files_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'{settings.MEDIA_URL}review_files/{files_url}')
        return None