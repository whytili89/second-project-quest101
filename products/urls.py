from django.urls import path

from .views import CommentView, OrderView

urlpatterns = [
    path('/<int:course_id>/order', OrderView.as_view()),
    path('/<int:course_id>/comment', CommentView.as_view())
]