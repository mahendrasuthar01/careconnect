from django.shortcuts import render
from .models import Category, WorkingTime
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer
from mongoengine.errors import ValidationError
from django.http import Http404

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WorkingTimeViewSet(viewsets.ModelViewSet):
    serializer_class = WorkingTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = WorkingTime.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            instance = WorkingTime.objects.get(pk=pk)
            serializer = self.serializer_class(instance)
            return Response(serializer.data)
        except (WorkingTime.DoesNotExist, ValidationError):
            raise Http404

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        try:
            instance = WorkingTime.objects.get(pk=pk)
        except (WorkingTime.DoesNotExist, ValidationError):
            raise Http404

        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            instance = WorkingTime.objects.get(pk=pk)
        except (WorkingTime.DoesNotExist, ValidationError):
            raise Http404

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)