from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework import authentication, views, permissions, status
from rest_framework.exceptions import AuthenticationFailed, ParseError
from apis.utils import get_db
from rest_framework.response import Response
from .serializers import UserSerializer


class JWTAuthentication(authentication.BaseAuthentication):
    def __init__(self):
        self.db = get_db()
        self.users_collection = self.db['users']

    def authenticate(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')

        if not jwt_token:
            return None
        
        jwt_token = self.get_the_token_from_header(jwt_token)

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise ParseError('Invalid token')
        except Exception as e:
            raise ParseError(f"JWT error: {str(e)}")

        user_identifier = payload.get('user_identifier')
        if not user_identifier:
            raise ParseError('Invalid token payload')

        user = self.users_collection.find_one({
            "$or": [
                {"username": user_identifier},
                {"phone_number": user_identifier}
            ]
        })

        if not user:
            raise AuthenticationFailed('User not found')
        
        return user, payload
    
    def authenticate_header(self, request):
        return 'Bearer'


    @classmethod
    def get_the_token_from_header(cls, token):
        return token.replace('Bearer', '').strip()
    

class ObtainJWTToken(views.APIView):
    # permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            db = get_db()
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = db['user'].find_one({'username': username,
                                          'email': email,
                                          'password': password})
            print("============user============", user)
            if not user:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            # jwt_auth = JWTAuthentication()
            token = create_jwt(user)

            return Response({'token': token}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def create_jwt(user):
    payload = {
        'user_identifier': user['username'],
        'exp': int((datetime.utcnow() + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])).timestamp()),
        'iat': datetime.utcnow().timestamp(),
        'username': user['username'],
        'phone_number': user.get('phone_number', '')
    }

    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return jwt_token