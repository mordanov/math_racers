# Research: Race Experience Improvements

## Existing System Findings

### Race timing and timeout answer

- The frontend engine measures obstacle time and already treats an empty
  submitted answer as incorrect with zero movement.
- The race answer endpoint accepts an answer string, and the repository saves
  competitive answers in `answer_index` order. Repeating an identical answer
  at an already-saved index returns its saved response; a different answer at
  that index is rejected.
- Competitive results require eight saved answers. Therefore, a timeout must
  be submitted once through this same answer endpoint before result submission;
  it must not be represented only in client state.
- Training is a separate untimed flow and must not use competitive timeout
  behavior.
- The existing race specification pauses the game clock when the browser tab
  loses focus; the new problem timer follows the same pause/resume behavior.

### Math generation

- Browser gameplay generates problems locally; the backend also generates and
  validates reference problems. Their seeded operation/operand rules must
  remain equivalent.
- `TierConfig` currently has one shared minimum/maximum operand range. Keep
  tier 6's parent-configured behavior intact and use small operation-specific
  range rules for tiers 3–5 rather than broadening the saved Tier 6 schema.
- Existing exact division chooses a positive integer multiplier that can be
  one. Requiring a quotient of at least two excludes self-division while
  retaining exact results. This applies to every tier that includes division,
  including parent-configured Tier 6.
- Tier 6 accepts parent ranges from 1 through 100. If the selected range cannot
  contain an allowed divisor `b` and dividend `b × q` with `q >= 2`, reject the
  configuration when saved or before race start rather than falling back to
  self-division or silently removing division.

### Championship result handoff

- The Results page submits the race result, records its championship race in a
  second request, then fetches progression. A failure after the first request
  can leave the race persisted while championship standings remain unchanged.
- Existing tests cover page-level success/error behavior, and backend tests cover
  standings/completion. The precise reported failure is not yet isolated.
- Reproduce the ordered API flow with persisted state before modifying domain
  behavior. The correction must preserve retry safety if the race result was
  saved but championship recording or the final progression read failed.

### Avatars and audio settings

- Race setup already knows the selected avatar, while track lanes currently
  render abstract markers. The existing avatar list is scoped to the active
  child, and no app-wide catalog endpoint exists. Use the selected avatar for
  the player, and add an authenticated catalog that exposes only active portrait
  URLs for published avatars for opponents. Use a presentation-only fallback
  where needed; do not expose account, child-profile, name, or other profile
  data.
- Settings already persist separate `settings.musicVolume` and
  `settings.sfxVolume` values. SFX reads its preference when playing; active
  music listens for a `storage` event, but same-page Settings updates do not
  currently notify it.
- Settings defaults are music 70% / SFX 80%; audio-hook fallbacks use 100% for
  music. Align these defaults and notify active music after same-page changes.

## Decisions

### Decision: Store the race timer as a browser preference and snapshot per race

- **Decision**: Use a validated 10–60 second value in 5-second increments, with
  30 seconds as default. Read it at competitive race setup and keep that value
  for the full race. Pause/resume it with the existing race clock when the tab
  loses/gains focus. Training remains untimed.
- **Rationale**: This matches the clarified user requirement, fits existing
  device-level settings, and avoids adding account endpoints or schema fields
  for a presentation/gameplay preference.
- **Alternatives considered**: Server-synchronized preference would add API and
  persistence complexity without an established requirement. Changing the
  active race when Settings changes would make rounds inconsistent. Letting the
  timer run while the tab is hidden would contradict the existing race-clock
  behavior.

### Decision: Submit timeouts as empty answers using the existing answer contract

- **Decision**: Submit `answer: ""` for the active answer index once when the
  timer expires. Use the normal answer endpoint and response to progress the
  race.
- **Rationale**: The current endpoint accepts an answer string, the frontend
  engine treats empty input as incorrect with zero movement, and ordered
  persistence is required to submit the final result.
- **Alternatives considered**: A new timeout endpoint or request flag would
  duplicate answer persistence and change the public API without need.

### Decision: Apply operation-specific limits only to tiers 3–5

- **Decision**: Keep tier and seed semantics. Make tiers 3–5 generate the
  operand patterns in the feature specification. Exclude quotient one in every
  tier that includes division, including Tier 6; reject Tier 6 ranges that
  cannot produce a valid quotient greater than one. Mirror exact rules in
  TypeScript and Python.
- **Rationale**: This corrects the mental-arithmetic balance without changing
  the parent-configured Tier 6 contract or adding a generic configuration
  abstraction for a single feature.
- **Alternatives considered**: Expanding `TierConfig` to multiple ranges would
  require schema/API changes. Silently omitting division for an invalid Tier 6
  range would contradict the parent's selected operation set; keeping quotient
  one would violate the requested global limit.

### Decision: Diagnose before changing championship persistence

- **Decision**: Add regression coverage for the exact frontend/backend handoff
  and only change the failing layer after reproducing it.
- **Rationale**: The current page performs multiple sequential requests, while
  the domain service already has result and completion coverage. The failure
  may be request ordering, recovery, or persistence rather than the standings
  calculation itself.
- **Alternatives considered**: Rewriting championship domain logic without
  evidence risks breaking working idempotency and award behavior.

### Decision: Reuse current avatar and audio presentation surfaces

- **Decision**: Use the selected player portrait and portraits from an
  authenticated, app-wide published-avatar catalog for opponents; the catalog
  response contains only active portrait URLs. Otherwise use a distinct
  fallback. Retain the existing Settings music/SFX sliders and make changes
  update active music immediately.
- **Rationale**: A global catalog endpoint does not exist, so one is needed.
  Limiting its response to published portrait URLs avoids exposing child or
  account metadata while matching the selected opponent-image behavior.
- **Alternatives considered**: Fetching private portraits from other child
  profiles would introduce a privacy and authorization risk. Generating new
  assets or adding duplicate volume controls would increase scope without
  improving the requested behavior.

## Resolved Unknowns

- Backend runtime floor is Python 3.12; frontend TypeScript dependency is
  `^5.4.0`.
- No new API schema, database table, migration, runtime dependency, or service is
  needed for race timing or audio settings.
- Championship regression must exercise real ordered requests and persisted
  state; exact failing layer remains a discovery task for implementation.
