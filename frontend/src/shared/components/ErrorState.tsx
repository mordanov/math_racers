import { APIError } from '../../infrastructure/api-client';
import tokens from '../tokens';
import { Button } from './Button';
import { useLocale } from '../../infrastructure/localization/LocaleContext';
import type { TranslationKey } from '../../infrastructure/localization/catalogs';

export function getChildFriendlyMessage(error: Error): TranslationKey {
  if (error instanceof APIError) {
    const body =
      typeof error.body === 'object' && error.body !== null
        ? (error.body as Record<string, unknown>)
        : {};
    if (body.error_code === 'CSRF_ORIGIN_REJECTED') {
      return 'This request could not be verified. Refresh the page and try again.';
    }
    if (error.status === 404) return 'We couldn’t find that. Let’s go back!';
    if (error.status === 401 || error.status === 403) return 'Please log in again.';
    return 'Something went wrong. Let’s try again!';
  }
  return 'Oops! Check your internet connection and try again.';
}

interface ErrorStateProps {
  error: Error | null;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const { t } = useLocale();
  const message = error ? getChildFriendlyMessage(error) : 'Something went wrong.';

  return (
    <div
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: tokens.spacing.md,
        padding: tokens.spacing.xl,
        color: tokens.color.textPrimary,
        textAlign: 'center',
      }}
    >
      <span style={{ fontSize: 32 }} aria-hidden="true">
        😕
      </span>
      <p style={{ fontSize: 18, margin: 0 }}>{t(message)}</p>
      {onRetry && (
        <Button variant="primary" onClick={onRetry}>
          {t('Try Again')}
        </Button>
      )}
    </div>
  );
}
