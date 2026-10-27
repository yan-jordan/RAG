import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "پرسند — از اسنادت بپرس",
  description: "فایل‌های Word رو بارگذاری کن و از محتوای خودشون جواب بگیر؛ هر پاسخ با منبعش علامت می‌خوره.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f3f4f9" },
    { media: "(prefers-color-scheme: dark)", color: "#0b0d1c" },
  ],
};

// Runs before paint so the page never flashes the wrong theme.
const themeScript = `(function(){try{var t=localStorage.getItem("theme");if(!t){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}document.documentElement.dataset.theme=t}catch(e){}})()`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="h-dvh overflow-hidden">{children}</body>
    </html>
  );
}
