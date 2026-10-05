const tokens = {
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  radius: {
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  animation: {
    micro: '100ms',
    quick: '150ms',
    standard: '250ms',
    expressive: '400ms',
  },
  color: {
    primary: '#4A90D9',
    primaryHover: '#3A7BC8',
    primaryActive: '#2E6AAD',
    success: '#5CB85C',
    warning: '#F0AD4E',
    error: '#D9534F',
    focus: '#60A5FA',
    background: '#FEFAF3',
    surface: '#FFFFFF',
    textPrimary: '#1E1B18',
    textSecondary: '#6B6560',
    textOnPrimary: '#FFFFFF',
    border: '#E8E2D9',
    shadow: 'rgba(0,0,0,0.08)',
  },
  shadow: {
    card: '0 4px 16px rgba(0,0,0,0.08)',
    cardHover: '0 8px 24px rgba(0,0,0,0.12)',
    overlay: '0 16px 48px rgba(0,0,0,0.2)',
  },
  touchTarget: 44,
} as const;

export default tokens;
