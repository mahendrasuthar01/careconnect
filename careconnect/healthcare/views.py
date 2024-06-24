from django.shortcuts import render, get_object_or_404
from .models import Category, WorkingTime, Hospital, Doctor
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .serializers import CategorySerializer, WorkingTimeSerializer, HospitalSerializer, DoctorSerializer
from mongoengine.errors import ValidationError
from django.http import Http404
from mongoengine.errors import DoesNotExist

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class WorkingTimeViewSet(viewsets.ModelViewSet):
    queryset = WorkingTime.objects.all()
    serializer_class = WorkingTimeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        serializer = self.get_serializer()
        try:
            response_data = serializer.delete_instance(pk)
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'message': 'Working-Time not found'}, status=status.HTTP_404_NOT_FOUND)
    

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        serializer = self.get_serializer()
        try:
            response_data = serializer.delete_instance(pk)
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'message': 'Hospital not found'}, status=status.HTTP_404_NOT_FOUND)
    
    

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
     
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        serializer = self.get_serializer()
        try:
            response_data = serializer.delete_instance(pk)
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)