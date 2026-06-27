import os
import requests
from django.utils.deprecation import MiddlewareMixin

LOG_API = os.environ.get('LOG_API', 'https://4.224.186.213/evaluation-service/logs')
ACCESS_TOKEN = os.environ.get('LOG_ACCESS_TOKEN') or os.environ.get('DEPOT_API_TOKEN') or ''


def log(stack, level, package_name, message):
    """Synchronous helper for logging. Errors are swallowed to avoid crashing handlers."""
    try:
        headers = {'Content-Type': 'application/json'}
        if ACCESS_TOKEN:
            headers['Authorization'] = f'Bearer {ACCESS_TOKEN}'
        requests.post(
            LOG_API,
            json={'stack': stack, 'level': level, 'package': package_name, 'message': message},
            headers=headers,
            timeout=5,
        )
    except Exception as e:
        # Best effort: don't raise
        print('Remote logging failed:', str(e))


class LoggingMiddleware(MiddlewareMixin):
    """Attaches a request.log function and emits a basic request-level info log."""

    def process_request(self, request):
        request.log = lambda stack, level, package, message: log(stack, level, package, message)
        # fire-and-forget basic info
        try:
            log('backend', 'info', 'http', f"{request.method} {request.get_full_path()}")
        except Exception:
            pass