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
    created_at_date_formatted = serializers.SerializerMethodField()
    created_at_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        exclude = ['cancellation_reason', 'cancellation_time']

    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)
    
    def get_created_at_date_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%d %b, %Y')
        return None
        
    def get_created_at_time_formatted(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%I:%M %p')
        return None

    
class AppointmentCancellationSerializer(DocumentSerializer):
    appointment_id = serializers.CharField(write_only=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        exclude = ['doctor_id', 'package_id', 'patient_id', 'booking_id', 'created_at', 'confirm', 'status']

    def validate_appointment_id(self, value):
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found")
        return value
    


    def update(self, instance, validated_data):
        instance.status = AppointmentStatusChoice.CANCELLED
        instance.cancellation_reason = validated_data.get('cancellation_reason', instance.cancellation_reason)
        instance.save()
        return instance
    

