from mongoengine import Document, StringField, URLField, EmailField
from django.db import models
from django.utils import timezone
# Create your models here.

class Category(Document):
    name = StringField(max_length=100, unique=True)
    description = StringField(max_length=500, blank=True, null=True)

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
    category_id = StringField(max_length=255, required=True)
    name = StringField(max_length=255, required=True)
    review_id = StringField(max_length=255)
    website = URLField(max_length=200, blank=True, null=True)
    phone_number = StringField(max_length=10, required=True)
    email = EmailField(max_length=254, required=True)
    location_id = StringField()
    working_time_id = StringField(max_length=255)

    def __str__(self):
        return self.name
    

class Doctor(Document):
    user_id = StringField(max_length=255, required=True)
    name = StringField(max_length=255, required=True)
    speciality_id = StringField(max_length=255)
    working_time_id = StringField(max_length=255)
    about = models.TextField()
    location_id = StringField(max_length=255)
    sign_up_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    total_experience = models.IntegerField()
    total_patients = models.IntegerField()
    review_id = StringField(max_length=255)
    hospital_id = StringField(max_length=255, required=True)

    def __str__(self):
        return self.name