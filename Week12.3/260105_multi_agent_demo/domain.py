from pathlib import Path
import os
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, field_validator


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=False)
# No automatic LangSmith callbacks/network telemetry; Langfuse is an approved tool.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


class Settings:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = Path(data_dir or os.getenv("DEMO_DATA_DIR") or ROOT / "runtime").resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.input_price = float(os.getenv("INPUT_USD_PER_MILLION", "0.25"))
        self.output_price = float(os.getenv("OUTPUT_USD_PER_MILLION", "1.5"))
        if self.input_price < 0 or self.output_price < 0:
            raise ValueError("Token prices must be nonnegative")
        self.lf_public = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.lf_secret = os.getenv("LANGFUSE_SECRET_KEY", "")
        self.lf_url = os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Turn(StrictModel):
    message: str = Field(min_length=1, max_length=3000)
    action: Literal["ask", "fee", "remember", "recall", "ticket", "email", "research_ticket", "export_trace"] = "ask"
    args: dict[str, Any] = Field(default_factory=dict)
    mode: Literal["auto", "offline", "gemini"] = "auto"

    @field_validator("message")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("Message must not be blank")
        return value.strip()


class FeeArgs(StrictModel):
    books: int = Field(strict=True, ge=1, le=10)
    days: int = Field(strict=True, ge=0, le=365)


class MemoryArgs(StrictModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")
    value: str = Field(min_length=1, max_length=500)


class RecallArgs(StrictModel):
    key: str = Field(default="", pattern=r"^[a-z0-9_]{0,40}$")


class TicketArgs(StrictModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=1000)


class EmailArgs(StrictModel):
    # Demo only stages an email in local DB. No SMTP or external mail delivery.
    to: Literal["hotro@binhminh.example"] = "hotro@binhminh.example"
    subject: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=1000)


class ExportArgs(StrictModel):
    trace_id: str = Field(pattern=r"^[0-9a-f]{32}$")


ARG_SCHEMAS = {"fee": FeeArgs, "remember": MemoryArgs, "recall": RecallArgs,
               "ticket": TicketArgs, "research_ticket": TicketArgs, "email": EmailArgs,
               "export_trace": ExportArgs}


def validate_args(turn: Turn) -> dict:
    if turn.action == "ask":
        if turn.args:
            raise ValueError("ask does not accept tool arguments")
        return {}
    return ARG_SCHEMAS[turn.action].model_validate(turn.args).model_dump()
