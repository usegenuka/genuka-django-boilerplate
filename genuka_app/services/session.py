"""
Session Service for JWT-based double cookie authentication
"""
import jwt
import time
import logging
from typing import Optional
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from ..models import Company

logger = logging.getLogger(__name__)


class SessionService:
    """
    Handles JWT session management with double cookie pattern.

    Uses two HTTP-only cookies:
    - session: Short-lived (7 hours) for accessing protected routes
    - refresh_session: Long-lived (30 days) for refreshing expired sessions
    """

    SESSION_COOKIE_NAME = 'session'
    REFRESH_COOKIE_NAME = 'refresh_session'
    SESSION_MAX_AGE = 60 * 60 * 7  # 7 hours in seconds
    REFRESH_MAX_AGE = 60 * 60 * 24 * 30  # 30 days in seconds

    def __init__(self):
        self.secret = settings.GENUKA_CLIENT_SECRET

    def create_session(self, company_id: str, response: HttpResponse) -> str:
        """
        Create both session and refresh cookies.

        Args:
            company_id: Genuka company ID
            response: Django HttpResponse to set cookies on

        Returns:
            Session JWT token
        """
        is_production = not settings.DEBUG
        current_time = int(time.time())

        # Create session token (short-lived: 7h)
        session_payload = {
            'companyId': company_id,
            'type': 'session',
            'iat': current_time,
            'exp': current_time + self.SESSION_MAX_AGE,
        }
        session_token = jwt.encode(session_payload, self.secret, algorithm='HS256')

        # Create refresh token (long-lived: 30 days)
        refresh_payload = {
            'companyId': company_id,
            'type': 'refresh',
            'iat': current_time,
            'exp': current_time + self.REFRESH_MAX_AGE,
        }
        refresh_token = jwt.encode(refresh_payload, self.secret, algorithm='HS256')

        # Set session cookie (7h)
        response.set_cookie(
            self.SESSION_COOKIE_NAME,
            session_token,
            max_age=self.SESSION_MAX_AGE,
            path='/',
            secure=is_production,
            httponly=True,
            samesite='Lax',
        )

        # Set refresh cookie (30 days)
        response.set_cookie(
            self.REFRESH_COOKIE_NAME,
            refresh_token,
            max_age=self.REFRESH_MAX_AGE,
            path='/',
            secure=is_production,
            httponly=True,
            samesite='Lax',
        )

        return session_token

    def verify_jwt(self, token: str) -> Optional[dict]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            # Don't log expected expiration
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"JWT verification failed: {e}")
            return None

    def verify_refresh_token(self, request: HttpRequest) -> Optional[str]:
        """
        Verify refresh token and return companyId.

        Args:
            request: Django HttpRequest

        Returns:
            Company ID or None if invalid
        """
        token = request.COOKIES.get(self.REFRESH_COOKIE_NAME)

        if not token:
            return None

        payload = self.verify_jwt(token)

        # Ensure it's a refresh token, not a session token
        if not payload or payload.get('type') != 'refresh':
            return None

        return payload.get('companyId')

    def get_current_company_id(self, request: HttpRequest) -> Optional[str]:
        """
        Get current company ID from session cookie.

        Args:
            request: Django HttpRequest

        Returns:
            Company ID or None if not authenticated
        """
        token = request.COOKIES.get(self.SESSION_COOKIE_NAME)

        if not token:
            return None

        payload = self.verify_jwt(token)

        if not payload or payload.get('type') != 'session':
            return None

        return payload.get('companyId')

    def get_authenticated_company(self, request: HttpRequest) -> Optional[Company]:
        """
        Get authenticated company from current request.

        Args:
            request: Django HttpRequest

        Returns:
            Company model or None if not authenticated
        """
        company_id = self.get_current_company_id(request)

        if not company_id:
            return None

        try:
            return Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return None

    def is_authenticated(self, request: HttpRequest) -> bool:
        """
        Check if user is authenticated.

        Args:
            request: Django HttpRequest

        Returns:
            True if authenticated
        """
        return self.get_current_company_id(request) is not None

    def destroy_session(self, response: HttpResponse) -> None:
        """
        Destroy both session and refresh cookies.

        Args:
            response: Django HttpResponse to delete cookies from
        """
        response.delete_cookie(self.SESSION_COOKIE_NAME, path='/')
        response.delete_cookie(self.REFRESH_COOKIE_NAME, path='/')

    @classmethod
    def get_session_cookie_name(cls) -> str:
        """Get the session cookie name."""
        return cls.SESSION_COOKIE_NAME

    @classmethod
    def get_refresh_cookie_name(cls) -> str:
        """Get the refresh cookie name."""
        return cls.REFRESH_COOKIE_NAME
