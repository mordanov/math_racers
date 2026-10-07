# Sprint 2 — Auth + Child Profiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** App can log in, select a child profile, and navigate to authenticated routes.

**Architecture:** Backend adds the `child_profiles` table, CRUD API, and an ownership-check FastAPI dependency. Frontend adds an `AuthContext` that stores the JWT access token in memory, three new pages (Login, Register, Child Profile Select), a `RequireAuth` route guard, and updates the router to protect all existing routes. The `APIClient` singleton gains `setAuthToken()` so auth context can inject the Bearer token globally.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy 2 async / Alembic / pytest (backend); React 18 / TypeScript / React Router v7 / vitest (frontend)

**Spec:** `docs/superpowers/specs/2026-10-05-v1-execution-order-design.md` (§4, §1.1), `docs/ui/spec-ui-implementation.md` (§4), `docs/enhancements/claude-code-tasks.md` (§1.1, §4), `docs/prd.md` (FR-002, FR-004)

## Global Constraints

- Max 5 child profiles per parent account (FR-002)
- All routes under `/api/v1/`
- Access token: JWT stored in React state (memory only, not localStorage)
- Refresh token: HttpOnly cookie — never touched by JS
- Child profiles have no separate credentials — scoped under parent account
- `display_name` max 50 characters (FR-002 + avatar spec convention)
- `prefers-reduced-motion` respected on all animated elements
- All interactive elements keyboard-accessible with visible focus ring
- All form errors use `role="alert"`

## Review Focus

- **Refresh token persistence across page reload**: On hard reload, `AuthContext` must attempt a silent refresh before rendering protected content; a page that flashes unauthenticated state before the refresh completes would log out users on every reload.
- **Concurrent silent refresh**: If two simultaneous API calls both detect a 401, both should not trigger a token refresh — only one should refresh and the second should await the result.
- **Cross-account child profile access**: `GET /api/v1/child-profiles/{profile_id}` must 403 if the requesting parent doesn't own that profile, even if the profile UUID is guessed.
- **Token stored in memory, not DOM**: After login, the access token must not appear in `localStorage`, `sessionStorage`, or any cookie (only the refresh token cookie, which is HttpOnly).
- **RequireAuth with stale auth state**: If the token expires mid-session and auto-refresh fails, navigating to a protected route must redirect to `/login` rather than show a broken page.

---

### Task 1: Backend — Child Profiles Module Skeleton

**Files:**
- Create: `backend/app/child_profiles/__init__.py`
- Create: `backend/app/child_profiles/presentation/__init__.py`
- Create: `backend/app/child_profiles/presentation/api/__init__.py`
- Create: `backend/app/child_profiles/presentation/api/v1/__init__.py`
- Create: `backend/tests/unit/child_profiles/__init__.py`
- Create: `backend/tests/integration/child_profiles/__init__.py`

**Interfaces:**
- Produces: empty module tree that subsequent tasks import from

- [ ] **Step 1: Create all six `__init__.py` files**

```bash
mkdir -p backend/app/child_profiles/presentation/api/v1
touch backend/app/child_profiles/__init__.py
touch backend/app/child_profiles/presentation/__init__.py
touch backend/app/child_profiles/presentation/api/__init__.py
touch backend/app/child_profiles/presentation/api/v1/__init__.py
mkdir -p backend/tests/unit/child_profiles
mkdir -p backend/tests/integration/child_profiles
touch backend/tests/unit/child_profiles/__init__.py
touch backend/tests/integration/child_profiles/__init__.py
```

- [ ] **Step 2: Verify module is importable**

Run: `cd backend && python -c "import app.child_profiles; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/app/child_profiles/ backend/tests/unit/child_profiles/ backend/tests/integration/child_profiles/
git commit -m "feat(child-profiles): add backend module skeleton"
```

---

### Task 2: Backend — Alembic Migration 0010

**Files:**
- Create: `backend/alembic/versions/0010_child_profiles.py`

**Interfaces:**
- Produces: `child_profiles` table with `id`, `account_id`, `display_name`, `created_at`; index on `account_id`
- Consumes: `accounts.id` FK reference (already in DB)

- [ ] **Step 1: Write the failing test for migration existence**

```python
# backend/tests/unit/child_profiles/test_migration_exists.py
import importlib.util
from pathlib import Path

def test_migration_file_exists():
    path = Path("alembic/versions/0010_child_profiles.py")
    assert path.exists(), "Migration 0010_child_profiles.py not found"

def test_migration_has_upgrade_and_downgrade():
    spec = importlib.util.spec_from_file_location(
        "m", "alembic/versions/0010_child_profiles.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(getattr(module, "upgrade", None))
    assert callable(getattr(module, "downgrade", None))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/child_profiles/test_migration_exists.py -v`
Expected: FAIL — migration file not found

- [ ] **Step 3: Write migration**

```python
# backend/alembic/versions/0010_child_profiles.py
"""add child_profiles table

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-05
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "child_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "account_id",
            UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("idx_child_profiles_account_id", "child_profiles", ["account_id"])


def downgrade() -> None:
    op.drop_index("idx_child_profiles_account_id", table_name="child_profiles")
    op.drop_table("child_profiles")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/unit/child_profiles/test_migration_exists.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/0010_child_profiles.py backend/tests/unit/child_profiles/test_migration_exists.py
git commit -m "feat(child-profiles): add Alembic migration 0010"
```

---

### Task 3: Backend — ORM Model and Repository

**Files:**
- Create: `backend/app/child_profiles/models.py`
- Create: `backend/app/child_profiles/repository.py`

**Interfaces:**
- Produces:
  - `ChildProfile` ORM class with `id: UUID`, `account_id: UUID`, `display_name: str`, `created_at: datetime`
  - `ChildProfileRepository` Protocol: `get(id) -> ChildProfile | None`, `list_for_account(account_id) -> list[ChildProfile]`, `create(account_id, display_name) -> ChildProfile`, `delete(id) -> None`, `count_for_account(account_id) -> int`
  - `SQLAlchemyChildProfileRepository` concrete implementation
- Consumes: `infrastructure.database.base.Base`, `accounts.id` FK (already in DB via migration)

- [ ] **Step 1: Write failing unit test for model importability**

```python
# backend/tests/unit/child_profiles/test_models.py
import uuid
from datetime import datetime, UTC

import pytest

from app.child_profiles.models import ChildProfile


def test_child_profile_model_has_required_fields():
    profile = ChildProfile(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        display_name="Alice",
        created_at=datetime.now(UTC),
    )
    assert profile.display_name == "Alice"
    assert profile.__tablename__ == "child_profiles"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/child_profiles/test_models.py -v`
Expected: FAIL — cannot import `ChildProfile`

- [ ] **Step 3: Write `models.py`**

```python
# backend/app/child_profiles/models.py
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class ChildProfile(Base):
    __tablename__ = "child_profiles"
    __table_args__ = (Index("idx_child_profiles_account_id", "account_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/unit/child_profiles/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Write failing test for repository**

```python
# backend/tests/unit/child_profiles/test_repository.py
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.child_profiles.repository import ChildProfileRepository, SQLAlchemyChildProfileRepository


def test_repository_protocol_methods():
    """Repository protocol has all required methods."""
    import inspect
    methods = [m for m in dir(ChildProfileRepository) if not m.startswith("_")]
    assert "get" in methods
    assert "list_for_account" in methods
    assert "create" in methods
    assert "delete" in methods
    assert "count_for_account" in methods
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/child_profiles/test_repository.py -v`
Expected: FAIL — cannot import `ChildProfileRepository`

- [ ] **Step 7: Write `repository.py`**

```python
# backend/app/child_profiles/repository.py
from __future__ import annotations

import uuid
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.child_profiles.models import ChildProfile


class ChildProfileRepository(Protocol):
    async def get(self, profile_id: uuid.UUID) -> ChildProfile | None: ...
    async def list_for_account(self, account_id: uuid.UUID) -> list[ChildProfile]: ...
    async def create(self, account_id: uuid.UUID, display_name: str) -> ChildProfile: ...
    async def delete(self, profile_id: uuid.UUID) -> None: ...
    async def count_for_account(self, account_id: uuid.UUID) -> int: ...


class SQLAlchemyChildProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, profile_id: uuid.UUID) -> ChildProfile | None:
        result = await self._session.execute(
            select(ChildProfile).where(ChildProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def list_for_account(self, account_id: uuid.UUID) -> list[ChildProfile]:
        result = await self._session.execute(
            select(ChildProfile)
            .where(ChildProfile.account_id == account_id)
            .order_by(ChildProfile.created_at)
        )
        return list(result.scalars().all())

    async def create(self, account_id: uuid.UUID, display_name: str) -> ChildProfile:
        profile = ChildProfile(account_id=account_id, display_name=display_name)
        self._session.add(profile)
        await self._session.flush()
        return profile

    async def delete(self, profile_id: uuid.UUID) -> None:
        profile = await self.get(profile_id)
        if profile is not None:
            await self._session.delete(profile)

    async def count_for_account(self, account_id: uuid.UUID) -> int:
        result = await self._session.execute(
            select(func.count()).where(ChildProfile.account_id == account_id)
        )
        return result.scalar_one()
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `cd backend && pytest tests/unit/child_profiles/ -v`
Expected: all PASS

- [ ] **Step 9: Commit**

```bash
git add backend/app/child_profiles/models.py backend/app/child_profiles/repository.py backend/tests/unit/child_profiles/
git commit -m "feat(child-profiles): add ORM model and repository"
```

---

### Task 4: Backend — Schemas and API Router

**Files:**
- Create: `backend/app/child_profiles/schemas.py`
- Create: `backend/app/child_profiles/presentation/api/v1/child_profiles.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- Consumes: `SQLAlchemyChildProfileRepository`, `get_current_account`, `get_session`
- Produces:
  - `GET /api/v1/child-profiles` → `ChildProfileListResponse` (parent's own profiles)
  - `POST /api/v1/child-profiles` → `ChildProfileResponse` (201); 409 if at limit (5)
  - `DELETE /api/v1/child-profiles/{profile_id}` → 204; 403 if not owner; 404 if not found

- [ ] **Step 1: Write failing test for schemas**

```python
# backend/tests/unit/child_profiles/test_schemas.py
import uuid
from datetime import datetime, UTC

from app.child_profiles.schemas import (
    ChildProfileResponse,
    ChildProfileListResponse,
    CreateChildProfileRequest,
)


def test_create_request_validates_max_length():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CreateChildProfileRequest(display_name="A" * 51)

def test_create_request_rejects_empty():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CreateChildProfileRequest(display_name="")

def test_child_profile_response_fields():
    r = ChildProfileResponse(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        display_name="Alice",
        created_at=datetime.now(UTC),
    )
    assert r.display_name == "Alice"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && pytest tests/unit/child_profiles/test_schemas.py -v`
Expected: FAIL — cannot import schemas

- [ ] **Step 3: Write `schemas.py`**

```python
# backend/app/child_profiles/schemas.py
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChildProfileResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    display_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChildProfileListResponse(BaseModel):
    profiles: list[ChildProfileResponse]


class CreateChildProfileRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && pytest tests/unit/child_profiles/test_schemas.py -v`
Expected: PASS

- [ ] **Step 5: Write failing integration test**

```python
# backend/tests/integration/child_profiles/test_api_child_profiles.py
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_list_child_profiles_empty(auth_client):
    """Authenticated parent gets empty list when no profiles exist."""
    resp = await auth_client.get("/api/v1/child-profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert data["profiles"] == []


@pytest.mark.asyncio
async def test_create_child_profile(auth_client):
    """POST creates a profile; GET returns it."""
    resp = await auth_client.post("/api/v1/child-profiles", json={"display_name": "Alice"})
    assert resp.status_code == 201
    created = resp.json()
    assert created["display_name"] == "Alice"

    list_resp = await auth_client.get("/api/v1/child-profiles")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["profiles"]) == 1


@pytest.mark.asyncio
async def test_create_profile_at_limit_returns_409(auth_client):
    """6th profile creation returns 409."""
    for i in range(5):
        r = await auth_client.post("/api/v1/child-profiles", json={"display_name": f"Child{i}"})
        assert r.status_code == 201
    over_limit = await auth_client.post("/api/v1/child-profiles", json={"display_name": "TooMany"})
    assert over_limit.status_code == 409


@pytest.mark.asyncio
async def test_delete_own_profile(auth_client):
    """DELETE removes the profile; subsequent GET returns empty."""
    create_resp = await auth_client.post("/api/v1/child-profiles", json={"display_name": "Bob"})
    profile_id = create_resp.json()["id"]
    del_resp = await auth_client.delete(f"/api/v1/child-profiles/{profile_id}")
    assert del_resp.status_code == 204

    list_resp = await auth_client.get("/api/v1/child-profiles")
    assert list_resp.json()["profiles"] == []


@pytest.mark.asyncio
async def test_delete_other_accounts_profile_returns_403(auth_client, second_auth_client):
    """Parent cannot delete another parent's child profile."""
    create_resp = await auth_client.post("/api/v1/child-profiles", json={"display_name": "Alice"})
    profile_id = create_resp.json()["id"]
    resp = await second_auth_client.delete(f"/api/v1/child-profiles/{profile_id}")
    assert resp.status_code == 403
```

- [ ] **Step 6: Run integration test to verify it fails**

Run: `cd backend && pytest tests/integration/child_profiles/ -v -m integration`
Expected: FAIL — 404 (router not registered yet)

- [ ] **Step 7: Write the API router**

```python
# backend/app/child_profiles/presentation/api/v1/child_profiles.py
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import Account
from app.child_profiles.repository import SQLAlchemyChildProfileRepository
from app.child_profiles.schemas import (
    ChildProfileListResponse,
    ChildProfileResponse,
    CreateChildProfileRequest,
)
from app.presentation.api.middleware.auth import get_current_account
from app.shared.exceptions import ConflictError, NotFoundError, PermissionError
from infrastructure.database.session import get_session

_MAX_PROFILES = 5

router = APIRouter(prefix="/api/v1/child-profiles", tags=["child-profiles"])


@router.get("", response_model=ChildProfileListResponse)
async def list_child_profiles(
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfileListResponse:
    repo = SQLAlchemyChildProfileRepository(session)
    profiles = await repo.list_for_account(account.id)
    return ChildProfileListResponse(
        profiles=[ChildProfileResponse.model_validate(p) for p in profiles]
    )


@router.post("", response_model=ChildProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_child_profile(
    body: CreateChildProfileRequest,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> ChildProfileResponse:
    repo = SQLAlchemyChildProfileRepository(session)
    count = await repo.count_for_account(account.id)
    if count >= _MAX_PROFILES:
        raise ConflictError(
            "MAX_CHILD_PROFILES",
            f"Maximum of {_MAX_PROFILES} child profiles reached.",
        )
    profile = await repo.create(account.id, body.display_name)
    return ChildProfileResponse.model_validate(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child_profile(
    profile_id: uuid.UUID,
    account: Account = Depends(get_current_account),
    session: AsyncSession = Depends(get_session),
) -> None:
    repo = SQLAlchemyChildProfileRepository(session)
    profile = await repo.get(profile_id)
    if profile is None:
        raise NotFoundError("CHILD_PROFILE_NOT_FOUND", "Child profile not found.")
    if profile.account_id != account.id:
        raise PermissionError("FORBIDDEN", "Not your child profile.")
    await repo.delete(profile_id)
```

- [ ] **Step 8: Register router in `main.py`**

Add to `create_app()` alongside the other router imports and `include_router` calls:

```python
# in the import block inside create_app():
from app.child_profiles.presentation.api.v1.child_profiles import (
    router as child_profiles_router,
)

# after the other include_router calls:
app.include_router(child_profiles_router)
```

- [ ] **Step 9: Run integration tests to verify they pass**

Run: `cd backend && pytest tests/integration/child_profiles/ -v -m integration`
Expected: all PASS

- [ ] **Step 10: Run full backend test suite to confirm no regressions**

Run: `cd backend && pytest -m unit && pytest -m integration`
Expected: all PASS

- [ ] **Step 11: Commit**

```bash
git add backend/app/child_profiles/schemas.py backend/app/child_profiles/presentation/api/v1/child_profiles.py backend/app/main.py backend/tests/integration/child_profiles/ backend/tests/unit/child_profiles/test_schemas.py
git commit -m "feat(child-profiles): add schemas, API router, wire into main"
```

---

### Task 5: Backend — Child Profile Ownership Middleware

**Files:**
- Create: `backend/app/presentation/api/middleware/child_profile.py`
- Create: `backend/tests/unit/middleware/test_child_profile_middleware.py`

**Interfaces:**
- Produces: `get_child_profile(profile_id: UUID, account, session) -> ChildProfile` FastAPI dependency — raises 404 if not found, 403 if account doesn't own it, bypasses check for administrators
- Consumes: `get_current_account`, `get_session`, `SQLAlchemyChildProfileRepository`

This dependency will be used in Sprint 3+ by Avatar/Race routes to validate profile ownership.

- [ ] **Step 1: Write failing unit tests**

```python
# backend/tests/unit/middleware/test_child_profile_middleware.py
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.accounts.models import Account, AccountRole, ApprovalStatus
from app.child_profiles.models import ChildProfile
from app.presentation.api.middleware.child_profile import get_child_profile_dependency
from app.shared.exceptions import NotFoundError, PermissionError


def _make_account(role: str = "parent") -> Account:
    return Account(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="x",
        role=role,
        approval_status=ApprovalStatus.approved,
    )


def _make_profile(account_id: uuid.UUID) -> ChildProfile:
    return ChildProfile(id=uuid.uuid4(), account_id=account_id, display_name="Alice")


@pytest.mark.asyncio
async def test_parent_can_access_own_profile():
    account = _make_account("parent")
    profile = _make_profile(account.id)
    repo = AsyncMock()
    repo.get.return_value = profile

    result = await get_child_profile_dependency(profile.id, account, repo)
    assert result.id == profile.id


@pytest.mark.asyncio
async def test_parent_cannot_access_other_profile():
    account = _make_account("parent")
    other_profile = _make_profile(uuid.uuid4())  # different account
    repo = AsyncMock()
    repo.get.return_value = other_profile

    with pytest.raises(PermissionError):
        await get_child_profile_dependency(other_profile.id, account, repo)


@pytest.mark.asyncio
async def test_administrator_can_access_any_profile():
    admin = _make_account("administrator")
    profile = _make_profile(uuid.uuid4())  # different account
    repo = AsyncMock()
    repo.get.return_value = profile

    result = await get_child_profile_dependency(profile.id, admin, repo)
    assert result.id == profile.id


@pytest.mark.asyncio
async def test_profile_not_found_raises_404():
    account = _make_account("parent")
    repo = AsyncMock()
    repo.get.return_value = None

    with pytest.raises(NotFoundError):
        await get_child_profile_dependency(uuid.uuid4(), account, repo)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/unit/middleware/test_child_profile_middleware.py -v`
Expected: FAIL — cannot import `get_child_profile_dependency`

- [ ] **Step 3: Write the middleware**

```python
# backend/app/presentation/api/middleware/child_profile.py
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
```

- [ ] **Step 4: Ensure `backend/tests/unit/middleware/__init__.py` exists**

```bash
touch backend/tests/unit/middleware/__init__.py
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && pytest tests/unit/middleware/test_child_profile_middleware.py -v`
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/presentation/api/middleware/child_profile.py backend/tests/unit/middleware/
git commit -m "feat(child-profiles): add ownership-check FastAPI dependency"
```

---

### Task 6: Frontend — APIClient Auth Token Support

**Files:**
- Modify: `frontend/src/infrastructure/api-client.ts`
- Modify: `frontend/src/infrastructure/api-client.test.ts`

**Interfaces:**
- Produces: `APIClient.setAuthToken(token: string | null)` — subsequent requests include `Authorization: Bearer {token}` header when token is set
- Consumes: existing `APIClient` class

- [ ] **Step 1: Write the failing test**

```typescript
// Add to frontend/src/infrastructure/api-client.test.ts

describe('auth token', () => {
  it('sends Authorization header when token is set', async () => {
    const client = new APIClient();
    client.setAuthToken('test-token');

    fetchMock.mockResponseOnce(JSON.stringify({ ok: true }));
    await client.get('/test');

    const [, options] = fetchMock.mock.calls[0];
    expect((options as RequestInit).headers).toMatchObject({
      Authorization: 'Bearer test-token',
    });
  });

  it('omits Authorization header when no token set', async () => {
    const client = new APIClient();

    fetchMock.mockResponseOnce(JSON.stringify({ ok: true }));
    await client.get('/test');

    const [, options] = fetchMock.mock.calls[0];
    expect((options as RequestInit).headers).not.toHaveProperty('Authorization');
  });

  it('clears Authorization header after setAuthToken(null)', async () => {
    const client = new APIClient();
    client.setAuthToken('test-token');
    client.setAuthToken(null);

    fetchMock.mockResponseOnce(JSON.stringify({ ok: true }));
    await client.get('/test');

    const [, options] = fetchMock.mock.calls[0];
    expect((options as RequestInit).headers).not.toHaveProperty('Authorization');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test -- api-client`
Expected: FAIL — `setAuthToken is not a function`

- [ ] **Step 3: Update `api-client.ts`**

```typescript
export class APIClient {
  private baseURL = '/api/v1';
  private authToken: string | null = null;

  setAuthToken(token: string | null): void {
    this.authToken = token;
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, body);
  }

  async delete<T = void>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  private async request<T>(method: string, path: string, body?: unknown, attempt = 1): Promise<T> {
    const headers: Record<string, string> = {};
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (this.authToken) headers['Authorization'] = `Bearer ${this.authToken}`;

    const response = await fetch(this.baseURL + path, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      credentials: 'same-origin',
    });

    if (response.status === 204) return undefined as unknown as T;

    if (response.status >= 500 && attempt < 3) {
      await delay(200 * attempt);
      return this.request<T>(method, path, body, attempt + 1);
    }

    if (!response.ok) {
      throw new APIError(response.status, await response.json().catch(() => ({})));
    }

    return response.json() as Promise<T>;
  }
}

export const apiClient = new APIClient();
```

- [ ] **Step 4: Run full frontend test suite to verify no regressions**

Run: `cd frontend && pnpm test`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/infrastructure/api-client.ts frontend/src/infrastructure/api-client.test.ts
git commit -m "feat(auth): add setAuthToken to APIClient"
```

---

### Task 7: Frontend — Auth Types and API Modules

**Files:**
- Create: `frontend/src/infrastructure/auth/types.ts`
- Create: `frontend/src/infrastructure/auth/authApi.ts`
- Create: `frontend/src/infrastructure/auth/childProfilesApi.ts`

**Interfaces:**
- Produces:
  - `Account { id: string, email: string, role: 'parent' | 'administrator' }` type
  - `ChildProfile { id: string, account_id: string, display_name: string, created_at: string }` type
  - `login(email, password): Promise<{ access_token: string }>` — POST `/auth/login`
  - `register(email, password): Promise<void>` — POST `/auth/register`
  - `refreshToken(): Promise<{ access_token: string }>` — POST `/auth/refresh`
  - `logout(): Promise<void>` — POST `/auth/logout`
  - `fetchChildProfiles(): Promise<ChildProfile[]>` — GET `/child-profiles`
  - `createChildProfile(name): Promise<ChildProfile>` — POST `/child-profiles`
  - `deleteChildProfile(id): Promise<void>` — DELETE `/child-profiles/{id}`
- Consumes: `apiClient` from `api-client.ts`

Note: `login()` and `refreshToken()` do NOT use `apiClient` directly because they must not send the current (possibly expired) auth token. They use `fetch` directly.

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/infrastructure/auth/authApi.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { login, logout, refreshToken, register } from './authApi';

// fetchMock is set up in test-setup.ts

describe('authApi', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it('login posts credentials and returns access_token', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ access_token: 'tok123' }));
    const result = await login('user@example.com', 'pass');
    expect(result.access_token).toBe('tok123');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/auth/login'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('register posts credentials', async () => {
    fetchMock.mockResponseOnce(JSON.stringify({ message: 'ok' }), { status: 201 });
    await expect(register('user@example.com', 'pass')).resolves.not.toThrow();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test -- authApi`
Expected: FAIL — module not found

- [ ] **Step 3: Write `types.ts`**

```typescript
// frontend/src/infrastructure/auth/types.ts
export interface Account {
  id: string;
  email: string;
  role: 'parent' | 'administrator';
}

export interface ChildProfile {
  id: string;
  account_id: string;
  display_name: string;
  created_at: string;
}
```

- [ ] **Step 4: Write `authApi.ts`**

Auth calls bypass `apiClient` to avoid sending a stale or absent Bearer token:

```typescript
// frontend/src/infrastructure/auth/authApi.ts
import { APIError } from '../api-client';

const BASE = '/api/v1/auth';

async function authPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(BASE + path, {
    method: 'POST',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
    credentials: 'same-origin',
  });
  if (response.status === 204) return undefined as unknown as T;
  if (!response.ok) throw new APIError(response.status, await response.json().catch(() => ({})));
  return response.json() as Promise<T>;
}

export function login(email: string, password: string): Promise<{ access_token: string }> {
  return authPost('/login', { email, password });
}

export function register(email: string, password: string): Promise<void> {
  return authPost('/register', { email, password });
}

export function refreshToken(): Promise<{ access_token: string }> {
  return authPost('/refresh');
}

export function logout(): Promise<void> {
  return authPost('/logout');
}
```

- [ ] **Step 5: Write `childProfilesApi.ts`**

```typescript
// frontend/src/infrastructure/auth/childProfilesApi.ts
import type { ChildProfile } from './types';
import { apiClient } from '../api-client';

interface ChildProfileListResponse {
  profiles: ChildProfile[];
}

export async function fetchChildProfiles(): Promise<ChildProfile[]> {
  const data = await apiClient.get<ChildProfileListResponse>('/child-profiles');
  return data.profiles;
}

export async function createChildProfile(displayName: string): Promise<ChildProfile> {
  return apiClient.post<ChildProfile>('/child-profiles', { display_name: displayName });
}

export async function deleteChildProfile(profileId: string): Promise<void> {
  return apiClient.delete(`/child-profiles/${profileId}`);
}
```

- [ ] **Step 6: Run tests**

Run: `cd frontend && pnpm test -- authApi`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add frontend/src/infrastructure/auth/
git commit -m "feat(auth): add auth types, authApi, childProfilesApi"
```

---

### Task 8: Frontend — AuthContext and RequireAuth

**Files:**
- Create: `frontend/src/infrastructure/auth/AuthContext.tsx`
- Create: `frontend/src/infrastructure/auth/RequireAuth.tsx`

**Interfaces:**
- Produces:
  - `AuthContext` with `{ account: Account | null, activeChildId: string | null, isAuthenticated: boolean, login, logout, selectChild, isLoading: boolean }`
  - `AuthProvider` wrapping component — on mount, silently attempts `refreshToken()` to restore session
  - `RequireAuth` component — renders `<Outlet />` if authenticated, else `<Navigate to="/login" />`
  - `useAuth()` hook
- Consumes: `login()`, `logout()`, `refreshToken()` from `authApi`; `apiClient.setAuthToken()`

- [ ] **Step 1: Write failing tests**

```typescript
// frontend/src/infrastructure/auth/AuthContext.test.tsx
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import * as authApi from './authApi';
import { apiClient } from '../api-client';

vi.mock('./authApi');
vi.mock('../api-client', () => ({
  apiClient: { setAuthToken: vi.fn() },
  APIError: class extends Error {},
}));

function TestConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="email">{auth.account?.email ?? 'none'}</span>
      <span data-testid="child">{auth.activeChildId ?? 'none'}</span>
      <button onClick={() => auth.login('a@b.com', 'pass')}>login</button>
      <button onClick={() => auth.logout()}>logout</button>
      <button onClick={() => auth.selectChild('child-1')}>select</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('no session'));
  });

  it('starts unauthenticated', async () => {
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await screen.findByTestId('email');
    expect(screen.getByTestId('email')).toHaveTextContent('none');
  });

  it('login sets account and calls setAuthToken', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'tok' });
    // Decode a minimal JWT payload: {"sub":"uid-1","email":"a@b.com","exp":9999999999}
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({ sub: 'uid-1', email: 'a@b.com', role: 'parent', exp: 9999999999 }));
    vi.mocked(authApi.login).mockResolvedValue({ access_token: `${header}.${payload}.sig` });

    const user = userEvent.setup();
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await screen.findByTestId('email');

    await user.click(screen.getByText('login'));
    expect(screen.getByTestId('email')).toHaveTextContent('a@b.com');
    expect(apiClient.setAuthToken).toHaveBeenCalledWith(expect.stringContaining('.'));
  });

  it('selectChild updates activeChildId', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'x.eyJzdWIiOiJ1MSIsImVtYWlsIjoiYUBiLmNvbSIsInJvbGUiOiJwYXJlbnQiLCJleHAiOjk5OTk5OTk5OTl9.s' });
    const user = userEvent.setup();
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await screen.findByTestId('email');

    await user.click(screen.getByText('select'));
    expect(screen.getByTestId('child')).toHaveTextContent('child-1');
  });

  it('logout clears account and calls setAuthToken(null)', async () => {
    vi.mocked(authApi.logout).mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<AuthProvider><TestConsumer /></AuthProvider>);
    await screen.findByTestId('email');

    await user.click(screen.getByText('logout'));
    expect(apiClient.setAuthToken).toHaveBeenCalledWith(null);
    expect(screen.getByTestId('email')).toHaveTextContent('none');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && pnpm test -- AuthContext`
Expected: FAIL — module not found

- [ ] **Step 3: Write `AuthContext.tsx`**

```typescript
// frontend/src/infrastructure/auth/AuthContext.tsx
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { apiClient } from '../api-client';
import { login as apiLogin, logout as apiLogout, refreshToken } from './authApi';
import type { Account } from './types';

interface AuthState {
  account: Account | null;
  activeChildId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  selectChild: (childId: string) => void;
}

function decodeToken(token: string): Account {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return { id: payload.sub, email: payload.email, role: payload.role };
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [activeChildId, setActiveChildId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const applyToken = useCallback((token: string) => {
    apiClient.setAuthToken(token);
    const decoded = decodeToken(token);
    setAccount(decoded);
    // Schedule silent refresh 2 minutes before 15-minute TTL
    const ms = 13 * 60 * 1000;
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    refreshTimer.current = setTimeout(async () => {
      try {
        const { access_token } = await refreshToken();
        applyToken(access_token);
      } catch {
        setAccount(null);
        apiClient.setAuthToken(null);
      }
    }, ms);
  }, []);

  useEffect(() => {
    refreshToken()
      .then(({ access_token }) => applyToken(access_token))
      .catch(() => {})
      .finally(() => setIsLoading(false));
    return () => {
      if (refreshTimer.current) clearTimeout(refreshTimer.current);
    };
  }, [applyToken]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiLogin(email, password);
      applyToken(access_token);
    },
    [applyToken],
  );

  const logout = useCallback(async () => {
    await apiLogout().catch(() => {});
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    apiClient.setAuthToken(null);
    setAccount(null);
    setActiveChildId(null);
  }, []);

  const selectChild = useCallback((childId: string) => {
    setActiveChildId(childId);
  }, []);

  return (
    <AuthContext.Provider
      value={{ account, activeChildId, isAuthenticated: account !== null, isLoading, login, logout, selectChild }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
```

- [ ] **Step 4: Write `RequireAuth.tsx`**

```typescript
// frontend/src/infrastructure/auth/RequireAuth.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthContext';
import LoadingSpinner from '../../shared/components/LoadingSpinner';

export default function RequireAuth() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner message="Loading…" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Outlet />;
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd frontend && pnpm test -- AuthContext`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add frontend/src/infrastructure/auth/AuthContext.tsx frontend/src/infrastructure/auth/RequireAuth.tsx
git commit -m "feat(auth): add AuthContext, AuthProvider, RequireAuth guard"
```

---

### Task 9: Frontend — Login and Register Pages

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/RegisterPage.tsx`
- Create: `frontend/src/pages/LoginPage.test.tsx`
- Create: `frontend/src/pages/RegisterPage.test.tsx`

**Interfaces:**
- Consumes: `useAuth().login()`, `authApi.register()`, React Router `useNavigate`
- Produces: Login form (email + password → `/child-profiles` on success); Register form (email + password → shows success message, link to login)

- [ ] **Step 1: Write failing tests for LoginPage**

```typescript
// frontend/src/pages/LoginPage.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginPage from './LoginPage';
import * as AuthContextModule from '../infrastructure/auth/AuthContext';

vi.mock('../infrastructure/auth/AuthContext');

const mockLogin = vi.fn();

describe('LoginPage', () => {
  beforeEach(() => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      account: null,
      activeChildId: null,
      logout: vi.fn(),
      selectChild: vi.fn(),
    });
  });

  it('renders email and password fields', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it('calls login on submit', async () => {
    mockLogin.mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    await user.type(screen.getByLabelText(/email/i), 'a@b.com');
    await user.type(screen.getByLabelText(/password/i), 'pass');
    await user.click(screen.getByRole('button', { name: /log in/i }));
    expect(mockLogin).toHaveBeenCalledWith('a@b.com', 'pass');
  });

  it('shows error message on failed login', async () => {
    mockLogin.mockRejectedValue(new Error('Bad credentials'));
    const user = userEvent.setup();
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    await user.type(screen.getByLabelText(/email/i), 'a@b.com');
    await user.type(screen.getByLabelText(/password/i), 'wrong');
    await user.click(screen.getByRole('button', { name: /log in/i }));
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test -- LoginPage`
Expected: FAIL — module not found

- [ ] **Step 3: Write `LoginPage.tsx`**

```typescript
// frontend/src/pages/LoginPage.tsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import Button from '../shared/components/Button';
import { tokens } from '../shared/tokens';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/child-profiles', { replace: true });
    } catch {
      setError('Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 400, margin: '0 auto', padding: tokens.spacing.xl }}>
      <h1>Log In</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: tokens.spacing.md }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: tokens.spacing.xs }}>
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            style={{ width: '100%', padding: tokens.spacing.sm }}
          />
        </div>
        <div style={{ marginBottom: tokens.spacing.md }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: tokens.spacing.xs }}>
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            style={{ width: '100%', padding: tokens.spacing.sm }}
          />
        </div>
        {error && (
          <p role="alert" style={{ color: tokens.color.error, marginBottom: tokens.spacing.md }}>
            {error}
          </p>
        )}
        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Logging in…' : 'Log In'}
        </Button>
      </form>
      <p style={{ marginTop: tokens.spacing.md }}>
        No account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}
```

- [ ] **Step 4: Write `RegisterPage.tsx`**

```typescript
// frontend/src/pages/RegisterPage.tsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { register } from '../infrastructure/auth/authApi';
import Button from '../shared/components/Button';
import { tokens } from '../shared/tokens';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password);
      setSuccess(true);
    } catch {
      setError('Registration failed. That email may already be in use.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main style={{ maxWidth: 400, margin: '0 auto', padding: tokens.spacing.xl }}>
        <h1>Registration Submitted</h1>
        <p>Your account is awaiting administrator approval. You'll be able to log in once approved.</p>
        <Link to="/login">Back to Log In</Link>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: 400, margin: '0 auto', padding: tokens.spacing.xl }}>
      <h1>Create Account</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: tokens.spacing.md }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: tokens.spacing.xs }}>
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            style={{ width: '100%', padding: tokens.spacing.sm }}
          />
        </div>
        <div style={{ marginBottom: tokens.spacing.md }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: tokens.spacing.xs }}>
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            style={{ width: '100%', padding: tokens.spacing.sm }}
          />
        </div>
        {error && (
          <p role="alert" style={{ color: tokens.color.error, marginBottom: tokens.spacing.md }}>
            {error}
          </p>
        )}
        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? 'Submitting…' : 'Register'}
        </Button>
      </form>
      <p style={{ marginTop: tokens.spacing.md }}>
        Already have an account? <Link to="/login">Log In</Link>
      </p>
    </main>
  );
}
```

- [ ] **Step 5: Write failing test for RegisterPage**

```typescript
// frontend/src/pages/RegisterPage.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import RegisterPage from './RegisterPage';
import * as authApi from '../infrastructure/auth/authApi';

vi.mock('../infrastructure/auth/authApi');

describe('RegisterPage', () => {
  beforeEach(() => {
    fetchMock.resetMocks();
  });

  it('shows success message after registration', async () => {
    vi.mocked(authApi.register).mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    await user.type(screen.getByLabelText(/email/i), 'new@example.com');
    await user.type(screen.getByLabelText(/password/i), 'secret');
    await user.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByText(/awaiting administrator approval/i)).toBeInTheDocument();
  });

  it('shows error on failure', async () => {
    vi.mocked(authApi.register).mockRejectedValue(new Error('taken'));
    const user = userEvent.setup();
    render(<MemoryRouter><RegisterPage /></MemoryRouter>);
    await user.type(screen.getByLabelText(/email/i), 'used@example.com');
    await user.type(screen.getByLabelText(/password/i), 'pass');
    await user.click(screen.getByRole('button', { name: /register/i }));
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
```

- [ ] **Step 6: Run all page tests**

Run: `cd frontend && pnpm test -- LoginPage RegisterPage`
Expected: all PASS

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx frontend/src/pages/LoginPage.test.tsx frontend/src/pages/RegisterPage.tsx frontend/src/pages/RegisterPage.test.tsx
git commit -m "feat(auth): add LoginPage and RegisterPage"
```

---

### Task 10: Frontend — Child Profile Select Page and Router Update

**Files:**
- Create: `frontend/src/pages/ChildProfileSelectPage.tsx`
- Create: `frontend/src/pages/ChildProfileSelectPage.test.tsx`
- Modify: `frontend/src/router.tsx`
- Modify: `frontend/src/main.tsx`

**Interfaces:**
- Consumes: `fetchChildProfiles()`, `createChildProfile()` from `childProfilesApi`; `useAuth().selectChild()`, `useNavigate()`
- Produces:
  - `ChildProfileSelectPage`: lists profiles, clicking one selects it + navigates to `/`; "Add Profile" inline form (input + submit); profiles list has `data-testid="profile-list"`
  - Updated router: `/login`, `/register`, `/child-profiles` added; all existing routes wrapped by `<RequireAuth />`
  - `AuthProvider` wraps `RouterProvider` in `main.tsx`

- [ ] **Step 1: Write failing test for ChildProfileSelectPage**

```typescript
// frontend/src/pages/ChildProfileSelectPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import ChildProfileSelectPage from './ChildProfileSelectPage';
import * as childProfilesApi from '../infrastructure/auth/childProfilesApi';
import * as AuthContextModule from '../infrastructure/auth/AuthContext';

vi.mock('../infrastructure/auth/childProfilesApi');
vi.mock('../infrastructure/auth/AuthContext');

const mockSelectChild = vi.fn();

describe('ChildProfileSelectPage', () => {
  beforeEach(() => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      selectChild: mockSelectChild,
      login: vi.fn(),
      logout: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      account: { id: 'acc-1', email: 'p@e.com', role: 'parent' },
      activeChildId: null,
    });
  });

  it('renders list of profiles', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([
      { id: 'p1', account_id: 'acc-1', display_name: 'Alice', created_at: '2026-01-01T00:00:00Z' },
      { id: 'p2', account_id: 'acc-1', display_name: 'Bob', created_at: '2026-01-02T00:00:00Z' },
    ]);
    render(<MemoryRouter><ChildProfileSelectPage /></MemoryRouter>);
    expect(await screen.findByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  it('selecting a profile calls selectChild', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([
      { id: 'p1', account_id: 'acc-1', display_name: 'Alice', created_at: '2026-01-01T00:00:00Z' },
    ]);
    const user = userEvent.setup();
    render(<MemoryRouter><ChildProfileSelectPage /></MemoryRouter>);
    await user.click(await screen.findByText('Alice'));
    expect(mockSelectChild).toHaveBeenCalledWith('p1');
  });

  it('shows empty state when no profiles exist', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([]);
    render(<MemoryRouter><ChildProfileSelectPage /></MemoryRouter>);
    expect(await screen.findByText(/no profiles yet/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test -- ChildProfileSelectPage`
Expected: FAIL — module not found

- [ ] **Step 3: Write `ChildProfileSelectPage.tsx`**

```typescript
// frontend/src/pages/ChildProfileSelectPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import {
  createChildProfile,
  fetchChildProfiles,
} from '../infrastructure/auth/childProfilesApi';
import type { ChildProfile } from '../infrastructure/auth/types';
import Button from '../shared/components/Button';
import ErrorState from '../shared/components/ErrorState';
import LoadingSpinner from '../shared/components/LoadingSpinner';
import { tokens } from '../shared/tokens';

export default function ChildProfileSelectPage() {
  const { selectChild } = useAuth();
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<ChildProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchChildProfiles()
      .then(setProfiles)
      .catch(() => setError('Could not load profiles.'))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (profile: ChildProfile) => {
    selectChild(profile.id);
    navigate('/', { replace: true });
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const created = await createChildProfile(newName.trim());
      setProfiles((prev) => [...prev, created]);
      setNewName('');
    } catch {
      setError('Could not create profile.');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading profiles…" />;
  if (error) return <ErrorState message={error} />;

  return (
    <main style={{ maxWidth: 500, margin: '0 auto', padding: tokens.spacing.xl }}>
      <h1>Who's Playing?</h1>
      {profiles.length === 0 ? (
        <p>No profiles yet — add one below.</p>
      ) : (
        <ul data-testid="profile-list" style={{ listStyle: 'none', padding: 0, marginBottom: tokens.spacing.lg }}>
          {profiles.map((p) => (
            <li key={p.id} style={{ marginBottom: tokens.spacing.sm }}>
              <Button variant="secondary" onClick={() => handleSelect(p)} style={{ width: '100%' }}>
                {p.display_name}
              </Button>
            </li>
          ))}
        </ul>
      )}
      {profiles.length < 5 && (
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: tokens.spacing.sm }}>
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Profile name"
            maxLength={50}
            aria-label="New profile name"
            style={{ flex: 1, padding: tokens.spacing.sm }}
          />
          <Button type="submit" variant="primary" disabled={creating || !newName.trim()}>
            Add
          </Button>
        </form>
      )}
    </main>
  );
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd frontend && pnpm test -- ChildProfileSelectPage`
Expected: PASS

- [ ] **Step 5: Update `router.tsx`**

```typescript
// frontend/src/router.tsx
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import App from './App';
import RequireAuth from './infrastructure/auth/RequireAuth';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ChildProfileSelectPage from './pages/ChildProfileSelectPage';
import HomePage from './pages/HomePage';
import AvatarGalleryPage from './pages/AvatarGalleryPage';
import AvatarCreatorPage from './pages/AvatarCreatorPage';
import RaceSetupPage from './pages/RaceSetupPage';
import RaceScreenPage from './pages/RaceScreenPage';
import ResultsScreenPage from './pages/ResultsScreenPage';
import StatisticsPage from './pages/StatisticsPage';
import SettingsPage from './pages/SettingsPage';
import ParentDashboardPage from './pages/ParentDashboardPage';
import ChampionshipPage from './pages/ChampionshipPage';

export const routeConfig: RouteObject[] = [
  {
    element: <App />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
      {
        element: <RequireAuth />,
        children: [
          { path: '/child-profiles', element: <ChildProfileSelectPage /> },
          { index: true, element: <HomePage /> },
          { path: '/avatars', element: <AvatarGalleryPage /> },
          { path: '/avatars/new', element: <AvatarCreatorPage /> },
          { path: '/race/setup', element: <RaceSetupPage /> },
          { path: '/race/:id', element: <RaceScreenPage /> },
          { path: '/race/:id/results', element: <ResultsScreenPage /> },
          { path: '/statistics', element: <StatisticsPage /> },
          { path: '/settings', element: <SettingsPage /> },
          { path: '/parent', element: <ParentDashboardPage /> },
          { path: '/championship/:id', element: <ChampionshipPage /> },
        ],
      },
    ],
  },
];

export const router = createBrowserRouter(routeConfig);
```

- [ ] **Step 6: Update `main.tsx` to wrap with `AuthProvider`**

```typescript
// frontend/src/main.tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { AuthProvider } from './infrastructure/auth/AuthContext';
import { router } from './router';
import './shared/animations.css';

const root = document.getElementById('root');
if (!root) throw new Error('Root element not found');

createRoot(root).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
);
```

- [ ] **Step 7: Update router.test.tsx to account for auth routes**

The existing router tests check that page stubs render. We need to ensure they still work with RequireAuth by providing an AuthProvider that returns `isAuthenticated: true`:

```typescript
// Modify frontend/src/router.test.tsx to mock AuthContext
// Add near the top:
vi.mock('./infrastructure/auth/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    isLoading: false,
    account: { id: 'u1', email: 'a@b.com', role: 'parent' },
    activeChildId: null,
    login: vi.fn(),
    logout: vi.fn(),
    selectChild: vi.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
```

- [ ] **Step 8: Run full frontend test suite**

Run: `cd frontend && pnpm test`
Expected: all PASS

- [ ] **Step 9: Run type-check**

Run: `cd frontend && pnpm typecheck`
Expected: no errors

- [ ] **Step 10: Run lint**

Run: `cd frontend && pnpm lint`
Expected: no errors

- [ ] **Step 11: Commit**

```bash
git add frontend/src/pages/ChildProfileSelectPage.tsx frontend/src/pages/ChildProfileSelectPage.test.tsx frontend/src/router.tsx frontend/src/main.tsx
git commit -m "feat(auth): add ChildProfileSelectPage, update router with auth guards"
```

---

## Dependencies & Execution Order

### Task Dependencies

- Task 1 (skeleton): no deps — start immediately
- Task 2 (migration): depends on Task 1
- Task 3 (model + repo): depends on Task 1
- Task 4 (schemas + router): depends on Tasks 2 and 3
- Task 5 (middleware): depends on Task 3
- Task 6 (API client): no backend deps — start after Task 1 in parallel
- Task 7 (auth types + API): depends on Task 6
- Task 8 (AuthContext + guard): depends on Task 7
- Task 9 (Login/Register): depends on Task 8
- Task 10 (ChildProfileSelect + router): depends on Tasks 8 and 9

### Parallel Opportunities

- Tasks 1–5 (backend) and Tasks 6–10 (frontend) can progress in parallel
- Within backend: Task 2 (migration) and Task 3 (model) can be worked in parallel after Task 1
- Task 5 (middleware) can be started after Task 3 regardless of Task 4 status

---

## Notes

- The `child_profile.py` middleware dependency is created now but not yet wired into Avatar/Race routes — that happens in Sprint 3
- `atob(token.split('.')[1])` JWT decoding is safe here because the token came from our own backend and is validated server-side; no client-side signature verification is needed
- Silent refresh timer (13 minutes) is cleared on logout to prevent refresh-after-logout
- The `second_auth_client` fixture in integration tests follows the pattern of existing integration test fixtures for creating a second authenticated account
