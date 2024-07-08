from .models import DoctorPackage, Appointment, AppointmentStatusChoice
from .serializers import DoctorPackageSerializer, AppointmentSerializer, AppointmentCancellationSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from datetime import datetime
from accounts.authentication import JWTAuthentication

# Create your views here.
class DoctorPackageViewset(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DoctorPackageSerializer
    queryset = DoctorPackage.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            package = self.get_object()
            package.delete()
            return Response({"message": "Package deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Package not found"}, status=status.HTTP_404_NOT_FOUND)
        

class AppointmentViewset(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            return Appointment.objects.filter(doctor_id=doctor_id)
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        try:
            appointment = self.get_object()
            appointment.delete()
            return Response({"message": "Appointment deleted successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def update(self, request, *args, **kwargs):
        try:
            appointment = self.get_object()
            serializer = self.get_serializer(appointment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
class AppointmentsByUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = AppointmentSerializer
            
    def get(self, request, user_id):
        try:
            appointments = Appointment.objects.filter(user_id=user_id)
            if not appointments:
                return Response({"error": {"message": "No appointments found for this user"}}, status=status.HTTP_404_NOT_FOUND)
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": {"message": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class AppointmentCancellationView(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentCancellationSerializer
    permission_classes = [AllowAny]

    def partial_update(self, request, *args, **kwargs):
        try:
            appointment_id = request.data.get('appointment_id')
            if not appointment_id:
                return Response({"error": "Appointment ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            appointment = self.queryset.filter(id=appointment_id).first()
            if not appointment:
                return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

            appointment.status = AppointmentStatusChoice.CANCELLED
            cancellation_reason = request.data.get('cancellation_reason')
            cancellation_time = datetime.now()
            if cancellation_reason:
                appointment.cancellation_reason = cancellation_reason
                appointment.cancellation_time = cancellation_time
            appointment.save()

            serializer = self.get_serializer(appointment)
            return Response({"message": "Appointment cancelled successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
