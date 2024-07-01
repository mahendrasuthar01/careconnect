from .models import DoctorPackage, Appointment
from .serializers import DoctorPackageSerializer, AppointmentSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

# Create your views here.
class DoctorPackageViewset(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = DoctorPackage.objects.all()
    serializer_class = DoctorPackageSerializer

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

    # http://127.0.0.1:8000/appointments/appointments/?doctor_id=667ac517e10c5c23626764a6
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
    
    