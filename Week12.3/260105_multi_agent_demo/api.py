from contextlib import asynccontextmanager
import json
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import Field, ValidationError

from .domain import ROOT, Settings, StrictModel, Turn
from .engine import Engine
from .storage import canonical


class Decision(StrictModel):
    action_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    decision: Literal["approve", "reject"]


def create_app(settings: Settings | None = None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.engine = Engine(settings)
        try:
            yield
        finally:
            app.state.engine.close()

    app = FastAPI(title="Week 10 Multi-agent Library Demo", version="1.0.0", lifespan=lifespan)

    @app.exception_handler(PermissionError)
    async def permission_error(request, error):
        return Response(json.dumps({"detail": "Không có quyền truy cập tài nguyên này."}), 403, media_type="application/json")

    @app.exception_handler(ValueError)
    async def value_error(request, error):
        # Validation messages never contain raw provider errors or API keys.
        detail = "Tham số không hợp lệ." if isinstance(error, ValidationError) else str(error)
        return Response(json.dumps({"detail": detail}, ensure_ascii=False), 409, media_type="application/json")

    def engine(request: Request):
        return request.app.state.engine

    def actor(authorization: str = Header(default=""), e: Engine = Depends(engine)):
        if not authorization.startswith("Bearer "):
            raise HTTPException(401, "Cần demo session token")
        with e.lock:
            return e.store.authenticate(authorization[7:])

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(ROOT / "static" / "index.html")

    @app.get("/health")
    def health(e: Engine = Depends(engine)):
        return {"status": "ok", "gemini_configured": bool(e.settings.gemini_key),
                "langfuse_configured": bool(e.settings.lf_public and e.settings.lf_secret),
                "model": e.settings.model, "specialists": ["researcher", "operations"],
                "tools": ["search_documents", "read_memory", "calculate_late_fee", "save_memory", "create_ticket", "stage_email", "export_langfuse"],
                "email_delivery": "local_outbox_only", "tracing": "local; Langfuse export requires approval"}

    @app.post("/api/session")
    def session(e: Engine = Depends(engine)):
        with e.lock:
            return e.store.create_user()

    @app.post("/api/threads")
    def new_thread(user: str = Depends(actor), e: Engine = Depends(engine)):
        with e.lock:
            return {"thread_id": e.store.thread(user)}

    @app.get("/api/threads/{thread_id}")
    def state(thread_id: str, user: str = Depends(actor), e: Engine = Depends(engine)):
        return e.view(user, thread_id)

    @app.post("/api/threads/{thread_id}/turn")
    def turn(thread_id: str, payload: Turn, user: str = Depends(actor), e: Engine = Depends(engine)):
        return e.start(user, thread_id, payload)

    @app.post("/api/threads/{thread_id}/approval")
    def approve(thread_id: str, payload: Decision, user: str = Depends(actor), e: Engine = Depends(engine)):
        return e.resume(user, thread_id, payload.action_id, payload.digest, payload.decision)

    @app.get("/api/inventory")
    def inventory(user: str = Depends(actor), e: Engine = Depends(engine)):
        with e.lock:
            return e.store.inventory(user)

    @app.get("/api/traces")
    def traces(user: str = Depends(actor), e: Engine = Depends(engine)):
        with e.lock:
            return e.store.traces(user)

    @app.get("/api/traces/{trace_id}")
    def trace(trace_id: str, user: str = Depends(actor), e: Engine = Depends(engine)):
        with e.lock:
            events = e.store.events(user, trace_id)
        if not events:
            raise HTTPException(404, "Không có trace thuộc session này")
        return {"trace_id": trace_id, "events": events}

    @app.get("/api/traces/{trace_id}/download")
    def download(trace_id: str, user: str = Depends(actor), e: Engine = Depends(engine)):
        data = trace(trace_id, user, e)
        text = "\n".join(canonical(event) for event in data["events"]) + "\n"
        return Response(text, media_type="application/x-ndjson", headers={"Content-Disposition": 'attachment; filename="trace.jsonl"'})

    return app


app = create_app()
