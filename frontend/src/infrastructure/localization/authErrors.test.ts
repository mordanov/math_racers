import { describe, expect, it } from 'vitest';
import { APIError } from '../api-client';
import { getAuthErrorMessage } from './authErrors';

describe('getAuthErrorMessage', () => {
  it('localizes CSRF origin rejections with the specific recovery message', () => {
    expect(
      getAuthErrorMessage(new APIError(403, { error_code: 'CSRF_ORIGIN_REJECTED' }), 'Log In'),
    ).toBe('This request could not be verified. Refresh the page and try again.');
  });

  it('does not expose HTTP status details for credential errors', () => {
    expect(
      getAuthErrorMessage(
        new APIError(401, {}),
        'Something went wrong. Please try again.',
        'The sign-in details are incorrect or the account is not approved yet.',
      ),
    ).toBe('The sign-in details are incorrect or the account is not approved yet.');
  });
});
