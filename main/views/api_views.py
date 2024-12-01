from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate, login
from rest_framework import status
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from ..forms import CustomUserCreationForm
import requests
from django.shortcuts import redirect
from decouple import config
import pyotp
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from functools import wraps
from dotenv import load_dotenv
load_dotenv(override=True)  # override=True를 추가하여 강제 재로드

User = get_user_model()
CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')
LOCAL_HOST_IP = config('LOCAL_HOST_IP')
REDIRECT_URI = f"https://{LOCAL_HOST_IP}/api/oauth/callback"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"


def check_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 세션 또는 access_token 확인
        access_token = request.COOKIES.get('access_token')

        if not request.user.is_authenticated or not access_token:
            return JsonResponse({
                'error': 'Authentication required',
                'detail': 'No valid session or access token found.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # access_token을 검증
            token = AccessToken(access_token)
            # 토큰이 유효하면 view_func 호출
        except (TokenError, InvalidToken) as e:
            # 토큰 검증 실패시
            return JsonResponse({
                'error': 'Invalid or expired token',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 토큰 검증 성공하면 원래의 view 함수 실행
        return view_func(request, *args, **kwargs)

    return wrapper

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # JSON 형태의 응답 반환
        response = Response({
            'message': 'Login successful',
            'access_token': access_token,
            'username': user.username
        }, status=status.HTTP_200_OK)

        # 쿠키 설정
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,  # JavaScript에서 쿠키 접근 금지
            secure=True,   # HTTPS 환경에서는 True로 설정
            samesite='Lax', # CSRF 방지 관련 설정
            max_age=timedelta(minutes=120).total_seconds()
        )
        return response
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def signup_api(request):
    form = CustomUserCreationForm(request.data)  # CustomUserCreationForm에 데이터 전달

    if form.is_valid(): # form 클래스에 저장된 필드에 입력된 데이터가 유효한지 확인.
        form.save()  # 유효한 데이터를 저장
        return Response({'message': 'Signup successful'}, status=status.HTTP_201_CREATED)
    else:
        # 폼 오류 메시지 가져오기
        errors = {field: [error['message'] for error in error_list] for field, error_list in form.errors.get_json_data().items()}
        return Response({'error': 'Signup failed', 'details': errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def callback_view_api(request):
    # Get the authorization code from the URL
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)

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

    if token_response.status_code != 200:
        return Response({'error': 'Failed to fetch access token'}, status=status.HTTP_400_BAD_REQUEST)

    token_json = token_response.json()
    access_token = token_json.get('access_token')
    if not access_token:
        return Response({'error': 'Access token not found in response'}, status=status.HTTP_400_BAD_REQUEST)

    # Use the access token to fetch user data
    user_response = requests.get(
        'https://api.intra.42.fr/v2/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if user_response.status_code != 200:
        return Response({'error': 'Failed to fetch user data'}, status=status.HTTP_400_BAD_REQUEST)

    user_data = user_response.json()

    # Check if user exists, if not, create a new one
    user, created = User.objects.get_or_create(
        email=user_data.get('email'),
        defaults={
            'username': user_data.get('login'),
            'is_active': True,
        }
    )

    if created:
        user.set_unusable_password()  # Set unusable password to enforce OAuth-only login
        user.save()

    login(request, user)

    # Issue JWT token
    refresh = RefreshToken.for_user(user)
    jwt_access_token = str(refresh.access_token)

    # Set JWT token in cookies
    response = redirect('/')  # Redirect to home page
    response.set_cookie(
        key="access_token",
        value=jwt_access_token,
        httponly=True,  # Prevent JavaScript access
        secure=False,   # Set to True in production with HTTPS
        samesite='Lax', # CSRF protection
        max_age=timedelta(minutes=120).total_seconds()
    )
    return response

@check_auth
@api_view(['POST'])
def generate_otp(request):
    user = request.user
    totp = pyotp.TOTP(user.otp_key)
    otp = totp.now()

    # 이메일로 OTP 전송
    subject = "Your OTP Code"
    message = f"Your OTP code is {otp}. It is valid for 30 seconds."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

    return Response({'message': 'OTP sent to your email.'}, status=status.HTTP_200_OK)

@check_auth
@api_view(['POST'])
def verify_otp(request):
    user = request.user
    otp = request.data.get('otp')

    if not otp:
        return Response({'error': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.otp_key)

    if totp.verify(otp, valid_window=1):
        user.is_otp_verified = True
        user.save()
        return Response({'message': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

@check_auth
@api_view(['POST'])  # Using POST to handle session cookies securely
def user_status(request):
    """
    Returns the current user's authentication status and details if logged in.
    """
    try:
        # Ensure the session is active
        if not request.session.session_key:
            return Response({'is_authenticated': False, 'detail': 'No active session.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({
                'is_authenticated': False,
                'detail': 'User is not authenticated.',
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Prepare user data
        user_data = {
            'is_authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'is_otp_verified': getattr(request.user, 'is_otp_verified', False),
        }

        # Return the user data
        return Response(user_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({
            'error': 'An unexpected error occurred.',
            'detail': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@check_auth 
@api_view(['POST'])
def logout_view(request):
    # Django 세션 로그아웃
    logout(request)

    response = JsonResponse({'message': 'Logout successful'})

    # 쿠키 삭제 (쿠키의 도메인과 경로를 정확히 지정)
    response.delete_cookie('access_token', path='/', domain=f'{LOCAL_HOST_IP}')
    response.delete_cookie('sessionid', path='/', domain=f'{LOCAL_HOST_IP}')
    response.delete_cookie('csrftoken', path='/', domain=f'{LOCAL_HOST_IP}')
    return response

