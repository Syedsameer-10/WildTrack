from typing import Any

from sqlalchemy import text

from app.db.engine import get_engine


def managed_areas_feature_collection() -> dict[str, Any]:
    query = text(
        """
        select json_build_object(
          'type', 'FeatureCollection',
          'features', coalesce(json_agg(feature order by name), '[]'::json)
        )
        from (
          select name, json_build_object(
            'type', 'Feature',
            'id', code,
            'geometry', ST_AsGeoJSON(geometry)::json,
            'properties', json_build_object(
              'code', code,
              'name', name,
              'area_class', area_class,
              'description', description,
              'data_source', data_source,
              'area_sq_km', round((ST_Area(geometry::geography) / 1000000)::numeric, 2)
            )
          ) as feature
          from public.managed_areas
        ) areas
        """
    )
    with get_engine().connect() as connection:
        return connection.execute(query).scalar_one()


def query_point(longitude: float, latitude: float) -> dict[str, Any]:
    point_sql = "ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)"
    matching_query = text(
        f"""
        select code, name, area_class, description,
          round((ST_Area(geometry::geography) / 1000000)::numeric, 2) as area_sq_km
        from public.managed_areas
        where ST_Covers(geometry, {point_sql})
        order by name
        """
    )
    nearest_query = text(
        f"""
        select code, name,
          round(ST_Distance(geometry::geography, {point_sql}::geography)::numeric, 1) as distance_m
        from public.managed_areas
        order by geometry <-> {point_sql}
        limit 1
        """
    )
    parameters = {"longitude": longitude, "latitude": latitude}
    with get_engine().connect() as connection:
        matches = [dict(row) for row in connection.execute(matching_query, parameters).mappings()]
        nearest_row = connection.execute(nearest_query, parameters).mappings().one_or_none()

    for match in matches:
        match["area_sq_km"] = float(match["area_sq_km"])
    nearest = dict(nearest_row) if nearest_row else None
    if nearest:
        nearest["distance_m"] = float(nearest["distance_m"])
    return {
        "point": {"longitude": longitude, "latitude": latitude},
        "inside_managed_area": bool(matches),
        "matched_areas": matches,
        "nearest_area": nearest,
    }
