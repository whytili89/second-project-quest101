import json

from django.db.utils import IntegrityError
from django.http     import JsonResponse
from django.views    import View

from core.utils   import Authorize
from users.models import UserCourse

class OrderView(View):
    @Authorize
    def post(self,request,course_id):
        try:
            user, is_user = UserCourse.objects.get_or_create(user_id=request.user.id, course_id=course_id)
        
            if not is_user:
                return JsonResponse({"message" : "USER ALREADY EXISTS"}, status=401)
            return JsonResponse({"message": "SUCCESS"}, status=200)       

        except IntegrityError : 
            return JsonResponse({"message" : "INVALID_VALUE"}, status=400)