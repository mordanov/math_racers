# What Needs External Implementation

**Status:** Reference — assets and services that Claude Code cannot produce alone
**Date:** 2026-10-05
**Context:** Code is the easy part. Every item below requires a human decision, a creative
tool, a third-party service, or a real-money expenditure. Each section describes what is
needed, why it matters, and exactly how to produce it.

---

## 1. Game Artwork (Images)

The avatar portraits are generated at runtime by the AI pipeline — no manual work needed
for those. All *static* game artwork must be created once and committed to the repo.

### 1.1 Stadium / Race Track Background

**What:** One wide illustration used as the background of the Race Screen.
**Specs:** PNG, 2560×720px (crops gracefully to 1920×720 and 1280×720), transparent sky
strip at top so the runner track sits cleanly on it. No people in the image.
**Style:** See `docs/art/image-generation-standards.md` and `docs/art/visual-language.md`.
**Where used:** `Race Screen` behind the horizontal runner track.

**GPT Image prompt** (use the template from `docs/prompts/gpt-image-prompts.md`):

```
A premium stylized 3D animated illustration for a modern children's educational game.
Warm, cheerful, colorful, rounded shapes, expressive character design, feature-film
quality, soft global illumination, vibrant harmonious colors, family-friendly, highly
readable, polished, timeless visual style, original artwork, not based on any existing
franchise.

A colorful athletics stadium for children. A straight running track with 8 lane
markers. Green grass on both sides. Rounded trees in the background. Blue sunny sky.
Colorful banners and bunting. Happy crowd silhouettes in the far background. Wide
panoramic composition. Very horizontal layout. Highly detailed but visually calm.
Bright primary colors. Stadium lights off — daylight scene.

No text, no letters, no numbers, no logos, no watermark, no signature, no frame,
no border, no extra characters, no people in the foreground, no weapons, no violence,
no horror, no realistic anatomy, no photorealism, no anime, no comic book style,
no low-quality rendering, no blur.
```

**Tool:** GPT Image (gpt-image-1), 1792×1024 → upscale / crop to 2560×720.
**Variants needed:** 1 (one fixed stadium for v1.0; seasonal variants in v1.5).

---

### 1.2 Achievement Badge Icons

**What:** One distinct icon image per achievement, displayed in the AchievementToast and
the Achievements gallery page.
**Count:** 8 initial achievements (`first_race`, `perfect_race`, `podium_finisher`,
`champion`, `level_5`, `level_10`, `level_20`, `hidden_speedster`).
**Specs:** PNG, 256×256px, transparent background, circular badge shape with enamel
pin style (per `docs/art/image-generation-standards.md`).

**GPT Image prompt template per badge** (fill in `{{theme}}`):

```
A premium stylized 3D animated illustration for a modern children's educational game.
Warm, cheerful, colorful, rounded shapes, feature-film quality, soft global
illumination, vibrant harmonious colors, family-friendly, polished, timeless style,
original artwork.

A collectible achievement badge for a children's racing game. Circular enamel pin
style. Rounded border in gold. Subject: {{theme}}. Bright flat enamel colors.
Premium quality. Slight 3D depth. Very clean design. Transparent background.

No text, no letters, no numbers, no logos, no watermark, no border frame,
no photo-realism, no blur.
```

**Theme per badge:**

| Key | `{{theme}}` |
|-----|------------|
| `first_race` | A running shoe leaving a starting block, motion blur on the sole |
| `perfect_race` | A golden star with eight points, each tipped with a sparkle |
| `podium_finisher` | A three-step podium in gold, silver, bronze, small trophy on top |
| `champion` | A laurel wreath crown, golden, with a tiny trophy centered |
| `level_5` | The number five rendered as a gem-cut shape, ruby red |
| `level_10` | A stylised "10" gem, sapphire blue, double the size of level_5 |
| `level_20` | A diamond-cut "20", emerald green, large and glowing |
| `hidden_speedster` | A lightning bolt wrapped in a question mark, silver |

**Tool:** GPT Image (gpt-image-1). Generate each at 1024×1024; crop to 256×256 circle.

---

### 1.3 Main Menu Illustration

**What:** Hero illustration for the Home / Main Menu page.
**Specs:** PNG, 1920×900px, transparent elements acceptable.

**GPT Image prompt:**

```
A premium stylized 3D animated illustration for a modern children's educational game.
Warm, cheerful, colorful, rounded shapes, expressive character design, feature-film
quality, soft global illumination, vibrant harmonious colors, family-friendly, highly
readable, polished, timeless visual style, original artwork.

A joyful children's athletics festival. Several unique animal runners (fox, rabbit,
bear, cat, mouse) in colorful sports outfits warming up at a large colorful stadium.
Bright morning light. Soft clouds. Friendly, welcoming atmosphere. Highly cinematic
composition. Wide landscape format. Dynamic energy.

No text, no letters, no numbers, no logos, no watermark, no frame, no border,
no realistic anatomy, no photorealism, no anime, no horror, no weapons.
```

**Tool:** GPT Image (gpt-image-1), 1792×1024 → crop/scale.

---

### 1.4 Empty-State Illustration (Avatar Gallery)

**What:** Friendly illustration shown when a child has no avatars yet.
**Specs:** PNG, 512×400px, transparent background.

**GPT Image prompt:**

```
A premium stylized 3D animated illustration for a modern children's educational game.
Warm, cheerful, colorful, rounded shapes, feature-film quality, vibrant colors,
family-friendly, polished.

A friendly open picture frame with a big "+" sign in the centre, surrounded by
colorful sparkles and stars. Inviting and exciting. Warm pastel colors. As if
inviting a child to create something magical. Transparent background.

No text, no letters, no numbers, no logos, no watermark, no characters,
no photorealism, no blur.
```

---

### 1.5 Loading / Placeholder Screens

**What:** 2–3 landscape illustrations for loading screens (shown while assets load).
**Specs:** PNG, 1280×720px each.

**GPT Image prompt (one of three):**

```
A premium stylized 3D animated illustration for a modern children's educational game.
Warm, cheerful, colorful, rounded shapes, feature-film quality, vibrant colors.

Animal children practicing mathematics problems before a fun race. Playful stadium
environment. Joyful atmosphere. Numbers floating in the air. Lots of movement and
energy. Warm sunlight. Landscape composition.

No text, no letters, no numbers on paper, no logos, no photorealism, no horror.
```

Generate three variants by changing the animals and activities in the prompt.

---

## 2. Audio Assets

The audio engine code is buildable by Claude Code (see `claude-code-tasks.md §9`), but it
needs real audio files. All sounds must be delivered as both **WebM/Opus** and **MP3**
(spec: `docs/engineering/audio-design.md §Technical Notes`).

Total audio bundle target: **< 10 MB** for the initial pack before lazy-loading.

### 2.1 Background Music Tracks

Four tracks corresponding to the adaptive music progression in
`docs/engineering/audio-design.md §Music`:

| Track | Mood | Duration | Loop? |
|-------|------|----------|-------|
| `music_menu.ogg` | Warm, welcoming, relaxed, orchestral-light | 60–90 s | Yes |
| `music_race.ogg` | Medium tempo, rhythmic, optimistic, highly repeatable | 60–90 s | Yes |
| `music_final_sprint.ogg` | Brighter, stronger percussion, same tempo | 30 s | Yes |
| `music_victory.ogg` | Short triumphant phrase | < 3 s | No |

**Specification:** Uplifting, playful, orchestral with light electronic elements, melodic,
memorable. Inspired by animated feature films and modern family games. Must avoid: aggressive
rock, heavy electronic, dramatic tension.

**How to produce:**
- **AI music tools:** Use Udio (udio.com) or Suno (suno.com).
- **Udio prompt (race track):**
  ```
  Uplifting children's educational game background music. Playful and energetic.
  Melodic orchestral style with light synthesizer accents. Medium tempo around 120 BPM.
  Major key. Warm brass, pizzicato strings, xylophone melody. No vocals. Loop-friendly.
  Family-friendly. Inspired by animated film soundtracks. High quality production.
  ```
- Export as WAV; convert to WebM/Opus with `ffmpeg -i input.wav -c:a libopus output.opus`
  and to MP3 with `ffmpeg -i input.wav -q:a 2 output.mp3`.
- Loop edit: ensure the last beat aligns with bar 1 for seamless looping.

---

### 2.2 Gameplay Sound Effects

Short clips, < 1 second each, bundled into a sprite for low-latency playback.

| File key | Event | Description |
|----------|-------|-------------|
| `sfx_correct` | Correct answer | Pleasant chime + sparkle (bright, ascending notes) |
| `sfx_incorrect` | Wrong answer | Soft bounce + gentle "oops" (not a buzzer — cheerful) |
| `sfx_obstacle_jump` | Runner clears obstacle | Whoosh → soft landing |
| `sfx_obstacle_hit` | Runner hits obstacle | Boing → dust (comedic, not alarming) |
| `sfx_achievement` | Achievement unlock | Sparkle → ascending scale → short fanfare (< 2 s) |
| `sfx_levelup` | Level up | Upward glissando + sustained chord (< 2 s) |
| `sfx_countdown` | 3–2–1 ticks | Metronome tick × 3 + "GO!" accent |

**How to produce:**
- **AI SFX tools:** Use ElevenLabs Sound Effects (elevenlabs.io/sound-effects) or
  Freesound (freesound.org, CC0 licence filter).
- **ElevenLabs prompt for `sfx_correct`:**
  ```
  A bright, cheerful, short chime sound. Three ascending notes. Sparkle quality.
  Like a correct-answer reward sound in a children's game. Duration 0.5 seconds.
  High quality. No distortion.
  ```
- **ElevenLabs prompt for `sfx_incorrect`:**
  ```
  A soft, comedic bounce sound followed by a gentle "oops" tone. Cheerful, not harsh.
  Never a buzzer. Friendly mistake sound for a children's game. Duration 0.6 seconds.
  ```
- Bundle all clips into a single sprite using `audiosprite` npm package:
  `npx audiosprite sfx_*.wav --output sprite --format howler2`

---

### 2.3 UI Sound Effects

| File key | Interaction | Description |
|----------|------------|-------------|
| `ui_hover` | Button hover | Tiny pop (very subtle) |
| `ui_click` | Button click | Soft click |
| `ui_card_select` | Card selection | Paper flip |
| `ui_window_open` | Window opening | Gentle swoosh |
| `ui_window_close` | Window closing | Soft fade out |
| `ui_avatar_select` | Avatar selected | Friendly short greeting chime |

**How to produce:** Use the same ElevenLabs or Freesound workflow as 2.2.
These are all < 0.3 seconds and should be bundled into the same sprite as gameplay SFX.

---

### 2.4 Crowd Ambience

| File | Duration | Loop? |
|------|----------|-------|
| `ambience_crowd_baseline.ogg` | 30 s | Yes |
| `ambience_crowd_cheer_short.ogg` | 2 s | No (trigger on event) |
| `ambience_crowd_applause.ogg` | 3 s | No |

The baseline crowd loops continuously during a race. Short cheers trigger on leader
changes and correct answers.

**How to produce:**
- **Freesound search:** `"crowd stadium"` filtered to CC0. Pick clean, non-descript
  crowd noise without identifiable chants.
- Edit to a seamless loop in Audacity (crossfade the loop points).
- Export as WebM/Opus + MP3.

---

### 2.5 Character Voice Sounds

Short (< 0.5 s) non-verbal sound-only expressions per species. Four expressions × 5 species
= 20 clips.

| Expression | Sound concept |
|------------|--------------|
| Happy | "Yay!" (non-verbal) |
| Thinking | "Hmm…" |
| Celebrating | "Woohoo!" |
| Surprised | "Oh!" |

| Species | Pitch profile |
|---------|--------------|
| Fox | Higher pitch, bright |
| Rabbit | Medium-high, bouncy |
| Bear | Deep and warm |
| Cat | Mid-range, smooth |
| Mouse | Very high, squeaky |

**How to produce:**
- **ElevenLabs Voice Design** or **ElevenLabs Sound Effects:**
  ```
  A small cartoon fox character making a happy "yay!" non-verbal exclamation.
  High-pitched, cheerful, friendly. Duration 0.4 seconds. No words — just the
  emotional vocal sound.
  ```
- Generate one per expression per species. Name files `voice_{species}_{expression}.ogg`.

---

## 3. External API Keys and Services

### 3.1 OpenAI API (GPT Image — Avatar Generation)

**What it does:** `backend/app/avatars/generation_service.py` calls GPT Image API
(`gpt-image-1`) to generate avatar portraits from the prompt built by `PromptBuilder`.

**Setup:**
1. Create an OpenAI account and generate an API key at platform.openai.com.
2. Add `OPENAI_API_KEY=sk-...` to `.env` (already documented in `.env.example`).
3. Budget: each avatar generation costs approximately $0.02–0.08 depending on model.
   Plan for a monthly budget based on expected avatar creation volume.
4. Enable usage limits in the OpenAI dashboard to avoid runaway costs.

**Test:** Run a Quick Race → create an avatar → confirm portrait appears. If generation
fails, check `job_audit` table and worker logs for the error.

---

### 3.2 LLM API (Avatar Bio & Name Generation)

**What it does:** `GenerationService.run()` calls an LLM to produce:
- Character name (2–3 options for the child to choose from)
- Biography paragraph (2–3 sentences, child-friendly)
- Structured character appearance metadata (feeds into PromptBuilder)

**Which LLM:** The code uses whichever LLM client is configured. Claude (via Anthropic API)
is the recommended default because the prompt is already written for it in
`docs/prompts/llm-prompts.md`.

**Setup:**
1. Create an Anthropic account at console.anthropic.com.
2. Generate an API key.
3. Add `ANTHROPIC_API_KEY=sk-ant-...` to `.env`.
4. Model recommendation: `claude-haiku-4-5-20251001` — fast and cheap for structured
   character generation.

---

## 4. Production Deployment

The infrastructure code (Docker Compose, nginx, CI/CD) is complete. What's missing is a
real server and domain.

### 4.1 Server

**Recommended minimal setup for v1.0:**
- 1 VPS, 2 vCPU / 4 GB RAM (e.g. Hetzner CX22, ~€4/month)
- PostgreSQL: managed instance (Hetzner Managed Database or Supabase free tier)
- Redis: single node on the same VPS is fine for v1.0
- Object Storage (S3-compatible): Cloudflare R2 (free egress) or AWS S3

**Steps:**
1. Provision the VPS. Add SSH key.
2. Install Docker and Docker Compose.
3. Point DNS A record for your domain to the VPS IP.
4. Obtain a TLS certificate:
   ```bash
   docker run --rm -it certbot/certbot certonly \
     --standalone -d yourdomain.com --email you@example.com --agree-tos
   ```
   Place certs in the `nginx_certs` volume. See `quickstart.md §TLS Certificate Renewal`.
5. Copy `.env.example` → `.env`; fill in all secrets including API keys from §3.
6. Run `make up` — the `scripts/docker-verify.sh` confirms all services healthy.

### 4.2 Object Storage for Avatar Portraits

**What:** Generated avatar portraits (PNG + 3 thumbnail sizes) must be stored somewhere
the frontend can load them. The `GenerationService` uploads to S3-compatible storage.

**Cloudflare R2 setup (recommended — free egress):**
1. Create a Cloudflare account and navigate to R2.
2. Create a bucket named `math-racers-avatars`.
3. Create an API token with R2 read/write permissions.
4. Add to `.env`:
   ```
   S3_ENDPOINT_URL=https://<accountid>.r2.cloudflarestorage.com
   S3_BUCKET_NAME=math-racers-avatars
   S3_ACCESS_KEY_ID=...
   S3_SECRET_ACCESS_KEY=...
   S3_PUBLIC_BASE_URL=https://your-r2-custom-domain.com
   ```
5. Enable public access on the bucket (avatars are public URLs in the game).

---

## 5. Content Safety and Moderation

### 5.1 Automated Content Safety (Already Coded)

`GenerationService` already applies three quality gates (technical, artistic, content
safety) per `docs/art/image-generation-standards.md`. Forbidden content triggers an
automatic retry with a stricter prompt. After 3 failures the job is marked failed and
the child sees a friendly retry message.

**No manual action needed for the automated gate.**

### 5.2 Manual Review Queue (v1.5 Roadmap Item)

For v1.0 the automated gate is sufficient. For v1.5, implement an admin review queue:
- Admin endpoint: `GET /api/v1/admin/portraits/pending-review`
- Admin can approve or flag a portrait
- Flagged portraits are replaced with the previous version

This is an internal tool — it does not require external design work.

---

## 6. Summary Table

| Asset / Service | Tool / Vendor | Effort | Cost |
|-----------------|--------------|--------|------|
| Race track background | GPT Image | 30 min | ~$0.10 |
| Achievement badge icons (×8) | GPT Image | 1 hour | ~$0.80 |
| Main menu illustration | GPT Image | 30 min | ~$0.10 |
| Empty state illustration | GPT Image | 15 min | ~$0.05 |
| Loading screen illustrations (×3) | GPT Image | 30 min | ~$0.30 |
| Music tracks (×4) | Udio / Suno | 2 hours | Free–$10/mo |
| Gameplay SFX sprite | ElevenLabs / Freesound | 1 hour | Free–$5 |
| UI SFX sprite | ElevenLabs / Freesound | 30 min | Free |
| Crowd ambience | Freesound | 30 min | Free |
| Character voices (×20 clips) | ElevenLabs | 1 hour | ~$5 |
| OpenAI API key | OpenAI | 5 min | Pay-per-use |
| Anthropic API key | Anthropic | 5 min | Pay-per-use |
| VPS + domain | Hetzner + any registrar | 1 hour | ~€6/mo |
| Object storage | Cloudflare R2 | 30 min | Free tier |
| TLS certificate | Let's Encrypt (certbot) | 15 min | Free |

**Total one-time creative effort: ~8 hours**
**Total recurring infrastructure cost: ~€10–15/month** (excluding API usage)
