from django.urls import path

from .views import UserCreateAPIView, UserLoginAPIView, UserDetailAPIView

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('detail/', UserDetailAPIView.as_view(), name='detail')
]
