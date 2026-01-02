import json
from datetime import datetime
from typing import Any, Optional

from openai import OpenAI

SCHEMA_PROMPT = """Du bist ein Extraktionsassistent. Antworte nur mit JSON, das dem vorgegebenen Schema entspricht."""


class LLMExtractor:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def extract(self, text: str, schema: dict[str, Any]) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": SCHEMA_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object", "schema": schema},
        )
        content = response.output_parsed or {}
        if not content:
            content = json.loads(response.output_text)
        return content


def parse_date(value: Optional[str]) -> Optional[datetime.date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None
