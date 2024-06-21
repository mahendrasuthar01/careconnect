from mongoengine import Document, StringField
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
    start_time = StringField(max_length=5)
    end_time = StringField(max_length=5)


    meta = {
        'indexes': [
            'entity_id',
            'entity_type',
            'day',
            'start_time',
            'end_time',
        ]
    }