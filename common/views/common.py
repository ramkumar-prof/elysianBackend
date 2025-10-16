from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.sessions.models import Session
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import os
import mimetypes

class SessionOrJWTAuthentication:
    """
    Custom authentication that requires either valid JWT access token or valid session
    """
    def authenticate(self, request):
        # Try JWT authentication first
        jwt_auth = JWTAuthentication()
        try:
            jwt_result = jwt_auth.authenticate(request)
            if jwt_result:
                return jwt_result
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

        # Check if session exists (for anonymous users)
        if request.session.session_key:
            return (None, None)  # Anonymous user with valid session

        # No valid authentication found
        raise AuthenticationFailed('Authentication required: Please provide JWT token or valid session')

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
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
    """
    if not request.session.session_key:
        request.session.create()

    response = Response({}, status=status.HTTP_200_OK)

    # Set session cookie in browser
    response.set_cookie(
        'sessionid',
        request.session.session_key,
        httponly=True,
        secure=False,  # Set to True for production over HTTPS
        samesite='Lax'
    )

    return response