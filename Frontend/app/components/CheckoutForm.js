"use client";

import { useState } from "react";

export default function CheckoutForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    customerName: "",
    customerEmail: "",
    productName: "Sample Product",
    amount: 5000,
    quantity: 1,
  });

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? (value === "" ? "" : Number(value)) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate form
    if (!formData.customerName.trim()) {
      alert("Please enter your name");
      return;
    }
    if (!formData.customerEmail.trim()) {
      alert("Please enter your email");
      return;
    }
    if (formData.amount <= 0) {
      alert("Amount must be greater than 0");
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="customerName"
          style={{ display: "block", marginBottom: "0.5rem", color: "#e2e8f0" }}
        >
          Full Name
        </label>
        <input
          id="customerName"
          type="text"
          name="customerName"
          value={formData.customerName}
          onChange={handleInputChange}
          placeholder="John Doe"
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.75rem",
            borderRadius: 8,
            border: "1px solid rgba(255, 255, 255, 0.1)",
            background: "rgba(255, 255, 255, 0.05)",
            color: "#e2e8f0",
            fontSize: "1rem",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="customerEmail"
          style={{ display: "block", marginBottom: "0.5rem", color: "#e2e8f0" }}
        >
          Email
        </label>
        <input
          id="customerEmail"
          type="email"
          name="customerEmail"
          value={formData.customerEmail}
          onChange={handleInputChange}
          placeholder="john@example.com"
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.75rem",
            borderRadius: 8,
            border: "1px solid rgba(255, 255, 255, 0.1)",
            background: "rgba(255, 255, 255, 0.05)",
            color: "#e2e8f0",
            fontSize: "1rem",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="productName"
          style={{ display: "block", marginBottom: "0.5rem", color: "#e2e8f0" }}
        >
          Product Name
        </label>
        <input
          id="productName"
          type="text"
          name="productName"
          value={formData.productName}
          onChange={handleInputChange}
          placeholder="Product Name"
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.75rem",
            borderRadius: 8,
            border: "1px solid rgba(255, 255, 255, 0.1)",
            background: "rgba(255, 255, 255, 0.05)",
            color: "#e2e8f0",
            fontSize: "1rem",
            boxSizing: "border-box",
          }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
        <div>
          <label
            htmlFor="amount"
            style={{ display: "block", marginBottom: "0.5rem", color: "#e2e8f0" }}
          >
            Amount (cents)
          </label>
          <input
            id="amount"
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleInputChange}
            min="1"
            required
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.75rem",
              borderRadius: 8,
              border: "1px solid rgba(255, 255, 255, 0.1)",
              background: "rgba(255, 255, 255, 0.05)",
              color: "#e2e8f0",
              fontSize: "1rem",
              boxSizing: "border-box",
            }}
          />
        </div>
        <div>
          <label
            htmlFor="quantity"
            style={{ display: "block", marginBottom: "0.5rem", color: "#e2e8f0" }}
          >
            Quantity
          </label>
          <input
            id="quantity"
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleInputChange}
            min="1"
            disabled={loading}
            style={{
              width: "100%",
              padding: "0.75rem",
              borderRadius: 8,
              border: "1px solid rgba(255, 255, 255, 0.1)",
              background: "rgba(255, 255, 255, 0.05)",
              color: "#e2e8f0",
              fontSize: "1rem",
              boxSizing: "border-box",
            }}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          width: "100%",
          padding: "0.75rem",
          borderRadius: 8,
          border: 0,
          background: loading ? "#475569" : "#38bdf8",
          color: "#0f172a",
          fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "1rem",
          transition: "background 0.2s",
        }}
        onMouseEnter={(e) => {
          if (!loading) e.target.style.background = "#06b6d4";
        }}
        onMouseLeave={(e) => {
          if (!loading) e.target.style.background = "#38bdf8";
        }}
      >
        {loading ? "Processing..." : "Continue to Payment"}
      </button>
    </form>
  );
}
