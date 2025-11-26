import "leaflet/dist/leaflet.css";
import "react-leaflet-cluster/lib/assets/MarkerCluster.css";
import "react-leaflet-cluster/lib/assets/MarkerCluster.Default.css";
import "./globals.css";

import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Meridian Command Center",
  description: "Real-time geospatial operations intelligence dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
