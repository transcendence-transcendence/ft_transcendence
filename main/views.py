from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http.response import JsonResponse
from .forms import CustomUserCreationForm
from django.contrib.messages import get_messages # 메시지 초기화를 위해서 가져옴.
from django.contrib.auth.decorators import login_required # 로그인 체크.
from django.core.mail import send_mail # 메일 때문에 추가함.
from django.conf import settings # email_host_user 을 가져오려고.
import pyotp # otp 설정 때문에.

User = get_user_model()

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
        if generated_otp != otp_code:
            messages.error(request, 'OTP code has expired. Please request a new one.')
            return redirect('two_factor')  # 다시 받기 페이지로 리다이렉트

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