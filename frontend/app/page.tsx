import { LiveMap } from "../components/live-map";

export default function HomePage() {
  return (
    <main className="page-shell">
      <header className="hero">
        <h1>Meridian: Real-Time Geospatial Command Center</h1>
        <p>
          Phase 1 and Phase 2 implementation: live ingest, Redis fanout, persisted entity state,
          and clustered map rendering for high-volume tracking.
        </p>
      </header>

      <section>
        <LiveMap />
      </section>
    </main>
  );
}
