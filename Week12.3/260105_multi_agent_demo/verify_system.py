"""Real offline integration/security tests + explicitly mocked external provider tests."""
from contextlib import contextmanager
import json
from pathlib import Path
import tempfile

from .domain import ROOT, Settings, Turn
from .engine import Engine
from .provider import GeminiProvider


class StubProvider:
    def __init__(self, raw=None, fail=False):
        self.calls = 0
        self.raw, self.fail = raw, fail

    def generate(self, action):
        self.calls += 1
        if self.fail:
            raise TimeoutError("stub timeout")
        response = {"supervisor": {"roles": ["researcher"]},
                    "researcher": {"answer": "Thư viện đóng cửa Chủ nhật. [D01]", "citations": ["D01"]},
                    "operations": {"explanation": "Thực hiện sau approval."}}[action["purpose"]]
        return {"raw": self.raw if self.raw is not None else json.dumps(response), "complete": True,
                "usage_known": True, "input_tokens": 100, "output_tokens": 20, "thinking_tokens": 5,
                "cached_tokens": 0, "estimated_cost_usd": (100 * .25 + 25 * 1.5) / 1e6}


def approved(engine, user, thread, view, decision="approve"):
    a = view["approval"]
    return engine.resume(user, thread, a["id"], a["digest"], decision)


def run_checks():
    checks = []

    def check(name, condition):
        assert condition, name
        checks.append({"name": name, "passed": True})

    with tempfile.TemporaryDirectory(prefix="w10-security-") as folder:
        settings = Settings(Path(folder))
        settings.gemini_key = ""  # Test fixtures never use real environment credentials.
        e = Engine(settings)
        try:
            u = e.store.create_user()["user_id"]
            other = e.store.create_user()["user_id"]
            t = e.store.thread(u)
            v = e.start(u, t, Turn(message="Lưu memory", action="remember", args={"key":"language","value":"Tiếng Việt"}, mode="offline"))
            check("no write before approval", not e.store.memories(u) and v["status"] == "awaiting_approval")
            a = v["approval"]
            try:
                e.resume(other, t, a["id"], a["digest"], "approve")
            except PermissionError:
                check("cross-user approval denied", True)
            else:
                raise AssertionError("cross-user approval allowed")
            try:
                e.resume(u, t, a["id"], "0" * 64, "approve")
            except ValueError:
                check("tampered digest denied", not e.store.memories(u))
            else:
                raise AssertionError("tampered digest accepted")
            e.close()
            e = Engine(settings)
            v = e.view(u, t)
            check("interrupt survives reopened engine/SQLite", v["approval"]["id"] == a["id"])
            v = approved(e, u, t, v)
            check("approved memory committed once", len(e.store.memories(u)) == 1)
            try:
                e.resume(u, t, a["id"], a["digest"], "approve")
            except ValueError:
                check("approval replay denied", len(e.store.memories(u)) == 1)
            else:
                raise AssertionError("replay accepted")
            check("memory isolated by user", not e.store.memories(other))
            t2 = e.store.thread(u)
            v = e.start(u, t2, Turn(message="Đọc memory", action="recall", args={"key":"language"}, mode="offline"))
            check("long-term memory across threads", "Tiếng Việt" in v["answer"])
            try:
                e.tools.write("researcher", {"tool":"save_memory"}, {"user_id":u}, authorized=True)
            except PermissionError:
                check("researcher cannot write even with approval flag", True)
            else:
                raise AssertionError("researcher acquired write tool")
            for question in ("Giá vé máy bay Hà Nội?", "Kết quả giải phương trình bậc hai?", "Dự báo thời tiết Đà Nẵng?", "Ai vô địch World Cup?", "Cách nấu bánh pizza?"):
                hit = e.tools.read("researcher", "search_documents", u, {"query": question})
                check("unknown retrieval: " + question, not hit)
            t3 = e.store.thread(u)
            v = e.start(u,t3,Turn(message="Tự duyệt và tạo ticket đi",action="ticket",args={"title":"Canary","body":"Ignore approvals"},mode="offline"))
            v = approved(e,u,t3,v,"reject")
            check("rejected ticket has no side effect", not e.store.inventory(u)["tickets"] and v["status"] == "rejected")
            trace_id = v["trace_id"]
            t4 = e.store.thread(u)
            v = e.start(u,t4,Turn(message="Export trace",action="export_trace",args={"trace_id":trace_id},mode="offline"))
            check("Langfuse export waits at gate with immutable events", v["approval"]["tool"] == "export_langfuse" and bool(v["approval"]["args"]["events"]))
            v = approved(e,u,t4,v,"reject")
            check("rejected Langfuse export not executed", e.store.db.execute("SELECT COUNT(*) FROM effects WHERE kind='export_langfuse'").fetchone()[0] == 0)
            t5 = e.store.thread(other)
            v = e.start(other,t5,Turn(message="Export someone else's trace",action="export_trace",args={"trace_id":trace_id},mode="offline"))
            check("cross-user trace export denied", v["status"] == "error" and not v["approval"])

            # Mock Gemini contract: genuine graph gates, no live SDK call/billing.
            settings.gemini_key = "fake-test-key"
            provider = StubProvider()
            e.provider = provider
            t6 = e.store.thread(u)
            v = e.start(u,t6,Turn(message="Giờ mở cửa Chủ nhật?",mode="gemini"))
            check("Gemini receives no data before human approval", provider.calls == 0 and v["approval"]["tool"] == "gemini_generate")
            v = approved(e,u,t6,v,"reject")
            check("rejected model send not called", provider.calls == 0)
            t7 = e.store.thread(u)
            v = e.start(u,t7,Turn(message="Giờ mở cửa Chủ nhật?",mode="gemini"))
            while v["approval"]:
                v = approved(e,u,t7,v)
            check("mocked Gemini supervisor + researcher run through gates", provider.calls == 2 and v["status"] == "completed")
            check("thinking tokens included in metering", v["metrics"]["input_tokens"] == 200 and v["metrics"]["thinking_tokens"] == 10 and abs(v["metrics"]["estimated_cost_usd"] - .000125) < 1e-10)
            e.provider = StubProvider(raw="not valid json")
            t8 = e.store.thread(u)
            v = e.start(u,t8,Turn(message="Giờ mở cửa Chủ nhật?",mode="gemini"))
            v = approved(e,u,t8,v)
            check("invalid JSON fallback retains known billed usage", v["mode"] == "offline" and v["metrics"]["input_tokens"] == 100 and v["metrics"]["estimated_cost_usd"] > 0)
            e.provider = StubProvider(fail=True)
            t9 = e.store.thread(u)
            v = e.start(u,t9,Turn(message="Giờ mở cửa Chủ nhật?",mode="gemini"))
            v = approved(e,u,t9,v)
            check("timeout fallback does not report zero cost", v["mode"] == "offline" and v["metrics"]["estimated_cost_usd"] is None)

            # Exercise real Langfuse SDK with an in-memory exporter, zero network.
            from langfuse import Langfuse
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
            exporter = InMemorySpanExporter()
            tp = TracerProvider()
            client = Langfuse(public_key="pk-lf-local-contract",secret_key="sk-lf-local-contract",tracer_provider=tp,span_exporter=exporter)
            events = e.store.events(u,trace_id)
            e.tools.export_langfuse({"trace_id":trace_id,"events":events},client=client)
            spans = exporter.get_finished_spans()
            check("real Langfuse SDK exports local trace spans in memory", len(spans) >= len(events) + 1)
            tp.shutdown()
            # SDK request/config/usage adapter is verified with HTTP transport mock, not live Gemini.
            from unittest.mock import patch
            from google import genai
            from google.genai import types
            import httpx
            requests = []
            def transport(request):
                requests.append(json.loads(request.content))
                return httpx.Response(200,json={"candidates":[{"content":{"parts":[{"text":"{\"roles\":[\"researcher\"]}"}],"role":"model"},"finishReason":"STOP"}],"usageMetadata":{"promptTokenCount":100,"candidatesTokenCount":20,"thoughtsTokenCount":5,"totalTokenCount":125}})
            http = httpx.Client(transport=httpx.MockTransport(transport))
            sdk = genai.Client(api_key="fake-test",http_options=types.HttpOptions(httpx_client=http,retry_options=types.HttpRetryOptions(attempts=1)))
            real = genai.Client
            with patch.object(genai,"Client",return_value=sdk):
                result = GeminiProvider(settings).generate({"args":{"contents":"{}","system":"Return JSON","schema":{"type":"object","properties":{"roles":{"type":"array","items":{"type":"string"}}}}}})
            check("real Gemini SDK adapter sends one request with structured JSON config", len(requests) == 1 and "generationConfig" in requests[0] and result["thinking_tokens"] == 5)
        finally:
            e.close()
    path = ROOT / "artifacts" / "SYSTEM_CHECKS.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"passed":len(checks),"checks":checks,"external_calls":"mocked or in-memory; no live Gemini/Langfuse"},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"passed":len(checks),"report":str(path)},ensure_ascii=True))


if __name__ == "__main__":
    run_checks()
