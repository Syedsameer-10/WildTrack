from sqlalchemy import text

from app.db.engine import get_engine

SEED_SQL = """
insert into public.zone_types (code, label, description, sort_order) values
  ('core', 'Core conservation zone', 'Highest protection demonstration area.', 10),
  ('buffer', 'Buffer zone', 'Managed transition around a core zone.', 20),
  ('restricted', 'Restricted zone', 'Entry produces an active-database evaluation.', 30)
on conflict (code) do update set
  label = excluded.label,
  description = excluded.description,
  sort_order = excluded.sort_order;

insert into public.alert_severities (code, label, priority) values
  ('info', 'Information', 10),
  ('warning', 'Warning', 20),
  ('critical', 'Critical', 30)
on conflict (code) do update set label = excluded.label, priority = excluded.priority;

insert into public.device_statuses (code, label, is_operational) values
  ('active', 'Active', true),
  ('low_battery', 'Low battery', true),
  ('offline', 'Offline', false),
  ('maintenance', 'Under maintenance', false)
on conflict (code) do update set
  label = excluded.label,
  is_operational = excluded.is_operational;
"""


def seed() -> None:
    with get_engine().begin() as connection:
        connection.execute(text(SEED_SQL))


if __name__ == "__main__":
    seed()
    print("WildTrack lookup seed completed successfully.")
