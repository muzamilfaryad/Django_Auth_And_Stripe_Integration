# Django Auth and Stripe Integration

Backend API for authentication, profile management, password recovery, email verification, and Stripe Checkout payments built with Django, Django REST Framework, JWT, and Stripe.

## Features

- Custom user model with email-based authentication
- JWT login and refresh tokens with SimpleJWT
- User registration with verification email flow
- Password change and password reset endpoints
- Stripe Checkout session creation for one-time payments
- Swagger and ReDoc API documentation
- PostgreSQL-backed data storage

## Tech Stack

- Django 5.2
- Django REST Framework
- djangorestframework-simplejwt
- drf-yasg
- django-cors-headers
- Stripe Python SDK
- PostgreSQL

## Project Structure

- `accounts/` - custom user model, auth views, serializers, and email backend
- `payments/` - Stripe checkout endpoints and payment helpers
- `core/` - project settings, root URLs, and WSGI/ASGI config

## Requirements

- Python 3.11+
- PostgreSQL
- Stripe account and API keys

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root.
4. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Start the development server:

```bash
python manage.py runserver
```

## Environment Variables

The project reads configuration from environment variables via `python-decouple`.

### Core Settings

- `SECRET_KEY`
- `DEBUG`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

### Email Settings

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `PASSWORD_RESET_CONFIRM_URL`
- `EMAIL_VERIFICATION_URL`

### Stripe Settings

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DOMAIN`

## Authentication

Authentication is email-first. The custom user model uses `email` as the login identifier, and JWT is the primary authentication mechanism.

### Auth Endpoints

- `POST /register/` - register a new user
- `POST /login/` - obtain access and refresh tokens
- `POST /change-password/` - change the authenticated user password
- `POST /reset-password/request/` - request a password reset email
- `POST /reset-password/confirm/` - confirm a password reset
- `POST /verify-email/` - verify an email address
- `POST /resend-verification-email/` - resend verification email

### JWT Endpoints

- `POST /api/token/` - obtain token pair
- `POST /api/token/refresh/` - refresh access token

## Payments

Stripe Checkout sessions are exposed under the payments API.

### Payment Endpoints

- `POST /api/payments/create-checkout-session/` - create a hosted Stripe Checkout session
- `GET /payments/success/` - success callback response
- `GET /payments/cancel/` - cancel callback response

### Checkout Request Example

```json
{
  "product_name": "Premium Plan",
  "amount": 2500,
  "quantity": 1,
  "currency": "usd"
}
```

### Checkout Response Example

```json
{
  "checkout_url": "https://checkout.stripe.com/..."
}
```

## API Documentation

- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`
- OpenAPI JSON: `/swagger.json`

## Notes

- The project uses PostgreSQL by default, so local SQLite will not work unless you update `core/settings.py`.
- CORS is currently open to all origins in development.
- Stripe checkout success and cancel URLs are set to local frontend routes in the payment view.

## License

No license has been specified yet.