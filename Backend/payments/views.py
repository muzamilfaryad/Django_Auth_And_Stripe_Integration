import stripe
import logging
import json
import uuid
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Order, Payment, PaymentWebhookLog
from .serializers import PaymentIntentSerializer, OrderSerializer, PaymentSerializer
from .services import StripeService

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    """
    Create a Stripe PaymentIntent with proper authentication and error handling.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Create Payment Intent",
        operation_description="Create a Stripe PaymentIntent for client-side payment processing",
        request_body=PaymentIntentSerializer,
        responses={
            200: openapi.Response(
                description="Payment intent created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "clientSecret": openapi.Schema(type=openapi.TYPE_STRING),
                        "paymentIntentId": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
            500: openapi.Response(description="Stripe API error"),
        },
    )
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            amount = data.get('amount')
            currency = data.get('currency', 'usd')
            customer_email = data.get('customer_email')
            customer_name = data.get('customer_name', '')
            product_name = data.get('product_name', 'Product')
            quantity = data.get('quantity', 1)
            metadata = data.get('metadata', {})
            idempotency_key = data.get('idempotency_key') or str(uuid.uuid4())
            
            # Generate order ID
            order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
            
            # Create order record
            order = Order.objects.create(
                order_id=order_id,
                product_name=product_name,
                amount=amount,
                currency=currency,
                quantity=quantity,
                customer_email=customer_email or 'guest@example.com',
                customer_name=customer_name,
                metadata=metadata,
                user=request.user if request.user.is_authenticated else None,
            )
            
            # Create payment intent using service
            stripe_service = StripeService()
            metadata['order_id'] = order_id
            
            payment_intent = stripe_service.create_payment_intent(
                amount=amount,
                currency=currency,
                customer_email=customer_email,
                metadata=metadata,
                idempotency_key=idempotency_key,
            )
            
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                payment_intent_id=payment_intent.id,
                amount=amount,
                currency=currency,
                status='processing',
            )
            
            return Response({
                'clientSecret': payment_intent.client_secret,
                'paymentIntentId': payment_intent.id,
                'orderId': order_id,
            }, status=status.HTTP_201_CREATED)
        
        except stripe.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            return Response(
                {'error': 'Card error: ' + e.user_message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.RateLimitError:
            logger.error("Rate limit error")
            return Response(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid request: {e}")
            return Response(
                {'error': f'Invalid request: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.AuthenticationError:
            logger.error("Stripe authentication failed")
            return Response(
                {'error': 'Stripe authentication failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except stripe.error.APIConnectionError:
            logger.error("Stripe connection failed")
            return Response(
                {'error': 'Connection error with payment provider'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateCheckoutSessionView(APIView):
    """
    Create a Stripe Checkout Session for hosted checkout flow.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Create Checkout Session",
        operation_description="Create a Stripe Checkout Session for hosted checkout",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_name': openapi.Schema(type=openapi.TYPE_STRING),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                'currency': openapi.Schema(type=openapi.TYPE_STRING),
                'customer_email': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(description="Checkout session created"),
            400: openapi.Response(description="Validation error"),
        },
    )
    def post(self, request):
        try:
            product_name = request.data.get('product_name')
            amount = request.data.get('amount')
            quantity = request.data.get('quantity', 1)
            currency = request.data.get('currency', 'usd')
            customer_email = request.data.get('customer_email')
            
            if not product_name or not amount:
                return Response(
                    {'error': 'product_name and amount are required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Generate order ID
            order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"
            
            # Create order record
            order = Order.objects.create(
                order_id=order_id,
                product_name=product_name,
                amount=amount,
                currency=currency,
                quantity=quantity,
                customer_email=customer_email or 'guest@example.com',
                user=request.user if request.user.is_authenticated else None,
            )
            
            # Create checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': currency,
                            'product_data': {
                                'name': product_name,
                            },
                            'unit_amount': amount,
                        },
                        'quantity': quantity,
                    },
                ],
                mode='payment',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                customer_email=customer_email,
                metadata={'order_id': order_id},
            )
            
            return Response({'checkout_url': checkout_session.url})
        
        except Exception as exc:
            logger.error(f"Checkout session error: {str(exc)}")
            return Response(
                {'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        logger.warning("Webhook received without signature header")
        return JsonResponse({'error': 'Missing signature'}, status=400)
    
    try:
        stripe_service = StripeService()
        event = stripe_service.verify_webhook_signature(payload, sig_header)
        
        # Log the webhook event
        webhook_log = stripe_service.log_webhook_event(event)
        
        # Handle different event types
        event_type = event['type']
        data = event.get('data', {}).get('object', {})
        
        if event_type == 'payment_intent.succeeded':
            payment_intent_id = data.get('id')
            stripe_service.handle_payment_intent_succeeded(payment_intent_id)
            webhook_log.processed = True
            webhook_log.save()
        
        elif event_type == 'payment_intent.payment_failed':
            payment_intent_id = data.get('id')
            error_message = data.get('last_payment_error', {}).get('message')
            stripe_service.handle_payment_intent_payment_failed(payment_intent_id, error_message)
            webhook_log.processed = True
            webhook_log.save()
        
        elif event_type == 'charge.refunded':
            payment_intent_id = data.get('payment_intent')
            refund_amount = data.get('amount_refunded')
            stripe_service.handle_charge_refunded(payment_intent_id, refund_amount)
            webhook_log.processed = True
            webhook_log.save()
        
        logger.info(f"Processed webhook event: {event_type}")
        return JsonResponse({'success': True}, status=200)
    
    except ValueError as e:
        logger.error(f"Webhook payload error: {str(e)}")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature error: {str(e)}")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def payment_success(request):
    """Redirect page after successful payment."""
    return JsonResponse({'message': 'Payment successful'})


def payment_cancel(request):
    """Redirect page after cancelled payment."""
    return JsonResponse({'message': 'Payment cancelled'})
