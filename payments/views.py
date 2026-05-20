import stripe

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .serializers import CheckoutSessionSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
	@swagger_auto_schema(
		operation_summary="Create Stripe checkout session",
		operation_description="Creates a Stripe Checkout Session from request data and returns the hosted checkout URL.",
		request_body=CheckoutSessionSerializer,
		responses={
			200: openapi.Response(
				description="Checkout session created successfully",
				schema=openapi.Schema(
					type=openapi.TYPE_OBJECT,
					properties={
						"checkout_url": openapi.Schema(type=openapi.TYPE_STRING),
					},
					required=["checkout_url"],
				),
			),
			400: openapi.Response(
				description="Checkout session creation failed",
				schema=openapi.Schema(
					type=openapi.TYPE_OBJECT,
					properties={
						"error": openapi.Schema(type=openapi.TYPE_STRING),
					},
					required=["error"],
				),
			),
		},
	)
	def post(self, request):
		serializer = CheckoutSessionSerializer(data=request.data)

		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		data = serializer.validated_data

		try:
			checkout_session = stripe.checkout.Session.create(
				payment_method_types=["card"],
				line_items=[
					{
						"price_data": {
							"currency": data["currency"],
							"product_data": {
								"name": data["product_name"],
							},
							"unit_amount": data["amount"],
						},
						"quantity": data["quantity"],
					},
				],
				mode="payment",
				success_url="http://localhost:3000/success",
				cancel_url="http://localhost:3000/cancel",
			)

			return Response({"checkout_url": checkout_session.url})

		except Exception as exc:
			return Response(
				{"error": str(exc)},
				status=status.HTTP_400_BAD_REQUEST,
			)


def payment_success(request):
	return JsonResponse({"message": "Payment successful"})


def payment_cancel(request):
	return JsonResponse({"message": "Payment cancelled"})
