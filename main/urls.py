# main/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views.home_views import home
from .views.auth_views import LoginView, signup
from .views.otp_views import TwoFactorAuthView

urlpatterns = [
    path('', home, name='home'),  # 메인 페이지 URL을 ''로 설정
    path('accounts/signup/', signup, name='signup'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/two-factor/', TwoFactorAuthView.as_view(), name='two_factor'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
