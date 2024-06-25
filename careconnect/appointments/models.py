from mongoengine import Document, StringField, IntField, ReferenceField, CASCADE, DateTimeField, BooleanField
from healthcare.models import Doctor

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

class DoctorPackage(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    duration = StringField(max_length=100, default='15')
    package = StringField(max_length=100, choices=PackageChoice.CHOICES)
    amount = IntField(default=0)

class Appointment(Document):
    doctor_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    patient_id = ReferenceField(Doctor, reverse_delete_rule=CASCADE, required=True)
    package_id = ReferenceField(DoctorPackage, reverse_delete_rule=CASCADE, required=True)
    date = DateTimeField(required=True)
    time = StringField(required=True)
    # confirm_status = 