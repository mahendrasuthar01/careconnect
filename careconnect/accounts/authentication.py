# apis/authentication.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None
        print("------------")
        try:
            # Extract the token value (remove 'Bearer ' prefix if present)
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            # Decode the token using the secret key and algorithm from settings
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            
            # Retrieve the user based on user_id from the token payload
            user = User.objects.get(id=payload.get('user_id', {}).get('id'))
            
            return (user, token)  # Authentication successful
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid token')
        
    def get_current_user(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None
        try:
            
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
           
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            
           
            user = User.objects.get(id=payload.get('user_id', {}).get('id'))
            
            return user  
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid token')


    @staticmethod
    def generate_jwt(user):
        payload = {
            'user_id': {'id': str(user.id), 'username': user.username},
            'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
