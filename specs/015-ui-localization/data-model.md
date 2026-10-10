# Data Model: UI Localization

## Locale

Represents the active interface language.

| Field | Type | Rules |
|---|---|---|
| `code` | `ru` \| `en` \| `es` | Only supported codes are accepted. Browser tags such as `es-MX` normalize to their supported base language. |

## Language Preference

Represents the user's explicit choice on the current browser.

| Field | Type | Rules |
|---|---|---|
| `locale` | Supported locale code | A valid stored value takes precedence over browser detection. Invalid or absent values are ignored. |
| `source` | `saved` \| `browser` \| `fallback` | Saved values are written only after an explicit user selection. |

Initial selection order:

1. Valid explicit preference stored for the app.
2. First supported browser language, normalized to `ru`, `en`, or `es`.
3. Russian fallback.

## Message Catalog

An application-authored interface message identified by a stable key and carrying equivalent text in all supported locales.

Validation rules:

- All three catalogs have exactly the same message keys.
- Values are non-empty strings.
- Runtime interpolation values are data, not message keys; user-authored names remain unchanged.

No backend entity, database migration, or API schema change is required.
