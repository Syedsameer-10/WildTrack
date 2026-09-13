export interface ServiceStatus {
  service: string;
  status: "operational";
  environment: string;
  api_version: string;
  timestamp: string;
}

export interface DatabaseStatus {
  status: "ready";
  provider: string;
  database: string;
  postgis_version: string;
  schema_version: string;
  lookup_records: number;
}

export interface SpatialFeatureCollection {
  type: "FeatureCollection";
  features: Array<{
    type: "Feature";
    id: string;
    geometry: { type: "Polygon" | "MultiPolygon"; coordinates: number[][][][] };
    properties: { code: string; name: string; area_class: string; description: string; data_source: string; area_sq_km: number };
  }>;
}

export interface SpatialPointResult {
  point: { longitude: number; latitude: number };
  inside_managed_area: boolean;
  matched_areas: Array<{
    code: string;
    name: string;
    area_class: string;
    description: string;
    area_sq_km: number;
  }>;
  nearest_area: { code: string; name: string; distance_m: number } | null;
}

export interface TemporalObservation {
  id: number; observation_key: string; revision: number; animal_tag: string; species: string; zone_code: string; zone_name: string;
  area_class: string; observed_at: string; recorded_at: string; confidence: number;
  correction_reason: string | null; late_arrival: boolean; longitude: number; latitude: number;
}

export interface TemporalTimeline { as_of: string; system_at: string; history_anchor: string | null; observations: TemporalObservation[]; }

export interface WildlifeEvent {
  event_id: string; event_type: string; source_type: string; source_id: string;
  zone_code: string | null; occurred_at: string; received_at: string; severity: string;
  dedupe_key: string; payload: Record<string, unknown>;
}

export interface EventFeed { count: number; events: WildlifeEvent[]; }
export interface ActiveAlert { id: number; rule_id: number; event_id: string; message: string; severity: string; created_at: string; }
export interface AlertFeed { count: number; alerts: ActiveAlert[]; }

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL?.trim() || "http://127.0.0.1:8000/api/v1").replace(/\/$/, "");

export async function fetchServiceStatus(signal?: AbortSignal): Promise<ServiceStatus> {
  const response = await fetch(`${API_BASE_URL}/status`, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) throw new Error(`Status request failed with HTTP ${response.status}.`);
  return (await response.json()) as ServiceStatus;
}

export async function fetchDatabaseStatus(signal?: AbortSignal): Promise<DatabaseStatus> {
  const response = await fetch(`${API_BASE_URL}/database/status`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok) throw new Error(`Database request failed with HTTP ${response.status}.`);
  return (await response.json()) as DatabaseStatus;
}

export async function fetchMapAreas(signal?: AbortSignal): Promise<SpatialFeatureCollection> {
  const response = await fetch(`${API_BASE_URL}/map/areas`, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) throw new Error(`Map-area request failed with HTTP ${response.status}.`);
  return (await response.json()) as SpatialFeatureCollection;
}

export async function queryMapPoint(longitude: number, latitude: number): Promise<SpatialPointResult> {
  const search = new URLSearchParams({ longitude: String(longitude), latitude: String(latitude) });
  const response = await fetch(`${API_BASE_URL}/map/query?${search}`, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`Spatial query failed with HTTP ${response.status}.`);
  return (await response.json()) as SpatialPointResult;
}

export async function fetchObservationTimeline(options: { asOf?: string; systemAt?: string; signal?: AbortSignal } = {}): Promise<TemporalTimeline> {
  const search = new URLSearchParams();
  if (options.asOf) search.set("as_of", options.asOf);
  if (options.systemAt) search.set("system_at", options.systemAt);
  const response = await fetch(`${API_BASE_URL}/observations${search.size ? `?${search}` : ""}`, { headers: { Accept: "application/json" }, signal: options.signal });
  if (!response.ok) throw new Error(`Observation request failed with HTTP ${response.status}.`);
  return (await response.json()) as TemporalTimeline;
}

export async function fetchEventFeed(signal?: AbortSignal): Promise<EventFeed> {
  const response = await fetch(`${API_BASE_URL}/events`, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) throw new Error(`Event request failed with HTTP ${response.status}.`);
  return (await response.json()) as EventFeed;
}

export async function fetchAlerts(signal?: AbortSignal): Promise<AlertFeed> {
  const response = await fetch(`${API_BASE_URL}/alerts`, { headers: { Accept: "application/json" }, signal });
  if (!response.ok) throw new Error(`Alert request failed with HTTP ${response.status}.`);
  return (await response.json()) as AlertFeed;
}
