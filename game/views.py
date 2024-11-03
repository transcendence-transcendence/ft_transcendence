from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from main.auth import JWTAuthenticationWithSessionAndCookie
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

class RoomView(APIView):
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
        if not request.user.is_otp_verified:
            return redirect('login')
        return render(request, 'game/room.html')

class GameView(APIView):
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

    def get(self, request, room_name):
        if not request.user.is_otp_verified:
            return redirect('login')
        context = {'room_name': room_name}
        return render(request, 'game/game.html', context)


class TournamentView(APIView):
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
        if not request.user.is_otp_verified:
            return redirect('login')
        context = {'room_name': 'test'}
        return render(request, 'game/torunament.html', context)


class TournamentGameView(APIView):
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
        if not request.user.is_otp_verified:
            return redirect('login')
        context = {'room_name': 'test'}
        return render(request, 'game/torunament_game.html', context)
