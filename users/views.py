import jwt, requests

from django.views import View
from django.http  import JsonResponse
from datetime     import datetime, timedelta

from quest101.settings import SECRET_KEY, ALGORITHM
from users.models      import User

class KakaoAPI:
    def __init__(self, access_token):
        self.kakao_token = access_token
        self.kakao_url = 'https://kapi.kakao.com/v2/user/me'

    def get_kakao_user(self):
        kakao_headers = {'Authorization' : f'Bearer {self.kakao_token}'}
        response = requests.get(self.kakao_url, headers=kakao_headers, timeout = 5)
        
        if response.json().get('code') == -401: 
                return JsonResponse({'message': 'INVALID KAKAO USER'}, status=400)
            
        return response.json()

class KakaoSignInView(View):
    def get(self, request):
        try:
            kakao_token = request.headers.get('Authorization', None)
            kakao_api   = KakaoAPI(kakao_token)
            kakao_user  = kakao_api.get_kakao_user()
            
            kakao_id      = kakao_user['id']
            name          = kakao_user['kakao_account']['profile']['nickname']
            email         = kakao_user['kakao_account']['email']
            profile_image = kakao_user['kakao_account']['profile']['thumbnail_image_url']
            
            user, created = User.objects.get_or_create(
                kakao_id = kakao_id,
                defaults = {'name'          : name,
                            'email'         : email,
                            'profile_image' : profile_image
                        }
            )
            
            status_code  = 201 if created else 200
        
            access_token = jwt.encode({'user_id' : user.id, 'exp' : datetime.utcnow() + timedelta(days=7)}, SECRET_KEY, ALGORITHM)
            
            return JsonResponse({'message':'SUCCESS', 'access_token' : access_token}, status = status_code)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status = 400)
        
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 404)
        
        except jwt.ExpiredSignatureError:
            return JsonResponse({'message':'TOKEN_EXPIRED'}, status = 400)