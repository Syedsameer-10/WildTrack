"""Create the hosted PostGIS foundation and controlled lookups."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260909_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("create extension if not exists postgis")
    op.create_table(
        "system_metadata",
        sa.Column("key", sa.Text(), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_table(
        "zone_types",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False),
        sa.CheckConstraint("sort_order > 0", name="ck_zone_types_positive_sort_order"),
    )
    op.create_table(
        "alert_severities",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False, unique=True),
        sa.Column("priority", sa.SmallInteger(), nullable=False, unique=True),
        sa.CheckConstraint("priority > 0", name="ck_alert_severities_positive_priority"),
    )
    op.create_table(
        "device_statuses",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("label", sa.Text(), nullable=False, unique=True),
        sa.Column("is_operational", sa.Boolean(), nullable=False),
    )
    op.execute(
        """
        insert into public.system_metadata (key, value, description) values
          ('schema_version', '20260909_0001', 'Latest WildTrack application schema revision.'),
          ('coordinate_reference_system', 'EPSG:4326', 'WGS 84; GeoJSON longitude-latitude order.'),
          ('study_region_status', 'synthetic', 'Ooty study geometries are demonstration data.')
        """
    )


def downgrade() -> None:
    op.drop_table("device_statuses")
    op.drop_table("alert_severities")
    op.drop_table("zone_types")
    op.drop_table("system_metadata")
