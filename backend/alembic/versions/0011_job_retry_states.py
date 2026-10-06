"""add retrying and permanent_failure states to generation_jobs

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-06
"""

from __future__ import annotations

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_generation_jobs_status", "generation_jobs", type_="check")
    op.create_check_constraint(
        "ck_generation_jobs_status",
        "generation_jobs",
        "status IN ('queued','llm_running','prompt_building','generating','validating',"
        "'storing','complete','failed','retrying','permanent_failure')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_generation_jobs_status", "generation_jobs", type_="check")
    op.create_check_constraint(
        "ck_generation_jobs_status",
        "generation_jobs",
        "status IN ('queued','llm_running','prompt_building','generating','validating',"
        "'storing','complete','failed')",
    )
