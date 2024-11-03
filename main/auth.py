from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthenticationWithSessionAndCookie(BaseAuthentication):
    def authenticate(self, request):
        session_authenticator = SessionAuthentication()
        session_auth = session_authenticator.authenticate(request)
        
        if session_auth is None:
            raise AuthenticationFailed("Session authentication required.")
        
        jwt_authenticator = JWTAuthentication()
        header = jwt_authenticator.get_header(request)
        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = jwt_authenticator.get_raw_token(header)
        
        if raw_token is None:
            raise AuthenticationFailed("JWT token required.")
        
        validated_token = jwt_authenticator.get_validated_token(raw_token)
        user = jwt_authenticator.get_user(validated_token)
        
        return (user, validated_token)