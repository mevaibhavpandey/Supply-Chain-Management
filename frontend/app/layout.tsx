import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Trust Validator — SCM Agent Validation Platform',
  description:
    'Validate your SCM AI agents with deterministic trust scoring across 6 dimensions: Security, Reliability, Observability, I/O Clarity, Specification, and SCM Readiness.',
  keywords: 'AI agent validation, SCM, supply chain, trust score, agent audit',
};

function NavBar() {
  return (
    <nav className="nav">
      <Link href="/" className="nav-logo">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <rect width="28" height="28" rx="8" fill="url(#logo-grad)" />
          <path d="M8 14l4 4 8-8" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          <defs>
            <linearGradient id="logo-grad" x1="0" y1="0" x2="28" y2="28">
              <stop stopColor="#6366f1" />
              <stop offset="1" stopColor="#8b5cf6" />
            </linearGradient>
          </defs>
        </svg>
        <span>AI Trust Validator</span>
      </Link>
      <div className="nav-links">
        <Link href="/submit" className="nav-link">
          Validate Agent
        </Link>
        <Link href="/history" className="nav-link">
          History
        </Link>
        <Link
          href="/submit"
          className="btn btn-primary btn-sm"
          style={{ marginLeft: 8 }}
        >
          + New Validation
        </Link>
      </div>
    </nav>
  );
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body>
        <NavBar />
        <main>{children}</main>
      </body>
    </html>
  );
}
