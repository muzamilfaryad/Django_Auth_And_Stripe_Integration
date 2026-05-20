import StripeProvider from "./providers";

export const metadata = {
  title: "Django Auth Stripe Checkout",
  description: "Custom Stripe checkout flow for the Django Auth backend.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <StripeProvider>{children}</StripeProvider>
      </body>
    </html>
  );
}