# main/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지 URL을 ''로 설정
	path('signup/', views.signup, name='signup'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('sensitive/', views.SensitiveAPIView.as_view(), name='sensitive'), # JWT 와 세션 test 용 endpoint
    path('two-factor/', views.two_factor_auth, name='two_factor'),
    path('check-otp-status/', views.check_otp_status, name='check_otp_status'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
