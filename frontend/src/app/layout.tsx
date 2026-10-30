import type { Metadata } from "next";
import { Workspace } from "@/components/workspace";
import "./globals.css";
export const metadata: Metadata = { title: "SchemeRadar | Student opportunities, clarified", description: "Discover scholarships with official sources and explainable eligibility." };
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="en"><body><Workspace>{children}</Workspace></body></html>;
}
