# Math Generation and Tier 6 Settings Contract

This feature changes validation and generated values on existing mathematics
and race APIs; it adds no request fields or endpoints.

## Tier 3–5 generation

The frontend and backend generators use the same deterministic rules for the
same tier and seed:

- Tier 3 multiplication uses a two-digit multiplicand and one-digit
  multiplier.
- Tier 4 division is exact, uses a one-digit divisor, and has a quotient
  greater than one. The existing maximum dividend remains 25.
- Tier 5 addition uses two two-digit operands; multiplication follows Tier 3
  operand widths; division uses a two-digit dividend, one-digit divisor, and
  exact quotient greater than one.
- Division with quotient one is excluded from every tier that includes
  division.

## Tier 6 custom settings

Existing endpoints remain:

- `GET /api/v1/players/{player_id}/tier-6-settings`
- `PATCH /api/v1/players/{player_id}/tier-6-settings`

The existing `operations`, `min_operand`, and `max_operand` fields are
unchanged. When `division` is selected, the configured range must permit at
least one divisor `b` and dividend `b × q` within the range, for an integer
`q >= 2`. Reject a saved settings update or race-session configuration that
cannot satisfy this rule (HTTP 422); do not remove division silently or emit a
self-division problem.

The UI validates the same constraint before allowing Tier 6 settings to be
saved or a race to start. Valid configurations remain deterministic and retain
the parent's selected operations and operand bounds.
