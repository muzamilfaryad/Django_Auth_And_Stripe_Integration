from rest_framework import serializers
from .models import Order, Payment, PaymentWebhookLog


class CheckoutSessionSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(default=1, min_value=1, required=False)
    currency = serializers.CharField(default="usd", max_length=10, required=False)


class PaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating a payment intent."""
    amount = serializers.IntegerField(min_value=1, help_text="Amount in cents")
    currency = serializers.CharField(default="usd", max_length=10, required=False)
    customer_email = serializers.EmailField(required=False)
    customer_name = serializers.CharField(max_length=255, required=False)
    product_name = serializers.CharField(max_length=255, required=False)
    quantity = serializers.IntegerField(default=1, min_value=1, required=False)
    metadata = serializers.JSONField(required=False, default=dict)
    idempotency_key = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'product_name', 'amount', 'currency', 'quantity', 
                  'status', 'customer_email', 'customer_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_intent_id', 'status', 'amount', 'currency', 
                  'card_brand', 'card_last_four', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentWebhookLog
        fields = ['id', 'event_id', 'event_type', 'processed', 'error', 'created_at']
        read_only_fields = ['id', 'created_at']