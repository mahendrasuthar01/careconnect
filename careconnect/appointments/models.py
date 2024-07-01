from mongoengine import Document, StringField, IntField, ReferenceField, CASCADE, DateTimeField, BooleanField
from healthcare.models import Doctor
from accounts.models import Patient
from mongoengine.signals import pre_save
from django.dispatch import receiver
import random
import string



class PackageChoice:
    MESSAGING = 'messaging'
    VOICE_CALL = 'voice_call'
    VIDEO_CALL = 'video_call'
    IN_PERSON = 'in_person'
    CHOICES = [
        (MESSAGING, 'Messaging'),
        (VOICE_CALL, 'Voice Call'),
        (VIDEO_CALL, 'Video Call'),
        (IN_PERSON, 'In-Person')
    ]


class AppointmentStatusChoice:
    UPCOMING = 'upcoming'
    COMPLETED = 'completed'
    CANCELLED = 'canceled'
    CHOICES = [
        (UPCOMING, 'Upcoming'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled')
    ]


class DoctorPackage(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    duration = StringField(max_length=100, default='15')
    package = StringField(max_length=100, choices=PackageChoice.CHOICES)
    amount = IntField(default=0)


class Appointment(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    package_id = ReferenceField(DoctorPackage, reverse_delete_rule=CASCADE, required=True)
    patient_id = ReferenceField(Patient, reverse_delete_rule=CASCADE, required=True)
    booking_id = StringField(max_length=9, default=lambda: 'DR' + ''.join(random.choices(string.digits, k=7)))
    date = DateTimeField(required=True)
    time = StringField(required=True)
    confirm = BooleanField(default=False)
    status = StringField(max_length=100, choices=AppointmentStatusChoice.CHOICES)
    cancellation_reason = StringField(max_length=500)

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