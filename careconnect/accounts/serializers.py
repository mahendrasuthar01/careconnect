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


class PatientSerializer(DocumentSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
    
    def create(self, validated_data):

        """
        Create a new Patient object based on the validated data.

        Args:
            validated_data (dict): A dictionary containing the validated data for the Patient object.

        Returns:
            Patient: The newly created Patient object.

        Raises:
            serializers.ValidationError: If a Patient object with the same booking_for and user already exists.
        """

        booking_for = validated_data['booking_for']
        user = validated_data['user']

        if booking_for == 'self':
            if Patient.objects(user=user).first():
                raise serializers.ValidationError({"error": {"message": "Patient already exists"}})
            
            validated_data['name'] = user.username if hasattr(user, 'username') else ''
            validated_data['gender'] = user.gender if hasattr(user, 'gender') else ''
            validated_data['age'] = user.dob if hasattr(user, 'dob') else ''

        else:
            name = validated_data.get('name', '')
            if Patient.objects(
                booking_for='other',
                name=name,
                user=user,
            ).first():
                raise serializers.ValidationError({"error": {"message": "Patient already exists"}})

        patient = Patient(**validated_data)
        patient.save()
        return patient
