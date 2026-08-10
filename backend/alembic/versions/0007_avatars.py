"""avatars, avatar_portraits, generation_jobs tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: create avatars WITHOUT the active_portrait_id FK (circular FK would block CREATE)
    op.create_table(
        "avatars",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("species", sa.String(), nullable=False),
        sa.Column("fur_color", sa.String(7), nullable=False),
        sa.Column("eye_color", sa.String(7), nullable=False),
        sa.Column("hairstyle", sa.String(), nullable=False),
        sa.Column("accessories", postgresql.JSONB(), nullable=False, server_default="'[]'"),
        sa.Column("clothes_top_color", sa.String(7), nullable=False),
        sa.Column("clothes_bottom_color", sa.String(7), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("appearance_summary", sa.Text(), nullable=True),
        sa.Column("favorite_subject", sa.String(), nullable=True),
        sa.Column("running_style", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="'pending'"),
        sa.Column("is_favourite", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("active_portrait_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "species IN ('fox','rabbit','bear','cat','mouse','panda')",
            name="ck_avatars_species",
        ),
        sa.CheckConstraint(
            "status IN ('pending','published','failed')",
            name="ck_avatars_status",
        ),
    )
    op.create_index("idx_avatars_account_id", "avatars", ["account_id"])

    # Step 2: create avatar_portraits
    op.create_table(
        "avatar_portraits",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "avatar_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("avatars.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("prompt_version", sa.String(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=False),
        sa.Column("full_url", sa.String(), nullable=False),
        sa.Column("medium_url", sa.String(), nullable=False),
        sa.Column("small_url", sa.String(), nullable=False),
        sa.Column("thumb_url", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("avatar_id", "version", name="uq_avatar_portraits_avatar_version"),
    )
    op.create_index("idx_avatar_portraits_avatar_id", "avatar_portraits", ["avatar_id"])

    # Step 3: add active_portrait_id FK now that avatar_portraits exists
    op.create_foreign_key(
        "fk_avatars_active_portrait_id",
        "avatars",
        "avatar_portraits",
        ["active_portrait_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Step 4: create generation_jobs
    op.create_table(
        "generation_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "avatar_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("avatars.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "portrait_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("avatar_portraits.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(), nullable=False, server_default="'queued'"),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("prompt_version", sa.String(), nullable=True),
        sa.Column("model_version", sa.String(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('queued','llm_running','prompt_building','generating','validating',"
            "'storing','complete','failed')",
            name="ck_generation_jobs_status",
        ),
    )
    op.create_index("idx_generation_jobs_avatar_id", "generation_jobs", ["avatar_id"])
    op.create_index("idx_generation_jobs_status", "generation_jobs", ["status"])


def downgrade() -> None:
    op.drop_table("generation_jobs")
    op.drop_constraint("fk_avatars_active_portrait_id", "avatars", type_="foreignkey")
    op.drop_table("avatar_portraits")
    op.drop_table("avatars")
