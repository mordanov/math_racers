import { APIError } from '../api-client';
import type { TranslationKey } from './catalogs';

export function getAuthErrorMessage(
  error: unknown,
  fallback: TranslationKey,
  credentialsFallback?: TranslationKey,
): TranslationKey {
  if (error instanceof APIError) {
    const body =
      typeof error.body === 'object' && error.body !== null
        ? (error.body as Record<string, unknown>)
        : {};
    if (body.error_code === 'CSRF_ORIGIN_REJECTED') {
      return 'This request could not be verified. Refresh the page and try again.';
    }
    if ((error.status === 401 || error.status === 403) && credentialsFallback) {
      return credentialsFallback;
    }
  }
  return fallback;
}
