export type LiveEntity = {
  entity_id: string;
  external_id: string;
  type: string;
  status: string;
  last_seen_at: string;
  latitude: number;
  longitude: number;
  speed: number | null;
  heading: number | null;
};

export type PositionUpdateMessage = {
  type: "position_update";
  event_id: string;
  entity_id: string;
  external_id: string;
  status: string;
  event_time: string;
  latitude: number;
  longitude: number;
  speed: number | null;
  heading: number | null;
};
