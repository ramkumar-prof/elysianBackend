"""
URL configuration for elysianBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404

def disabled_admin_view(request, path=None):
    """
    Custom view to return 404 for admin access attempts
    Accepts optional path parameter for admin sub-routes
    """
    raise Http404("Admin interface is disabled")

# Base URL patterns
urlpatterns = [
    # API endpoints
    path('api/restaurant/', include('restaurent.urls')),
    path('api/common/', include('common.urls')),
    path('api/user/', include('user.urls')),
]

# Conditionally add admin URLs based on environment setting
if getattr(settings, 'ADMIN_ENABLED', False):
    # Admin is enabled - add normal admin URLs
    urlpatterns.insert(0, path('admin/', admin.site.urls))
else:
    # Admin is disabled - add disabled admin view
    urlpatterns.extend([
        path('admin/', disabled_admin_view),
        path('admin/<path:path>', disabled_admin_view),
    ])

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
