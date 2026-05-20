import Link from "next/link";

export default function HomePage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
        background:
          "radial-gradient(circle at top, rgba(0, 153, 255, 0.12), transparent 40%), linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%)",
      }}
    >
      <div
        style={{
          maxWidth: 640,
          width: "100%",
          background: "white",
          borderRadius: 24,
          padding: "3rem",
          boxShadow: "0 20px 60px rgba(15, 23, 42, 0.12)",
        }}
      >
        <p style={{ margin: 0, color: "#2563eb", fontWeight: 700 }}>
          Stripe checkout
        </p>
        <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", margin: "0.75rem 0" }}>
          Custom payment flow for the Django backend
        </h1>
        <p style={{ color: "#475569", lineHeight: 1.6 }}>
          Open the checkout page to test the embedded CardElement flow against
          the payment-intent endpoint.
        </p>
        <Link
          href="/checkout"
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            marginTop: "1.5rem",
            padding: "0.9rem 1.4rem",
            borderRadius: 999,
            background: "#111827",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          Go to checkout
        </Link>
      </div>
    </main>
  );
}