"""Add valid-time and system-time history to wildlife observations."""

# ruff: noqa: E501

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260911_0005"
down_revision: str | None = "20260911_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("wildlife_observations", sa.Column("observation_key", sa.Text(), nullable=True))
    op.add_column("wildlife_observations", sa.Column("revision", sa.Integer(), nullable=True))
    op.add_column(
        "wildlife_observations", sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "wildlife_observations", sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "wildlife_observations", sa.Column("system_from", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "wildlife_observations", sa.Column("system_to", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("wildlife_observations", sa.Column("correction_reason", sa.Text(), nullable=True))
    op.execute(
        "update public.wildlife_observations set observation_key = 'OBS-' || lpad(id::text, 4, '0'), revision = 1, valid_from = observed_at, system_from = recorded_at"
    )
    for column in ("observation_key", "revision", "valid_from", "system_from"):
        op.alter_column("wildlife_observations", column, nullable=False)
    op.create_check_constraint("ck_observation_revision", "wildlife_observations", "revision > 0")
    op.create_check_constraint(
        "ck_observation_valid_period",
        "wildlife_observations",
        "valid_to is null or valid_to > valid_from",
    )
    op.create_check_constraint(
        "ck_observation_system_period",
        "wildlife_observations",
        "system_to is null or system_to > system_from",
    )
    op.execute(
        "create unique index uq_observation_current_version on public.wildlife_observations (observation_key) where system_to is null"
    )
    op.execute(
        "create index ix_observation_valid_period on public.wildlife_observations using gist (tstzrange(valid_from, coalesce(valid_to, 'infinity'::timestamptz), '[)'))"
    )
    op.execute(
        "create index ix_observation_system_period on public.wildlife_observations using gist (tstzrange(system_from, coalesce(system_to, 'infinity'::timestamptz), '[)'))"
    )
    op.execute(
        "update public.wildlife_observations set system_to = now() where animal_tag = 'LE-031' and revision = 1"
    )
    op.execute("""
        insert into public.wildlife_observations
          (animal_tag, species, zone_code, observed_at, recorded_at, confidence, location,
           observation_key, revision, valid_from, valid_to, system_from, correction_reason)
        select animal_tag, species, 'ketti-monitoring-zone', observed_at, now(), 0.947,
          ST_SetSRID(ST_MakePoint(76.713, 11.402), 4326), observation_key, 2,
          valid_from, valid_to, now(), 'Camera coordinates corrected after field verification.'
        from public.wildlife_observations where animal_tag = 'LE-031' and revision = 1
    """)
    op.execute("""
        insert into public.wildlife_observations
          (animal_tag, species, zone_code, observed_at, recorded_at, confidence, location,
           observation_key, revision, valid_from, system_from, correction_reason)
        values ('AE-044', 'Asian elephant', 'lovedale-patrol-sector', now() - interval '12 hours',
          now(), 0.901, ST_SetSRID(ST_MakePoint(76.696, 11.403), 4326),
          'OBS-LATE-0001', 1, now() - interval '12 hours', now(),
          'Late-arriving sensor record synchronized after connectivity returned.')
    """)
    op.execute(
        "update public.system_metadata set value = '20260911_0005', updated_at = now() where key = 'schema_version'"
    )


def downgrade() -> None:
    op.execute("delete from public.wildlife_observations where observation_key = 'OBS-LATE-0001'")
    op.execute(
        "delete from public.wildlife_observations where revision = 2 and animal_tag = 'LE-031'"
    )
    op.execute(
        "update public.wildlife_observations set system_to = null where animal_tag = 'LE-031' and revision = 1"
    )
    op.execute("drop index if exists public.ix_observation_system_period")
    op.execute("drop index if exists public.ix_observation_valid_period")
    op.execute("drop index if exists public.uq_observation_current_version")
    op.drop_constraint("ck_observation_system_period", "wildlife_observations", type_="check")
    op.drop_constraint("ck_observation_valid_period", "wildlife_observations", type_="check")
    op.drop_constraint("ck_observation_revision", "wildlife_observations", type_="check")
    for column in (
        "correction_reason",
        "system_to",
        "system_from",
        "valid_to",
        "valid_from",
        "revision",
        "observation_key",
    ):
        op.drop_column("wildlife_observations", column)
    op.execute(
        "update public.system_metadata set value = '20260911_0004', updated_at = now() where key = 'schema_version'"
    )
