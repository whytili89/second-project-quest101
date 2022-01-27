import jwt
from django.http import JsonResponse
from quest101.settings import ALGORITHM, SECRET_KEY
from rest_framework import authentication, permissions
from users.models import User


class MyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user, True)

class Authorize(authentication.BaseAuthentication):
    def __init__(self, original_function):
        self.original_function = original_function
    
    def __call__(self, request, *args, **kwargs):
        try:
            token = request.headers.get('Authorization')

            if not token:
                return JsonResponse({'message' : 'TOKEN_REQUIRED'}, status=401)

            payload      = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user         = User.objects.get(id=payload['user_id'])
            request.user = user
            return self.original_function(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status=401)

        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=401)


class AuthorizeProduct(authentication.BaseAuthentication):
    def __init__(self, original_function):
        self.original_function = original_function
    
    def __call__(self, request, *args, **kwargs):   
        token = request.headers.get('Authorization')

        if not token:
            request.user = None
            return self.original_function(self, request, *args, **kwargs)
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user         = User.objects.get(id=payload['user_id'])
        request.user = user

        return self.original_function(self, request, *args, **kwargs)