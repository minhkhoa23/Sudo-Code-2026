"""Run real LangGraph cases; offline default. Gemini mode asks a human at EVERY gate."""
import argparse
import csv
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import statistics
from time import perf_counter

from .domain import ROOT, Settings, Turn
from .engine import Engine


def run_eval(mode="offline"):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    destination = ROOT / "artifacts" / "evals" / stamp
    destination.mkdir(parents=True)
    settings = Settings(destination / "state")
    if mode == "gemini" and not settings.gemini_key:
        raise ValueError("Gemini eval needs a configured API key; no relabelled offline scores")
    engine = Engine(settings)
    cases = json.loads((ROOT / "data" / "eval_cases.json").read_text(encoding="utf-8"))
    rows, outputs, all_traces = [], [], []
    try:
        for case in cases:
            started = perf_counter()
            user = engine.store.create_user()["user_id"]
            thread = engine.store.thread(user)
            view, error = None, None
            try:
                kind = case["type"]
                action = {"memory": "remember", "compound": "research_ticket"}.get(kind, kind)
                if kind in ("qa", "unknown", "followup"):
                    action = "ask"
                view = engine.start(user, thread, Turn(message=case["message"], action=action, args=case.get("args", {}), mode=mode))
                if kind == "followup":
                    while view["approval"]:
                        a = view["approval"]
                        answer = input(f"Review {json.dumps(a, ensure_ascii=False)}\nType approve/reject: ")
                        view = engine.resume(user, thread, a["id"], a["digest"], answer)
                    # Force close/reopen engine: checkpoint is read from disk, not an in-memory variable.
                    engine.close()
                    engine = Engine(settings)
                    restored = engine.view(user, thread)
                    assert len(restored["history"]) == 1
                    view = engine.start(user, thread, Turn(message=case["followup"], mode=mode))
                while view["approval"]:
                    a = view["approval"]
                    before = engine.store.inventory(user)
                    assert not before["memories"] and not before["tickets"] and not before["outbox"], "A tool wrote before approval"
                    if a["tool"] == "gemini_generate":
                        # Never batch-autoapprove external sends, even when invoked from eval.
                        decision = input(f"\n{json.dumps(a, ensure_ascii=False, indent=2)}\nApprove Gemini send? Type approve/reject: ").strip()
                    else:
                        decision = case.get("decision", "approve")  # Scripted fixture decisions in an isolated local test DB.
                    view = engine.resume(user, thread, a["id"], a["digest"], decision)
                passed = True
                if kind in ("qa", "followup"):
                    passed = case["contains"].lower() in view["answer"].lower() and case["doc"] in {d["doc_id"] for d in view["sources"]}
                elif kind == "unknown":
                    passed = not view["sources"] and "chưa có thông tin" in view["answer"]
                elif kind == "fee":
                    passed = f"= {case['expected']} đồng" in view["answer"]
                elif kind == "memory":
                    expected = 1 if case["decision"] == "approve" else 0
                    passed = len(engine.store.memories(user)) == expected
                    engine.close()
                    engine = Engine(settings)
                    next_thread = engine.store.thread(user)
                    # Actual long-term memory survives a new graph/thread/connection.
                    memory = engine.store.memories(user)
                    passed = passed and len(memory) == expected
                    if expected:
                        recall = engine.start(user, next_thread, Turn(message="Đọc ngôn ngữ đã lưu", action="recall", args={"key": "language"}, mode="offline"))
                        passed = passed and case["args"]["value"] in recall["answer"]
                elif kind in ("ticket", "compound"):
                    passed = len(engine.store.inventory(user)["tickets"]) == (case["decision"] == "approve")
                    if kind == "compound":
                        roles = {event["data"].get("node") for event in engine.store.events(user, view["trace_id"]) if event["kind"] == "node_end"}
                        passed = passed and {"researcher", "operations", "supervisor"}.issubset(roles)
                        if case.get("expected_doc"):
                            passed = passed and case["expected_doc"] in {source["doc_id"] for source in view["sources"]}
                elif kind == "email":
                    box = engine.store.inventory(user)["outbox"]
                    passed = len(box) == 1 and box[0]["recipient"].endswith(".example") and "local_draft_only" in view["answer"]
                passed = bool(passed and view["status"] == ("rejected" if case.get("decision") == "reject" else "completed"))
            except Exception as exc:
                passed, error = False, type(exc).__name__
            case_events = []
            for trace in engine.store.traces(user):
                case_events.extend(engine.store.events(user, trace["trace_id"]))
            all_traces.extend(case_events)
            usage = [event["data"] for event in case_events if event["kind"] == "llm_usage"]
            unknown_cost = any(event["kind"] == "run_end" and event["data"]["metrics"]["estimated_cost_usd"] is None for event in case_events)
            unknown_cost = unknown_cost or any(not item["usage_known"] for item in usage) or error is not None
            metrics = {
                "steps": sum(event["kind"] == "node_end" for event in case_events),
                "input_tokens": sum(item["input_tokens"] for item in usage),
                "output_tokens": sum(item["output_tokens"] for item in usage),
                "thinking_tokens": sum(item["thinking_tokens"] for item in usage),
                "estimated_cost_usd": None if unknown_cost else sum(item["estimated_cost_usd"] for item in usage),
            }
            rows.append({"id": case["id"], "type": case["type"], "passed": passed, "requested_mode": mode,
                         "effective_mode": view["mode"] if view else "error", "steps": metrics.get("steps", 0),
                         "latency_ms": round((perf_counter() - started) * 1000, 3),
                         "input_tokens": metrics.get("input_tokens", 0), "output_tokens": metrics.get("output_tokens", 0),
                         "thinking_tokens": metrics.get("thinking_tokens", 0), "estimated_cost_usd": metrics.get("estimated_cost_usd"),
                         "trace_id": view["trace_id"] if view else "", "error": error})
            outputs.append({"case": case, "result": view, "error": error})
    finally:
        engine.close()
    summary = {"mode": mode, "cases": len(rows), "passed": sum(r["passed"] for r in rows),
               "success_rate": sum(r["passed"] for r in rows) / len(rows),
               "avg_steps": statistics.mean(r["steps"] for r in rows),
               "avg_latency_ms": statistics.mean(r["latency_ms"] for r in rows),
               "avg_cost_per_run_usd": statistics.mean(r["estimated_cost_usd"] for r in rows) if all(r["estimated_cost_usd"] is not None for r in rows) else None,
               "total_input_tokens": sum(r["input_tokens"] for r in rows),
               "total_output_tokens": sum(r["output_tokens"] for r in rows),
               "total_thinking_tokens": sum(r["thinking_tokens"] for r in rows),
               "python_packages": {n: importlib.metadata.version(n) for n in ("langgraph", "langgraph-checkpoint-sqlite", "langfuse", "google-genai", "fastapi")}}
    (destination / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (destination / "outputs.json").write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    (destination / "traces.jsonl").write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in all_traces) + "\n", encoding="utf-8")
    with (destination / "results.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    table = "\n".join(f"| {r['id']} | {r['type']} | {'PASS' if r['passed'] else 'FAIL'} | {r['steps']} | {r['estimated_cost_usd']} |" for r in rows)
    report = f"""# Eval report — Multi-agent Library

Run UTC: {stamp}. Mode: **{mode}**. Kết quả chạy LangGraph thật, không dùng số liệu minh họa.

| Scenarios | Success rate | Avg steps / scenario | Avg token cost / scenario (USD) |
|---:|---:|---:|---:|
| {len(rows)} | {summary['success_rate']:.2%} | {summary['avg_steps']:.2f} | {summary['avg_cost_per_run_usd']} |

Input tokens: {summary['total_input_tokens']}; output: {summary['total_output_tokens']}; thinking: {summary['total_thinking_tokens']}.

Offline là planner bằng code và trích đoạn tài liệu, không phải chất lượng suy luận của Gemini. Cost 0 chỉ nghĩa không có LLM call; không bao gồm hạ tầng. Gemini eval chưa chạy nếu report ghi offline. Không có chứng cứ trace đã được gửi lên Langfuse Cloud.

Mỗi case là một scenario; steps và token cost cộng tất cả lượt của scenario, gồm lượt dựng ngữ cảnh/recall. Số đo được tính từ event log thực tế. `outputs.json` và `traces.jsonl` giữ bằng chứng. Steps đếm node hoàn tất (gồm supervisor/tool gate), không đếm lần interrupt chưa hoàn tất. Thời gian gồm setup/kiểm tra; offline không chèn thời gian chờ con người, còn Gemini có tính thời gian chờ người duyệt.

QA chấm bằng nguồn mong đợi + một thông tin literal có trong câu trả lời, chưa đánh giá đầy đủ tính đúng/ngắn gọn. Offline trả trích đoạn, không dùng làm benchmark so sánh các LLM. Tool case kiểm tra DB trước/sau và trạng thái duyệt; compound kiểm tra cả hai specialist trong trace. Đây là bộ hồi quy nhỏ, chưa chứng minh an toàn trước mọi prompt injection.

Các case đã được dùng trong quá trình phát triển và điều chỉnh retrieval; chưa có bộ chất lượng held-out. Không trình bày success rate này như khả năng tổng quát hóa ngoài bộ hồi quy.

Giá Gemini chỉ là ước tính từ usage metadata, gồm thinking tokens ở output, dùng rate trong `.env`; cached input hiện tính theo giá input thường (có thể cao hơn bill). Nếu request lỗi không có usage, cost là unknown, không tự coi là 0. Không bao gồm phí Langfuse hoặc hạ tầng. Xem [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing).

| Case | Nhóm | Kết quả | Steps | Ước tính USD |
|---|---|---|---:|---:|
{table}

Chi tiết: `results.csv`, `outputs.json`, `summary.json`, `traces.jsonl` cạnh report này. Decision ghi/gửi local trong eval offline là fixture lập trình sẵn; GUI/API vẫn yêu cầu duyệt từng hành động. Bản chạy Gemini hỏi người dùng trong terminal trước từng lần gửi model.
"""
    (destination / "REPORT.md").write_text(report, encoding="utf-8")
    (ROOT / "EVAL_REPORT.md").write_text(report + f"\nArtifact directory: `{destination.relative_to(ROOT).as_posix()}`\n", encoding="utf-8")
    print(json.dumps({**summary, "artifacts": str(destination)}, ensure_ascii=True, indent=2))
    return rows, destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["offline", "gemini"], default="offline")
    args = parser.parse_args()
    rows, _ = run_eval(args.mode)
    raise SystemExit(0 if all(row["passed"] for row in rows) else 1)
