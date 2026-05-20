"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function SuccessPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const orderId = searchParams.get("order");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

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
          border: "1px solid rgba(34, 197, 94, 0.3)",
          borderRadius: 28,
          padding: "3rem 2rem",
          textAlign: "center",
          boxShadow: "0 25px 80px rgba(15, 23, 42, 0.45)",
        }}
      >
        <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>✓</div>

        <h1 style={{ margin: "0 0 1rem", fontSize: "2rem", color: "#86efac" }}>
          Payment Successful!
        </h1>

        <p style={{ margin: "0 0 1.5rem", color: "#cbd5e1", fontSize: "1rem" }}>
          Your payment has been processed successfully.
        </p>

        {orderId && (
          <div
            style={{
              padding: "1rem",
              borderRadius: 12,
              background: "rgba(34, 197, 94, 0.1)",
              border: "1px solid rgba(34, 197, 94, 0.2)",
              marginBottom: "2rem",
            }}
          >
            <p style={{ margin: "0.5rem 0 0", color: "#a7f3d0" }}>
              Order ID: <strong>{orderId}</strong>
            </p>
          </div>
        )}

        <p style={{ margin: "0 0 2rem", color: "#94a3b8", fontSize: "0.9rem" }}>
          You will receive a confirmation email shortly with your receipt and
          order details.
        </p>

        <button
          onClick={() => router.push("/")}
          style={{
            padding: "0.95rem 2rem",
            borderRadius: 999,
            border: 0,
            background: "#22c55e",
            color: "#0f172a",
            fontWeight: 800,
            cursor: "pointer",
            fontSize: "1rem",
          }}
          onMouseEnter={(e) => {
            e.target.style.background = "#16a34a";
          }}
          onMouseLeave={(e) => {
            e.target.style.background = "#22c55e";
          }}
        >
          Return to Home
        </button>
      </section>
    </main>
  );
}
