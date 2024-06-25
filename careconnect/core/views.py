from django.shortcuts import render
from rest_framework import viewsets, status
from .serializers import FavoriteSerializer
from rest_framework.permissions import AllowAny
from .models import Favorite
from rest_framework.response import Response

# Create your views here.
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]
    queryset = Favorite.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            favorite = self.get_object()
            favorite.delete()
            return Response({"message":"Favorite item removed sucessfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error":"Favorite item not found"}, status=status.HTTP_404_NOT_FOUND)