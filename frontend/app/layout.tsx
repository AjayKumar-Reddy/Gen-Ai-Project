import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KCET College Assistant | Engineering Cutoff Advisor",
  description:
    "AI-powered KCET College Information Assistant for Engineering Aspirants using Hybrid RAG (Dense PGVector + BM25 + RRF)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden flex flex-col font-sans bg-slate-100 text-slate-800 antialiased">
        {children}
      </body>
    </html>
  );
}
