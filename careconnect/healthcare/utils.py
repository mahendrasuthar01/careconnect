from collections import defaultdict
from core.models import Review
from .models import Doctor
from core.serializers import ReviewSerializer
import healthcare.serializers

def get_reviews_data(entity_ids, entity_type):

    """
    Retrieves review data for a given list of entity IDs and entity type.

    Parameters:
        entity_ids (list): A list of entity IDs.
        entity_type (int): The type of the entity.

    Returns:
        dict: A dictionary containing review data for each entity ID. The keys of the dictionary are the entity IDs, and the values are dictionaries with the following keys:
            - 'review_count' (int): The number of reviews.
            - 'average_rating' (float): The average rating of the reviews.
    """

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

    """
    Retrieves the reviews associated with a given entity.

    Args:
        entity_id (int): The ID of the entity.
        entity_type (int): The type of the entity.

    Returns:
        list: A list of serialized reviews.

    """

    reviews = Review.objects.filter(entity_id=entity_id, entity_type=entity_type)
    serializer = ReviewSerializer(reviews, many=True)
    return serializer.data


def get_hospital_specialists(hospital_id):

    """
    Retrieves the specialists associated with a given hospital.

    Args:
        hospital_id (int): The ID of the hospital.

    Returns:
        list: A list of serialized specialists.

    """

    doctors = Doctor.objects.filter(hospital_id=hospital_id)
    serializer = healthcare.serializers.DoctorSerializer(doctors, many=True)
    return serializer.data