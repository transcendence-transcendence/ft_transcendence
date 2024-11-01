from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages
from django.http.response import JsonResponse
from .forms import CustomUserCreationForm
from django.contrib.messages import get_messages # 메시지 초기화를 위해서 가져옴.
from django.contrib.auth.decorators import login_required # 로그인 체크.
from django.core.mail import send_mail # 메일 때문에 추가함.
from django.conf import settings # email_host_user 을 가져오려고.
import pyotp # otp 설정 때문에.
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from django.http import HttpResponseRedirect
from datetime import timedelta
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class LoginView(APIView):
    def get(self, request):
        return render(request, 'registration/login.html')

    def post(self, request):
        # 기존 세션을 로그아웃하여 초기화
        logout(request)
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        # 사용자 인증
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 세션을 통한 로그인 처리
            login(request, user)
            
            # 새로운 JWT 발급
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            response = HttpResponseRedirect(redirect_to='home')
            # 홈 페이지로 리디렉션 준비
            response = redirect('home')  # 'home' URL로 리디렉션
            
            # 쿠키에 access token 저장
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # HTTPS 환경에서는 True
                samesite='Lax',
                max_age=timedelta(minutes=30).total_seconds()
            )

            response['Authorization'] = f'Bearer {access_token}'

            return response  # 리디렉션 응답 반환
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class JWTAuthenticationWithSessionAndCookie(BaseAuthentication):
    def authenticate(self, request):
        # 세션 인증 시도
        session_authenticator = SessionAuthentication()
        session_auth = session_authenticator.authenticate(request)
        
        if session_auth is None:
            raise AuthenticationFailed("Session authentication required.")
        
        # JWT 인증 시도
        jwt_authenticator = JWTAuthentication()
        
        # Authorization 헤더가 없으면 쿠키에서 JWT 검색
        header = jwt_authenticator.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = jwt_authenticator.get_raw_token(header)
        
        # JWT 토큰이 없거나 유효하지 않으면 인증 실패
        if raw_token is None:
            raise AuthenticationFailed("JWT token required.")
        
        # 유효한 JWT가 있는지 확인
        validated_token = jwt_authenticator.get_validated_token(raw_token)
        user = jwt_authenticator.get_user(validated_token)
        
        # 세션과 JWT가 모두 인증된 경우 인증된 사용자와 토큰 반환
        return (user, validated_token)

class SensitiveAPIView(APIView):
    # 인증 클래스로 JWTAuthenticationWithSessionAndCookie 사용
    authentication_classes = [JWTAuthenticationWithSessionAndCookie]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 인증된 사용자의 민감한 데이터 반환
        return Response({"data": "Sensitive information only accessible with both JWT and session authentication"})

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

@login_required
def two_factor_auth(request):
    user = request.user
    totp = pyotp.TOTP(user.otp_key)

    # GET 요청 시: OTP 코드 생성 및 이메일 전송
    if request.method == 'GET':

        # 이전 메시지 초기화
        storage = get_messages(request)
        for _ in storage:
            pass  # 모든 메시지를 순회하며 삭제

        otp_code = totp.now()  # 새로운 OTP 코드 생성
        request.session['otp_generated_time'] = otp_code  # 생성된 OTP 코드를 세션에 저장
        subject = "Your OTP Code"
        message = f"Your OTP code is {otp_code}. This code is valid for 30 seconds."
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        messages.info(request, 'OTP code sent to your email.')
        return render(request, 'main/two_factor_auth.html')

    # POST 요청 시: 사용자가 입력한 OTP 검증
    elif request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        generated_otp = request.session.get('otp_generated_time')  # 세션에서 GET 요청 시 생성된 OTP 가져오기
        
        # POST 요청 시 입력된 OTP와 생성된 OTP가 다른 경우
        if generated_otp != totp.now():
            messages.error(request, 'OTP code has expired. Please request a new one.')
            return redirect('two_factor')  # 다시 받기 페이지로 리다이렉트
        print(f"hehe : {totp.now()}")
        print(generated_otp)
        # OTP 검증 - valid_window=1로 설정하여 최근 1분 이내 코드 허용 (하지만 현실은 15초...)
        if totp.verify(otp_code, valid_window=1):
            user.is_otp_verified = True
            user.save()
            # 세션에서 OTP 정보 삭제
            del request.session['otp_generated_time']
            return redirect('home')  # 인증 후 홈 페이지로 이동
        else:
            messages.error(request, 'Invalid OTP code. Please try again.')

    return render(request, 'main/two_factor_auth.html')

@login_required
def check_otp_status(request):
    return JsonResponse({"is_otp_verified": request.user.is_otp_verified})

def home(request):
    return render(request, 'main/home.html')