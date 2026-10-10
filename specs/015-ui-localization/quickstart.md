# Quickstart: UI Localization

## Automated checks

From `frontend/`:

```bash
pnpm vitest run src/infrastructure/localization/LocaleContext.test.tsx
pnpm typecheck
pnpm lint
pnpm build
```

Run the broader frontend suite after the focused checks:

```bash
pnpm test
```

## Manual acceptance checks

1. Clear the app's saved language preference and visit with browser language set to Russian, English, Spanish, and an unsupported locale. Verify supported locales are selected and unsupported locales fall back to Russian.
2. On every route, verify the selector stays visible and keyboard accessible.
3. Switch between all three languages on login, registration, authenticated pages, and while a race is in progress. Verify immediate updates without route changes, page reloads, lost form input, or race interruption.
4. Check dialogs, toasts, loading/empty states, validation feedback, API errors, dynamic labels, and assistive-technology names in each language.
5. Reload after choosing a language and verify it is restored.
6. Verify the root document `lang` value changes with the selected language.
