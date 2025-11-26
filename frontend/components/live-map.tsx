import dynamic from "next/dynamic";

const LiveMapClient = dynamic(() => import("./live-map-client"), {
  ssr: false,
  loading: () => <p className="loading-text">Loading map...</p>,
});

export function LiveMap() {
  return <LiveMapClient />;
}
