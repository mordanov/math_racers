# Data Model: Race Experience Improvements

No database entities or migrations are introduced by this feature. Existing
race, answer, result, championship, avatar, and audio-preference records remain
authoritative.

## Client race timing preference

| Field | Type | Rule |
|---|---|---|
| `settings.problemTimeLimitSeconds` | integer | One of 10, 15, …, 60; default 30 when missing or invalid. |

The preference is read when a competitive race is configured and copied into
that race's in-memory configuration. Updating the saved value does not change
the active race. The countdown pauses/resumes with the existing race clock when
the browser tab loses/gains focus. Training has no effective time limit.

## Race answer and timeout

| Existing field | Type | Timeout value |
|---|---|---|
| `answer_index` | integer | Current obstacle index, 0–7 |
| `operation` | operation enum | Operation shown for the problem |
| `answer` | string | Empty string (`""`) |
| `is_correct` | server result | `false` |
| `response_time_ms` | integer | Elapsed time when the timeout is handled |

The answer must be persisted in sequence using the existing answer API. An
empty answer string is the canonical persisted timeout marker; no new timeout
field is introduced. An identical retry at the same index returns the saved
answer; an answer with different contents at an occupied index remains a
conflict.

## Generated math problem

Existing `Problem` fields and seed remain unchanged. Tier-specific generation
constraints:

| Tier/operation | Operand constraint |
|---|---|
| 3 / multiplication | Two-digit multiplicand and one-digit multiplier |
| 4 / division | Exact division; one-digit divisor; quotient greater than one |
| 5 / addition | Two two-digit operands |
| 5 / multiplication | Same operand widths as tier 3 |
| 5 / division | Same exactness, divisor width, and quotient rule as tier 4 |

All generated division problems in every tier have quotient at least two; the
self-division frequency is therefore zero. Tier 6 keeps parent-selected
operations and ranges, but a range that includes division must support at
least one exact `dividend = divisor × quotient` with quotient greater than one;
otherwise the configuration is rejected before the race starts. Repeated
`(tier, seed, count)` inputs continue to produce identical problem ordering in
both generators.

## Championship

The existing championship state, scheduled race index, persisted race summary,
and standings are unchanged. Recording a race must remain retry-safe and advance
completion only once. A final race transitions the existing championship state
to completed; there is no new completion record.

## Racer presentation

Each participant has the existing race identity/progress plus a presentation
portrait URL when available. The player uses the selected avatar portrait;
opponents use a portrait from the shared published-avatar catalog or a distinct
built-in fallback. Private child-profile portraits are not used for opponents.
The authenticated catalog returns only active portrait URLs for published
avatars; it does not return avatar names, ownership identifiers, or profile
fields.
The portrait URL and animation state are presentation-only and are not stored
in race results.

## Audio preferences

Existing `settings.musicVolume` and `settings.sfxVolume` values remain
independent integer percentages from 0 through 100. Their Settings defaults
remain 70 and 80 respectively. Active music is refreshed after a music setting
change; effects continue to read the SFX preference when played.
