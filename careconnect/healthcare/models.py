from mongoengine import Document, StringField, URLField, EmailField
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
    category_id = StringField(max_length=255)
    name = StringField(max_length=255)
    review_id = StringField(max_length=255)
    website = URLField(max_length=200, blank=True, null=True)
    phone_number = StringField(max_length=10)
    email = EmailField(max_length=254)
    location_id = StringField()
    working_time_id = StringField(max_length=255)

    def __str__(self):
        return self.name