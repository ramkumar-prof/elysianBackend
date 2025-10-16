from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from common.views import SessionOrJWTAuthentication
from .models import RestaurentMenu
from .serializers import RestaurentMenuSerializer

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
