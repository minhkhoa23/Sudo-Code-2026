import json


class GeminiProvider:
    def __init__(self, settings):
        self.settings = settings

    def generate(self, action):
        """Only called by the approved executor; no automatic tool execution/retries."""
        from google import genai
        from google.genai import types
        if not self.settings.gemini_key:
            raise ValueError("Gemini API key is not configured")
        client = genai.Client(api_key=self.settings.gemini_key,
                              http_options=types.HttpOptions(timeout=30_000, retry_options=types.HttpRetryOptions(attempts=1)))
        try:
            response = client.models.generate_content(
                model=action["args"].get("model", self.settings.model),
                contents=action["args"]["contents"],
                config=types.GenerateContentConfig(
                    system_instruction=action["args"]["system"], temperature=0, max_output_tokens=900,
                    response_mime_type="application/json", response_json_schema=action["args"]["schema"],
                    thinking_config=types.ThinkingConfig(thinking_level="minimal"),
                    automatic_continuation=False,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
            text = response.text or ""
            usage = response.usage_metadata
            candidate = response.candidates[0] if response.candidates else None
            # Meter usage before parsing JSON: invalid JSON can still be billable.
            data = {"raw": text, "complete": bool(candidate and candidate.finish_reason == types.FinishReason.STOP), "usage_known": usage is not None,
                    "input_tokens": int(getattr(usage, "prompt_token_count", 0) or 0),
                    "output_tokens": int(getattr(usage, "candidates_token_count", 0) or 0),
                    "thinking_tokens": int(getattr(usage, "thoughts_token_count", 0) or 0),
                    "cached_tokens": int(getattr(usage, "cached_content_token_count", 0) or 0)}
            data["estimated_cost_usd"] = (
                data["input_tokens"] * self.settings.input_price
                + (data["output_tokens"] + data["thinking_tokens"]) * self.settings.output_price
            ) / 1_000_000
            return data
        finally:
            client.close()
