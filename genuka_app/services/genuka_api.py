"""
Genuka API Service for interacting with Genuka platform
"""
import requests
from django.conf import settings


class GenukaApiService:
    """Handles all interactions with the Genuka API"""

    def __init__(self):
        self.base_url = settings.GENUKA_URL
        self.client_id = settings.GENUKA_CLIENT_ID
        self.client_secret = settings.GENUKA_CLIENT_SECRET
        self.redirect_uri = settings.GENUKA_REDIRECT_URI
        # Disable SSL verification in debug mode (local development)
        self.verify_ssl = not settings.DEBUG

    def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Dictionary with access_token, refresh_token, expires_in_minutes

        Raises:
            Exception: If token exchange fails
        """
        token_url = f"{self.base_url}/oauth/token"

        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(token_url, data=payload, headers=headers, verify=self.verify_ssl)

        if not response.ok:
            raise Exception(f"Token exchange failed: {response.status_code} {response.text}")

        data = response.json()
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in_minutes': data.get('expires_in_minutes', 60),
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Genuka refresh token

        Returns:
            Dictionary with access_token, refresh_token, expires_in_minutes

        Raises:
            Exception: If token refresh fails
        """
        refresh_url = f"{self.base_url}/oauth/refresh"

        payload = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.post(refresh_url, json=payload, headers=headers, verify=self.verify_ssl)

        if not response.ok:
            raise Exception(f"Token refresh failed: {response.status_code} {response.text}")

        data = response.json()
        return {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_in_minutes': data.get('expires_in_minutes', 60),
        }

    def get_company_info(self, company_id: str) -> dict:
        """
        Get company information from Genuka.

        Args:
            company_id: Genuka company ID

        Returns:
            Dictionary with company information
        """
        # Using Genuka API to get company info
        url = f"{self.base_url}/companies/{company_id}"

        response = requests.get(url, verify=self.verify_ssl)

        if not response.ok:
            # Return minimal info if API call fails
            return {'name': f'Company {company_id}'}

        return response.json()

    def get(self, endpoint: str, access_token: str) -> dict:
        """
        Make authenticated GET request to Genuka API.

        Args:
            endpoint: API endpoint (e.g., '/api/orders')
            access_token: OAuth access token

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers, verify=self.verify_ssl)

        if not response.ok:
            raise Exception(f"GET {endpoint} failed: {response.status_code}")

        return response.json()

    def post(self, endpoint: str, access_token: str, data: dict) -> dict:
        """
        Make authenticated POST request to Genuka API.

        Args:
            endpoint: API endpoint
            access_token: OAuth access token
            data: Request body data

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}{endpoint}"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        response = requests.post(url, json=data, headers=headers, verify=self.verify_ssl)

        if not response.ok:
            raise Exception(f"POST {endpoint} failed: {response.status_code}")

        return response.json()
