# Research: UI Localization

## Decision

Use a small typed React context with three in-bundle catalogs rather than adding an internationalization framework. Derive the supported locale from an explicit saved choice or, on first use, the browser language; persist manual selections in `localStorage`; update the root document `lang` attribute on locale changes. Use one catalog key type for every language and test catalog parity.

## Rationale

The frontend currently uses React 18, TypeScript strict mode, Vite, and Vitest, with no existing localization package. The requested scope is three fixed UI languages, immediate client-side switching, persistence, and full static-message coverage. A typed context meets that scope with fewer dependencies and lets strict TypeScript catch incomplete catalogs. Browser locale detection, local preference storage, and document language are available through standard web APIs.

## Alternatives Considered

- **i18next + react-i18next + browser language detector**: provides established hooks, language detection, and fallback features, but has more runtime dependencies and configuration than the fixed three-catalog requirement needs. Reconsider if locale count, plural rules, translation management, or server-side rendering grows.
- **Unstructured component literals**: cannot support changing languages or reliable coverage checks.

## References

- MDN, [`Navigator.language`](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language): browser language preference source.
- MDN, [HTML `lang` global attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/lang): document language metadata used by browsers and assistive technologies.
- TypeScript strict mode and `Record` types support exhaustive catalog key checking at compile time; this is a project-level type-safety decision, not a library recommendation.
