import { useMemo, useState } from "react";
import type { EventFeed } from "./api";

interface EventPanelProps { feed: EventFeed | null; onRefresh?: () => void; }

function displayTime(value: string) {
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function EventPanel({ feed, onRefresh }: EventPanelProps) {
  const [typeFilter, setTypeFilter] = useState("all");
  const [zoneFilter, setZoneFilter] = useState("all");
  const types = useMemo(() => [...new Set(feed?.events.map((event) => event.event_type) ?? [])], [feed]);
  const zones = useMemo(() => [...new Set(feed?.events.map((event) => event.zone_code).filter((zone): zone is string => Boolean(zone)) ?? [])], [feed]);
  const events = feed?.events.filter((event) => (typeFilter === "all" || event.event_type === typeFilter) && (zoneFilter === "all" || event.zone_code === zoneFilter)) ?? [];
  return <section className="event-panel" aria-labelledby="events-title">
    <div className="event-heading"><div><p className="eyebrow">NOSQL EVENT STREAM</p><h2 id="events-title">Wildlife and sensor events</h2></div><div className="event-actions"><span className={`event-status ${feed ? "ready" : "waiting"}`}>{feed ? "MONGODB ATLAS" : "ATLAS UNAVAILABLE"}</span>{onRefresh && <button type="button" className="event-refresh" onClick={onRefresh}>Refresh</button>}</div></div>
    {!feed && <p className="event-empty">The Atlas event feed is unavailable. Spatial and temporal data remain available.</p>}
    {feed && <><div className="event-filters"><label>Type<select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}><option value="all">All types</option>{types.map((type) => <option key={type} value={type}>{type.replaceAll("_", " ")}</option>)}</select></label><label>Zone<select value={zoneFilter} onChange={(event) => setZoneFilter(event.target.value)}><option value="all">All zones</option>{zones.map((zone) => <option key={zone} value={zone}>{zone?.replaceAll("-", " ")}</option>)}</select></label></div><div className="event-list">{events.map((event) => <article key={event.event_id}><div className={`event-severity ${event.severity}`} /><div><strong>{event.event_type.replaceAll("_", " ")}</strong><span>{event.source_type} · {event.source_id}</span></div><time dateTime={event.occurred_at}>{displayTime(event.occurred_at)}</time><small>{event.zone_code?.replaceAll("-", " ") ?? "unassigned"}</small></article>)}</div></>}
  </section>;
}
