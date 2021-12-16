from django.urls import path

from .views import KakaoSignInView

urlpatterns = [
    path('/kakaosignin', KakaoSignInView.as_view())
]