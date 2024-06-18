from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .utils import get_db
from .serializers import UserSerializer

class UserListCreate(APIView):
    def get(self, request):
        db = get_db()
        persons = list(db['person'].find())
        for person in persons:
            person['_id'] = str(person['_id'])  # Convert ObjectId to string for JSON serialization
        return Response(persons, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            db = get_db()
            person = serializer.validated_data
            result = db['person'].insert_one(person)
            person['_id'] = str(result.inserted_id)
            return Response(person, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRetrieveUpdateDelete(APIView):
    def get_object(self, pk):
        db = get_db()
        person = db['person'].find_one({'_id': ObjectId(pk)})
        if person:
            person['_id'] = str(person['_id'])
        return person

    def get(self, request, pk):
        person = self.get_object(pk)
        if person:
            return Response(person, status=status.HTTP_200_OK)
        return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        person = self.get_object(pk)
        if not person:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            db = get_db()
            updated_person = serializer.validated_data
            db['person'].update_one({'_id': ObjectId(pk)}, {'$set': updated_person})
            updated_person['_id'] = pk
            return Response(updated_person, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        db = get_db()
        result = db['person'].delete_one({'_id': ObjectId(pk)})
        if result.deleted_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
