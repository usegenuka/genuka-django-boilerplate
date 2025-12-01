"""
OAuth Service for Genuka authentication
"""
import hmac
import hashlib
import time
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone

from .genuka_api import GenukaApiService
from .company import CompanyService


class OAuthService:
    """Handles OAuth authentication flow with Genuka"""

    def __init__(self):
        self.genuka_api = GenukaApiService()
        self.company_service = CompanyService()

    def generate_hmac(self, params: dict) -> str:
        """
        Generate HMAC signature for OAuth callback validation.

        Args:
            params: Dictionary with code, company_id, redirect_to, timestamp

        Returns:
            HMAC signature as hex string

        Note:
            The redirect_to parameter arrives already URL-encoded once (Django decodes query params).
            urlencode will encode it again, matching Genuka's double encoding.
            We use quote_via=quote to match PHP's http_build_query behavior.
        """
        from urllib.parse import quote

        # Sort parameters alphabetically by key
        sorted_params = dict(sorted(params.items()))

        # Build query string using quote (not quote_plus) to match PHP's http_build_query
        # PHP uses rawurlencode for values which encodes spaces as %20, not +
        query_string = urlencode(sorted_params, quote_via=quote)

        # Generate HMAC-SHA256
        signature = hmac.new(
            settings.GENUKA_CLIENT_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def verify_hmac(self, params: dict, received_hmac: str) -> bool:
        """
        Verify HMAC signature using constant-time comparison.

        Args:
            params: Dictionary with code, company_id, redirect_to, timestamp
            received_hmac: HMAC signature received from request

        Returns:
            True if HMAC is valid
        """
        expected_hmac = self.generate_hmac(params)
        return hmac.compare_digest(expected_hmac, received_hmac)

    def validate_timestamp(self, timestamp: str) -> bool:
        """
        Validate that timestamp is within tolerance (prevents replay attacks).

        Args:
            timestamp: Unix timestamp as string

        Returns:
            True if timestamp is valid
        """
        try:
            timestamp_int = int(timestamp)
            current_time = int(time.time())
            age = current_time - timestamp_int
            return age <= settings.OAUTH_TIMESTAMP_TOLERANCE
        except (ValueError, TypeError):
            return False

    def handle_callback(self, code: str, company_id: str, timestamp: str,
                        hmac_signature: str, redirect_to: str) -> dict:
        """
        Handle OAuth callback from Genuka.

        Args:
            code: Authorization code
            company_id: Genuka company ID
            timestamp: Request timestamp
            hmac_signature: HMAC signature
            redirect_to: Redirect URL after success

        Returns:
            Dictionary with success status and company_id

        Raises:
            ValueError: If validation fails
        """
        # Verify HMAC signature
        params = {
            'code': code,
            'company_id': company_id,
            'redirect_to': redirect_to,
            'timestamp': timestamp,
        }

        if not self.verify_hmac(params, hmac_signature):
            raise ValueError('Invalid HMAC signature')

        # Validate timestamp
        if not self.validate_timestamp(timestamp):
            raise ValueError('Request expired')

        # Exchange code for tokens
        token_data = self.genuka_api.exchange_code_for_token(code)

        # Fetch company information
        company_info = self.genuka_api.get_company_info(company_id)

        # Calculate token expiration time
        expires_in_minutes = token_data.get('expires_in_minutes', 60)
        token_expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

        # Save/update company in database
        company_data = {
            'id': company_id,
            'handle': company_info.get('handle'),
            'name': company_info.get('name', ''),
            'description': company_info.get('description'),
            'logo_url': company_info.get('logoUrl'),
            'authorization_code': code,
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'token_expires_at': token_expires_at,
            'phone': company_info.get('metadata', {}).get('contact'),
        }

        self.company_service.upsert_company(company_data)

        return {'success': True, 'company_id': company_id}

    def validate_callback_params(self, code: str, company_id: str,
                                  timestamp: str, hmac_signature: str) -> bool:
        """
        Validate that all required callback parameters are present.

        Returns:
            True if all parameters are present and non-empty
        """
        return all([code, company_id, timestamp, hmac_signature])
