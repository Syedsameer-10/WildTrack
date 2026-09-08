"""Add the synthetic Ooty spatial test area."""

# ruff: noqa: E501

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260909_0002"
down_revision: str | None = "20260909_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "managed_areas",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False, unique=True),
        sa.Column("area_class", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("data_source", sa.Text(), nullable=False),
        sa.Column("geometry", sa.Text(), nullable=False),
        sa.CheckConstraint(
            "area_class in ('study_area', 'protected_boundary', 'patrol_sector')",
            name="ck_managed_areas_class",
        ),
    )
    op.execute(
        "alter table public.managed_areas alter column geometry type geometry(MultiPolygon, 4326) "
        "using ST_Multi(ST_GeomFromText(geometry, 4326))"
    )
    op.create_index(
        "ix_managed_areas_geometry",
        "managed_areas",
        ["geometry"],
        postgresql_using="gist",
    )
    op.execute(
        """
        insert into public.managed_areas
          (code, name, area_class, description, data_source, geometry)
        values (
          'ooty-study-area',
          'Ooty / Nilgiris Test Area',
          'study_area',
          'Synthetic demonstration extent for Phase 3 spatial testing; not an official forest boundary.',
          'WildTrack demonstration geometry',
          ST_Multi(ST_GeomFromText(
            'POLYGON((76.675 11.416, 76.694 11.425, 76.714 11.417, 76.713 11.399, 76.691 11.393, 76.676 11.402, 76.675 11.416))',
            4326
          ))
        )
        """
    )
    op.execute(
        "update public.system_metadata set value = '20260909_0002', updated_at = now() "
        "where key = 'schema_version'"
    )


def downgrade() -> None:
    op.drop_index("ix_managed_areas_geometry", table_name="managed_areas")
    op.drop_table("managed_areas")
    op.execute(
        "update public.system_metadata set value = '20260909_0001', updated_at = now() "
        "where key = 'schema_version'"
    )
