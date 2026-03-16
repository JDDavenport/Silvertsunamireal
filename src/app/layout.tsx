import type { Metadata } from "next";
import { ThemeProvider } from "next-themes";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

export const metadata: Metadata = {
  title: "ACQUISITOR - Business Acquisition Intelligence Platform",
  description: "Discover, evaluate, and acquire businesses worth $200K-$5M. AI-powered deal sourcing and analysis for serious entrepreneurs.",
  keywords: ["business acquisition", "deal flow", "SMB", "entrepreneur", "M&A", "business broker", "buy a business"],
  authors: [{ name: "ACQUISITOR" }],
  openGraph: {
    title: "ACQUISITOR - Business Acquisition Intelligence Platform",
    description: "Discover, evaluate, and acquire businesses worth $200K-$5M. AI-powered deal sourcing for serious entrepreneurs.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ACQUISITOR - Business Acquisition Intelligence",
    description: "AI-powered deal sourcing for serious entrepreneurs",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased min-h-screen">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange={false}
        >
          <TooltipProvider>
            {children}
            <Toaster 
              position="bottom-right"
              toastOptions={{
                className: "font-sans",
              }}
            />
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
