"""Unit tests verifying migration 0010_child_profiles.py exists and is valid."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def test_migration_file_exists():
    path = Path("alembic/versions/0010_child_profiles.py")
    assert path.exists(), "Migration 0010_child_profiles.py not found"


def test_migration_has_upgrade_and_downgrade():
    spec = importlib.util.spec_from_file_location(
        "m", "alembic/versions/0010_child_profiles.py"
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    assert callable(getattr(module, "upgrade", None))
    assert callable(getattr(module, "downgrade", None))
