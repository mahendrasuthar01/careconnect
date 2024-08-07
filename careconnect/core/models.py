from mongoengine import Document,StringField, ReferenceField, IntField, CASCADE, StringField, FloatField, DateTimeField, DecimalField
from accounts.models import User
from constant import EntityChoices
from datetime import datetime

# Create your models here.
class Entity(Document):
    ENTITY_TYPE_CHOICES = EntityChoices.CHOICES
    entity_type = StringField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    name = StringField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.entity_type})"

class Favorite(Document):
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE, max_length=255, required=True)
    entity_id = StringField(max_length=255, required=True)
    entity_type = IntField(max_length=100, choices=
        [(1, "Doctor"),
        (2, "Hospital")])

class Location(Document):
    address = StringField(max_length=255, required=True)
    street = StringField(max_length=255)
    neighborhood = StringField()
    city = StringField(max_length=255, required=True)
    state = StringField(max_length=255, required=True)
    country = StringField(max_length=255, required=True)
    latitude = DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)
    longitude = DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)

class Review(Document):
    entity_id = StringField(max_length=255, required=True)
    entity_type = IntField(max_length=100, choices=
        [(1, "Doctor"),
        (2, "Hospital")])
    user_id = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    rating = FloatField(default=0.0, min_value=0.0, max_value=5.0)    
    description = StringField(required=False, null=True)
    files = StringField(required=False)
    created_at = DateTimeField(default=datetime.utcnow, required=True)