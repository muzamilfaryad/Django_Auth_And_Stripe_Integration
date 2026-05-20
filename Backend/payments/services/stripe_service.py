import stripe
import logging
from django.conf import settings
from payments.models import Payment, Order, PaymentWebhookLog

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment_intent(self, amount, currency='usd', customer_email=None, 
                             metadata=None, idempotency_key=None):
        """
        Create a Stripe PaymentIntent with proper error handling.
        
        Args:
            amount: Amount in cents
            currency: Currency code (default: 'usd')
            customer_email: Customer email for receipt
            metadata: Additional metadata
            idempotency_key: Idempotency key to prevent duplicate charges
            
        Returns:
            PaymentIntent object or raises exception
        """
        try:
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            params = {
                'amount': amount,
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            if customer_email:
                params['receipt_email'] = customer_email
            
            if metadata:
                params['metadata'] = metadata
            
            # Add idempotency key to prevent duplicate payment intents
            headers = {}
            if idempotency_key:
                headers['Idempotency-Key'] = idempotency_key
            
            payment_intent = self.stripe.PaymentIntent.create(
                **params,
                **({'idempotency_key': idempotency_key} if idempotency_key else {})
            )
            
            logger.info(f"Created PaymentIntent: {payment_intent.id}")
            return payment_intent
            
        except self.stripe.error.CardError as e:
            logger.error(f"Card error: {e.user_message}")
            raise
        except self.stripe.error.RateLimitError:
            logger.error("Rate limit error from Stripe")
            raise
        except self.stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid request: {e}")
            raise
        except self.stripe.error.AuthenticationError:
            logger.error("Stripe API authentication failed")
            raise
        except self.stripe.error.APIConnectionError:
            logger.error("Failed to connect to Stripe API")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {str(e)}")
            raise

    def handle_payment_intent_succeeded(self, payment_intent_id):
        """Handle successful payment intent event."""
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            payment.status = 'succeeded'
            
            # Extract card details
            if payment_intent_id:
                pi = self.stripe.PaymentIntent.retrieve(payment_intent_id)
                if pi.charges and len(pi.charges.data) > 0:
                    charge = pi.charges.data[0]
                    if charge.payment_method_details and charge.payment_method_details.card:
                        payment.card_brand = charge.payment_method_details.card.brand
                        payment.card_last_four = str(charge.payment_method_details.card.last4)
            
            payment.stripe_response = pi.to_dict() if payment_intent_id else {}
            payment.save()
            
            # Update order status
            payment.order.status = 'completed'
            payment.order.save()
            
            logger.info(f"Payment succeeded: {payment_intent_id}")
            
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for intent: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Error handling payment succeeded: {str(e)}")

    def handle_payment_intent_payment_failed(self, payment_intent_id, error_message=None):
        """Handle failed payment intent event."""
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            payment.status = 'failed'
            payment.error_message = error_message or "Payment failed"
            payment.save()
            
            # Update order status
            payment.order.status = 'failed'
            payment.order.save()
            
            logger.warning(f"Payment failed: {payment_intent_id}")
            
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for intent: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Error handling payment failed: {str(e)}")

    def handle_charge_refunded(self, payment_intent_id, refund_amount):
        """Handle refunded charge event."""
        try:
            payment = Payment.objects.get(payment_intent_id=payment_intent_id)
            payment.status = 'canceled'
            payment.save()
            logger.info(f"Payment refunded: {payment_intent_id}, amount: {refund_amount}")
        except Payment.DoesNotExist:
            logger.warning(f"Payment not found for intent: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Error handling charge refunded: {str(e)}")

    def verify_webhook_signature(self, payload, sig_header):
        """Verify Stripe webhook signature."""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            logger.error("Invalid webhook payload")
            raise
        except self.stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise

    def log_webhook_event(self, event):
        """Log webhook event in database."""
        try:
            event_log = PaymentWebhookLog(
                event_id=event['id'],
                event_type=event['type'],
                payload=event,
            )
            
            # Try to associate with payment if available
            if event['type'] in ['payment_intent.succeeded', 'payment_intent.payment_failed', 'charge.refunded']:
                data = event.get('data', {}).get('object', {})
                payment_intent_id = data.get('id') or data.get('payment_intent')
                try:
                    payment = Payment.objects.get(payment_intent_id=payment_intent_id)
                    event_log.payment = payment
                except Payment.DoesNotExist:
                    pass
            
            event_log.save()
            return event_log
            
        except Exception as e:
            logger.error(f"Error logging webhook event: {str(e)}")
            raise
