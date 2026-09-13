"""Replace the broad Ooty test extent with compact categorized zones."""

# ruff: noqa: E501

from collections.abc import Sequence

from alembic import op

revision: str = "20260911_0003"
down_revision: str | None = "20260909_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("delete from public.managed_areas where code = 'ooty-study-area'")
    op.execute(
        """
        insert into public.managed_areas
          (code, name, area_class, description, data_source, geometry)
        values
          ('ooty-north-monitoring', 'Ooty North Monitoring Zone', 'study_area',
           'Compact observation zone for testing sightings and sensor coverage.',
           'WildTrack demonstration geometry',
           ST_Multi(ST_GeomFromText('POLYGON((76.682 11.421,76.690 11.424,76.695 11.419,76.691 11.413,76.683 11.414,76.682 11.421))',4326))),
          ('doddabetta-conservation', 'Doddabetta Conservation Zone', 'protected_boundary',
           'Protected-boundary example used to test category-specific spatial rules.',
           'WildTrack demonstration geometry',
           ST_Multi(ST_GeomFromText('POLYGON((76.702 11.420,76.711 11.422,76.716 11.416,76.712 11.409,76.704 11.411,76.702 11.420))',4326))),
          ('lovedale-patrol-sector', 'Lovedale Patrol Sector', 'patrol_sector',
           'Small operational sector for route and presence checks.',
           'WildTrack demonstration geometry',
           ST_Multi(ST_GeomFromText('POLYGON((76.690 11.408,76.699 11.410,76.703 11.403,76.698 11.397,76.689 11.399,76.690 11.408))',4326))),
          ('ketti-monitoring-zone', 'Ketti Monitoring Zone', 'study_area',
           'Separate monitoring zone for testing multiple areas in one map view.',
           'WildTrack demonstration geometry',
           ST_Multi(ST_GeomFromText('POLYGON((76.708 11.405,76.716 11.407,76.720 11.400,76.716 11.394,76.707 11.396,76.708 11.405))',4326)))
        """
    )
    op.execute(
        "update public.system_metadata set value = '20260911_0003', updated_at = now() "
        "where key = 'schema_version'"
    )


def downgrade() -> None:
    op.execute(
        "delete from public.managed_areas where code in "
        "('ooty-north-monitoring','doddabetta-conservation','lovedale-patrol-sector','ketti-monitoring-zone')"
    )
    op.execute(
        """
        insert into public.managed_areas
          (code, name, area_class, description, data_source, geometry)
        values ('ooty-study-area', 'Ooty / Nilgiris Test Area', 'study_area',
          'Synthetic demonstration extent for Phase 3 spatial testing; not an official forest boundary.',
          'WildTrack demonstration geometry',
          ST_Multi(ST_GeomFromText('POLYGON((76.675 11.416,76.694 11.425,76.714 11.417,76.713 11.399,76.691 11.393,76.676 11.402,76.675 11.416))',4326)))
        """
    )
    op.execute(
        "update public.system_metadata set value = '20260909_0002', updated_at = now() "
        "where key = 'schema_version'"
    )
