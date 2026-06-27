import os
import requests

# Default URLs are taken from the assignment; note the original strings contained a space
# so prefer to set correct URLs via environment variables in production.
DEPOT_API_URL = os.environ.get('DEPOT_API_URL', 'http://4.224.186.213/evaluation%20service/depots')
VEHICLES_API_URL = os.environ.get('VEHICLES_API_URL', 'http://4.224.186.213/evaluation%20service/vehicles')
DEPOT_API_TOKEN = os.environ.get('DEPOT_API_TOKEN', '')


def _auth_headers():
    headers = {}
    if DEPOT_API_TOKEN:
        headers['Authorization'] = f'Bearer {DEPOT_API_TOKEN}'
    return headers


def fetch_depots():
    resp = requests.get(DEPOT_API_URL, headers=_auth_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()


def fetch_vehicles():
    """Fetch vehicles from the Vehicles API.

    Returns the parsed JSON. Raises for HTTP errors.
    """
    resp = requests.get(VEHICLES_API_URL, headers=_auth_headers(), timeout=10)
    resp.raise_for_status()
    return resp.json()