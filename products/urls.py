from django.urls import path

from .views import OrderView

urlpatterns = [
    path('/order/<int:course_id>', OrderView.as_view())
]