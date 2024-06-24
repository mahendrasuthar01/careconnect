from .healthcare.models import WorkingTime

class WorkingTimeManager:
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    days_of_week_choices = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday")
    )

    @classmethod
    def create_default_working_time(cls, entity, default_times):
        entity_type = entity.__class__.__name__
        entity_id = entity.id

        for day, day_name in cls.days_of_week_choices:
            # Fetch default times from frontend JSON or use class defaults
            start_time = default_times.get(day_name, '09:00')
            end_time = default_times.get(day_name, '17:00')

            working_time = WorkingTime.objects.create(
                entity_id=entity_id,
                entity_type=entity_type,
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            working_time.save()