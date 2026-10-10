import infrastructure.database.models  # noqa: F401
from infrastructure.database.base import Base


def test_model_registry_resolves_avatar_foreign_keys() -> None:
    tables = Base.metadata.tables

    child_profile_fk = next(iter(tables["avatars"].c.child_profile_id.foreign_keys))
    account_fk = next(iter(tables["avatars"].c.account_id.foreign_keys))
    assert child_profile_fk.column is tables["child_profiles"].c.id
    assert account_fk.column is tables["accounts"].c.id
