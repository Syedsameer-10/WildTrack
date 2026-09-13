import { useEffect, useRef, useState } from "react";
import { LngLatBounds, Map, Marker, NavigationControl, type GeoJSONSource, type StyleSpecification } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import { queryMapPoint, type SpatialFeatureCollection, type SpatialPointResult } from "./api";

interface MapPanelProps {
  areas: SpatialFeatureCollection | null;
  focusZone?: string | null;
}

const ootysCenter: [number, number] = [76.695, 11.41];
function createMapStyle(areas: SpatialFeatureCollection, focusZone?: string | null): StyleSpecification {
  return {
    version: 8,
    sources: {
      openstreetmap: {
        type: "raster",
        tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
        tileSize: 256,
        attribution: "© OpenStreetMap contributors",
      },
      "managed-areas": { type: "geojson", data: areas },
    },
    layers: [
      { id: "openstreetmap", type: "raster", source: "openstreetmap" },
      { id: "managed-areas-fill", type: "fill", source: "managed-areas", paint: { "fill-color": "#ff7a00", "fill-opacity": 0 } },
      { id: "managed-areas-outline", type: "line", source: "managed-areas", paint: { "line-color": "#172013", "line-width": 4 } },
      { id: "managed-areas-highlight", type: "line", source: "managed-areas", paint: { "line-color": ["match", ["get", "area_class"], "protected_boundary", "#ff6b6b", "patrol_sector", "#72e2ff", "#ffe66d"], "line-width": 2, "line-dasharray": [3, 2] } },
      { id: "alert-zone-highlight", type: "line", source: "managed-areas", filter: ["==", ["get", "code"], focusZone ?? ""], paint: { "line-color": "#ffffff", "line-width": 6 } },
    ],
  };
}

export function MapPanel({ areas, focusZone }: MapPanelProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const markerRef = useRef<Marker | null>(null);
  const [queryResult, setQueryResult] = useState<SpatialPointResult | null>(null);
  const [queryError, setQueryError] = useState(false);
  const [boundaryVisible, setBoundaryVisible] = useState(true);
  const [boundaryPoints, setBoundaryPoints] = useState<Array<{ code: string; areaClass: string; points: string }>>([]);

  useEffect(() => {
    if (!mapContainer.current || !areas || mapRef.current) return;

    const map = new Map({
      container: mapContainer.current,
      style: createMapStyle(areas, focusZone),
      center: ootysCenter,
      zoom: 12,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    map.addControl(new NavigationControl(), "top-right");
    map.fitBounds(new LngLatBounds([76.675, 11.393], [76.714, 11.425]), { padding: 70, duration: 0 });
    const updateBoundaryOverlay = () => {
      setBoundaryPoints(areas.features.flatMap((feature) => {
        if (feature.geometry.type !== "MultiPolygon") return [];
        const ring = feature.geometry.coordinates[0]?.[0] as number[][] | undefined;
        if (!ring) return [];
        return [{
          code: feature.properties.code,
          areaClass: feature.properties.area_class,
          points: ring.map(([lng, lat]) => {
            const point = map.project([lng, lat]);
            return `${point.x},${point.y}`;
          }).join(" "),
        }];
      }));
    };
    map.on("load", updateBoundaryOverlay);
    map.on("move", updateBoundaryOverlay);
    map.on("resize", updateBoundaryOverlay);
    updateBoundaryOverlay();

    map.on("click", async (event) => {
      markerRef.current?.remove();
      markerRef.current = new Marker({ color: "#b6e55c" }).setLngLat(event.lngLat).addTo(map);
      setQueryError(false);
      try {
        setQueryResult(await queryMapPoint(event.lngLat.lng, event.lngLat.lat));
      } catch {
        setQueryResult(null); setQueryError(true);
      }
    });

    return () => { markerRef.current?.remove(); map.remove(); mapRef.current = null; };
  }, [areas]);

  useEffect(() => {
    const source = mapRef.current?.getSource("managed-areas") as GeoJSONSource | undefined;
    if (source && areas) source.setData(areas);
  }, [areas]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.getLayer("managed-areas-fill")) return;
    const visibility = boundaryVisible ? "visible" : "none";
    map.setLayoutProperty("managed-areas-fill", "visibility", visibility);
    map.setLayoutProperty("managed-areas-outline", "visibility", visibility);
    map.setLayoutProperty("managed-areas-highlight", "visibility", visibility);
    map.setLayoutProperty("alert-zone-highlight", "visibility", visibility);
  }, [boundaryVisible]);

  const matchedArea = queryResult?.matched_areas[0];
  return <aside className="map-panel" aria-label="Ooty management zones map"><div className="map-header"><div><span className="map-kicker">SPATIAL TEST ZONES</span><strong>Ooty / Nilgiris · {areas?.features.length ?? 0} zones</strong></div><button className="map-layer-toggle" type="button" aria-pressed={boundaryVisible} onClick={() => setBoundaryVisible((visible) => !visible)}><span className="boundary-swatch" aria-hidden="true" />{boundaryVisible ? "Zones on" : "Zones off"}</button></div><div className="map-stage"><div ref={mapContainer} className="map-canvas" />{boundaryVisible && boundaryPoints.length > 0 && <svg className="boundary-overlay" aria-hidden="true">{boundaryPoints.map((boundary) => <g key={boundary.code} data-area-class={boundary.areaClass}><polygon className="boundary-edge" points={boundary.points} /><polygon className="boundary-highlight" points={boundary.points} /></g>)}</svg>}</div><div className={`map-query ${matchedArea ? "inside" : ""}`} aria-live="polite">{queryError ? <><strong>Query unavailable</strong><span>Check the API connection.</span></> : matchedArea ? <><strong>Inside {matchedArea.name}</strong><span>{matchedArea.area_class.replace("_", " ")} · {matchedArea.area_sq_km} km²</span><span>{matchedArea.description}</span></> : queryResult ? <><strong>Outside managed area</strong><span>Nearest: {queryResult.nearest_area?.name} · {queryResult.nearest_area?.distance_m} m</span></> : <><strong>Click the map</strong><span>PostGIS will classify that coordinate.</span></>}</div><div className="zone-legend"><span className="legend-study">Monitoring</span><span className="legend-protected">Protected</span><span className="legend-patrol">Patrol</span></div></aside>;
}
