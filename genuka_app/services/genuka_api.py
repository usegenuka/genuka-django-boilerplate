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

    def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Access token string

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

        response = requests.post(token_url, data=payload, headers=headers)

        if not response.ok:
            raise Exception(f"Token exchange failed: {response.status_code} {response.text}")

        data = response.json()
        return data.get('access_token')

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

        response = requests.get(url)

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

        response = requests.get(url, headers=headers)

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

        response = requests.post(url, json=data, headers=headers)

        if not response.ok:
            raise Exception(f"POST {endpoint} failed: {response.status_code}")

        return response.json()
