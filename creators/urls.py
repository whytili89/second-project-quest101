from django.urls import path

from .views import CoursesView, CourseView

urlpatterns = [
    path('', CoursesView.as_view()),
    path('/<int:course_id>', CourseView.as_view()),
]