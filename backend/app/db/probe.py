from dataclasses import asdict, dataclass

from sqlalchemy import text

from app.db.engine import DatabaseNotConfiguredError, get_engine


@dataclass(frozen=True)
class DatabaseProbe:
    status: str
    provider: str
    database: str
    postgis_version: str
    schema_version: str
    lookup_records: int


def probe_database() -> DatabaseProbe:
    engine = get_engine()
    query = text(
        """
        select
            current_database() as database_name,
            postgis_version() as postgis_version,
            coalesce(
                (select value from public.system_metadata where key = 'schema_version'),
                'unknown'
            ) as schema_version,
            (select count(*) from public.zone_types)
              + (select count(*) from public.alert_severities)
              + (select count(*) from public.device_statuses) as lookup_records
        """
    )
    with engine.connect() as connection:
        row = connection.execute(query).mappings().one()

    return DatabaseProbe(
        status="ready",
        provider="supabase-postgresql",
        database=row["database_name"],
        postgis_version=row["postgis_version"],
        schema_version=row["schema_version"],
        lookup_records=row["lookup_records"],
    )


def database_probe_payload() -> dict[str, str | int]:
    return asdict(probe_database())


__all__ = [
    "DatabaseNotConfiguredError",
    "DatabaseProbe",
    "database_probe_payload",
    "probe_database",
]
