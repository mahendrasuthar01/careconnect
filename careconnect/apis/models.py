# from django.db import models
from mongoengine import Document, StringField, DateField, EmailField, DateTimeField, BooleanField
from django.contrib.auth.hashers import make_password, check_password


class User(Document):
    username = StringField(max_length=100, unique=True)
    email = EmailField(unique=True)
    password = StringField(max_length=100, null=False, blank=False)
    phone_number = StringField(max_length=15, blank=True, null=True)
    dob = DateField(blank=True, null=True)
    gender = StringField(max_length=10, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    updated_by = StringField(max_length=100, blank=True, null=True)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    location = StringField(max_length=100, blank=True, null=True)

    # objects = UserManager()

    @property
    def is_authenticated(self):
        return True

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        # Hash the raw password before saving
        self.password = make_password(raw_password)
        # You may want to store other password-related attributes like salt

    def check_password(self, raw_password):
        # Check if the raw password matches the stored hashed password
        return check_password(raw_password, self.password)