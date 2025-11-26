"use client";

import { useEffect, useMemo, useState } from "react";
import L, { DivIcon } from "leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import type { LiveEntity, PositionUpdateMessage } from "../lib/types";

const DEFAULT_CENTER: [number, number] = [37.7749, -122.4194];

function toWsUrl(baseApiUrl: string): string {
  const wsProtocol = baseApiUrl.startsWith("https") ? "wss" : "ws";
  return baseApiUrl.replace(/^https?/, wsProtocol);
}

function markerIcon(status: string): DivIcon {
  return L.divIcon({
    className: `meridian-marker meridian-marker--${status}`,
    iconSize: [16, 16],
  });
}

function syntheticFleet(size: number): LiveEntity[] {
  return Array.from({ length: size }).map((_, index) => ({
    entity_id: `demo-${index}`,
    external_id: `DEMO-${index.toString().padStart(3, "0")}`,
    type: "vehicle",
    status: index % 4 === 0 ? "warning" : "active",
    last_seen_at: new Date().toISOString(),
    latitude: 37.60 + (index % 20) * 0.02,
    longitude: -122.55 + Math.floor(index / 20) * 0.02,
    speed: 10 + (index % 8),
    heading: (index * 17) % 360,
  }));
}

export default function LiveMapClient() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const wsBaseUrl = useMemo(() => toWsUrl(apiBaseUrl), [apiBaseUrl]);

  const [entities, setEntities] = useState<Record<string, LiveEntity>>({});
  const [streamStatus, setStreamStatus] = useState("connecting");

  useEffect(() => {
    let cancelled = false;

    async function loadSnapshot() {
      try {
        const response = await fetch(`${apiBaseUrl}/entities/live`, { cache: "no-store" });
        if (!response.ok) {
          return;
        }

        const payload: { entities: LiveEntity[] } = await response.json();
        if (cancelled) {
          return;
        }

        setEntities((existing) => {
          const next = { ...existing };
          for (const entity of payload.entities) {
            next[entity.entity_id] = entity;
          }
          return next;
        });
      } catch {
        // Ignore initial snapshot failures; stream may still recover.
      }
    }

    loadSnapshot();

    const socket = new WebSocket(`${wsBaseUrl}/stream/live`);

    socket.onopen = () => setStreamStatus("live");
    socket.onerror = () => setStreamStatus("degraded");
    socket.onclose = () => setStreamStatus("offline");

    socket.onmessage = (event) => {
      try {
        const parsed: unknown = JSON.parse(event.data);
        if (
          !parsed ||
          typeof parsed !== "object" ||
          (parsed as { type?: string }).type !== "position_update"
        ) {
          return;
        }
        const message = parsed as PositionUpdateMessage;

        setEntities((existing) => ({
          ...existing,
          [message.entity_id]: {
            entity_id: message.entity_id,
            external_id: message.external_id,
            type: "vehicle",
            status: message.status,
            last_seen_at: message.event_time,
            latitude: message.latitude,
            longitude: message.longitude,
            speed: message.speed,
            heading: message.heading,
          },
        }));
      } catch {
        // Ignore malformed messages and keep stream alive.
      }
    };

    return () => {
      cancelled = true;
      socket.close();
    };
  }, [apiBaseUrl, wsBaseUrl]);

  const entityList = useMemo(() => Object.values(entities), [entities]);

  const activeCount = entityList.filter((item) => item.status === "active").length;
  const warningCount = entityList.filter((item) => item.status !== "active").length;

  return (
    <div className="map-shell">
      <div className="map-toolbar">
        <div>
          <h2>Live Operations Map</h2>
          <p>{entityList.length} tracked entities with incremental WebSocket updates.</p>
        </div>
        <div className="metric-pills">
          <span className="pill">Stream: {streamStatus}</span>
          <span className="pill">Active: {activeCount}</span>
          <span className="pill">Attention: {warningCount}</span>
          <button className="pill-button" onClick={() => {
            const demo = syntheticFleet(220);
            setEntities(Object.fromEntries(demo.map((item) => [item.entity_id, item])));
          }}>
            Load 220-Entity Demo
          </button>
        </div>
      </div>

      <MapContainer center={DEFAULT_CENTER} zoom={10} className="map-canvas">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MarkerClusterGroup chunkedLoading>
          {entityList.map((entity) => (
            <Marker
              key={entity.entity_id}
              position={[entity.latitude, entity.longitude]}
              icon={markerIcon(entity.status)}
            >
              <Popup>
                <strong>{entity.external_id}</strong>
                <br />
                Status: {entity.status}
                <br />
                Speed: {entity.speed ?? "n/a"}
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      </MapContainer>
    </div>
  );
}
