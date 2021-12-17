import json

from django.http          import JsonResponse
from django.views         import View
from django.db.utils      import IntegrityError

from products.models      import Comment, Course, CourseStat
from core.utils           import Authorize, AuthorizeProduct
from users.models         import UserCourse, UserCourseStat
from django.db            import transaction

class OrderView(View):
    @Authorize
    def post(self,request,course_id):
        try:
            course_stat_id = CourseStat.objects.filter(course_id=course_id)
            with transaction.atomic():
                for course_stat_ids in course_stat_id:
                    UserCourseStat.objects.create(
                        user_id     = request.user.id,
                        course_stat = course_stat_ids
                    )
                UserCourse.objects.create(
                    course_id = course_id,
                    user_id   = request.user.id
                )
                return JsonResponse({"message": "SUCCESS"}, status=200)           
        
        except IntegrityError:
            return JsonResponse({"message" : "USER ALREADY EXISTS"}, status=401)
            
        except CourseStat.DoesNotExist :
            return JsonResponse({"message" : "INVAILD_COURSE_STAT"}, status=401)

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

class ProductView(View):
    @AuthorizeProduct
    def get(self,request,course_id):
        try:
            course=Course.objects.get(id=course_id)
            stats=course.coursestat_set.all().select_related('stat')
            media = course.media_set.get()
            
            results={
                "course_id"      : course.id,
                "sub_category"   : course.sub_category.name,
                "course_name"    : course.name,
                "description"    : course.description,
                "thumbnail_url"  : course.thumbnail_image_url,
                "page_image"     : media.url,
                "course_level"   : course.level.level,
                "price"          : course.price,
                "payment_period" : course.payment_period,
                "discount_rate"  : course.discount_rate,
                "discount_price" : (course.price * course.discount_rate)/100,
                "course_like"    : course.like_set.count(),
                "course_stat"    : [{"stat_name" : c_stat.stat.name,"score" : c_stat.score} for c_stat in stats],
                "is_like_True"   : True if course.like_set.filter(user_id=request.user).exists() else False,
                "user_name"      : course.user.name,
                "profile_image"  : course.user.profile_image
               }
                

            return JsonResponse({"results" : results}, status=200)

        except Course.DoesNotExist:
            return JsonResponse({"message" : "INVALID_COURSE"},status=401)
