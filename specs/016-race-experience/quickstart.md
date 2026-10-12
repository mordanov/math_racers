# Quickstart: Race Experience Improvements

## Focused verification

Run frontend checks from `frontend/`:

```bash
pnpm vitest run src/engine/math src/engine/race src/pages/RaceScreenPage.test.tsx src/pages/ResultsScreenPage.test.tsx src/pages/SettingsPage.test.tsx src/shared/hooks/useAudioManager.test.ts
pnpm typecheck
pnpm lint
```

Run focused backend unit tests from `backend/`:

```bash
pytest tests/unit/mathematics tests/unit/races tests/unit/championships -m unit
```

Run championship and race integration tests when the Docker Compose test stack
is available:

```bash
make test-int
```

## Manual acceptance walkthrough

1. Set the round duration to 30 seconds, start a competitive race, and confirm
   the selected duration is used per problem. Hide the tab and confirm the
   timer pauses; return and confirm it resumes. Let one expire and verify its
   ordered empty answer is saved and the race continues.
2. Start Training and leave a problem visible beyond 60 seconds; it must remain
   untimed.
3. Generate the same tier 3–6 seed twice. Confirm order is identical, tiers 3
   and 5 multiplication use two-digit-by-one-digit operands, tier 5 addition
   uses two two-digit operands, and every division has quotient greater than
   one. Confirm Tier 6 division settings with no valid non-self division are
   rejected before save/race start.
4. Complete and reload between championship races. Confirm standings update
   once per race and the last race completes the championship.
5. Race with player, shared published, and unavailable opponent imagery, then
   enable reduced motion. Confirm authorized imagery or fallbacks track
   progress accessibly without exposing private child-profile portraits.
6. Adjust music and SFX while both are active. Confirm immediate independent
   volume changes and persistence after reload.
