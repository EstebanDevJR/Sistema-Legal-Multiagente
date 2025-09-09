import type React from "react"
import type { Metadata, Viewport } from "next"
import { Figtree } from "next/font/google"
import { GeistMono } from "geist/font/mono"
import { Instrument_Serif } from "next/font/google"
import "./globals.css"
import { ToastProvider } from "@/components/toast-provider"
import { DocumentProvider } from "@/contexts/DocumentContext"
import OfflineIndicator from "@/components/offline-indicator"
import HydrationBoundary from "@/components/hydration-boundary"
import LegalDisclaimer from "@/components/legal-disclaimer"

const figtree = Figtree({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-figtree",
  display: "swap",
})

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  style: ["normal", "italic"],
  variable: "--font-instrument-serif",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Sistema Legal Multiagente",
  description: "Sistema inteligente de consultas legales especializado en derecho colombiano con IA multiagente",
  generator: "v0.app",
  keywords: "derecho colombiano, consultas legales, IA jurídica, abogado virtual, normativa colombia",
  authors: [{ name: "Esteban Ortiz" }],
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: 'any' }
    ],
    other: [
      { rel: 'mask-icon', url: '/safari-pinned-tab.svg', color: '#2563eb' }
    ]
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Legal IA",
  },
  other: {
    "mobile-web-app-capable": "yes",
  },
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
}

export const themeColor = "#2563eb"

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="mobile-web-app-capable" content="yes" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="alternate icon" href="/favicon.ico" />
        <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#2563eb" />
      </head>
      <body className={`${figtree.variable} ${GeistMono.variable} ${instrumentSerif.variable} bg-black min-h-screen`}>
        <HydrationBoundary>
          <ToastProvider>
            <DocumentProvider>
              <OfflineIndicator />
              <LegalDisclaimer />
              {children}
            </DocumentProvider>
          </ToastProvider>
        </HydrationBoundary>
      </body>
    </html>
  )
}
