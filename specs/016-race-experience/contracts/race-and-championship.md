# Race and Championship Contracts

This feature does not add or version a public API. It uses the existing
versioned race and championship endpoints.

## Competitive answer submission

`POST /api/v1/races/{race_id}/answers`

Submit every competitive answer in ascending `answer_index` order, including
timeouts, before posting race results.

```json
{
  "answer_index": 0,
  "operation": "multiplication",
  "answer": ""
}
```

An empty answer string is the canonical persisted timeout marker. The server
responds with the answer index, `is_correct: false`, and server-measured
response time. The same request retried at the same index is idempotent; a
different answer at an already occupied index is rejected. A competitive
result requires eight saved answers.

## Race result submission

`POST /api/v1/races/{race_id}/results`

Submit the existing result payload after all eight answers have been saved.
Result submission remains idempotent by its existing idempotency key and does
not include a new timer field.

## Championship race recording

`PATCH /api/v1/championships/{championship_id}/races/{race_id}`

After the race result is persisted, record the same race and participant
positions in the championship. Retrying the sequence after a later request
fails must not duplicate points or awards. Recording the final scheduled race
must leave the championship in its existing completed state.

## Local preference contracts

- `settings.problemTimeLimitSeconds`: integer 10–60 inclusive, step 5,
  default 30; captured at timed race start.
- `settings.musicVolume` and `settings.sfxVolume`: independent integer
  percentages 0–100; default 70 and 80 respectively.
- The Training mode does not consume the problem time-limit setting.
- The problem timer pauses/resumes with the existing race clock while the tab
  is unfocused.
- Opponent portrait URLs come only from the shared published-avatar catalog;
  private child-profile portraits are not exposed.
- `GET /api/v1/avatars/catalog` requires authentication but not an active-child
  header. It returns only `{ "portrait_url": "..." }` entries for published
  avatars with an active portrait; it exposes no avatar, account, or child
  profile identifiers.
