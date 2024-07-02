from mongoengine import Document, StringField, URLField, EmailField, ReferenceField, CASCADE, IntField, BooleanField, FloatField
from django.db import models
from django.utils import timezone
from accounts.models import User
from core.models import Review, Location
import os
# Create your models here.

class Category(Document):
    name = StringField(max_length=100, unique=True)
    description = StringField(max_length=500, blank=True, null=True)
    files = StringField()

    def __str__(self):
        return self.name
    

class WorkingTime(Document):
    entity_id = StringField()
    entity_type = IntField(max_length=100, choices=
        [(1, "Doctor"),
        (2, "Hospital")])
    day = StringField() 
    start_time = StringField(max_length=5, required=True)
    end_time = StringField(max_length=5, required=True)


    meta = {
        'indexes': [
            'entity_id',
            'entity_type',
            'day',
            'start_time',
            'end_time',
        ]
    }

    def __str__(self):
        return f"WorkingTime ID: {self.id}, Entity ID: {self.entity_id}, Day: {self.day}"
    

class Hospital(Document):
    category_id = ReferenceField(Category, reverse_delete_rule=CASCADE, max_length=255, required=True)
    name = StringField(max_length=255, required=True)
    review_id = StringField()
    website = URLField(max_length=200, blank=True, null=True)
    phone_number = StringField(max_length=10, required=True)
    email = EmailField(max_length=254, required=True)
    location_id = StringField()
    working_time_id = ReferenceField(WorkingTime, reverse_delete_rule=CASCADE, max_length=255)
    address = StringField(max_length=255, required=True)
    specialist = StringField(max_length=255, required=True)
    is_favorite = BooleanField(default=False)
    files = StringField()


    def __str__(self):
        return self.name
    

class Doctor(Document):
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE, max_length=255, required=True)
    name = StringField(max_length=255, required=True)
    speciality_id = ReferenceField(Category, reverse_delete_rule=CASCADE, max_length=255, required=True)
    working_time_id = ReferenceField(WorkingTime, reverse_delete_rule=CASCADE, max_length=255)
    about = StringField() 
    location_id = StringField(max_length=255)
    is_active = BooleanField(default=True)
    is_favorite = BooleanField(default=False)
    total_experience = IntField()
    total_patients = IntField()
    review_id = StringField()
    hospital_id = ReferenceField(Hospital, reverse_delete_rule=CASCADE, max_length=255)
    files = StringField()

    def __str__(self):
        return self.name