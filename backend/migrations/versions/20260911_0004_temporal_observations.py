"""Add timestamped wildlife observations for temporal playback."""

# ruff: noqa: E501

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260911_0004"
down_revision: str | None = "20260911_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wildlife_observations",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("animal_tag", sa.Text(), nullable=False),
        sa.Column("species", sa.Text(), nullable=False),
        sa.Column("zone_code", sa.Text(), sa.ForeignKey("managed_areas.code"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("location", sa.Text(), nullable=False),
        sa.CheckConstraint("confidence between 0 and 1", name="ck_observation_confidence"),
    )
    op.execute(
        "alter table public.wildlife_observations alter column location type geometry(Point, 4326) "
        "using ST_GeomFromText(location, 4326)"
    )
    op.create_index("ix_observations_observed_at", "wildlife_observations", ["observed_at"])
    op.create_index(
        "ix_observations_zone_time", "wildlife_observations", ["zone_code", "observed_at"]
    )
    op.create_index(
        "ix_observations_location", "wildlife_observations", ["location"], postgresql_using="gist"
    )
    op.execute(
        """
        insert into public.wildlife_observations
          (animal_tag, species, zone_code, observed_at, confidence, location)
        values
          ('NL-014', 'Nilgiri langur', 'ooty-north-monitoring', now() - interval '22 hours', 0.941, 'POINT(76.687 11.418)'),
          ('IG-207', 'Indian gaur', 'lovedale-patrol-sector', now() - interval '14 hours', 0.884, 'POINT(76.695 11.404)'),
          ('LE-031', 'Indian leopard', 'doddabetta-conservation', now() - interval '8 hours', 0.792, 'POINT(76.709 11.416)'),
          ('SD-118', 'Sambar deer', 'ketti-monitoring-zone', now() - interval '4 hours', 0.927, 'POINT(76.714 11.400)'),
          ('IG-207', 'Indian gaur', 'ooty-north-monitoring', now() - interval '2 hours', 0.913, 'POINT(76.689 11.416)'),
          ('NL-014', 'Nilgiri langur', 'doddabetta-conservation', now() - interval '25 minutes', 0.968, 'POINT(76.707 11.417)')
        """
    )
    op.execute(
        "update public.system_metadata set value = '20260911_0004', updated_at = now() where key = 'schema_version'"
    )


def downgrade() -> None:
    op.drop_index("ix_observations_location", table_name="wildlife_observations")
    op.drop_index("ix_observations_zone_time", table_name="wildlife_observations")
    op.drop_index("ix_observations_observed_at", table_name="wildlife_observations")
    op.drop_table("wildlife_observations")
    op.execute(
        "update public.system_metadata set value = '20260911_0003', updated_at = now() where key = 'schema_version'"
    )
