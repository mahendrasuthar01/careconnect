from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import User, Patient, BookingForChoices
from .email_utils import EmailUtil
from django.contrib.auth.models import AnonymousUser

class UserSerializer(DocumentSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        # Check if the username is unique
        if User.objects(username=username).count() > 0 or User.objects(email=email).count() > 0:
            raise serializers.ValidationError({"error": {"message": "Username or Email already exists"}})

        return super().validate(attrs)
        
    def create(self, validated_data):

        """
        Create a new user with the given validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the user.

        Returns:
            User
        """

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.generate_otp()
        user.save()

        email_data = {
            'email_subject': 'Your OTP Code',
            'email_body': f'Your OTP Code is {user.otp}',
            'to_email': user.email
        }

        EmailUtil.send_email(email_data)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'password']


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    otp = serializers.CharField()


class PatientSerializer(DocumentSerializer):  # Adjust DocumentSerializer as per your actual setup
    class Meta:
        model = Patient
        fields = '__all__'

    def validate(self, data):
        booking_for = data.get('booking_for')
        user = data.get('user')

        if booking_for == 'self' and not user:
            raise serializers.ValidationError({"error": {"message": "User is required when booking for self"}})
        
        return data
    
    def create(self, validated_data):
        if 'user' in validated_data and isinstance(validated_data['user'], AnonymousUser):
            validated_data['user'] = None

        check_patient_in_database = Patient.objects(
            booking_for=validated_data['booking_for'],
            name=validated_data['name'],
            user=validated_data['user'],
        )

        if check_patient_in_database:
            raise serializers.ValidationError({"error": {"message": "Patient already exists"}})

        patient = Patient(**validated_data)

        patient.save()
        return patient
