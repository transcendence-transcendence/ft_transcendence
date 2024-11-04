from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages
from django.contrib.auth import get_user_model
import requests
from ..models import User
from ..forms import CustomUserCreationForm
from ..auth import JWTAuthenticationWithSessionAndCookie
from decouple import config

User = get_user_model()
CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

# 42 API credentials
REDIRECT_URI = "http://127.0.0.1:8080/accounts/oauth/callback/"
AUTHORIZATION_BASE_URL = "https://api.intra.42.fr/oauth/authorize"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"

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

def login_view(request):
    # Redirect user to 42 OAuth authorization page
    authorization_url = f"{AUTHORIZATION_BASE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(authorization_url)

def callback_view(request):
    # Get the authorization code from the URL
    code = request.GET.get('code')

    # Exchange authorization code for an access token
    token_response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
    )

    token_json = token_response.json()
    access_token = token_json.get('access_token')

    # Use the access token to fetch user data
    user_response = requests.get(
        'https://api.intra.42.fr/v2/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_data = user_response.json()

    # Check if user exists, if not, create a new one
    user, created = User.objects.get_or_create(
        email=user_data.get('email'),
        defaults={
            'username': user_data.get('login'),
            'profile': user_data.get('cursus_users', [{}])[0].get('user', {}).get('id'),  # Example data field
            'is_active': True,
        }
    )

    if created:
        user.set_unusable_password()  # Set unusable password to enforce OAuth-only login
        user.save()

    # Log the user in
    login(request, user)

    # Issue JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Set JWT token in session and cookies
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
