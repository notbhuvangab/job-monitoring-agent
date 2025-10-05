import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Job Monitoring & Resume Fit Agent',
  description: 'AI-powered job matching system with real-time monitoring',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

