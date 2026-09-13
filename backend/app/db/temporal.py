# ruff: noqa: E501

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text

from app.db.engine import get_engine


def observation_timeline(
    valid_at: datetime | None = None,
    system_at: datetime | None = None,
) -> dict[str, Any]:
    valid_snapshot = valid_at or datetime.now(UTC)
    system_snapshot = system_at or datetime.now(UTC)
    query = text(
        """
        select json_build_object(
          'as_of', :valid_at,
          'system_at', :system_at,
          'history_anchor', (select min(system_to) - interval '1 millisecond' from public.wildlife_observations where system_to is not null),
          'observations', coalesce(json_agg(json_build_object(
            'id', id, 'observation_key', observation_key, 'revision', revision,
            'animal_tag', animal_tag,
            'species', species,
            'zone_code', zone_code,
            'zone_name', zone_name,
            'area_class', area_class,
            'observed_at', observed_at,
            'recorded_at', recorded_at,
            'confidence', confidence, 'correction_reason', correction_reason,
            'late_arrival', late_arrival,
            'longitude', longitude,
            'latitude', latitude
          ) order by observed_at), '[]'::json)
        )
        from (
          select o.id, o.observation_key, o.revision, o.animal_tag, o.species,
            o.zone_code, a.name as zone_name,
            a.area_class, o.observed_at, o.recorded_at, o.confidence,
            o.correction_reason,
            (o.revision = 1 and o.recorded_at - o.observed_at > interval '1 hour') as late_arrival,
            ST_X(o.location) as longitude, ST_Y(o.location) as latitude
          from public.wildlife_observations o
          join public.managed_areas a on a.code = o.zone_code
          where o.valid_from <= :valid_at
            and (o.valid_to is null or :valid_at < o.valid_to)
            and o.system_from <= :system_at
            and (o.system_to is null or :system_at < o.system_to)
          order by o.observed_at
          limit 100
        ) observations
        """
    )
    with get_engine().connect() as connection:
        return connection.execute(
            query, {"valid_at": valid_snapshot, "system_at": system_snapshot}
        ).scalar_one()


def observation_versions(observation_key: str) -> list[dict[str, Any]]:
    query = text("""
        select id, observation_key, revision, animal_tag, species, zone_code,
          observed_at, recorded_at, valid_from, valid_to, system_from, system_to,
          correction_reason, confidence
        from public.wildlife_observations
        where observation_key = :observation_key order by revision
    """)
    with get_engine().connect() as connection:
        return [
            dict(row)
            for row in connection.execute(query, {"observation_key": observation_key}).mappings()
        ]
