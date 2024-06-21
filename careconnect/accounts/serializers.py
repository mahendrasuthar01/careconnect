from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import User
from .email_utils import EmailUtil

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
        if User.objects(username=username).count() > 0:
            raise serializers.ValidationError({"username": "Username already exists"})

        # Check if the email is unique
        if User.objects(email=email).count() > 0:
            raise serializers.ValidationError({"email": "Email already exists"})

        return super().validate(attrs)

    def create(self, validated_data):
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
