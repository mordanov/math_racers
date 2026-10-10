# Race and Child Data Contracts

All paths use the `/api/v1/` prefix. Authenticated requests use the parent
access token and an `X-Child-Profile-Id` header for child-scoped operations.
The server validates that the profile belongs to the authenticated parent.
Parent administration uses explicit profile IDs and parent-only permission
checks.

## Create a race session

`POST /api/v1/races`

```json
{
  "mode": "quick",
  "difficulty_tier": 2,
  "avatar_id": "uuid",
  "opponent_count": 3,
  "championship_id": null
}
```

Success response:

```json
{
  "race_id": "uuid",
  "seed": 1234567890
}
```

The server stores the child profile and selected human avatar with the session.
The request does not accept Tier 6 settings. The server loads the saved settings
for the authenticated parent account when the selected tier is 6. A parent can
read and save those settings with `GET` and `PATCH
/api/v1/players/{account_id}/tier-6-settings`.

## Submit each answer

`POST /api/v1/races/{race_id}/answers`

```json
{
  "answer_index": 0,
  "operation": "multiplication",
  "answer": "12"
}
```

Answers must arrive in order. The server checks the operation and answer
against the saved race seed. It records the answer and server time. The
response contains the answer index, correctness, and server-measured response
time. An exact retry returns the saved response. A different answer at an
already used index returns a conflict.

## Submit a race result

`POST /api/v1/races/{race_id}/results`

```json
{
  "idempotency_key": "uuid",
  "human_avatar_id": "uuid",
  "participants": [
    {
      "avatar_id": "uuid",
      "position": 2
    }
  ]
}
```

The server confirms that `human_avatar_id` matches the session. It ignores any
client-supplied XP, answer correctness, participant statistics, or AI results.
For competitive modes, the server uses the saved answers and timings to derive
participant statistics and AI positions. It uses server timestamps for race
start and completion. A repeated key returns the original response without
reprocessing XP, statistics, or achievements. For offline Training only, the
result can include the queued answers and their local response times. The
server still checks each answer against the saved seed before it accepts the
result.

The result belongs to the child and human avatar stored on the race session.
The server does not identify the human by list order, rank, or a client-selected
winner. The first successful submission saves the result and all resulting
progress changes in one transaction. A retry with the same key and payload
returns the saved response. A second, different payload for a completed race
returns a conflict and changes no data.

## Legacy data assignment

`GET /api/v1/child-profiles/{profile_id}/legacy-data`

Returns unassigned records for the selected profile's parent. Each record has
`record_type`, `record_id`, and `label`. Supported record types are `avatar`,
`avatar_stats`, `achievement`, `race`, `statistics`, `xp_event`, and
`championship`, and `progression`. Assigning a progression record adds its XP
to the selected child's progression once. A repeated or conflicting assignment
does not apply XP again.

`POST /api/v1/child-profiles/{profile_id}/legacy-data/assign`

```json
{
  "records": [
    {
      "record_type": "avatar",
      "record_id": "uuid"
    }
  ]
}
```

The server verifies that the profile belongs to the parent and that every
record is unassigned and owned by that parent. The operation is atomic. A
record cannot have more than one child owner.

The migration leaves existing account-owned records unassigned. Child-facing
queries do not return those records until the parent assigns them. The parent
must choose a child for each returned record or defined record group; the
server does not infer or divide ownership.

`GET /api/v1/child-profiles/{profile_id}/export` returns the selected child's
JSON data. `DELETE /api/v1/child-profiles/{profile_id}` deletes the profile and
its child-owned data after the parent confirms the action.

## CSRF

`GET /api/v1/auth/csrf` sets the CSRF cookie before the first state change.
Every `POST`, `PUT`, `PATCH`, and `DELETE` request must include the same token
in the `X-CSRF-Token` header and the `csrf_token` cookie. The server also
requires an allowed `Origin`. Missing or invalid values return a structured
403 error.

Login, registration, and avatar generation use shared rate limits. Limits
must work across backend workers and must not rely on process-local memory.
