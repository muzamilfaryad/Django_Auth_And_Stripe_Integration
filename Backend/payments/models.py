from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    amount = models.IntegerField(help_text="Amount in cents")
    currency = models.CharField(max_length=10, default='usd')
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Billing details
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_id} - {self.product_name}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('requires_action', 'Requires Action'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_intent_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default='usd')
    
    # Payment method
    payment_method = models.CharField(max_length=255, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    card_last_four = models.CharField(max_length=4, blank=True)
    
    # Error handling
    error_code = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    
    # Stripe response
    stripe_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_intent_id} - {self.status}"


class PaymentWebhookLog(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhook_logs')
    
    payload = models.JSONField()
    processed = models.BooleanField(default=False)
    error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook {self.event_type} - {self.event_id}"
