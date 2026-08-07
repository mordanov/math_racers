# AI Architecture

**Level:** Specification
**Status:** Authoritative
**Source:** documentation/ADR/ADR-003.md; GDD Chapter 12 §28–29
**Parent:** [Epic E4 — Content Pipeline](../content/epic.md)
**See also:** [asset-pipeline.md](asset-pipeline.md), [../prompts/gpt-image-prompts.md](../prompts/gpt-image-prompts.md)

---

## Core Philosophy

> **AI generates assets. The game consumes assets.**

AI is infrastructure, not gameplay. The application's business logic must remain completely independent of any specific AI provider.

If AI services become temporarily unavailable, gameplay continues unaffected.

---

## Provider Abstraction

All AI provider interactions are hidden behind stable interfaces:

```python
class ImageGenerationProvider(Protocol):
    async def generate(self, prompt: str, params: GenerationParams) -> GeneratedImage: ...

class LLMProvider(Protocol):
    async def complete(self, system: str, user: str, schema: dict) -> dict: ...
```

**Current adapters:**
- `OpenAIImageAdapter` → GPT Image API
- `OpenAILLMAdapter` → OpenAI Chat Completions API

Swapping providers requires only a new adapter class. No business logic changes.

---

## Prompt Builder

The Prompt Builder is the single path to any generation prompt.

Rules:
- Receives structured metadata as input.
- Applies the Global Prefix and Global Negative Prompt automatically.
- Performs template variable substitution.
- Produces a versioned prompt record.
- Returns identical output given identical inputs (deterministic).

```python
class PromptBuilder:
    def build_character_prompt(self, metadata: AvatarMetadata) -> VersionedPrompt: ...
    def build_badge_prompt(self, achievement: Achievement) -> VersionedPrompt: ...
    # ... one method per asset category
```

**Forbidden:** the frontend calling any AI provider directly. The frontend never constructs or handles prompts.

---

## Async Generation Pipeline

Generation jobs are enqueued and processed by background workers:

```
API Request → Job Queue (Redis) → Background Worker → Storage → Notification
```

This pattern:
- Prevents API timeouts on long-running generations.
- Enables retry without user intervention.
- Decouples the web API from the AI provider.
- Allows multiple concurrent jobs.

---

## Asset Validation

Every generated asset passes the validation gates defined in [asset-pipeline.md](asset-pipeline.md) before being stored or published.

Validation is independent of the provider — it operates on the generated binary, not on the generation API.

---

## Retry Strategy

```
Attempt 1 → Standard generation
   ↓ (on failure)
Attempt 2 → Simplified prompt
   ↓ (on failure)
Attempt 3 → Alternative parameters
   ↓ (on failure)
Escalate → Log + user notification
```

Retry state is stored in the job record. Escalated failures are visible in the observability dashboard.

---

## Versioning

Every generation record stores:

| Field | Description |
|-------|-------------|
| `prompt_version` | Template version (e.g. `1.0.3`) |
| `model_version` | Provider model identifier |
| `generation_date` | ISO 8601 timestamp |
| `provider` | Provider identifier (e.g. `openai`) |

Prompt version changes trigger a review of existing assets for consistency.

---

## Security

- API keys are server-side only; never exposed to the client.
- All user inputs are sanitised before reaching the Prompt Builder.
- Rate limiting is enforced at the API layer before jobs are enqueued.
- Generated content undergoes content-safety validation before storage.

---

## Future Provider Support

The abstraction supports adding alternative providers with no changes to business logic:

- Alternative image generation models
- Self-hosted LLMs
- Specialised audio or animation generators

Provider selection can be controlled by feature flag or configuration without code changes.
