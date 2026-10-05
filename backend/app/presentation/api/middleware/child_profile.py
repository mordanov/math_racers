from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account, AccountRole
from app.child_profiles.models import ChildProfile
from app.child_profiles.repository import SQLAlchemyChildProfileRepository
from app.presentation.api.middleware.auth import get_current_account
from app.shared.exceptions import NotFoundError, PermissionError
from infrastructure.database.session import get_session


async def get_child_profile_dependency(
    profile_id: uuid.UUID,
    account: Account,
    repo: SQLAlchemyChildProfileRepository,
) -> ChildProfile:
    """Validate profile exists and belongs to the authenticated account.
    Administrators bypass the ownership check."""
    profile = await repo.get(profile_id)
    if profile is None:
        raise NotFoundError("CHILD_PROFILE_NOT_FOUND", "Child profile not found.")
    if account.role != AccountRole.administrator and profile.account_id != account.id:
        raise PermissionError("FORBIDDEN", "Not your child profile.")
    return profile


async def get_child_profile(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfile:
    """FastAPI dependency: resolves and validates child profile ownership."""
    repo = SQLAlchemyChildProfileRepository(session)
    return await get_child_profile_dependency(profile_id, account, repo)
