import jwt
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import User, Patient
from .serializers import UserSerializer, LoginSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer, VerifyOTPSerializer, PatientSerializer
from .authentication import JWTAuthentication
from .email_utils import EmailUtil

class UserViewSet(viewsets.ModelViewSet):

    """
    Allows users to register.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):

        """
        Deletes a user object from the database.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the user is deleted successfully,
                     otherwise an error response.

        Raises:
            Exception: If the user is not found in the database.
        """

        try:
            user = self.get_object()
            user.delete()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class CustomLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):

        """
        Handles the HTTP POST request for logging in a user.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the user's email and token,
                     if the login is successful. Otherwise, returns an error response.

        Raises:
            ValidationError: If the serializer is not valid.

        """

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

        """
        Handles the POST request for verifying OTP.
        
        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        
        Returns:
            Response: The HTTP response object with a message if OTP is verified successfully, 
                      otherwise an error response.
        """

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
                return Response({'message': 'OTP sent successfully', 'otp': user.otp}, status=status.HTTP_200_OK)
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
        


class PatientViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()

    def destroy(self, request, *args, **kwargs):

        """
        Deletes a patient object from the database.

        Args:
            request (Request): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object with a message if the patient is deleted successfully, 
                     otherwise an error response.

        Raises:
            Exception: If the patient is not found in the database.
        """

        try:
            patient = self.get_object()
            patient.delete()
            return Response({"message": "Patient deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

class PatientsByUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PatientSerializer

    def get(self, request, user_id):

        """
        Retrieves all patients associated with a specific user.

        Args:
            request (Request): The HTTP request object.
            user_id (int): The ID of the user.

        Returns:
            Response: If patients are found, returns a Response object with the serialized patient data and a 200 status code.
                     If no patients are found, returns a Response object with an error message and a 404 status code.
                     If an exception occurs, returns a Response object with the error message and a 500 status code.
        """

        try:
            patients = Patient.objects.filter(user=user_id)
            if not patients:
                return Response({"error": {"message": "No patients found for this user"}}, status=status.HTTP_404_NOT_FOUND)
            serializer = PatientSerializer(patients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"message": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)