import posthog
import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PostHogMiddleware(MiddlewareMixin):
    """
    Middleware to track API endpoint events in PostHog.

    This middleware captures all view endpoint calls in the tellme/call_miner
    and tellme/call_processing apps, and sends events to PostHog with the
    endpoint name, user information, and environment tagging.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # PostHog is initialized in apps.py, so we just need to check if it's configured
        self.posthog_enabled = settings.POSTHOG_API_KEY and (settings.TELLME_ENV != 'dev')
        super().__init__(get_response)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Store view information for later use in process_response.
        This runs before authentication, so we just store the view info.
        """
        if not self.posthog_enabled:
            return None

        # Get the view module to check if it's from our target apps
        view_module = view_func.__module__

        # Only track views from call_miner and call_processing apps
        if not (view_module.startswith('tellme.call_miner') or
                view_module.startswith('tellme.call_processing')):
            return None

        # Store view information on the request for later use
        request._posthog_view_func = view_func
        request._posthog_view_kwargs = view_kwargs
        request._posthog_view_module = view_module

        return None

    def process_response(self, request, response):
        """
        Called after the view has been processed. At this point, DRF authentication
        has run and request.user should be properly set.
        """
        if not self.posthog_enabled:
            return response

        # Check if we stored view information (meaning this is a tracked endpoint)
        if not hasattr(request, '_posthog_view_func'):
            return response

        try:
            # Get stored view information
            view_func = request._posthog_view_func
            view_kwargs = request._posthog_view_kwargs
            view_module = request._posthog_view_module

            # Get endpoint name
            endpoint_name = self._get_endpoint_name(request, view_func, view_kwargs)

            # Get user information (now after DRF authentication)
            user_info = self._get_user_info(request)

            # Prepare event data
            event_properties = {
                'endpoint': endpoint_name,
                'method': request.method,
                'app': f'tellme-app.{self._get_app_name(view_module)}',
                'environment': settings.TELLME_ENV,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip_address': self._get_client_ip(request),
                'status_code': response.status_code,
            }

            # Add any additional request metadata
            if hasattr(request, 'resolver_match') and request.resolver_match:
                event_properties['url_name'] = request.resolver_match.url_name
                event_properties['namespace'] = request.resolver_match.namespace

            # Send event to PostHog
            posthog.capture(
                distinct_id=user_info['distinct_id'],
                event=f'tellme-app: {endpoint_name}',
                properties=event_properties,
                groups={
                    'environment': settings.TELLME_ENV
                }
            )

        except Exception as e:
            # Log error but don't break the request
            logger.warning(
                "PostHog tracking error for endpoint %s: %s",
                getattr(request, '_posthog_view_func', {}).get('__name__', 'unknown'),
                str(e),
                exc_info=True,
                extra={
                    'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                    'endpoint': getattr(request, 'path', 'unknown'),
                    'method': getattr(request, 'method', 'unknown'),
                }
            )

        return response

    def _get_endpoint_name(self, request, view_func, view_kwargs):
        """
        Generate a meaningful endpoint name from the view function and URL pattern.
        """
        # Try to get the URL name first
        if hasattr(request, 'resolver_match') and request.resolver_match:
            url_name = request.resolver_match.url_name
            if url_name:
                return url_name

        # Fallback to view function name
        view_name = view_func.__name__

        # If it's a class-based view, get the class name
        if hasattr(view_func, 'view_class'):
            view_name = view_func.view_class.__name__

        # Add HTTP method for better clarity
        return f"{request.method} {view_name}"

    def _get_app_name(self, view_module):
        """
        Extract the app name from the view module path.
        """
        if 'call_miner' in view_module:
            return 'call_miner'
        elif 'call_processing' in view_module:
            return 'call_processing'
        return 'unknown'

    def _get_user_info(self, request):
        """
        Extract user information for PostHog tracking.
        """
        user_info = {
            'distinct_id': 'anonymous',
            'email': None,
            'is_authenticated': False
        }

        # Check if user exists and is not anonymous
        # In DRF with custom authentication, we need to check if user is not AnonymousUser
        if hasattr(request, 'user') and request.user and not request.user.is_anonymous:
            user_info.update({
                'distinct_id': request.user.email or str(request.user.id),
                'email': request.user.email,
                'is_authenticated': True,
                'user_id': str(request.user.id),
                'is_staff': getattr(request.user, 'is_staff', False),
                'is_superuser': getattr(request.user, 'is_superuser', False)
            })

            # Add organization info if available
            if hasattr(request.user, 'employee') and request.user.employee:
                employee = request.user.employee
                user_info.update({
                    'organization_id': employee.organization.id,
                    'organization_name': employee.organization.name,
                    'employee_role': employee.role,
                    'is_organization_admin': employee.is_organization_admin
                })

        return user_info

    def _get_client_ip(self, request):
        """
        Get the client IP address from request headers.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip