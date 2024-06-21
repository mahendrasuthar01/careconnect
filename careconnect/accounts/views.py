import jwt
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer, LoginSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer, VerifyOTPSerializer
from .authentication import JWTAuthentication
from .email_utils import EmailUtil

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user_obj = User.objects.get(email=email)
            if user_obj:
                if user_obj.check_password(password):
                    token = JWTAuthentication.generate_jwt(user_obj)
                    return_dict = {
                        'user': {'email': user_obj.email},
                        'token': {'type': 'Bearer', 'token': token}
                    }
                    return Response(return_dict, status=status.HTTP_200_OK)
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
        
            try:
                user = User.objects.get(email=email)
                if user.verify_otp(otp):
                    return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):

        """
        Handles the POST request for resetting the password.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.

        Raises:
            User.DoesNotExist: If the user is not found.

        This function validates the request data using the RequestPasswordResetSerializer. If the data is valid, it retrieves the user with the given email from the User model. It then generates and saves an OTP (One-Time Password) for the user. An email is sent to the user with the OTP. The email subject is 'Your OTP Code' and the email body contains the OTP. If the user is not found, a response with status code 404 and error message 'User not found' is returned. If the data is not valid, a response with status code 400 and serializer errors is returned. If the data is valid and the user is found, a response with status code 200 and message 'OTP sent successfully' is returned.
        """

        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                user.generate_otp()  # Generates and saves the OTP
                send_email_data = {
                    'email_subject': 'Your OTP Code',
                    'email_body': f'Your OTP Code is {user.otp}',
                    'to_email': user.email
                }
                EmailUtil.send_email(send_email_data)
                return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        """
        Resets the password for a user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object.

        Raises:
            User.DoesNotExist: If the user is not found.

        """
        
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                if user.verify_otp(otp):
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

