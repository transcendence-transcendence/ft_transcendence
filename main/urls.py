# main/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views.home_views import home
from .views.auth_views import LoginView, signup, login_view, callback_view
from .views.otp_views import TwoFactorAuthView
from .views.api_views import login_api, signup_api, callback_view_api, verify_otp, generate_otp, user_status, logout_view
from django.shortcuts import render

def spa_view(request):
    return render(request, 'base_spa.html')

urlpatterns = [
    path('', home, name='home'),  # 메인 페이지 URL을 ''로 설정
    path('accounts/signup/', signup, name='signup'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/two-factor/', TwoFactorAuthView.as_view(), name='two_factor'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/oauth/login/', login_view, name='oauth_login'),
    path('accounts/oauth/callback/', callback_view, name='oauth_callback'),

    # API 라우팅
    path('api/login', login_api, name='login_api'),
    path('api/signup', signup_api, name='signup_api'), 
    path('api/oauth/callback', callback_view_api, name='oauth_callback_api'),
    path('api/two-factor/generate', generate_otp, name='generate_otp'),
    path('api/two-factor/verify', verify_otp, name='verify_otp'),
    path('api/auth/status', user_status, name='user_status'),
    path('api/logout', logout_view, name='logout_api'),

    # SPA 라우팅
    path('spa/', spa_view, name='spa_home'),
]