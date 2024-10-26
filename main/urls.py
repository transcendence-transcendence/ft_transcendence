# main/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # 메인 페이지 URL을 ''로 설정
	path('signup/', views.signup, name='signup'),
	path('login/', LoginView.as_view(), name='login'),  # 로그인 페이지
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
