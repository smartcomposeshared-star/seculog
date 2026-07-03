import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "SecuLog",
  description: "Security log analysis dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen">
        <nav className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center gap-6">
          <span className="font-bold text-blue-400 mr-2">SecuLog</span>
          <Link href="/" className="hover:text-blue-300 transition-colors">Overview</Link>
          <Link href="/events" className="hover:text-blue-300 transition-colors">All Events</Link>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
