from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .utils import get_db
from .serializers import UserSerializer
from apis.authentication import JWTAuthentication

class UserListCreate(APIView):
    # authentication_classes = [JWTAuthentication]
    def get(self, request):
        db = get_db()
        users = list(db['user'].find())
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
        return Response(users, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            db = get_db()
            user = serializer.validated_data
            result = db['user'].insert_one(user)
            user['_id'] = str(result.inserted_id)
            return Response(user, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRetrieveUpdateDelete(APIView):
    # authentication_classes = [JWTAuthentication]
    def get_object(self, pk):
        db = get_db()
        user = db['user'].find_one({'_id': ObjectId(pk)})
        if user:
            user['_id'] = str(user['_id'])
        return user

    def get(self, request, pk):
        user = self.get_object(pk)
        if user:
            return Response(user, status=status.HTTP_200_OK)
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            db = get_db()
            updated_user = serializer.validated_data
            db['user'].update_one({'_id': ObjectId(pk)}, {'$set': updated_user})
            updated_user['_id'] = pk
            return Response(updated_user, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        db = get_db()
        result = db['user'].delete_one({'_id': ObjectId(pk)})
        if result.deleted_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
