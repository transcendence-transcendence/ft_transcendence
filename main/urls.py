# main/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지 URL을 ''로 설정
	path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/two-factor/', views.TwoFactorAuthView.as_view(), name='two_factor'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
