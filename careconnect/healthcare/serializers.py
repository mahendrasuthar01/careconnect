from rest_framework_mongoengine.serializers import DocumentSerializer
from .models import Category, WorkingTime, Hospital, Doctor
from django.http import Http404

class CategorySerializer(DocumentSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    

class WorkingTimeSerializer(DocumentSerializer):
    class Meta:
        model = WorkingTime
        fields = '__all__'

    def delete_instance(self, pk):
        try:
            instance = WorkingTime.objects.get(pk=pk)
            instance.delete()
            return {'message': 'WorkingTime deleted successfully'}
        except WorkingTime.DoesNotExist:
            raise Http404("WorkingTime not found")


class HospitalSerializer(DocumentSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'

    def delete_instance(self, pk):
        try:
            instance = Hospital.objects.get(pk=pk)
            instance.delete()
            return {'message': 'Hospital deleted successfully'}
        except Hospital.DoesNotExist:
            raise Http404("Hospital not found")


class DoctorSerializer(DocumentSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

    def delete_instance(self, pk):
        try:
            instance = Doctor.objects.get(pk=pk)
            instance.delete()
            return {'message': 'Doctor deleted successfully'}
        except Doctor.DoesNotExist:
            raise Http404("Doctor not found")