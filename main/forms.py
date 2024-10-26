# main/forms.py
from django.contrib.auth.forms import UserCreationForm
from .models import User  # main.User 모델을 가져옴

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')  # 사용자명과 이메일을 필수 필드로 설정
