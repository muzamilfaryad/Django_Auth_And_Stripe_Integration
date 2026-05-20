"use client";

import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { useState, useCallback } from "react";
import CheckoutForm from "../components/CheckoutForm";
import { v4 as uuidv4 } from "uuid";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const stripePromise = publishableKey ? loadStripe(publishableKey) : null;

function PaymentFormContent({
  clientSecret,
  orderId,
  loading,
  setLoading,
  message,
  messageType,
  setMessage,
  setMessageType,
  handleBackToForm,
}) {
  const stripe = useStripe();
  const elements = useElements();

  const handlePaymentSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      if (!stripe || !elements || !clientSecret) {
        setMessage("Payment system not ready");
        setMessageType("error");
        return;
      }

      setLoading(true);
      setMessage("");
      setMessageType("");

      try {
        const { error: submitError } = await elements.submit();

        if (submitError) {
          setMessage(submitError.message || "Please check your payment details.");
          setMessageType("error");
          setLoading(false);
          return;
        }

        const { error, paymentIntent } = await stripe.confirmPayment({
          elements,
          clientSecret,
          redirect: "if_required",
          confirmParams: {
            return_url: `${window.location.origin}/payment/success?order=${orderId}`,
          },
        });

        if (error) {
          setMessage(error.message || "Payment failed");
          setMessageType("error");
          setLoading(false);
        } else if (paymentIntent) {
          if (paymentIntent.status === "succeeded") {
            setMessage("Payment successful!");
            setMessageType("success");
            window.location.href = `/payment/success?order=${orderId}`;
          }
        }
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unexpected error");
        setMessageType("error");
        setLoading(false);
      }
    },
    [stripe, elements, clientSecret, orderId, setLoading, setMessage, setMessageType]
  );

  return (
    <>
      {clientSecret && (
        <form onSubmit={handlePaymentSubmit}>
          <div
            style={{
              padding: "1rem",
              borderRadius: 18,
              background: "rgba(255, 255, 255, 0.04)",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              marginBottom: "1rem",
            }}
          >
            <PaymentElement
              options={{
                layout: "tabs",
              }}
            />
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "1rem",
            }}
          >
            <button
              type="button"
              onClick={handleBackToForm}
              disabled={loading}
              style={{
                padding: "0.95rem 1.25rem",
                borderRadius: 999,
                border: "1px solid rgba(255, 255, 255, 0.2)",
                background: "transparent",
                color: "#38bdf8",
                fontWeight: 800,
                cursor: loading ? "not-allowed" : "pointer",
                opacity: loading ? 0.6 : 1,
              }}
            >
              Back
            </button>
            <button
              type="submit"
              disabled={!stripe || loading}
              style={{
                padding: "0.95rem 1.25rem",
                borderRadius: 999,
                border: 0,
                background: loading ? "#475569" : "#38bdf8",
                color: "#0f172a",
                fontWeight: 800,
                cursor: loading ? "not-allowed" : "pointer",
              }}
            >
              {loading ? "Processing..." : "Pay Now"}
            </button>
          </div>
        </form>
      )}

      {message && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            borderRadius: 12,
            background:
              messageType === "error"
                ? "rgba(239, 68, 68, 0.1)"
                : messageType === "success"
                ? "rgba(34, 197, 94, 0.1)"
                : "rgba(59, 130, 246, 0.1)",
            border:
              messageType === "error"
                ? "1px solid rgba(239, 68, 68, 0.3)"
                : messageType === "success"
                ? "1px solid rgba(34, 197, 94, 0.3)"
                : "1px solid rgba(59, 130, 246, 0.3)",
            color:
              messageType === "error"
                ? "#fca5a5"
                : messageType === "success"
                ? "#86efac"
                : "#93c5fd",
          }}
        >
          {message}
        </div>
      )}
    </>
  );
}

export default function CheckoutPage() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState(""); // 'success', 'error', 'info'
  const [clientSecret, setClientSecret] = useState("");
  const [paymentIntentId, setPaymentIntentId] = useState("");
  const [orderId, setOrderId] = useState("");
  const [formStep, setFormStep] = useState("form"); // 'form' or 'payment'

  const handleFormSubmit = useCallback(
    async (formData) => {
      setLoading(true);
      setMessage("");
      setMessageType("");

      try {
        // Generate idempotency key for this payment attempt
        const idempotencyKey = uuidv4();

        // Create payment intent
        const response = await fetch(
          `${API_URL}/api/payments/create-payment-intent/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              amount: formData.amount,
              currency: "usd",
              customer_email: formData.customerEmail,
              customer_name: formData.customerName,
              product_name: formData.productName,
              quantity: formData.quantity,
              metadata: {
                product_name: formData.productName,
                quantity: formData.quantity,
              },
              idempotency_key: idempotencyKey,
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "Failed to create payment intent");
        }

        setClientSecret(data.clientSecret);
        setPaymentIntentId(data.paymentIntentId);
        setOrderId(data.orderId);
        setFormStep("payment");
        setLoading(false);
        setMessage("Payment details form loaded. Please complete your payment.");
        setMessageType("info");
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "An error occurred");
        setMessageType("error");
        setLoading(false);
      }
    },
    []
  );

  const handleBackToForm = () => {
    setFormStep("form");
    setClientSecret("");
    setPaymentIntentId("");
    setMessage("");
    setMessageType("");
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "2rem",
        background:
          "linear-gradient(180deg, #0f172a 0%, #111827 42%, #1e293b 100%)",
        color: "white",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: 520,
          background: "rgba(15, 23, 42, 0.9)",
          border: "1px solid rgba(148, 163, 184, 0.2)",
          borderRadius: 28,
          padding: "2rem",
          boxShadow: "0 25px 80px rgba(15, 23, 42, 0.45)",
        }}
      >
        <h1 style={{ margin: "0 0 0.5rem", fontSize: "2rem" }}>Checkout</h1>
        <p style={{ margin: 0, color: "#94a3b8", marginBottom: "2rem" }}>
          {formStep === "form"
            ? "Enter your details to create a payment"
            : "Complete your payment"}
        </p>

        {formStep === "form" ? (
          <CheckoutForm onSubmit={handleFormSubmit} loading={loading} />
        ) : clientSecret && stripePromise ? (
          <Elements
            stripe={stripePromise}
            options={{
              clientSecret: clientSecret,
              appearance: {
                theme: "night",
              },
            }}
          >
            <PaymentFormContent
              clientSecret={clientSecret}
              orderId={orderId}
              loading={loading}
              setLoading={setLoading}
              message={message}
              messageType={messageType}
              setMessage={setMessage}
              setMessageType={setMessageType}
              handleBackToForm={handleBackToForm}
            />
          </Elements>
        ) : null}

        {formStep === "form" && message && (
          <div
            style={{
              marginTop: "1rem",
              padding: "1rem",
              borderRadius: 12,
              background:
                messageType === "error"
                  ? "rgba(239, 68, 68, 0.1)"
                  : messageType === "success"
                  ? "rgba(34, 197, 94, 0.1)"
                  : "rgba(59, 130, 246, 0.1)",
              border:
                messageType === "error"
                  ? "1px solid rgba(239, 68, 68, 0.3)"
                  : messageType === "success"
                  ? "1px solid rgba(34, 197, 94, 0.3)"
                  : "1px solid rgba(59, 130, 246, 0.3)",
              color:
                messageType === "error"
                  ? "#fca5a5"
                  : messageType === "success"
                  ? "#86efac"
                  : "#93c5fd",
            }}
          >
            {message}
          </div>
        )}
      </section>
    </main>
  );
}
