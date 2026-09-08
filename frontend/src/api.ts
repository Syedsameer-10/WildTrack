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

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL?.trim() || "http://localhost:8000/api/v1").replace(/\/$/, "");

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
