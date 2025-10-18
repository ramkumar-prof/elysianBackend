from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from common.views.common import SessionOrJWTAuthentication, JWTOnlyAuthentication
from user.permissions import IsAdminUser
from .models import RestaurentMenu
from .serializers import RestaurentMenuSerializer, AddMenuItemSerializer

@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def restaurant_menu_list(request):
    """
    API endpoint that returns all restaurant menu items
    """
    menu_items = RestaurentMenu.objects.select_related('product', 'product__category', 'default_variant').all()
    serializer = RestaurentMenuSerializer(menu_items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_menu_item(request):
    """
    Admin-only API endpoint to add new items to restaurant menu

    Required fields:
    - product_id: ID of the product to add
    - restaurent_id: ID of the restaurant
    - is_available: Boolean indicating if item is available (default: True)
    - is_veg: Boolean indicating if item is vegetarian (default: False)
    - default_variant_id: Optional ID of the default variant for this menu item

    Returns:
    - 201: Menu item created successfully
    - 400: Validation errors
    - 401: Authentication required
    - 403: Admin permission required
    """
    serializer = AddMenuItemSerializer(data=request.data)

    if serializer.is_valid():
        menu_item = serializer.save()

        # Return the created menu item using the display serializer
        response_serializer = RestaurentMenuSerializer(menu_item)

        return Response({
            'message': 'Menu item added successfully',
            'menu_item': response_serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
