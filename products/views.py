import json

from django.http          import JsonResponse
from django.views         import View
from django.db.utils      import IntegrityError

from products.models      import Comment, Course
from core.utils           import Authorize
from users.models         import UserCourse

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

class CommentView(View):
    @Authorize
    def post(self,request,course_id):
        try:
            data    = json.loads(request.body)
            user_id = request.user.id
            
            Comment.objects.create(content=data['content'],course_id=course_id,user_id=user_id)
            
            comments        = Course.objects.get(id=course_id).comment_set.all()
            course_comments = [{
                'id'     :comment.id,
                'name'   :comment.user.name,
                'content':comment.content
            } for comment in comments]

            return JsonResponse({'message':course_comments},status=200)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'},status=401)

    def get(self,request,course_id):
        try:
            comments        = Course.objects.get(id=course_id).comment_set.all()
            course_comments = [{
                'id'     :comment.id,
                'name'   :comment.user.name,
                'content':comment.content
            } for comment in comments]

            return JsonResponse({'result':course_comments},status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'},status=401)

    @Authorize
    def delete(self,request,course_id):
        try:
            user_id    = request.user.id
            data       = json.loads(request.body)
            comment_id = data['comment_id']

            comment = Comment.objects.get(id=comment_id,user_id=user_id)
            comment.delete()

            return JsonResponse({'message':'SUCCESS_DELETE'},status=200)
        
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'},status=401)

        except Comment.DoesNotExist:
            return JsonResponse({'message':'INVAILD_COMMENT'},status=401)