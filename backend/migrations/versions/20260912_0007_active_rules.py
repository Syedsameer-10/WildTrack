"""Add configurable event-condition-action rules and alerts."""
# ruff: noqa: E501, I001

from collections.abc import Sequence
from alembic import op

revision: str = "20260912_0007"
down_revision: str | None = "20260911_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
      create table public.active_rules (
        id bigserial primary key, name text not null unique, event_type text not null,
        severity text not null default 'warning', condition jsonb not null default '{}'::jsonb,
        action text not null, enabled boolean not null default true,
        created_at timestamptz not null default now()
      );
      create table public.active_alerts (
        id bigserial primary key, rule_id bigint not null references public.active_rules(id),
        event_id text not null, message text not null, severity text not null,
        created_at timestamptz not null default now(), unique(rule_id, event_id)
      );
      insert into public.active_rules (name,event_type,severity,condition,action) values
        ('Elephant boundary crossing','boundary_crossing','warning',jsonb_build_object('species','Asian elephant'),'Create conservation alert'),
        ('Low sensor battery','sensor_reading','warning',jsonb_build_object('battery_below',20),'Create maintenance alert');
      update public.system_metadata set value = '20260912_0007', updated_at = now() where key = 'schema_version';
    """)


def downgrade() -> None:
    op.execute("drop table if exists public.active_alerts; drop table if exists public.active_rules;")
    op.execute("update public.system_metadata set value = '20260911_0006', updated_at = now() where key = 'schema_version';")
