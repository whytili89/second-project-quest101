from django.urls import path

from .views import OrderView, CommentView

urlpatterns = [
    path('/order/<int:course_id>', OrderView.as_view()),
    path('/<int:course_id>/comments', CommentView.as_view())
]