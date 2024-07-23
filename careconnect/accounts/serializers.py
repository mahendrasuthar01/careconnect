from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
from .models import User, Patient
from .email_utils import EmailUtil

class UserSerializer(DocumentSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):

        """
        Validates the given attributes for the username and email.

        Args:
            attrs (dict): A dictionary containing the attributes to be validated.

        Raises:
            serializers.ValidationError: If the username or email already exists.

        Returns:
            dict: The validated attributes.
        """

        username = attrs.get('username')
        email = attrs.get('email')

        if self.instance:
            return attrs

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
    # user_id = serializers.CharField()
    email = serializers.CharField()
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ['email', 'password']


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class ForgotPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

class ResetPasswordProfileSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        fields = ['current_password', 'new_password']

    def validate_current_password(self, value):
        if value is None or not value:
            raise serializers.ValidationError({"current_password": "Field required."})
        return value

    def validate_new_password(self, value: str):
        if not value:
            raise serializers.ValidationError({"new_password": "Field required."})
        return value

class ResetPasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()

    class Meta:
        fields = ['email', 'new_password']


class PatientSerializer(DocumentSerializer):
    user = UserSerializer(source='user_id', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    class Meta:
        model = Patient
        include = '__all__'

    def validate_name(self, value):
        """
        Ensure the name field returns an empty string if no value is provided.
        """
        return value or ""
    
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
        user_id = validated_data['user_id']

        validated_data['patient_name'] = validated_data.get('patient_name', '')

        if booking_for == 'Self':

            user = User.objects.get(id=user_id.id)
            
            validated_data['patient_name'] = user.username if hasattr(user, 'username') else ''
            validated_data['gender'] = user.gender if hasattr(user, 'gender') else ''
            validated_data['age'] = user.dob if hasattr(user, 'dob') else ''

        elif booking_for == 'Other':
            validated_data.get('patient_name', '')

            if validated_data['patient_name'] == '' or validated_data['gender'] == None or validated_data['age'] == None:
                raise serializers.ValidationError({"error": {"message": "Please select all fields"}})

        else:
            raise serializers.ValidationError({"error": {"message": "Please select all fields"}})

        patient = Patient(**validated_data)
        patient.save()
        return patient
