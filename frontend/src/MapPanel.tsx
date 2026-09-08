import { useEffect, useRef, useState } from "react";
import { LngLatBounds, Map, Marker, NavigationControl, type GeoJSONSource, type StyleSpecification } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

import { queryMapPoint, type SpatialFeatureCollection, type SpatialPointResult } from "./api";

interface MapPanelProps {
  areas: SpatialFeatureCollection | null;
}

const ootysCenter: [number, number] = [76.695, 11.41];
const openStreetMapStyle: StyleSpecification = {
  version: 8,
  sources: {
    openstreetmap: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap contributors",
    },
  },
  layers: [{ id: "openstreetmap", type: "raster", source: "openstreetmap" }],
};

export function MapPanel({ areas }: MapPanelProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const markerRef = useRef<Marker | null>(null);
  const [queryResult, setQueryResult] = useState<SpatialPointResult | null>(null);
  const [queryError, setQueryError] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || !areas || mapRef.current) return;

    const map = new Map({
      container: mapContainer.current,
      style: openStreetMapStyle,
      center: ootysCenter,
      zoom: 12,
      attributionControl: { compact: true },
    });
    mapRef.current = map;
    map.addControl(new NavigationControl(), "top-right");
    map.on("load", () => {
      map.addSource("managed-areas", { type: "geojson", data: areas });
      map.addLayer({ id: "managed-areas-fill", type: "fill", source: "managed-areas", paint: { "fill-color": "#b6e55c", "fill-opacity": 0.2 } });
      map.addLayer({ id: "managed-areas-outline", type: "line", source: "managed-areas", paint: { "line-color": "#d9ff89", "line-width": 2.5 } });
      map.fitBounds(new LngLatBounds([76.675, 11.393], [76.714, 11.425]), { padding: 70, duration: 0 });
    });

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

  const matchedArea = queryResult?.matched_areas[0];
  return <aside className="map-panel" aria-label="Ooty study area map"><div className="map-header"><div><span className="map-kicker">SPATIAL TEST AREA</span><strong>Ooty / Nilgiris</strong></div><span className="map-live">POSTGIS</span></div><div ref={mapContainer} className="map-canvas" /><div className={`map-query ${matchedArea ? "inside" : ""}`} aria-live="polite">{queryError ? <><strong>Query unavailable</strong><span>Check the API connection.</span></> : matchedArea ? <><strong>Inside {matchedArea.name}</strong><span>{matchedArea.area_class.replace("_", " ")} · {matchedArea.area_sq_km} km²</span></> : queryResult ? <><strong>Outside managed area</strong><span>Nearest: {queryResult.nearest_area?.name} · {queryResult.nearest_area?.distance_m} m</span></> : <><strong>Click the map</strong><span>PostGIS will classify that coordinate.</span></>}</div><p className="map-note">Synthetic test boundary · not an official forest boundary</p></aside>;
}
