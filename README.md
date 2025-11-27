# Genuka Django Boilerplate

A Django boilerplate for building integrations with the Genuka e-commerce platform. Implements OAuth 2.0 authentication, webhook handling, and company data synchronization.

## Quick Start

```bash
git clone https://github.com/usegenuka/genuka-django-boilerplate.git
cd genuka-django-boilerplate
```

## Features

- OAuth 2.0 authentication flow with Genuka
- HMAC signature validation for secure callbacks
- Webhook event handling for real-time updates
- Company data synchronization and storage
- Service layer architecture pattern

## Requirements

- Python 3.10+
- Django 5.x
- pip or pipenv

## Installation

### 1. Clone and navigate to the project

```bash
cd genuka-django-boilerplate
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your Genuka credentials
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start development server

```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

## Project Structure

```
genuka-django-boilerplate/
├── config/                     # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI entry point
├── genuka_app/                # Main application
│   ├── models.py              # Company model
│   ├── views.py               # API views
│   ├── urls.py                # App URL routes
│   └── services/              # Business logic
│       ├── oauth.py           # OAuth service
│       ├── company.py         # Company DB service
│       └── genuka_api.py      # Genuka API client
├── manage.py
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/callback` | OAuth callback handler |
| POST | `/api/auth/webhook` | Webhook event receiver |
| GET | `/health` | Health check endpoint |

## OAuth Flow

1. User is redirected to Genuka authorization page
2. After authorization, Genuka redirects to `/api/auth/callback` with:
   - `code`: Authorization code
   - `company_id`: Genuka company ID
   - `timestamp`: Request timestamp
   - `hmac`: HMAC signature
   - `redirect_to`: Post-auth redirect URL
3. The callback handler:
   - Validates HMAC signature
   - Checks timestamp freshness (replay attack prevention)
   - Exchanges code for access token
   - Fetches and stores company data
   - Redirects user to the specified URL

## Webhook Events

Supported webhook events:

| Event | Description |
|-------|-------------|
| `company.updated` | Company information updated |
| `company.deleted` | Company deleted |
| `order.created` | New order created |
| `order.updated` | Order updated |
| `product.created` | New product created |
| `product.updated` | Product updated |
| `subscription.created` | New subscription created |
| `subscription.updated` | Subscription updated |
| `subscription.cancelled` | Subscription cancelled |
| `payment.succeeded` | Payment successful |
| `payment.failed` | Payment failed |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Django debug mode | `True` |
| `SECRET_KEY` | Django secret key | Required |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection URL | SQLite |
| `GENUKA_URL` | Genuka API base URL | `https://api.genuka.com` |
| `GENUKA_CLIENT_ID` | OAuth client ID | Required |
| `GENUKA_CLIENT_SECRET` | OAuth client secret | Required |
| `GENUKA_REDIRECT_URI` | OAuth callback URL | Required |
| `GENUKA_DEFAULT_REDIRECT` | Default post-auth redirect | `/dashboard` |
| `OAUTH_TIMESTAMP_TOLERANCE` | Max timestamp age (seconds) | `300` |

## Database Support

The boilerplate supports multiple databases:

### SQLite (Default)
No configuration needed. Uses `db.sqlite3` in project root.

### PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost:5432/genuka_db
```

### MySQL/MariaDB
```env
DATABASE_URL=mysql://user:password@localhost:3306/genuka_db
```

## Development Commands

```bash
# Run development server
python manage.py runserver

# Run on specific port
python manage.py runserver 0.0.0.0:4000

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Django shell
python manage.py shell
```

## Services

### OAuthService
Handles OAuth authentication flow:
- HMAC signature generation and validation
- Timestamp verification
- Code-to-token exchange
- Company data synchronization

### CompanyService
Database operations for Company model:
- `find_by_id()` - Find company by Genuka ID
- `find_by_handle()` - Find company by handle
- `find_by_access_token()` - Find company by token
- `find_all()` - List all companies
- `upsert_company()` - Create or update company
- `update_by_id()` - Update company fields
- `delete_by_id()` - Delete company

### GenukaApiService
Genuka API client:
- `exchange_code_for_token()` - OAuth token exchange
- `get_company_info()` - Fetch company details
- `get()` - Authenticated GET request
- `post()` - Authenticated POST request

## Extending the Boilerplate

### Adding New Webhook Handlers

Edit `genuka_app/views.py` and implement the handler methods:

```python
def _handle_order_created(self, data: dict, company_id: str):
    """Handle order.created event"""
    logger.info(f"Order created: {data}")
    # Your order creation logic here
```

### Adding New API Endpoints

1. Add the view in `genuka_app/views.py`
2. Add the URL pattern in `genuka_app/urls.py`

## License

MIT
