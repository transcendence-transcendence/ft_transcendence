# main/urls.py
from django.urls import path
from .views.api_views import login_api, signup_api, callback_view_api, verify_otp, generate_otp, user_status, logout_view

urlpatterns = [
    # API 라우팅
    path('api/login', login_api, name='login_api'),
    path('api/signup', signup_api, name='signup_api'), 
    path('api/oauth/callback', callback_view_api, name='oauth_callback_api'),
    path('api/two-factor/generate', generate_otp, name='generate_otp'),
    path('api/two-factor/verify', verify_otp, name='verify_otp'),
    path('api/auth/status', user_status, name='user_status'),
    path('api/logout', logout_view, name='logout_api'),
]