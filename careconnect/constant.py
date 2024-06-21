from .healthcare.models import WorkingTime

# // Prashnsha will improve this

def create_default_working_time(entity_id, entity_type):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    default_start_time = '09:00'
    default_end_time = '17:00'

    for day in weekdays:
        working_time = WorkingTime.objects.create(
            entity_id=entity_id,
            entity_type=entity_type,
            day=day,
            start_time=default_start_time,
            end_time=default_end_time
        )
        working_time.save()
