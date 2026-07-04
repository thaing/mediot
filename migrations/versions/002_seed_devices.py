"""Seed 10 devices (HM-001 through HM-010) — unassigned by default.

Revision ID: 002_seed
Revises: e1f889aaf35c
Create Date: 2026-07-03
"""

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_seed"
down_revision: Union[str, None] = "e1f889aaf35c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    device_table = sa.table(
        "device",
        sa.column("id", sa.String(36)),
        sa.column("d_id", sa.String(50)),
        sa.column("user_id", sa.String(36)),
    )

    devices = [
        {"id": str(uuid.uuid4()), "d_id": f"HM-{i:03d}", "user_id": None}
        for i in range(1, 11)
    ]

    op.bulk_insert(device_table, devices)


def downgrade() -> None:
    op.execute("DELETE FROM device WHERE d_id LIKE 'HM-0%'")
