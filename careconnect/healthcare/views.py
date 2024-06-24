from django.shortcuts import render
from .models import Category, WorkingTime, Hospital
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer
from mongoengine.errors import ValidationError
from django.http import Http404
from mongoengine.errors import DoesNotExist

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
            raise Http404("Working-Time with the given ID not found.")

        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            instance = WorkingTime.objects.get(pk=pk)
        except (WorkingTime.DoesNotExist, ValidationError):
            raise Http404("Working-Time with the given ID not found.")

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class HospitalViewSet(viewsets.ModelViewSet):
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Hospital.objects.all()

    def get_object(self, pk):
        try:
            return Hospital.objects.get(pk=pk)
        except (DoesNotExist, ValidationError):
            raise Http404("Hospital with the given ID not found.")

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        instance = self.get_object(pk)
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        instance = self.get_object(pk)
        serializer = self.serializer_class(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        instance = self.get_object(pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)