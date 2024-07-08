from mongoengine import Document, StringField, IntField, ReferenceField, CASCADE, DateTimeField, BooleanField
from healthcare.models import Doctor
from accounts.models import Patient, User
from mongoengine.signals import pre_save
import random, string
from datetime import datetime



class PackageChoice:
    MESSAGING = 1
    VOICE_CALL = 2
    VIDEO_CALL = 3
    IN_PERSON = 4
    CHOICES = [
        (MESSAGING, 'Messaging'),
        (VOICE_CALL, 'Voice Call'),
        (VIDEO_CALL, 'Video Call'),
        (IN_PERSON, 'In-Person')
    ]


class AppointmentStatusChoice:
    UPCOMING = 1
    COMPLETED = 2
    CANCELLED = 3
    CHOICES = [
        (UPCOMING, 'Upcoming'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled')
    ]


class DoctorPackage(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    duration = StringField(max_length=100, default='15')
    package_type = IntField(max_length=100, choices=PackageChoice.CHOICES)
    amount = IntField(default=20)


class Appointment(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    package_id = ReferenceField(DoctorPackage, reverse_delete_rule=CASCADE, required=True)
    patient_id = ReferenceField(Patient, reverse_delete_rule=CASCADE, required=True)
    booking_id = StringField(max_length=9, default=lambda: 'DR' + ''.join(random.choices(string.digits, k=7)))
    created_at = DateTimeField(required=True, auto_now_add=True)
    confirm = BooleanField(default=False)
    status = IntField(max_length=100, choices=AppointmentStatusChoice.CHOICES)
    cancellation_reason = StringField(max_length=500)
    cancellation_time = DateTimeField(required=False, auto_now_add=True)
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE)

    @property
    def doctor(self):
        return self.package_id.doctor_id

    @doctor.setter
    def doctor(self, value):
        self.package_id.doctor_id = value

def set_doctor_id(sender, document, **kwargs):
    if not document.doctor_id:
        document.doctor_id = document.package_id.doctor_id

pre_save.connect(set_doctor_id, sender=Appointment)