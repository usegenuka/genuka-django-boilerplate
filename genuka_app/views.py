"""
Views for Genuka OAuth and Webhook handling
"""
import json
import logging
from datetime import timedelta
from urllib.parse import unquote

from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings

from .services import OAuthService, CompanyService, SessionService, GenukaApiService
from .models import Company

logger = logging.getLogger(__name__)


class CallbackView(View):
    """OAuth callback handler"""

    def get(self, request):
        """
        Handle GET /api/auth/callback

        Query Parameters:
            - code: Authorization code
            - company_id: Genuka company ID
            - timestamp: Request timestamp
            - hmac: HMAC signature
            - redirect_to: Redirect URL after success (optional)
        """
        try:
            # Extract parameters
            code = request.GET.get('code')
            company_id = request.GET.get('company_id')
            timestamp = request.GET.get('timestamp')
            hmac_signature = request.GET.get('hmac')
            redirect_to = request.GET.get('redirect_to', settings.GENUKA_DEFAULT_REDIRECT)

            # Validate required parameters
            oauth_service = OAuthService()

            if not oauth_service.validate_callback_params(
                code, company_id, timestamp, hmac_signature
            ):
                return JsonResponse({
                    'error': 'Missing required parameters',
                    'required': ['code', 'company_id', 'timestamp', 'hmac'],
                }, status=400)

            # Process OAuth callback
            oauth_service.handle_callback(
                code=code,
                company_id=company_id,
                timestamp=timestamp,
                hmac_signature=hmac_signature,
                redirect_to=redirect_to,
            )

            # Decode redirect_to for actual redirect
            decoded_redirect = unquote(redirect_to)

            # Create response with redirect
            response = HttpResponseRedirect(decoded_redirect)

            # Create session cookies
            session_service = SessionService()
            session_service.create_session(company_id, response)

            return response

        except ValueError as e:
            logger.error(f"OAuth validation error: {e}")
            return JsonResponse({'error': str(e)}, status=400)

        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


# Webhook event types
WEBHOOK_EVENTS = {
    'COMPANY_UPDATED': 'company.updated',
    'COMPANY_DELETED': 'company.deleted',
    'ORDER_CREATED': 'order.created',
    'ORDER_UPDATED': 'order.updated',
    'PRODUCT_CREATED': 'product.created',
    'PRODUCT_UPDATED': 'product.updated',
    'SUBSCRIPTION_CREATED': 'subscription.created',
    'SUBSCRIPTION_UPDATED': 'subscription.updated',
    'SUBSCRIPTION_CANCELLED': 'subscription.cancelled',
    'PAYMENT_SUCCEEDED': 'payment.succeeded',
    'PAYMENT_FAILED': 'payment.failed',
}


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """Webhook event handler"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.company_service = CompanyService()

    def post(self, request):
        """
        Handle POST /api/auth/webhook

        Body:
            - type: Event type
            - data: Event data
            - timestamp: Event timestamp
            - company_id: Genuka company ID
        """
        try:
            # Parse JSON body
            body = json.loads(request.body)

            event_type = body.get('type')
            event_data = body.get('data', {})
            company_id = body.get('company_id')

            logger.info(f"Webhook received: {event_type} for company {company_id}")

            # Process event based on type
            self._process_event(event_type, event_data, company_id)

            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JsonResponse({'error': 'Failed to process webhook'}, status=500)

    def _process_event(self, event_type: str, data: dict, company_id: str):
        """Process webhook event by type"""

        handlers = {
            WEBHOOK_EVENTS['COMPANY_UPDATED']: self._handle_company_updated,
            WEBHOOK_EVENTS['COMPANY_DELETED']: self._handle_company_deleted,
            WEBHOOK_EVENTS['ORDER_CREATED']: self._handle_order_created,
            WEBHOOK_EVENTS['ORDER_UPDATED']: self._handle_order_updated,
            WEBHOOK_EVENTS['PRODUCT_CREATED']: self._handle_product_created,
            WEBHOOK_EVENTS['PRODUCT_UPDATED']: self._handle_product_updated,
            WEBHOOK_EVENTS['SUBSCRIPTION_CREATED']: self._handle_subscription_created,
            WEBHOOK_EVENTS['SUBSCRIPTION_UPDATED']: self._handle_subscription_updated,
            WEBHOOK_EVENTS['SUBSCRIPTION_CANCELLED']: self._handle_subscription_cancelled,
            WEBHOOK_EVENTS['PAYMENT_SUCCEEDED']: self._handle_payment_succeeded,
            WEBHOOK_EVENTS['PAYMENT_FAILED']: self._handle_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(data, company_id)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")

    # Company event handlers
    def _handle_company_updated(self, data: dict, company_id: str):
        """Handle company.updated event"""
        logger.info(f"Company updated: {company_id}")

        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']

        if update_data:
            self.company_service.update_by_id(company_id, update_data)

    def _handle_company_deleted(self, data: dict, company_id: str):
        """Handle company.deleted event"""
        logger.info(f"Company deleted: {company_id}")
        self.company_service.delete_by_id(company_id)

    # Order event handlers
    def _handle_order_created(self, data: dict, company_id: str):
        """Handle order.created event"""
        logger.info(f"Order created: {data}")
        # TODO: Implement your order creation logic

    def _handle_order_updated(self, data: dict, company_id: str):
        """Handle order.updated event"""
        logger.info(f"Order updated: {data}")
        # TODO: Implement your order update logic

    # Product event handlers
    def _handle_product_created(self, data: dict, company_id: str):
        """Handle product.created event"""
        logger.info(f"Product created: {data}")
        # TODO: Implement your product creation logic

    def _handle_product_updated(self, data: dict, company_id: str):
        """Handle product.updated event"""
        logger.info(f"Product updated: {data}")
        # TODO: Implement your product update logic

    # Subscription event handlers
    def _handle_subscription_created(self, data: dict, company_id: str):
        """Handle subscription.created event"""
        logger.info(f"Subscription created: {data}")
        # TODO: Implement your subscription creation logic

    def _handle_subscription_updated(self, data: dict, company_id: str):
        """Handle subscription.updated event"""
        logger.info(f"Subscription updated: {data}")
        # TODO: Implement your subscription update logic

    def _handle_subscription_cancelled(self, data: dict, company_id: str):
        """Handle subscription.cancelled event"""
        logger.info(f"Subscription cancelled: {data}")
        # TODO: Implement your subscription cancellation logic

    # Payment event handlers
    def _handle_payment_succeeded(self, data: dict, company_id: str):
        """Handle payment.succeeded event"""
        logger.info(f"Payment succeeded: {data}")
        # TODO: Implement your payment success logic

    def _handle_payment_failed(self, data: dict, company_id: str):
        """Handle payment.failed event"""
        logger.info(f"Payment failed: {data}")
        # TODO: Implement your payment failure logic


class HealthView(View):
    """Health check endpoint"""

    def get(self, request):
        """Handle GET /health"""
        return JsonResponse({
            'status': 'ok',
            'service': 'Genuka Django Boilerplate',
        })


class HomeView(View):
    """Home page - shows current company info if authenticated"""

    def get(self, request):
        """Handle GET /"""
        session_service = SessionService()
        company = session_service.get_authenticated_company(request)

        if company:
            return JsonResponse({
                'message': f'Bienvenue, {company.name}!',
                'authenticated': True,
                'company': {
                    'id': company.id,
                    'name': company.name,
                    'handle': company.handle,
                },
            })

        return JsonResponse({
            'message': 'Bienvenue sur Genuka Django Boilerplate',
            'authenticated': False,
            'hint': 'Installez l\'app via Genuka pour vous connecter',
        })


@method_decorator(csrf_exempt, name='dispatch')
class CheckView(View):
    """Check authentication status"""

    def get(self, request):
        """
        Handle GET /api/auth/check

        Returns:
            JSON with authenticated status
        """
        session_service = SessionService()
        is_authenticated = session_service.is_authenticated(request)

        return JsonResponse({
            'authenticated': is_authenticated,
        })


@method_decorator(csrf_exempt, name='dispatch')
class RefreshView(View):
    """Refresh session using refresh cookie"""

    def post(self, request):
        """
        Handle POST /api/auth/refresh

        No request body required - companyId comes from signed JWT cookie.
        """
        session_service = SessionService()

        # Get companyId from signed refresh cookie (tamper-proof)
        company_id = session_service.verify_refresh_token(request)

        if not company_id:
            return JsonResponse({
                'error': 'Invalid or expired refresh token',
                'code': 'REFRESH_TOKEN_INVALID',
            }, status=401)

        # Get company from database
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return JsonResponse({
                'error': 'Company not found',
                'code': 'COMPANY_NOT_FOUND',
            }, status=404)

        # Check if company has a refresh token
        if not company.refresh_token:
            return JsonResponse({
                'error': 'No refresh token available. Please reinstall the app.',
                'code': 'NO_REFRESH_TOKEN',
            }, status=401)

        try:
            # Call Genuka API to refresh tokens
            genuka_api = GenukaApiService()
            token_data = genuka_api.refresh_access_token(company.refresh_token)

            # Calculate new expiration time
            expires_in_minutes = token_data.get('expires_in_minutes', 60)
            token_expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)

            # Update company with new tokens
            company.access_token = token_data.get('access_token')
            company.refresh_token = token_data.get('refresh_token') or company.refresh_token
            company.token_expires_at = token_expires_at
            company.save()

            # Create new session cookies
            response = JsonResponse({
                'success': True,
                'message': 'Session refreshed successfully',
            })
            session_service.create_session(company_id, response)

            return response

        except Exception as e:
            logger.error(f"Session refresh failed: {e}")
            return JsonResponse({
                'error': 'Failed to refresh session. Please reinstall the app.',
                'code': 'REFRESH_FAILED',
            }, status=401)


class MeView(View):
    """Get current authenticated company"""

    def get(self, request):
        """
        Handle GET /api/auth/me

        Returns:
            JSON with current company info
        """
        session_service = SessionService()
        company = session_service.get_authenticated_company(request)

        if not company:
            return JsonResponse({
                'error': 'Not authenticated',
                'code': 'UNAUTHORIZED',
            }, status=401)

        return JsonResponse({
            'id': company.id,
            'handle': company.handle,
            'name': company.name,
            'description': company.description,
            'logo_url': company.logo_url,
            'phone': company.phone,
            'created_at': company.created_at.isoformat() if company.created_at else None,
            'updated_at': company.updated_at.isoformat() if company.updated_at else None,
        })


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    """Logout and destroy session"""

    def post(self, request):
        """
        Handle POST /api/auth/logout

        Returns:
            JSON with success status
        """
        session_service = SessionService()

        response = JsonResponse({
            'success': True,
            'message': 'Successfully logged out',
        })

        session_service.destroy_session(response)

        return response
