import { useEffect, useMemo, useState } from "react";
import { fetchObservationTimeline, type TemporalTimeline } from "./api";

interface TemporalPanelProps { timeline: TemporalTimeline | null; }
type KnowledgeMode = "current" | "historical";

function displayTime(value: string) {
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function TemporalPanel({ timeline }: TemporalPanelProps) {
  const baseObservations = timeline?.observations ?? [];
  const [position, setPosition] = useState(0);
  const [mode, setMode] = useState<KnowledgeMode>("current");
  const [snapshot, setSnapshot] = useState<TemporalTimeline | null>(timeline);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setPosition(Math.max(baseObservations.length - 1, 0));
    setSnapshot(timeline);
  }, [timeline, baseObservations.length]);

  const selected = baseObservations[position];
  useEffect(() => {
    if (!selected || !timeline) return;
    const controller = new AbortController();
    setLoading(true);
    void fetchObservationTimeline({
      asOf: selected.observed_at,
      systemAt: mode === "historical" ? timeline.history_anchor ?? undefined : undefined,
      signal: controller.signal,
    }).then(setSnapshot).catch(() => undefined).finally(() => setLoading(false));
    return () => controller.abort();
  }, [selected, mode, timeline]);

  const observations = useMemo(() => snapshot?.observations ?? [], [snapshot]);
  return <section className="temporal-panel" aria-labelledby="temporal-title">
    <div className="temporal-heading"><div><p className="eyebrow">BITEMPORAL DATABASE</p><h2 id="temporal-title">Observation playback</h2></div><div className="temporal-mode"><span className="live-dot" />{loading ? "QUERYING" : mode === "current" ? "CURRENT KNOWLEDGE" : "EARLIER KNOWLEDGE"}</div></div>
    {baseObservations.length === 0 ? <p className="temporal-empty">Temporal records are unavailable.</p> : <>
      <div className="knowledge-switch" aria-label="Transaction-time view"><button className={mode === "current" ? "selected" : ""} onClick={() => setMode("current")} type="button">Current database</button><button className={mode === "historical" ? "selected" : ""} onClick={() => setMode("historical")} type="button" disabled={!timeline?.history_anchor}>Before correction</button></div>
      <div className="playback-control"><label htmlFor="playback-time">Valid-time snapshot <strong>{displayTime(selected.observed_at)}</strong></label><input id="playback-time" type="range" min="0" max={baseObservations.length - 1} value={position} onChange={(event) => setPosition(Number(event.target.value))} /><div><span>{displayTime(baseObservations[0].observed_at)}</span><span>Latest event</span></div></div>
      <div className="temporal-summary"><span>{observations.length} facts visible</span><span>System time: {mode === "current" ? "now" : "before correction"}</span></div>
      <div className="timeline-list">{observations.slice().reverse().map((observation) => <article key={observation.id}><time dateTime={observation.observed_at}>{displayTime(observation.observed_at)}</time><div><strong>{observation.species}</strong><span>{observation.animal_tag} · {observation.zone_name}</span>{(observation.revision > 1 || observation.late_arrival) && <div className="temporal-tags">{observation.revision > 1 && <mark>corrected v{observation.revision}</mark>}{observation.late_arrival && <mark>late arrival</mark>}</div>}</div><small>{Math.round(Number(observation.confidence) * 100)}%</small></article>)}</div>
    </>}
  </section>;
}
