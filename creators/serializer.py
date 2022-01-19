from rest_framework import serializers
from products.models import Course, CourseStat, Level, CourseStatus, SubCategory
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
            "thumbnail_image_url",
            "description",
            "price",
            "start_date",
            "end_date",
            "limit",
            "payment_period",
            "user",
            "sub_category",
            "level",
            "course_status",
            "discount_rate",
        ]
        
class CourseStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStat
        fields = "__all__"
        
    