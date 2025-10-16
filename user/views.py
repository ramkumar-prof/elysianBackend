from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from common.views import SessionOrJWTAuthentication
from .models import CustomUser, Address
from .serializers import UserRegistrationSerializer, UserLoginSerializer, AddressSerializer

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

        # Set refresh token as HttpOnly cookie
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=False,  # Set to True for production over HTTPS
            samesite='Lax',
            max_age=7 * 24 * 60 * 60  # 7 days (same as JWT refresh token lifetime)
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

            response = Response({
                'message': 'Login successful',
                'user': {
                    'mobile_number': user.mobile_number,
                    'alternate_mobile_number': user.alternate_mobile_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None
                },
                'access_token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)

            # Set refresh token as HttpOnly cookie
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,  # Set to True for production over HTTPS
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,  # 7 days (same as JWT refresh token lifetime)
                path=''
            )

            return response
        else:
            return Response({
                'error': 'Invalid mobile number or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_current_user(request):
    """
    Get current authenticated user details
    """
    user = request.user
    return Response({
        'user': {
            'mobile_number': user.mobile_number,
            'alternate_mobile_number': user.alternate_mobile_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture.url if user.profile_picture else None
        }
    }, status=status.HTTP_200_OK)

@api_view(['PUT', 'PATCH'])
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
        return Response({
            'message': 'User updated successfully',
            'user': {
                'mobile_number': user.mobile_number,
                'alternate_mobile_number': user.alternate_mobile_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_picture': user.profile_picture.url if user.profile_picture else None
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Failed to update user',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
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
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh JWT access token using refresh token from cookie
    """
    refresh_token = request.COOKIES.get('refresh_token')

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

        # Set new refresh token as HttpOnly cookie (if rotation is enabled)
        response.set_cookie(
            'refresh_token',
            str(refresh),
            httponly=True,
            secure=False,  # Set to True for production over HTTPS
            samesite='Lax',
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return response

    except TokenError:
        return Response({
            'error': 'Invalid or expired refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
