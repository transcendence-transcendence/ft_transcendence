# main/forms.py
from django.contrib.auth.forms import UserCreationForm
from .models import User  # main.User 모델을 가져옴

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
