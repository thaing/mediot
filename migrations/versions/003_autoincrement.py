"""Switch IDs from VARCHAR(36) UUID to auto-increment Integer.

Revision ID: 003_autoincrement
Revises: 002_seed
Create Date: 2026-07-04
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "003_autoincrement"
down_revision: Union[str, None] = "002_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("vitals")
    op.drop_table("device")
    op.drop_table("user")

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("social_provider", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_email", "user", ["email"])

    op.create_table(
        "device",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("d_id", sa.String(50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("d_id"),
    )
    op.create_index("ix_device_d_id", "device", ["d_id"])

    op.create_table(
        "vitals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.BigInteger(), nullable=False),
        sa.Column("hr", sa.Integer(), nullable=True),
        sa.Column("spo2", sa.Integer(), nullable=True),
        sa.Column("bp_sys", sa.Integer(), nullable=True),
        sa.Column("bp_dia", sa.Integer(), nullable=True),
        sa.Column("bat", sa.Integer(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["device.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vitals_device_id", "vitals", ["device_id"])
    op.create_index("ix_vitals_device_id_ts", "vitals", ["device_id", "ts"])

    # Re-seed 10 devices
    device_table = sa.table(
        "device",
        sa.column("d_id", sa.String(50)),
        sa.column("user_id", sa.Integer()),
    )
    devices = [{"d_id": f"HM-{i:03d}", "user_id": None} for i in range(1, 11)]
    op.bulk_insert(device_table, devices)


def downgrade() -> None:
    op.drop_table("vitals")
    op.drop_table("device")
    op.drop_table("user")

    # Recreate with UUID strings (original schema from 001)
    op.create_table(
        "user",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("social_provider", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_email", "user", ["email"])

    op.create_table(
        "device",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("d_id", sa.String(50), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("d_id"),
    )
    op.create_index("ix_device_d_id", "device", ["d_id"])

    op.create_table(
        "vitals",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=False),
        sa.Column("ts", sa.BigInteger(), nullable=False),
        sa.Column("hr", sa.Integer(), nullable=True),
        sa.Column("spo2", sa.Integer(), nullable=True),
        sa.Column("bp_sys", sa.Integer(), nullable=True),
        sa.Column("bp_dia", sa.Integer(), nullable=True),
        sa.Column("bat", sa.Integer(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["device.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_vitals_device_id", "vitals", ["device_id"])
    op.create_index("ix_vitals_device_id_ts", "vitals", ["device_id", "ts"])
