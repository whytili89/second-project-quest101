import json, boto3, uuid

from enum import Enum

from django.http                  import JsonResponse
from django.views                 import View
from django.db                    import transaction
from core.utils                   import Authorize, MyPermission
from creators.serializer          import CourseSerializer, UserSerializer
from rest_framework.views         import APIView
from rest_framework.response      import Response
from rest_framework               import status

from products.models   import Course, CourseStat, CourseStatus, SubCategory, Level, Media, Stat
from quest101.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_REGION

class CourseStatusEnum(Enum):
    PENDING   = "클래스 준비"
    RUNNING   = "클래스 운영"
    REVIEWING = "클래스 검토중"

class ImageHandler:
    def __init__(self, client, bucket, region):
        self.client = client
        self.bucket = bucket
        self.region = region

    def upload_file(self, file):
        unique_key = str(uuid.uuid4())

        self.client.put_object(
            Bucket      = self.bucket,
            Key         = unique_key,
            Body        = file.file.read(),
            ContentType = file.content_type
        )

        return '%s.s3.%s.amazonaws.com/%s' % (self.bucket, self.region, unique_key)

    def upload_files(self, files):
        return [self.upload_file(file) for file in files]
    
boto3_client = boto3.client(
    's3',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)
    
image_handler = ImageHandler(boto3_client, AWS_STORAGE_BUCKET_NAME, AWS_REGION)

class CoursesView(APIView):
    permission_classes = [MyPermission]
    
    def get(self, request):
        courses = request.user.course_set.all()
        
        results = [{
            'id'                  : course.id,
            'name'                : course.name,
            'thumbnail_image_url' : course.thumbnail_image_url,
            'detail_media'        : [{'type' : image.type,
                                     'url':image.url} for image in course.media_set.all()],
            'description'         : course.course_description,
            'sub_category'        : course.sub_category.name if course.sub_category != None else None,
            'category'            : course.sub_category.category.name 
                                    if course.sub_category != None 
                                    else None,
            "healthStat"          : CourseStat.objects.get(course=course, stat__name="체력").score,
            "intellectStat"       : CourseStat.objects.get(course=course, stat__name="지능").score,
            "charmStat"           : CourseStat.objects.get(course=course, stat__name="매력").score,
            "artStat"             : CourseStat.objects.get(course=course, stat__name="예술").score,
            'status'              : course.course_status.status,
            'level'               : course.course_level.level if course.course_level != None else None ,
            'user_name'           : request.user.name,
            'user_profile_image'  : request.user.profile_image,
            'user_phone_number'   : request.user.phone_number,
            'user_description'    : request.user.description,
            'social_account'      : [{
                'channel' :social_account.social_channel, 
                'url' : social_account.social_url
            } for social_account in course.user.socialaccount_set.all()]
        } for course in courses]
        
        return JsonResponse({"results" : results}, status=200)

    @Authorize
    @transaction.atomic()
    def put(self, request):
        course = Course.objects.get(id = request.POST['course_id'], user=request.user)

        course_data = {
            "user"          : request.user.id,
            "name"          : request.POST.get('course_name', course.name),
            "description"   : request.POST.get('course_description', course.description),
            "price"         : request.POST.get('price', course.price),
            "start_date"    : request.POST.get('start_date', course.start_date),
            "end_date"      : request.POST.get('end_date', course.end_date),
            "limit"         : request.POST.get('limit', course.limit),
            "payment_period": request.POST.get('payment_period', course.payment_period),
            "course_status" : CourseStatus.objects.get(status=request.POST.get('course_status', '클래스 준비')).id,
            "discount_rate" : request.POST.get('discount_rate', course.discount_rate)
        }
        
        if 'level' in request.POST:
            course_data['level'] = Level.objects.get(level=request.POST['level']).id

        if 'sub_category' in request.POST:
            course_data['sub_category'] = SubCategory.objects.get(name=request.POST['sub_category']).id
        
        user_data = {
            "name"        : request.POST.get('user_name', request.user.name),
            "description" : request.POST.get('user_description', request.user.description),
            "phone_number": request.POST.get('user_phone_number', request.user.phone_number)
        }
        
        stats = CourseStat.objects.filter(course=course)
        stat_dict = {
            "매력" : request.POST.get('charm_stat', stats.get(stat=Stat.objects.get(name="매력")).score),
            "예술" : request.POST.get('art_stat', stats.get(stat=Stat.objects.get(name="예술")).score),
            "체력" : request.POST.get('health_stat', stats.get(stat=Stat.objects.get(name="체력")).score),
            "지능" : request.POST.get('intellect_stat', stats.get(stat=Stat.objects.get(name="지능")).score)
        }
        stat_update_list = []
        
        for key, value in stat_dict.items():
            stat = CourseStat.objects.get(course = course, stat=Stat.objects.get(name=key))
            stat.score = value
            stat_update_list.append(stat)
        CourseStat.objects.bulk_update(stat_update_list, ['score'])
        
        course_serializer = CourseSerializer(course, data=course_data, partial=True)
        user_serializer   = UserSerializer(request.user, data=user_data, partial=True)
        
        if course_serializer.is_valid():
            course_serializer.save()
        if user_serializer.is_valid():
            user_serializer.save()
            updated_data = {'course' : course_serializer.data, 'user' : user_serializer.data, 'stat' : [stat.score for stat in stats]}
            return Response(updated_data)
        return Response(course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @Authorize
    @transaction.atomic()
    def delete(self, request):
        try:
            user         = request.user
            data         = json.loads(request.body)
            course       = Course.objects.get(id = data['course_id'], user = user)
            course_stats = CourseStat.objects.filter(course=course)

            if not Course.objects.filter(id = data['course_id'], user = user).exists():
                return JsonResponse({"message" : "NOT_EXIST"}, status=400)
            
            course.delete()
            [course_stat.delete() for course_stat in course_stats]

            return JsonResponse({"message" : "DELETE_SUCCESS"}, status=200)
        
        except Course.DoesNotExist:
            return JsonResponse({"message" : "INVALID_COURSE"}, status=404)

    @Authorize
    @transaction.atomic()
    def post(self,request):
        course = Course.objects.create(user = request.user, 
                                        course_status=CourseStatus.objects.get(status=CourseStatusEnum.PENDING.value))
        
        if not request.user.is_creator:
            request.user.is_creator = True
            request.user.save()
          
        stats = Stat.objects.all()    
        stat_names = [stat.name for stat in stats]
        for stat_name in stat_names:    
            CourseStat.objects.create(course=course, stat= Stat.objects.get(name=stat_name), score=0)
            
        return JsonResponse({"courseId": course.id}, status = 201)

class CourseView(View):
    @Authorize
    def get(self, request, course_id):
        course = Course.objects.get(id = course_id, user = 2)

        results = {
            'name'                : course.name,
            'thumbnail_image_url' : course.thumbnail_image_url,
            'detail_media'        : [{'type' : image.type, 'url':image.url} for image in course.media_set.all()],
            'description'         : course.description,
            'sub_category'        : course.sub_category.name if course.sub_category != None else None,
            'category'            : course.sub_category.category.name if course.sub_category != None else None,
            'level'               : course.course_level.level if course.course_level != None else None ,
            'is_course_created'   : False,
            'user_name'           : course.user.name,
            'user_profile_image'  : course.user.profile_image,
            'user_phone_number'   : course.user.phone_number,
            'user_description'    : course.user.description,
            "healthStat"          : CourseStat.objects.get(course=course, stat__name="체력").score,
            "intellectStat"       : CourseStat.objects.get(course=course, stat__name="지능").score,
            "charmStat"           : CourseStat.objects.get(course=course, stat__name="매력").score,
            "artStat"             : CourseStat.objects.get(course=course, stat__name="예술").score,
            'social_account'      : [{
                'channel' : social_account.social_channel,
                'url'     : social_account.social_url
            } for social_account in course.user.socialaccount_set.all()]
        }
        
        return JsonResponse({"results" : results}, status=200)
    
    @Authorize
    @transaction.atomic()
    def post(self,request, course_id):
        try:
            print(request.FILES)
            course = Course.objects.get(user=request.user, id=course_id)
            urls = image_handler.upload_files(request.FILES.getlist('detail_image_url'))
            
            course.thumbnail_image_url = image_handler.upload_file(request.FILES.__getitem__('thumbnail_image_url'))
            course.save()
        
            Media.objects.bulk_create([Media(type = 'image', course = course, url = url) for url in urls])
            return JsonResponse({"message":"SUCCESS"},status=201)

        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)