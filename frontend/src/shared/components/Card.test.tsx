import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { Card } from './Card';

it('renders children', () => {
  render(<Card>Hello</Card>);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});

it('renders as a div by default', () => {
  render(<Card data-testid="c">Content</Card>);
  expect(screen.getByTestId('c').tagName).toBe('DIV');
});

it('calls onClick when clicked and is interactive', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<Card onClick={onClick}>Click me</Card>);
  await user.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalledOnce();
});

it('renders as button when onClick is provided', () => {
  render(<Card onClick={vi.fn()}>Clickable</Card>);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
