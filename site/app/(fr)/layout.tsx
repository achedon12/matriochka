import type { ReactNode } from "react";
import "../globals.css";
import { fontVars } from "@/lib/fonts";

export { viewport } from "@/lib/meta";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr" className={fontVars}>
      <body>{children}</body>
    </html>
  );
}
