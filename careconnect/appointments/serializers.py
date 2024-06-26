from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import DoctorPackage, Appointment

class DoctorPackageSerializer(DocumentSerializer):
    class Meta:
        model = DoctorPackage
        fields = '__all__'
    
    def create(self, validated_data):
        return DoctorPackage.objects.create(**validated_data)
    

class AppointmentSerializer(DocumentSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)