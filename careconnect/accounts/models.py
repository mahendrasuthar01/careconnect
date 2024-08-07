# from django.db import models
from mongoengine import Document, StringField, DateField, EmailField, DateTimeField, BooleanField, ReferenceField, CASCADE
from django.contrib.auth.hashers import make_password, check_password
import random
import string
from datetime import datetime, timedelta

class User(Document):
    username = StringField(max_length=100)
    email = EmailField()
    password = StringField(max_length=100, null=False, blank=False)
    phone_number = StringField(max_length=15, blank=True, null=True)
    dob = DateField(blank=True, null=True)
    gender = StringField(max_length=10, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    updated_by = StringField(max_length=100, blank=True, null=True)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    location_id = ReferenceField('core.models.Location', max_length=100, blank=True, null=True)
    is_email_verified = BooleanField(default=False)
    otp = StringField(max_length=4, blank=True, null=True)
    otp_expires_at = DateTimeField(blank=True, null=True)

    @property
    def is_authenticated(self):
        return True

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=4))
        # self.otp = '0000'
        self.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
        self.save()

    def verify_otp(self, otp):
        if self.otp == otp and self.otp_expires_at > datetime.utcnow():
        # if self.otp == otp:
            self.is_email_verified = True
            # self.otp = None
            # self.otp_expires_at = None
            self.save()
            return True
        return False
    
class BookingForChoices:
    SELF = 'Self'
    OTHER = 'Other'
    SELECT = ''
    CHOICES = [
        (SELF, 'Self'),
        (OTHER, 'Other'),
        (SELECT, '')
    ]

class Patient(Document):
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    patient_name = StringField(max_length=100, default='', blank=True, null=True)
    booking_for = StringField(max_length=100, choices=BookingForChoices.CHOICES, default='Self')
    gender = StringField(max_length=10, blank=True, null=True)
    age = StringField(max_length=10, blank=True, null=True)
    problem_description = StringField(max_length=500, blank=True, null=True)

