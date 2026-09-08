import { useCallback, useEffect, useState } from "react";
import { MapPanel } from "./MapPanel";
import { API_BASE_URL, fetchDatabaseStatus, fetchMapAreas, fetchServiceStatus, type DatabaseStatus, type ServiceStatus, type SpatialFeatureCollection } from "./api";

type ConnectionState = "checking" | "online" | "offline";
const concepts = [
  ["Spatial", "PostGIS-powered zones, proximity, and movement paths"],
  ["Temporal", "Timestamped observations and historical playback"],
  ["Active", "Event–Condition–Action rules that generate alerts"],
  ["NoSQL", "Flexible wildlife and sensor event documents"],
] as const;

export default function App() {
  const [connection, setConnection] = useState<ConnectionState>("checking");
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null);
  const [databaseStatus, setDatabaseStatus] = useState<DatabaseStatus | null>(null);
  const [mapAreas, setMapAreas] = useState<SpatialFeatureCollection | null>(null);
  const [message, setMessage] = useState("Contacting the WildTrack API…");
  const checkConnection = useCallback(async () => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 5000);
    setConnection("checking"); setMessage("Contacting the WildTrack API…"); setDatabaseStatus(null); setMapAreas(null);
    try {
      const status = await fetchServiceStatus(controller.signal);
      setServiceStatus(status); setConnection("online");
      setMessage("Frontend and API are communicating normally.");
      try {
        const [database, areas] = await Promise.all([fetchDatabaseStatus(controller.signal), fetchMapAreas(controller.signal)]);
        setDatabaseStatus(database); setMapAreas(areas);
      } catch { setDatabaseStatus(null); setMapAreas(null); }
    } catch {
      setServiceStatus(null); setConnection("offline");
      setMessage("The interface is running, but the API is unavailable.");
    } finally { window.clearTimeout(timeout); }
  }, []);
  useEffect(() => { void checkConnection(); }, [checkConnection]);

  return <main>
    <nav className="topbar" aria-label="Primary navigation"><a className="brand" href="#top"><span className="brand-mark">W</span><span>WildTrack</span></a><span className="phase-badge">Foundation · Phase 1</span></nav>
    <section className="hero" id="top">
      <div className="hero-copy"><p className="eyebrow">ADVANCED DATABASE PROJECT</p><h1>Wildlife intelligence,<br /><em>mapped in motion.</em></h1><p className="lede">A deployment-ready monitoring platform designed to connect spatial reasoning, temporal history, active rules, and event data.</p>
        <section className={`status-card ${connection}`} aria-live="polite"><span className="status-dot" /><div><strong>{connection === "checking" ? "Checking connection" : connection === "online" ? "API operational" : "API offline"}</strong><p>{message}</p>{serviceStatus && <small>API {serviceStatus.api_version} · {serviceStatus.environment}</small>}</div><button type="button" onClick={() => void checkConnection()}>Check again</button></section>
        <p className="endpoint">Connected endpoint: <code>{API_BASE_URL}</code></p>
        <div className={`database-chip ${databaseStatus ? "ready" : "waiting"}`}><span>{databaseStatus ? "POSTGIS READY" : "DATABASE UNAVAILABLE"}</span><strong>{databaseStatus ? `${databaseStatus.schema_version} · ${databaseStatus.lookup_records} lookups` : "Check hosted connection"}</strong></div>
      </div>
      <MapPanel areas={mapAreas} />
    </section>
    <section className="concept-grid" aria-label="Core database concepts">{concepts.map(([title, description], index) => <article key={title}><span>0{index + 1}</span><h2>{title}</h2><p>{description}</p></article>)}</section>
  </main>;
}
