import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as HotToaster } from "react-hot-toast";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ResMatch - Research Participant Recruitment Platform",
  description: "Connect researchers with qualified participants through AI-powered matching. Streamline your research recruitment process.",
  keywords: ["research", "participants", "recruitment", "clinical trials", "academic research", "AI matching"],
  authors: [{ name: "ResMatch Team" }],
  icons: {
    icon: "/favicon.ico",
  },
  openGraph: {
    title: "ResMatch - Research Participant Recruitment",
    description: "AI-powered platform connecting researchers with qualified participants",
    url: "https://resmatch.com",
    siteName: "ResMatch",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ResMatch - Research Participant Recruitment",
    description: "AI-powered platform connecting researchers with qualified participants",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
        <HotToaster position="top-right" />
      </body>
    </html>
  );
}
