from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import DoctorPackage, Appointment, AppointmentStatusChoice
from healthcare.serializers import DoctorSerializer
from accounts.serializers import PatientSerializer

class DoctorPackageSerializer(DocumentSerializer):
    doctor = DoctorSerializer(source='doctor_id', read_only=True)
    class Meta:
        model = DoctorPackage
        fields = '__all__'
    
    def create(self, validated_data):

        """
        Creates a new DoctorPackage object based on the validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the DoctorPackage object.

        Returns:
            DoctorPackage: The newly created DoctorPackage object.
        """

        return DoctorPackage.objects.create(**validated_data)
    

class AppointmentSerializer(DocumentSerializer):
    doctor = DoctorSerializer(source='doctor_id', read_only=True)
    # doctor_name = serializers.CharField(read_only=True)
    booking_id = serializers.CharField(read_only=True)
    date_formatted = serializers.SerializerMethodField()
    time_formatted = serializers.SerializerMethodField()
    patient = PatientSerializer(source='patient_id', read_only=True)
    package = DoctorPackageSerializer(source='package_id', read_only=True)
    
    class Meta:
        model = Appointment
        exclude = ['cancellation_reason', 'cancellation_time']

    def create(self, validated_data):

        """
        Creates a new Appointment object based on the validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the Appointment object.

        Returns:
            Appointment: The newly created Appointment object.
        """

        return Appointment.objects.create(**validated_data)
    
    def get_date_formatted(self, obj):

        """
        Extracts and formats the date from the 'date_time' attribute of the provided object.

        Args:
            self: The AppointmentSerializer instance.
            obj: The object containing the 'date_time' attribute.

        Returns:
            str: The formatted date in the format '%d %b, %Y' if 'date_time' exists, None otherwise.
        """

        if obj.date_time:
            return obj.date_time.strftime('%d %b, %Y')
        return None

    def get_time_formatted(self, obj):

        """
        Extracts and formats the time from the 'date_time' attribute of the provided object.

        Args:
            self: The AppointmentSerializer instance.
            obj: The object containing the 'date_time' attribute.

        Returns:
            str: The formatted time in the format '%I:%M %p' if 'date_time' exists, None otherwise.
        """

        if obj.date_time:
            return obj.date_time.strftime('%I:%M %p')
        return None
    
    # def get_doctor_name(self, obj):

    
class AppointmentCancellationSerializer(DocumentSerializer):
    appointment_id = serializers.CharField(write_only=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        exclude = ['doctor_id', 'package_id', 'patient_id', 'booking_id', 'created_at', 'confirm', 'status']

    def validate_appointment_id(self, value):

        """
        A function that validates the appointment ID.

        Args:
            self: The AppointmentCancellationSerializer instance.
            value: The value to validate as an appointment ID.

        Returns:
            The validated appointment ID.

        Raises:
            serializers.ValidationError: If the appointment is not found.
        """

        try:
            Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found")
        return value
    
    def update(self, instance, validated_data):

        """
        A function to update an instance with the provided validated data.
        
        Parameters:
            self: The AppointmentCancellationSerializer instance.
            instance: The instance to be updated.
            validated_data: The validated data to update the instance.
        
        Returns:
            The updated instance after setting the status to 'CANCELLED' and updating the cancellation reason.
        """

        instance.status = AppointmentStatusChoice.CANCELLED
        instance.cancellation_reason = validated_data.get('cancellation_reason', instance.cancellation_reason)
        instance.save()
        return instance
    

