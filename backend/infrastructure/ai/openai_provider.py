from __future__ import annotations

import base64
import json
from typing import Any, cast

from infrastructure.config import get_config


class OpenAIAvatarGenerationProvider:
    image_model_version = "gpt-image-1"

    async def generate_metadata(self, prompt: str) -> dict[str, Any]:
        from openai import AsyncOpenAI

        cfg = get_config()
        client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY.get_secret_value())
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a creative writer for a children's educational game. "
                        "Generate a positive, age-appropriate character profile as JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
        )
        raw = response.choices[0].message.content
        if raw is None:
            raise ValueError("AI provider returned empty character metadata.")
        return dict(json.loads(raw))

    async def generate_image(self, prompt: str) -> bytes:
        from openai import AsyncOpenAI

        cfg = get_config()
        client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY.get_secret_value())
        response = await client.images.generate(
            model=self.image_model_version,
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="high",  # type: ignore[arg-type]  # GPT Image supports high quality.
        )
        data = response.data or []
        encoded = data[0].b64_json if data else None
        if not encoded:
            raise ValueError("AI image provider returned no image.")
        return base64.b64decode(encoded)

    async def validate_child_safety(self, image_bytes: bytes) -> dict[str, bool]:
        from openai import AsyncOpenAI

        cfg = get_config()
        client = AsyncOpenAI(api_key=cfg.OPENAI_API_KEY.get_secret_value())
        encoded = base64.b64encode(image_bytes).decode("ascii")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Review this image for a children's educational game. "
                        "Return JSON booleans for safe, single_character, full_body, "
                        "no_text, and no_watermark. Set a value to true only when the "
                        "image clearly passes that check. If uncertain, set false."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{encoded}"},
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Image safety service returned an empty response.")
        checks = json.loads(content)
        required = {"safe", "single_character", "full_body", "no_text", "no_watermark"}
        if set(checks) != required or any(type(checks[key]) is not bool for key in required):
            raise ValueError("Image safety service returned an invalid result.")
        return cast(dict[str, bool], checks)
