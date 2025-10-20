from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from common.views.common import SessionOrJWTAuthentication, JWTOnlyAuthentication
from user.permissions import IsAdminUser
from .models import RestaurentMenu
from .serializers import RestaurentMenuSerializer, AddMenuItemSerializer, RestaurentEntitySerializer
from common.models import Variant, RestaurentEntity

@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def restaurant_menu_list(request):
    """
    API endpoint that returns all restaurant menu items
    """
    # Only show menu items where product is available and has at least one available variant
    menu_items = RestaurentMenu.objects.select_related(
        'product', 'product__category', 'default_variant'
    ).filter(
        product__is_available=True,  # Product must be available
        product__variants__is_available=True  # At least one variant must be available
    ).distinct()

    serializer = RestaurentMenuSerializer(menu_items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([SessionOrJWTAuthentication])
@permission_classes([AllowAny])
def restaurant_list(request):
    """
    API endpoint that returns all restaurants

    Query Parameters:
    - is_available (optional): Filter by availability (true/false)
    - search (optional): Search in restaurant name and description (case-insensitive)

    Returns:
    - 200: List of restaurants

    Response format:
    [
        {
            "id": restaurant_id,
            "name": "Restaurant Name",
            "description": "Restaurant Description",
            "address": "Restaurant Address",
            "is_available": boolean
        }
    ]
    """
    # Start with all restaurants
    restaurants = RestaurentEntity.objects.all()

    # Apply filters based on query parameters
    is_available = request.query_params.get('is_available')
    if is_available is not None:
        is_available_bool = is_available.lower() == 'true'
        restaurants = restaurants.filter(is_available=is_available_bool)

    search = request.query_params.get('search')
    if search:
        restaurants = restaurants.filter(
            name__icontains=search
        ) | restaurants.filter(
            description__icontains=search
        )

    # Order by name for consistent results
    restaurants = restaurants.order_by('name')

    serializer = RestaurentEntitySerializer(restaurants, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_add_menu_item(request):
    """
    Admin-only API endpoint to add new items to restaurant menu

    Ensures unique combination of product_id and restaurent_id

    Required fields:
    - product_id: ID of the product to add
    - restaurent_id: ID of the restaurant
    - is_available: Boolean indicating if item is available (default: True)
    - is_veg: Boolean indicating if item is vegetarian (default: False)
    - default_variant_id: Optional ID of the default variant for this menu item

    Returns:
    - 201: Menu item created successfully
    - 400: Validation errors (including duplicate menu item)
    - 401: Authentication required
    - 403: Admin permission required
    """
    serializer = AddMenuItemSerializer(data=request.data)

    if serializer.is_valid():
        try:
            menu_item = serializer.save()

            # Return the created menu item using the display serializer
            response_serializer = RestaurentMenuSerializer(menu_item)

            return Response({
                'message': 'Menu item added successfully',
                'menu_item': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle unique constraint violation
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                return Response({
                    'error': 'Menu item already exists for this restaurant and product combination'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Failed to create menu item',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'error': 'Validation failed',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_menu_items_list(request):
    """
    Admin-only API endpoint that returns menu items filtered by restaurant

    Query Parameters:
    - restaurent_id (optional): Filter by specific restaurant ID
    - restaurent_name (optional): Filter by restaurant name (case-insensitive partial match)

    Returns:
    - 200: List of restaurants with their menu items
    - 401: Authentication required
    - 403: Admin permission required

    Response format:
    [
        {
            "id": restaurant_menu_item_id,
            "restaurent_entity_id": restaurant_id,
            "restaurent_name": "Restaurant Name",
            "products": [
                {
                    "menu_item_id": menu_item_id,
                    "product_id": product_id,
                    "product_name": "Product Name",
                    "is_available": boolean,
                    "is_veg": boolean,
                    "default_variant": {
                        "variant_id": variant_id,
                        "size": "variant_size"
                    }
                }
            ]
        }
    ]
    """
    # Start with base queryset
    menu_items_queryset = RestaurentMenu.objects.select_related(
        'restaurent', 'product', 'default_variant'
    )

    # Apply filters based on query parameters
    restaurent_id = request.query_params.get('restaurent_id')
    restaurent_name = request.query_params.get('restaurent_name')

    if restaurent_id:
        try:
            restaurent_id = int(restaurent_id)
            menu_items_queryset = menu_items_queryset.filter(restaurent_id=restaurent_id)
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid restaurent_id parameter. Must be a valid integer.'
            }, status=status.HTTP_400_BAD_REQUEST)

    if restaurent_name:
        menu_items_queryset = menu_items_queryset.filter(
            restaurent__name__icontains=restaurent_name
        )

    # Get filtered menu items
    menu_items = menu_items_queryset.order_by('restaurent__name', 'product__name')

    # Group menu items by restaurant
    restaurants_data = {}

    for menu_item in menu_items:
        restaurant_id = menu_item.restaurent.id

        if restaurant_id not in restaurants_data:
            restaurants_data[restaurant_id] = {
                'id': menu_item.id,  # Using the first menu item's id as restaurant entry id
                'restaurent_entity_id': restaurant_id,
                'restaurent_name': menu_item.restaurent.name,
                'products': []
            }

        # Prepare default variant data
        default_variant_data = None
        if menu_item.default_variant:
            default_variant_data = {
                'variant_id': menu_item.default_variant.id,
                'size': menu_item.default_variant.size
            }

        # Add product data
        product_data = {
            'menu_item_id': menu_item.id,
            'product_id': menu_item.product.id,
            'product_name': menu_item.product.name,
            'is_available': menu_item.is_available,
            'is_veg': menu_item.is_veg,
            'default_variant': default_variant_data
        }

        restaurants_data[restaurant_id]['products'].append(product_data)

    # Convert to list format
    result = list(restaurants_data.values())

    return Response(result, status=status.HTTP_200_OK)


@api_view(['PUT'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_update_menu_item(request, menu_item_id):
    """
    Admin-only API endpoint to update existing menu item

    Only allows updating: is_available, is_veg, default_variant
    product_id and restaurent_id cannot be changed

    Path Parameters:
    - menu_item_id: ID of the menu item to update

    Request Body:
    - is_available (optional): Boolean indicating if item is available
    - is_veg (optional): Boolean indicating if item is vegetarian
    - default_variant_id (optional): ID of the default variant for this menu item

    Returns:
    - 200: Menu item updated successfully
    - 400: Validation errors
    - 401: Authentication required
    - 403: Admin permission required
    - 404: Menu item not found
    """
    try:
        menu_item = RestaurentMenu.objects.get(id=menu_item_id)
    except RestaurentMenu.DoesNotExist:
        return Response({
            'error': 'Menu item not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Only allow updating specific fields
    allowed_fields = ['is_available', 'is_veg', 'default_variant_id']
    update_data = {}

    for field in allowed_fields:
        if field in request.data:
            update_data[field] = request.data[field]

    # Validate default_variant_id if provided
    if 'default_variant_id' in update_data:
        if update_data['default_variant_id'] is not None:
            try:
                variant = Variant.objects.get(
                    id=update_data['default_variant_id'],
                    product=menu_item.product
                )
                update_data['default_variant'] = variant
                del update_data['default_variant_id']
            except Variant.DoesNotExist:
                return Response({
                    'error': 'Invalid default_variant_id. Variant must belong to the same product.'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            update_data['default_variant'] = None
            del update_data['default_variant_id']

    # Update the menu item
    for field, value in update_data.items():
        setattr(menu_item, field, value)

    try:
        menu_item.save()
    except Exception as e:
        return Response({
            'error': 'Failed to update menu item',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

    # Return updated menu item
    serializer = RestaurentMenuSerializer(menu_item)
    return Response({
        'message': 'Menu item updated successfully',
        'menu_item': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
@authentication_classes([JWTOnlyAuthentication])
@permission_classes([IsAdminUser])
def admin_delete_menu_item(request, menu_item_id):
    """
    Admin-only API endpoint to delete existing menu item

    Path Parameters:
    - menu_item_id: ID of the menu item to delete

    Returns:
    - 200: Menu item deleted successfully
    - 401: Authentication required
    - 403: Admin permission required
    - 404: Menu item not found
    """
    try:
        menu_item = RestaurentMenu.objects.get(id=menu_item_id)
    except RestaurentMenu.DoesNotExist:
        return Response({
            'error': 'Menu item not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Store menu item data for response
    menu_item_data = {
        'id': menu_item.id,
        'restaurent_name': menu_item.restaurent.name,
        'product_name': menu_item.product.name
    }

    # Delete the menu item
    menu_item.delete()

    return Response({
        'message': 'Menu item deleted successfully',
        'deleted_item': menu_item_data
    }, status=status.HTTP_200_OK)
