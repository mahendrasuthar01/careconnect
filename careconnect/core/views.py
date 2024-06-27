from django.shortcuts import render
from rest_framework import viewsets, status
from .serializers import FavoriteSerializer, LocationSerializer, ReviewSerializer
from rest_framework.permissions import AllowAny
from .models import Favorite, Location, Review
from rest_framework.response import Response
import os
from django.conf import settings

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
        
        
class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [AllowAny]
    queryset = Location.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            location = self.get_object()
            location.delete()
            return Response({"message":"Location deleted sucessfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error":"Location not found"}, status=status.HTTP_404_NOT_FOUND)
        

