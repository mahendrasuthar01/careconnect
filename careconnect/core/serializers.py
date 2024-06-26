from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Favorite

class FavoriteSerializer(DocumentSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'