from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from common.views.common import SessionOrJWTAuthentication, JWTOnlyAuthentication, RefreshTokenAuthentication
from .models import CustomUser, Address
from .serializers import UserRegistrationSerializer, UserLoginSerializer, AddressSerializer
from elysianBackend.constants import (
    REFRESH_TOKEN_COOKIE_NAME, ACCESS_TOKEN_COOKIE_NAME, SESSION_COOKIE_NAME,
    REFRESH_TOKEN_EXPIRY, ACCESS_TOKEN_EXPIRY, SESSION_EXPIRY,
    COOKIE_SECURE, COOKIE_SAMESITE, COOKIE_HTTPONLY, COOKIE_PATH
)

@api_view(['POST'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user with mobile number, password, first name and last name
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        response = Response({
            'message': 'User registered successfully',
            'user': {
                'mobile_number': user.mobile_number,
                'alternate_mobile_number': user.alternate_mobile_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_picture': user.profile_picture.url if user.profile_picture else None
            },
            'access_token': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

        # Clear session cookie and any existing tokens first
        response.delete_cookie(SESSION_COOKIE_NAME, path=COOKIE_PATH)
        response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path=COOKIE_PATH)
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path=COOKIE_PATH)

        # Set new refresh token as HttpOnly cookie
        response.set_cookie(
            REFRESH_TOKEN_COOKIE_NAME,
            str(refresh),
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=REFRESH_TOKEN_EXPIRY,
            path=COOKIE_PATH
        )

        # Set new access token as HttpOnly cookie for automatic authentication
        response.set_cookie(
            ACCESS_TOKEN_COOKIE_NAME,
            str(refresh.access_token),
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=ACCESS_TOKEN_EXPIRY,
            path=COOKIE_PATH
        )

        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user with mobile number and password
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        mobile_number = serializer.validated_data['mobile_number']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=mobile_number, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            response_data = {
                    'mobile_number': user.mobile_number,
                    'alternate_mobile_number': user.alternate_mobile_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                }
            if user.is_staff:
                response_data['is_staff'] = True
            if user.is_superuser:
                response_data['is_superuser'] = True

            response = Response({
                'message': 'Login successful',
                'user': response_data,
                'access_token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)

            # Clear session cookie and any existing tokens first
            response.delete_cookie(SESSION_COOKIE_NAME, path=COOKIE_PATH)
            response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path=COOKIE_PATH)
            response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path=COOKIE_PATH)

            # Set new refresh token as HttpOnly cookie
            response.set_cookie(
                REFRESH_TOKEN_COOKIE_NAME,
                str(refresh),
                httponly=COOKIE_HTTPONLY,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=REFRESH_TOKEN_EXPIRY,
                path=COOKIE_PATH
            )

            # Set new access token as HttpOnly cookie for automatic authentication
            response.set_cookie(
                ACCESS_TOKEN_COOKIE_NAME,
                str(refresh.access_token),
                httponly=COOKIE_HTTPONLY,
                secure=COOKIE_SECURE,
                samesite=COOKIE_SAMESITE,
                max_age=ACCESS_TOKEN_EXPIRY,
                path=COOKIE_PATH
            )

            return response
        else:
            return Response({
                'error': 'Invalid mobile number or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def get_current_user(request):
    """
    Get current authenticated user details
    """
    user = request.user
    response_data = {
            'mobile_number': user.mobile_number,
            'alternate_mobile_number': user.alternate_mobile_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }
    if user.is_staff:
        response_data['is_staff'] = True
    if user.is_superuser:
        response_data['is_superuser'] = True
    return Response({
        'user': response_data
    }, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def update_current_user(request):
    """
    Update current authenticated user details (except mobile_number and password)
    """
    user = request.user
    
    # Only allow updating specific fields
    allowed_fields = ['first_name', 'last_name', 'email', 'profile_picture', 'alternate_mobile_number']
    update_data = {key: value for key, value in request.data.items() if key in allowed_fields}
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    try:
        user.save()
        response_data = {
            'mobile_number': user.mobile_number,
            'alternate_mobile_number': user.alternate_mobile_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }
        if user.is_staff:
            response_data['is_staff'] = True
        if user.is_superuser:
            response_data['is_superuser'] = True
        return Response({
            'message': 'User updated successfully',
            'user': response_data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to update user',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def get_user_addresses(request):
    """
    Get all addresses of current authenticated user
    """
    addresses = Address.objects.filter(user=request.user)
    serializer = AddressSerializer(addresses, many=True)
    return Response({
        'addresses': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def add_user_address(request):
    """
    Add new address for current authenticated user
    """
    serializer = AddressSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        address = serializer.save()
        return Response({
            'message': 'Address added successfully',
            'address': AddressSerializer(address).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def update_user_address(request, address_id):
    """
    Update specific address of current authenticated user
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    serializer = AddressSerializer(address, data=request.data, partial=True)
    if serializer.is_valid():
        address = serializer.save()
        return Response({
            'message': 'Address updated successfully',
            'address': AddressSerializer(address).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([AllowAny])
def delete_user_address(request, address_id):
    """
    Delete specific address of current authenticated user
    """
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return Response({
        'message': 'Address deleted successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([RefreshTokenAuthentication])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh JWT access token using refresh token from cookie
    """
    refresh_token = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token

        response = Response({
            'access_token': str(access_token)
        }, status=status.HTTP_200_OK)

        # Clear existing tokens first
        response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path=COOKIE_PATH)
        response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path=COOKIE_PATH)

        # Set new refresh token as HttpOnly cookie (if rotation is enabled)
        response.set_cookie(
            REFRESH_TOKEN_COOKIE_NAME,
            str(refresh),
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=REFRESH_TOKEN_EXPIRY,
            path=COOKIE_PATH
        )

        # Set new access token as HttpOnly cookie for automatic authentication
        response.set_cookie(
            ACCESS_TOKEN_COOKIE_NAME,
            str(access_token),
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=ACCESS_TOKEN_EXPIRY,
            path=COOKIE_PATH
        )

        return response

    except TokenError:
        return Response({
            'error': 'Invalid or expired refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def logout_user(request):
    """
    Logout user by clearing authentication cookies, invalidating refresh token, and creating new session
    """
    # Try to get refresh token from cookie to blacklist it
    refresh_token_value = request.COOKIES.get(REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token_value:
        try:
            # Blacklist the refresh token to invalidate it on server side
            refresh_token = RefreshToken(refresh_token_value)
            refresh_token.blacklist()
        except TokenError:
            # Token was already invalid/expired, continue with logout
            pass

    # Create a new session for anonymous browsing
    request.session.create()
    new_session_key = request.session.session_key

    response = Response({
        'message': 'Logout successful',
        'session_id': new_session_key
    }, status=status.HTTP_200_OK)

    # Clear JWT token cookies
    response.delete_cookie(
        REFRESH_TOKEN_COOKIE_NAME,
        path=COOKIE_PATH
    )

    response.delete_cookie(
        ACCESS_TOKEN_COOKIE_NAME,
        path=COOKIE_PATH
    )

    # Set new session cookie for anonymous browsing
    response.set_cookie(
        SESSION_COOKIE_NAME,
        new_session_key,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=SESSION_EXPIRY,
        path=COOKIE_PATH
    )

    return response
