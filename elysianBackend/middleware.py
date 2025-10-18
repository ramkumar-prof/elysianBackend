"""
Custom middleware for Elysian Backend
"""

from django.http import Http404
from django.conf import settings


class DisableAdminMiddleware:
    """
    Middleware to disable Django admin interface completely
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for admin interface
        if request.path.startswith('/admin/'):
            # You can customize the response:
            
            # Option 1: Return 404 (recommended for security)
            raise Http404("Admin interface is disabled")
            
            # Option 2: Return 403 Forbidden
            # from django.http import HttpResponseForbidden
            # return HttpResponseForbidden("Admin access is disabled")
            
            # Option 3: Redirect to homepage
            # from django.shortcuts import redirect
            # return redirect('/')
            
            # Option 4: Return custom message
            # from django.http import HttpResponse
            # return HttpResponse("Admin interface is disabled for security reasons", status=403)

        response = self.get_response(request)
        return response


class AdminIPWhitelistMiddleware:
    """
    Alternative middleware to allow admin access only from specific IPs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define allowed IPs for admin access
        self.allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [
            '127.0.0.1',
            'localhost',
            # Add your specific IPs here
        ])

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Get client IP
            client_ip = self.get_client_ip(request)
            
            # Check if IP is allowed
            if client_ip not in self.allowed_ips:
                raise Http404("Admin interface not accessible from this location")

        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AdminTimeRestrictedMiddleware:
    """
    Alternative middleware to allow admin access only during specific hours
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            from datetime import datetime
            
            # Define allowed hours (24-hour format)
            allowed_start_hour = getattr(settings, 'ADMIN_START_HOUR', 9)  # 9 AM
            allowed_end_hour = getattr(settings, 'ADMIN_END_HOUR', 17)     # 5 PM
            
            current_hour = datetime.now().hour
            
            if not (allowed_start_hour <= current_hour <= allowed_end_hour):
                raise Http404("Admin interface is only accessible during business hours")

        response = self.get_response(request)
        return response
