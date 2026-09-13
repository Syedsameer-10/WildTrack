"""Active event-condition-action evaluation."""
# ruff: noqa: E501, E701, I001
from typing import Any
from sqlalchemy import text
from app.db.engine import get_engine

def evaluate_event(event: dict[str, Any]) -> list[dict[str, Any]]:
    rules_sql = text("select id, name, event_type, severity, condition, action from public.active_rules where enabled")
    insert_sql = text("""insert into public.active_alerts (rule_id,event_id,message,severity)
      values (:rule_id,:event_id,:message,:severity) on conflict (rule_id,event_id) do nothing
      returning id, rule_id, event_id, message, severity, created_at""")
    alerts = []
    with get_engine().begin() as connection:
        for rule in connection.execute(rules_sql).mappings():
            payload = event.get("payload") or {}
            condition = rule["condition"] or {}
            matches = event.get("event_type") == rule["event_type"]
            if "species" in condition: matches = matches and payload.get("species") == condition["species"]
            if "battery_below" in condition: matches = matches and float(payload.get("battery_pct", 100)) < condition["battery_below"]
            if matches:
                row = connection.execute(insert_sql, {"rule_id": rule["id"], "event_id": event["event_id"], "message": f'{rule["name"]}: {rule["action"]}', "severity": rule["severity"]}).mappings().first()
                if row: alerts.append(dict(row))
    return alerts

def list_alerts(limit: int = 25) -> list[dict[str, Any]]:
    with get_engine().connect() as connection:
        return [dict(row) for row in connection.execute(text("select id, rule_id, event_id, message, severity, created_at from public.active_alerts order by created_at desc limit :limit"), {"limit": limit}).mappings()]
