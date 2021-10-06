from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter

from api import views

router = DefaultRouter()

urlpatterns = [
    path('user/forgot_pass/<str:phone>', views.forgot_send_confirm_code),
    path('user/forgot_pass/confirm_code/', views.forgot_confirm_code),
    path('user/forgot_pass/new_pass/', views.forgot_new_pass),
    path('user/phone/send_confirm_code/<str:phone>', views.send_confirm_code),
    path('user/phone/confirm_code/', views.confirm_phone_code),
    path('user/register/', views.UserRegister.as_view()),
    path('user/token/', views.MyTokenView.as_view()),
    path('user/token/social/', views.MySocialTokenView.as_view()),
    path('user/token/refresh/', views.RefreshTokenView.as_view()),

    path('user/token/test/', views.test_login, name='test_token'),

    path('user/notification/count/', views.notification_count),
    path('user/notification/<int:pk>/read/', views.notification_read),
    path('user/notification/list/', views.NotificationsList.as_view()),



]
