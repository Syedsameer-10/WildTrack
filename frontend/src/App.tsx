import { useCallback, useEffect, useState } from "react";
import { MapPanel } from "./MapPanel";
import { TemporalPanel } from "./TemporalPanel";
import { EventPanel } from "./EventPanel";
import { AlertPanel } from "./AlertPanel";
import { API_BASE_URL, fetchAlerts, fetchDatabaseStatus, fetchEventFeed, fetchMapAreas, fetchObservationTimeline, fetchServiceStatus, type AlertFeed, type DatabaseStatus, type EventFeed, type ServiceStatus, type SpatialFeatureCollection, type TemporalTimeline } from "./api";

type ConnectionState = "checking" | "online" | "offline";
const concepts = [
  ["Spatial", "PostGIS-powered zones, proximity, and movement paths"],
  ["Temporal", "Timestamped observations and historical playback"],
  ["Active", "Event–Condition–Action rules that generate alerts"],
  ["NoSQL", "Flexible wildlife and sensor event documents"],
] as const;

export default function App() {
  const readRoute = () => window.location.hash.replace(/^#\//, "").split("?")[0] || "dashboard";
  const [route, setRoute] = useState(readRoute);
  const [connection, setConnection] = useState<ConnectionState>("checking");
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null);
  const [databaseStatus, setDatabaseStatus] = useState<DatabaseStatus | null>(null);
  const [mapAreas, setMapAreas] = useState<SpatialFeatureCollection | null>(null);
  const [timeline, setTimeline] = useState<TemporalTimeline | null>(null);
  const [eventFeed, setEventFeed] = useState<EventFeed | null>(null);
  const [alertFeed, setAlertFeed] = useState<AlertFeed | null>(null);
  const [message, setMessage] = useState("Contacting the WildTrack API…");
  const refreshEvents = useCallback(async () => { try { setEventFeed(await fetchEventFeed()); } catch { setEventFeed(null); } }, []);
  const checkConnection = useCallback(async () => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    setConnection("checking"); setMessage("Contacting the WildTrack API…"); setDatabaseStatus(null); setMapAreas(null);
    try {
      const status = await fetchServiceStatus(controller.signal);
      window.clearTimeout(timeout);
      setServiceStatus(status); setConnection("online");
      setMessage("Frontend and API are communicating normally.");
      const [database, areas, observations, events, alerts] = await Promise.allSettled([
        fetchDatabaseStatus(), fetchMapAreas(), fetchObservationTimeline(), fetchEventFeed(), fetchAlerts(),
      ]);
      setDatabaseStatus(database.status === "fulfilled" ? database.value : null);
      setMapAreas(areas.status === "fulfilled" ? areas.value : null);
      setTimeline(observations.status === "fulfilled" ? observations.value : null);
      setEventFeed(events.status === "fulfilled" ? events.value : null);
      setAlertFeed(alerts.status === "fulfilled" ? alerts.value : null);
    } catch {
      setServiceStatus(null); setConnection("offline");
      setMessage("The interface is running, but the API is unavailable.");
    } finally { window.clearTimeout(timeout); }
  }, []);
  useEffect(() => { void checkConnection(); }, [checkConnection]);
  useEffect(() => { const onHash = () => setRoute(readRoute()); window.addEventListener("hashchange", onHash); return () => window.removeEventListener("hashchange", onHash); }, []);

  const pageTitle = route === "map" ? "Spatial map" : route === "temporal" ? "Temporal history" : route === "events" ? "NoSQL events" : route === "alerts" ? "Active alerts" : "Wildlife intelligence";
  const routeParams = new URLSearchParams(window.location.hash.split("?")[1] ?? "");

  return <main>
    <nav className="topbar" aria-label="Primary navigation"><a className="brand" href="#/"><span className="brand-mark">W</span><span>WildTrack</span></a><div className="section-nav"><a href="#/map">Map</a><a href="#/temporal">Temporal</a><a href="#/events">Events</a><a href="#/alerts">Alerts</a></div><span className="phase-badge">{pageTitle}</span></nav>
    {route === "dashboard" && <section className="hero" id="top">
      <div className="hero-copy"><p className="eyebrow">ADVANCED DATABASE PROJECT</p><h1>Wildlife intelligence,<br /><em>mapped in motion.</em></h1><p className="lede">A deployment-ready monitoring platform designed to connect spatial reasoning, temporal history, active rules, and event data.</p>
        <section className={`status-card ${connection}`} aria-live="polite"><span className="status-dot" /><div><strong>{connection === "checking" ? "Checking connection" : connection === "online" ? "API operational" : "API offline"}</strong><p>{message}</p>{serviceStatus && <small>API {serviceStatus.api_version} · {serviceStatus.environment}</small>}</div><button type="button" onClick={() => void checkConnection()}>Check again</button></section>
        <p className="endpoint">Connected endpoint: <code>{API_BASE_URL}</code></p>
        <div className={`database-chip ${databaseStatus ? "ready" : "waiting"}`}><span>{databaseStatus ? "POSTGIS READY" : "DATABASE UNAVAILABLE"}</span><strong>{databaseStatus ? `${databaseStatus.schema_version} · ${databaseStatus.lookup_records} lookups` : "Check hosted connection"}</strong></div>
      </div>
      <div id="map-view"><MapPanel areas={mapAreas} /></div>
    </section>}
    {route === "map" && <section className="route-page"><p className="eyebrow">SPATIAL DATABASE</p><h1>{pageTitle}</h1><MapPanel areas={mapAreas} focusZone={routeParams.get("zone")} /></section>}
    {route === "temporal" && <section className="route-page"><p className="eyebrow">BITEMPORAL DATABASE</p><h1>{pageTitle}</h1><TemporalPanel timeline={timeline} /></section>}
    {route === "events" && <section className="route-page"><p className="eyebrow">MONGODB ATLAS</p><h1>{pageTitle}</h1><EventPanel feed={eventFeed} onRefresh={() => void refreshEvents()} /></section>}
    {route === "alerts" && <section className="route-page"><p className="eyebrow">ACTIVE DATABASE · ECA</p><h1>{pageTitle}</h1><AlertPanel feed={alertFeed} events={eventFeed} /></section>}
    {route === "dashboard" && <section className="concept-grid" aria-label="Core database concepts">{concepts.map(([title, description], index) => <article key={title}><span>0{index + 1}</span><h2>{title}</h2><p>{description}</p></article>)}</section>}
  </main>;
}
