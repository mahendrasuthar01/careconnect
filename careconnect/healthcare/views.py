from django.shortcuts import render
from .models import Category
from rest_framework_mongoengine import viewsets
from rest_framework.permissions import AllowAny
from .serializers import CategorySerializer

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer