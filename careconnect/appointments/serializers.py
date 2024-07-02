from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import DoctorPackage, Appointment, AppointmentStatusChoice
from mongoengine import StringField

class DoctorPackageSerializer(DocumentSerializer):
    class Meta:
        model = DoctorPackage
        fields = '__all__'
    
    def create(self, validated_data):
        return DoctorPackage.objects.create(**validated_data)
    

class AppointmentSerializer(DocumentSerializer):
    doctor_id = serializers.StringRelatedField(source='doctor_id.id', read_only=True)
    booking_id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = '__all__'

    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)
    
class AppointmentCancellationSerializer(serializers.Serializer):
    cancellation_reason = serializers.CharField(max_length=500)
    status = StringField(max_length=100, choices=AppointmentStatusChoice.CHOICES)

    def validate_status(self, value):
        if value == AppointmentStatusChoice.CANCELLED:
            raise serializers.ValidationError("Status cannot be cancelled")
        return value
    
    