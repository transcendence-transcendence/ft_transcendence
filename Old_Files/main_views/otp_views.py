from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import TemplateHTMLRenderer
import pyotp
from django.core.mail import send_mail
from django.contrib.messages import get_messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework.permissions import IsAuthenticated
from ..auth import JWTAuthenticationWithSessionAndCookie

class TwoFactorAuthView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    authentication_classes = [JWTAuthenticationWithSessionAndCookie]
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return self.permission_denied(self.request, message=str(exc))
        return super().handle_exception(exc)

    def permission_denied(self, request, message=None, code=None):
        context = {'detail': message or "Session authentication or JWT token required."}
        return render(request, 'main/permission_denied.html', context, status=403)

    def get(self, request):
        user = request.user
        totp = pyotp.TOTP(user.otp_key)
        storage = get_messages(request)
        for _ in storage:
            pass  # 메시지 초기화
        otp_code = totp.now()
        request.session['otp_generated_time'] = otp_code
        subject = "Your OTP Code"
        message = f"Your OTP code is {otp_code}. This code is valid for 30 seconds."
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        messages.info(request, 'OTP code sent to your email.')
        return render(request, 'main/two_factor_auth.html')

    def post(self, request):
        user = request.user
        totp = pyotp.TOTP(user.otp_key)
        otp_code = request.POST.get('otp_code')
        generated_otp = request.session.get('otp_generated_time')

        if generated_otp != totp.now():
            messages.error(request, 'OTP code has expired. Please request a new one.')
            return redirect('two_factor')
        
        if totp.verify(otp_code, valid_window=1):
            user.is_otp_verified = True
            user.save()
            del request.session['otp_generated_time']
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP code. Please try again.')
        
        return render(request, 'main/two_factor_auth.html')
