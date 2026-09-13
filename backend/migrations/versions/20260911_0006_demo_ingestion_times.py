"""Normalize demonstration ingestion times for late-arrival testing."""

from collections.abc import Sequence

from alembic import op

revision: str = "20260911_0006"
down_revision: str | None = "20260911_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        update public.wildlife_observations
        set recorded_at = observed_at + interval '5 minutes',
            system_from = observed_at + interval '5 minutes'
        where revision = 1 and observation_key <> 'OBS-LATE-0001'
        """
    )
    op.execute(
        "update public.system_metadata set value = '20260911_0006', updated_at = now() "
        "where key = 'schema_version'"
    )


def downgrade() -> None:
    op.execute(
        "update public.system_metadata set value = '20260911_0005', updated_at = now() "
        "where key = 'schema_version'"
    )
