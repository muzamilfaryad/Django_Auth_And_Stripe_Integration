from rest_framework import serializers


class CheckoutSessionSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(default=1, min_value=1, required=False)
    currency = serializers.CharField(default="usd", max_length=10, required=False)