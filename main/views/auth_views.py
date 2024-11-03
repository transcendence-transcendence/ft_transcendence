from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from ..forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from ..auth import JWTAuthenticationWithSessionAndCookie

User = get_user_model()

class LoginView(APIView):
    def get(self, request):
        return render(request, 'registration/login.html')

    def post(self, request):
        logout(request)  # 기존 세션 초기화
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = redirect('home')
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # HTTPS 환경에서는 True
                samesite='Lax',
                max_age=timedelta(minutes=30).total_seconds()
            )
            response['Authorization'] = f'Bearer {access_token}'
            return response
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '회원가입이 완료되었습니다. 로그인 해주세요.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})