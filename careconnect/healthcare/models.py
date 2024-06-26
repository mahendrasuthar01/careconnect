from mongoengine import Document, StringField, URLField, EmailField, ReferenceField, ListField, CASCADE, ImageField
from django.db import models
from django.utils import timezone
from accounts.models import User
import os
from django.conf import settings

class Category(Document):
    name = StringField(max_length=100, unique=True)
    description = StringField(max_length=500, blank=True, null=True)
    files = StringField()
    # file_path = URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class WorkingTime(Document):
    entity_id = StringField()
    entity_type = StringField()
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
    category_id = ReferenceField(Category, reverse_delete_rule=CASCADE, required=True)
    name = StringField(max_length=255, required=True)
    review_id = StringField(max_length=255)
    website = URLField(max_length=200, blank=True, null=True)
    phone_number = StringField(max_length=10, required=True)
    email = EmailField(max_length=254, required=True)
    location_id = StringField()
    working_time_id = ReferenceField(WorkingTime, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return self.name
    

class Doctor(Document):
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    name = StringField(max_length=255, required=True)
    speciality_id = ReferenceField(Category, reverse_delete_rule=CASCADE, required=True)
    working_time_id = ReferenceField(WorkingTime, reverse_delete_rule=CASCADE, required=True)
    about = models.TextField()
    location_id = StringField(max_length=255)
    sign_up_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    total_experience = models.IntegerField()
    total_patients = models.IntegerField()
    review_id = StringField(max_length=255)
    hospital_id = ReferenceField(Hospital, reverse_delete_rule=CASCADE, required=True)

    def __str__(self):
        return self.name