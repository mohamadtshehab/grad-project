from rest_framework.throttling import SimpleRateThrottle


class PasswordResetThrottle(SimpleRateThrottle):
    """
    Custom throttle for password reset requests.
    Limits password reset requests to 5 per hour per IP address.
    This prevents abuse while allowing legitimate users to request resets.
    """
    
    scope = 'password_reset'
    
    def get_cache_key(self, request, view):
        """
        Generate a unique cache key based on the IP address.
        This ensures rate limiting is per IP, not per user.
        """
        # Use IP address for rate limiting (more secure for password reset)
        ident = self.get_ident(request)
        return f"password_reset_{ident}"
    
    def get_ident(self, request):
        """
        Get the IP address from the request.
        Handles various proxy scenarios.
        """
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            # Get the first IP in the chain (client IP)
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
