import jwt
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import User, Category
from .serializers import UserSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, CategorySerializer
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
        email = request.data.get('email')
        otp = request.data.get('otp')
        print("---------email---------",email)

        try:
            user = User.objects.get(email=email)
            if user.verify_otp(otp):
                return Response({'message': 'Email successfully verified'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        user.generate_otp()

        send_email_data = {
            'email_subject': 'Your OTP Code',
            'email_body': f'Your OTP Code is {user.otp}',
            'to_email': user.email
        }
        EmailUtil.send_email(send_email_data)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            if user.verify_otp(otp):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer