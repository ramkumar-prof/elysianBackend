from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.sessions.models import Session
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from elysianBackend.constants import (
    ACCESS_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    COOKIE_HTTPONLY,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    COOKIE_PATH,
    ACCESS_TOKEN_EXPIRY,
    REFRESH_TOKEN_EXPIRY,
    SESSION_EXPIRY
)
import os
import mimetypes




class SessionOrJWTAuthentication:
    """
    Authentication class that checks for either valid access token or valid session
    """
    def authenticate(self, request):
        # Try JWT authentication first (from Authorization header)
        jwt_auth = JWTAuthentication()
        try:
            jwt_result = jwt_auth.authenticate(request)
            if jwt_result:
                return jwt_result
        except:
            pass

        # Try JWT authentication from cookie
        try:
            access_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
            if access_token:
                original_auth = request.META.get('HTTP_AUTHORIZATION')
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

                try:
                    jwt_result = jwt_auth.authenticate(request)
                    if jwt_result:
                        return jwt_result
                except:
                    pass
                finally:
                    # Restore original authorization header
                    if original_auth:
                        request.META['HTTP_AUTHORIZATION'] = original_auth
                    else:
                        request.META.pop('HTTP_AUTHORIZATION', None)
        except:
            pass

        # Try session authentication
        session_auth = SessionAuthentication()
        try:
            session_result = session_auth.authenticate(request)
            if session_result:
                return session_result
        except:
            pass

        # Check if valid session exists (for anonymous users)
        if request.session.session_key and request.session.exists(request.session.session_key):
            return (None, None)  # Anonymous user with valid session

        # No valid authentication found
        raise AuthenticationFailed('Authentication required: Please provide JWT token or valid session')

    def authenticate_header(self, request):
        return 'Bearer'


class JWTOnlyAuthentication:
    """
    Authentication class that only checks for valid access token
    """
    def authenticate(self, request):
        # Try JWT authentication from Authorization header
        jwt_auth = JWTAuthentication()
        try:
            jwt_result = jwt_auth.authenticate(request)
            if jwt_result:
                return jwt_result
        except:
            pass

        # Try JWT authentication from cookie
        try:
            access_token = request.COOKIES.get(ACCESS_TOKEN_COOKIE_NAME)
            if access_token:
                original_auth = request.META.get('HTTP_AUTHORIZATION')
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

                try:
                    jwt_result = jwt_auth.authenticate(request)
                    if jwt_result:
                        return jwt_result
                except:
                    pass
                finally:
                    # Restore original authorization header
                    if original_auth:
                        request.META['HTTP_AUTHORIZATION'] = original_auth
                    else:
                        request.META.pop('HTTP_AUTHORIZATION', None)
        except:
            pass

        # No valid JWT token found
        raise AuthenticationFailed('Authentication required: Please provide valid JWT token')

    def authenticate_header(self, request):
        return 'Bearer'


class RefreshTokenAuthentication:
    """
    Authentication class that only checks for valid refresh token
    """
    def authenticate(self, request):
        # Try to get refresh token from cookie
        refresh_token_value = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)

        # Try to get refresh token from request body
        if not refresh_token_value and hasattr(request, 'data'):
            refresh_token_value = request.data.get('refresh_token')

        if not refresh_token_value:
            raise AuthenticationFailed('Refresh token required')

        try:
            # Validate refresh token
            refresh_token = RefreshToken(refresh_token_value)
            user_id = refresh_token.payload.get('user_id')
            if user_id:
                User = get_user_model()
                user_obj = User.objects.get(id=user_id)
                return (user_obj, refresh_token)
        except (InvalidToken, TokenError, User.DoesNotExist):
            raise AuthenticationFailed('Invalid refresh token')

        raise AuthenticationFailed('Invalid refresh token')

    def authenticate_header(self, request):
        return 'Bearer'

def serve_image(request, image_path):
    """
    API endpoint to serve images from media directory
    """
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'images', image_path)
    
    # Check if file exists and is within media directory
    if not os.path.exists(file_path) or not file_path.startswith(settings.MEDIA_ROOT):
        raise Http404("Image not found")
    
    # Get the content type
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Read and return the file
    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            return response
    except IOError:
        raise Http404("Image not found")

@api_view(['GET'])
@permission_classes([AllowAny])
def get_or_create_session(request):
    """
    Get or create session ID for anonymous users
    If valid refresh token exists, create access token
    Otherwise, clear existing tokens and create new session
    """
    # Check if there's a valid refresh token
    refresh_token_value = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token_value:
        try:
            # Try to use refresh token to create access token
            refresh_token = RefreshToken(refresh_token_value)
            access_token = refresh_token.access_token

            response = Response({
                'message': 'Access token refreshed',
                'access_token': str(access_token)
            }, status=status.HTTP_200_OK)

            # Clear existing tokens first
            response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path=COOKIE_PATH)
            response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path=COOKIE_PATH)

            # Set new access token cookie
            response.set_cookie(
                ACCESS_TOKEN_COOKIE_NAME,
                str(access_token),
                httponly=COOKIE_HTTPONLY,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=ACCESS_TOKEN_EXPIRY,
                path=COOKIE_PATH
            )

            # Set refresh token cookie (rotation)
            response.set_cookie(
                REFRESH_TOKEN_COOKIE_NAME,
                str(refresh_token),
                httponly=COOKIE_HTTPONLY,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=REFRESH_TOKEN_EXPIRY,
                path=COOKIE_PATH
            )

            return response

        except (TokenError, InvalidToken):
            # Refresh token is invalid, continue to create new session
            pass

    # No valid refresh token - clear existing tokens and create new session
    if not request.session.session_key:
        request.session.create()

    response = Response({
        'message': 'Session created',
        'session_id': request.session.session_key
    }, status=status.HTTP_200_OK)

    # Clear any existing JWT tokens
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path=COOKIE_PATH)
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path=COOKIE_PATH)

    # Set session cookie
    response.set_cookie(
        SESSION_COOKIE_NAME,
        request.session.session_key,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=SESSION_EXPIRY,
        path=COOKIE_PATH
    )

    return response