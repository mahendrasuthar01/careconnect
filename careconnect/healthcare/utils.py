from collections import defaultdict
from core.models import Review
from .models import Doctor
from core.serializers import ReviewSerializer
import healthcare.serializers

def get_reviews_data(entity_ids, entity_type):

    reviews = Review.objects.filter(entity_id__in=entity_ids, entity_type=entity_type)

    review_data = defaultdict(lambda: {'review_count': 0, 'average_rating': 0.0})

    for review in reviews:
        entity_id = str(review.entity_id)
        review_data[entity_id]['review_count'] += 1
        review_data[entity_id]['average_rating'] += review.rating

    for entity_id, data in review_data.items():
        if data['review_count'] > 0:
            data['average_rating'] /= data['review_count']

    return review_data

def get_entity_reviews(entity_id, entity_type):
    reviews = Review.objects.filter(entity_id=entity_id, entity_type=entity_type)
    serializer = ReviewSerializer(reviews, many=True)
    return serializer.data

def get_hospital_specialists(hospital_id):
    doctors = Doctor.objects.filter(hospital_id=hospital_id)
    serializer = healthcare.serializers.DoctorSerializer(doctors, many=True)
    return serializer.data

