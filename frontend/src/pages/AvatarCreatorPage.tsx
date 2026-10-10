import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAvatar, pollGenerationJob } from '../engine/avatar/avatarApi';
import type { CreateAvatarRequest } from '../engine/avatar/types';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import { useOffline } from '../shared/hooks/useOffline';
import { useLocale } from '../infrastructure/localization/LocaleContext';
import type { TranslationKey } from '../infrastructure/localization/catalogs';
import tokens from '../shared/tokens';

const SPECIES = ['fox', 'rabbit', 'bear', 'cat', 'mouse', 'panda'] as const;
const HAIRSTYLES = ['short', 'long', 'curly', 'braided'] as const;
const ACCESSORIES_OPTIONS = ['headband', 'glasses', 'hat', 'scarf'] as const;
const FUR_COLORS = ['#D2691E', '#F4A460', '#8B4513', '#FFFDD0', '#808080', '#1C1C1C'];
const EYE_COLORS = ['#4B0082', '#228B22', '#0000CD', '#8B0000', '#FF8C00', '#A9A9A9'];
const CLOTHES_COLORS = [
  '#4169E1',
  '#DC143C',
  '#228B22',
  '#FF8C00',
  '#800080',
  '#FFD700',
  '#FFFFFF',
  '#1C1C1C',
];

const TERMINAL_STATUSES = new Set(['complete', 'failed', 'permanent_failure']);

interface WizardState {
  step: 1 | 2 | 3 | 4 | 5;
  species: string;
  furColor: string;
  eyeColor: string;
  hairstyle: string;
  accessories: string[];
  topColor: string;
  bottomColor: string;
}

function ColorSwatch({
  color,
  selected,
  onSelect,
  label,
}: {
  color: string;
  selected: boolean;
  onSelect: (c: string) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-pressed={selected}
      onClick={() => onSelect(color)}
      style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        background: color,
        border: selected ? `3px solid ${tokens.color.primary}` : `2px solid ${tokens.color.border}`,
        cursor: 'pointer',
        outline: 'none',
      }}
      onFocus={(e) => {
        (e.currentTarget as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
      }}
      onBlur={(e) => {
        (e.currentTarget as HTMLElement).style.outline = 'none';
      }}
    />
  );
}

export default function AvatarCreatorPage() {
  const navigate = useNavigate();
  const { t } = useLocale();
  const isOffline = useOffline();
  const [wizard, setWizard] = useState<WizardState>({
    step: 1,
    species: '',
    furColor: FUR_COLORS[0],
    eyeColor: EYE_COLORS[0],
    hairstyle: 'short',
    accessories: [],
    topColor: CLOTHES_COLORS[0],
    bottomColor: CLOTHES_COLORS[7],
  });
  const [genError, setGenError] = useState<TranslationKey | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const set = <K extends keyof WizardState>(key: K, val: WizardState[K]) =>
    setWizard((w) => ({ ...w, [key]: val }));

  const next = () => setWizard((w) => ({ ...w, step: (w.step + 1) as WizardState['step'] }));
  const back = () => setWizard((w) => ({ ...w, step: (w.step - 1) as WizardState['step'] }));

  const toggleAccessory = (acc: string) =>
    setWizard((w) => ({
      ...w,
      accessories: w.accessories.includes(acc)
        ? w.accessories.filter((a) => a !== acc)
        : [...w.accessories, acc],
    }));

  const startGeneration = useCallback(async () => {
    setIsGenerating(true);
    setGenError(null);
    try {
      const req: CreateAvatarRequest = {
        species: wizard.species || 'fox',
        fur_color: wizard.furColor,
        eye_color: wizard.eyeColor,
        hairstyle: wizard.hairstyle,
        accessories: wizard.accessories,
        clothes_top_color: wizard.topColor,
        clothes_bottom_color: wizard.bottomColor,
      };
      const { avatar_id, job_id } = await createAvatar(req);

      pollRef.current = setInterval(() => {
        void (async () => {
          try {
            const job = await pollGenerationJob(avatar_id, job_id);
            if (job.status === 'complete') {
              if (pollRef.current) clearInterval(pollRef.current);
              void navigate('/avatars');
            } else if (TERMINAL_STATUSES.has(job.status)) {
              if (pollRef.current) clearInterval(pollRef.current);
              setIsGenerating(false);
              setGenError('Hmm, something went wobbly.');
            }
          } catch {
            if (pollRef.current) clearInterval(pollRef.current);
            setIsGenerating(false);
            setGenError('Looks like we lost the signal. Check your connection!');
          }
        })();
      }, 3000);
    } catch {
      setIsGenerating(false);
      setGenError('Hmm, something went wobbly.');
    }
  }, [wizard, navigate]);

  useEffect(() => {
    if (wizard.step === 5) {
      void startGeneration();
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [wizard.step]);

  const containerStyle: React.CSSProperties = {
    maxWidth: 480,
    margin: '0 auto',
    padding: tokens.spacing.xl,
  };

  const headingStyle: React.CSSProperties = {
    color: tokens.color.textPrimary,
    marginBottom: tokens.spacing.lg,
  };

  const navStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: tokens.spacing.xl,
  };

  const choiceButtonStyle = (selected: boolean): React.CSSProperties => ({
    padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
    borderRadius: tokens.radius.md,
    border: selected ? `2px solid ${tokens.color.primary}` : `2px solid ${tokens.color.border}`,
    background: selected ? tokens.color.primary : tokens.color.surface,
    color: selected ? tokens.color.textOnPrimary : tokens.color.textPrimary,
    cursor: 'pointer',
    fontWeight: 600,
    textTransform: 'capitalize' as const,
  });

  if (isOffline) {
    return (
      <div
        data-testid="page-avatar-creator"
        role="alert"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.lg,
          padding: tokens.spacing.xl,
          textAlign: 'center',
        }}
      >
        <p style={{ fontSize: 20, color: tokens.color.textPrimary }}>
          {t('Internet required to create avatars.')}
        </p>
        <Button variant="secondary" onClick={() => void navigate(-1)}>
          {t('Go Back')}
        </Button>
      </div>
    );
  }

  if (wizard.step === 1) {
    return (
      <div data-testid="page-avatar-creator" style={containerStyle}>
        <h1 style={headingStyle}>{t('Choose Your Animal')}</h1>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: tokens.spacing.sm }}>
          {SPECIES.map((sp) => (
            <button
              key={sp}
              type="button"
              aria-pressed={wizard.species === sp}
              onClick={() => set('species', sp)}
              style={choiceButtonStyle(wizard.species === sp)}
            >
              {t(sp)}
            </button>
          ))}
        </div>
        <div style={navStyle}>
          <span />
          <Button variant="primary" disabled={!wizard.species} onClick={next}>
            {t('Next')}
          </Button>
        </div>
      </div>
    );
  }

  if (wizard.step === 2) {
    return (
      <div style={containerStyle}>
        <h1 style={headingStyle}>{t('Choose Colours')}</h1>
        <p style={{ color: tokens.color.textSecondary }}>{t('Fur colour')}</p>
        <div
          style={{
            display: 'flex',
            gap: tokens.spacing.sm,
            flexWrap: 'wrap',
            marginBottom: tokens.spacing.md,
          }}
        >
          {FUR_COLORS.map((c) => (
            <ColorSwatch
              key={c}
              color={c}
              selected={wizard.furColor === c}
              onSelect={(v) => set('furColor', v)}
              label={t('Fur colour {{color}}', { color: c })}
            />
          ))}
        </div>
        <p style={{ color: tokens.color.textSecondary }}>{t('Eye colour')}</p>
        <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
          {EYE_COLORS.map((c) => (
            <ColorSwatch
              key={c}
              color={c}
              selected={wizard.eyeColor === c}
              onSelect={(v) => set('eyeColor', v)}
              label={t('Eye colour {{color}}', { color: c })}
            />
          ))}
        </div>
        <div style={navStyle}>
          <Button variant="secondary" onClick={back}>
            {t('Back')}
          </Button>
          <Button variant="primary" onClick={next}>
            {t('Next')}
          </Button>
        </div>
      </div>
    );
  }

  if (wizard.step === 3) {
    return (
      <div style={containerStyle}>
        <h1 style={headingStyle}>{t('Choose Your Style')}</h1>
        <p style={{ color: tokens.color.textSecondary }}>{t('Hairstyle')}</p>
        <div
          style={{
            display: 'flex',
            gap: tokens.spacing.sm,
            flexWrap: 'wrap',
            marginBottom: tokens.spacing.md,
          }}
        >
          {HAIRSTYLES.map((h) => (
            <button
              key={h}
              type="button"
              aria-pressed={wizard.hairstyle === h}
              onClick={() => set('hairstyle', h)}
              style={choiceButtonStyle(wizard.hairstyle === h)}
            >
              {t(h)}
            </button>
          ))}
        </div>
        <p style={{ color: tokens.color.textSecondary }}>{t('Accessories (optional)')}</p>
        <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
          {ACCESSORIES_OPTIONS.map((acc) => (
            <button
              key={acc}
              type="button"
              aria-pressed={wizard.accessories.includes(acc)}
              onClick={() => toggleAccessory(acc)}
              style={choiceButtonStyle(wizard.accessories.includes(acc))}
            >
              {t(acc)}
            </button>
          ))}
        </div>
        <div style={navStyle}>
          <Button variant="secondary" onClick={back}>
            {t('Back')}
          </Button>
          <Button variant="primary" onClick={next}>
            {t('Next')}
          </Button>
        </div>
      </div>
    );
  }

  if (wizard.step === 4) {
    return (
      <div style={containerStyle}>
        <h1 style={headingStyle}>{t('Choose Clothing')}</h1>
        <p style={{ color: tokens.color.textSecondary }}>{t('Top colour')}</p>
        <div
          style={{
            display: 'flex',
            gap: tokens.spacing.sm,
            flexWrap: 'wrap',
            marginBottom: tokens.spacing.md,
          }}
        >
          {CLOTHES_COLORS.map((c) => (
            <ColorSwatch
              key={c}
              color={c}
              selected={wizard.topColor === c}
              onSelect={(v) => set('topColor', v)}
              label={t('Top colour {{color}}', { color: c })}
            />
          ))}
        </div>
        <p style={{ color: tokens.color.textSecondary }}>{t('Shorts colour')}</p>
        <div style={{ display: 'flex', gap: tokens.spacing.sm, flexWrap: 'wrap' }}>
          {CLOTHES_COLORS.map((c) => (
            <ColorSwatch
              key={c}
              color={c}
              selected={wizard.bottomColor === c}
              onSelect={(v) => set('bottomColor', v)}
              label={t('Shorts colour {{color}}', { color: c })}
            />
          ))}
        </div>
        <div style={navStyle}>
          <Button variant="secondary" onClick={back}>
            {t('Back')}
          </Button>
          <Button variant="primary" onClick={next}>
            {t('Next')}
          </Button>
        </div>
      </div>
    );
  }

  // Step 5: Reveal / generation
  if (genError) {
    return (
      <div style={containerStyle}>
        <p style={{ color: tokens.color.error }}>{t(genError)}</p>
        <div style={navStyle}>
          <Button variant="secondary" onClick={back}>
            {t('Back')}
          </Button>
          <Button
            variant="primary"
            onClick={() => {
              setGenError(null);
              void startGeneration();
            }}
          >
            {t('Try Again')}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ ...containerStyle, textAlign: 'center' }}>
      <h1 style={headingStyle}>{t('Creating Your Avatar…')}</h1>
      <LoadingSpinner />
      <img
        src="/artwork/avatar_generation.jpeg"
        alt=""
        aria-hidden="true"
        style={{
          width: 240,
          borderRadius: tokens.radius.lg,
          objectFit: 'cover',
          display: 'block',
          margin: '0 auto',
        }}
      />
      {isGenerating && (
        <p style={{ color: tokens.color.textSecondary, marginTop: tokens.spacing.md }}>
          {t('Our AI artist is painting your character. This takes about 20 seconds.')}
        </p>
      )}
    </div>
  );
}
