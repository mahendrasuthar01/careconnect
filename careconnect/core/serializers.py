from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Favorite, Location, Review

class FavoriteSerializer(DocumentSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

class LocationSerializer(DocumentSerializer):
    class Meta:
        model = Location
        fields = '__all__'

