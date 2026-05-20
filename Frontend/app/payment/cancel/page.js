"use client";

import { useRouter } from "next/navigation";

export default function CancelPage() {
  const router = useRouter();

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
          border: "1px solid rgba(239, 68, 68, 0.3)",
          borderRadius: 28,
          padding: "3rem 2rem",
          textAlign: "center",
          boxShadow: "0 25px 80px rgba(15, 23, 42, 0.45)",
        }}
      >
        <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>✕</div>

        <h1 style={{ margin: "0 0 1rem", fontSize: "2rem", color: "#fca5a5" }}>
          Payment Cancelled
        </h1>

        <p style={{ margin: "0 0 1.5rem", color: "#cbd5e1", fontSize: "1rem" }}>
          Your payment has been cancelled. No charges have been made to your account.
        </p>

        <p style={{ margin: "0 0 2rem", color: "#94a3b8", fontSize: "0.9rem" }}>
          Please try again or contact support if you need assistance.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
          }}
        >
          <button
            onClick={() => router.push("/checkout")}
            style={{
              padding: "0.95rem 1.25rem",
              borderRadius: 999,
              border: "1px solid rgba(239, 68, 68, 0.3)",
              background: "transparent",
              color: "#fca5a5",
              fontWeight: 800,
              cursor: "pointer",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "rgba(239, 68, 68, 0.1)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "transparent";
            }}
          >
            Retry Payment
          </button>
          <button
            onClick={() => router.push("/")}
            style={{
              padding: "0.95rem 1.25rem",
              borderRadius: 999,
              border: 0,
              background: "#38bdf8",
              color: "#0f172a",
              fontWeight: 800,
              cursor: "pointer",
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#06b6d4";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#38bdf8";
            }}
          >
            Return to Home
          </button>
        </div>
      </section>
    </main>
  );
}
