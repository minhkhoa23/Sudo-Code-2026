from collections import Counter
from hashlib import sha256
import json
import math
import re
import unicodedata

from .domain import ROOT, MemoryArgs, TicketArgs, EmailArgs, FeeArgs
from .storage import canonical, now


def tokens(text):
    # Preserve accents: giá/giả, hỏa/họa are different Vietnamese words.
    text = unicodedata.normalize("NFC", text.casefold())
    stop = {"thư", "viện", "mình", "bình", "minh", "có", "không", "là", "gì", "ở", "và", "của", "cho", "tôi", "bạn", "được", "nào", "thì", "bao", "nhiêu", "mỗi", "người", "đọc", "hỏi", "xin", "hãy", "về"}
    return [t for t in re.findall(r"\w+", text) if t not in stop and len(t) > 1]


class Tools:
    READ_PERMISSIONS = {"researcher": {"search_documents", "read_memory"},
                        "operations": {"calculate_late_fee", "read_memory"}}
    WRITE_PERMISSIONS = {"operations": {"save_memory", "create_ticket", "stage_email", "export_langfuse"}}

    def __init__(self, store, settings):
        self.store, self.settings = store, settings
        self.documents = json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))

    def read(self, role, name, user_id, args):
        if name not in self.READ_PERMISSIONS.get(role, set()):
            raise PermissionError("Tool is not allowed for this specialist")
        if name == "read_memory":
            return self.store.memories(user_id, args.get("key", ""))
        if name == "calculate_late_fee":
            a = FeeArgs.model_validate(args)
            return {"books": a.books, "days": a.days, "rate_vnd": 2000, "total_vnd": a.books * a.days * 2000, "source": "D05"}
        query = set(tokens(args["query"]))
        candidates = []
        for doc in self.documents:
            terms = Counter(tokens(doc["title"] + " " + doc["text"]))
            overlap = query & terms.keys()
            coverage = len(overlap) / max(len(query), 1)
            score = sum(math.log(1 + terms[t]) for t in overlap) / math.sqrt(max(len(terms), 1))
            if coverage >= 0.55 and score > 0:
                candidates.append({**doc, "score": round(score, 5)})
        return sorted(candidates, key=lambda d: d["score"], reverse=True)[:3]

    def write(self, role, action, state, authorized=False):
        # The executor supplies authorized only after checking checkpointed approval.
        if not authorized or action["tool"] not in self.WRITE_PERMISSIONS.get(role, set()):
            raise PermissionError("Approval and tool permission are required")
        name, args, action_id = action["tool"], action["args"], action["id"]
        user_id = state["user_id"]
        old = self.store.db.execute("SELECT * FROM effects WHERE id=? AND user_id=?", (action_id, user_id)).fetchone()
        if old:
            if old["status"] == "done":
                return json.loads(old["result"])
            raise RuntimeError("Previous external action has uncertain outcome; automatic retry disabled")
        if name == "export_langfuse":
            with self.store.db:
                self.store.db.execute("INSERT INTO effects VALUES (?,?,?,?,?)", (action_id, user_id, name, "started", "{}"))
            # Export exactly the immutable payload shown at the approval gate.
            result = self.export_langfuse(args)
            with self.store.db:
                self.store.db.execute("UPDATE effects SET status='done',result=? WHERE id=?", (canonical(result), action_id))
            return result
        # Local mutations and idempotency ledger commit together.
        with self.store.db:
            if name == "save_memory":
                a = MemoryArgs.model_validate(args)
                self.store.db.execute("INSERT INTO memories VALUES (?,?,?,?) ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value,updated=excluded.updated", (user_id, a.key, a.value, now()))
                result = {"saved": a.key, "value": a.value}
            elif name == "create_ticket":
                a = TicketArgs.model_validate(args)
                self.store.db.execute("INSERT INTO tickets VALUES (?,?,?,?)", (action_id, user_id, a.title, a.body))
                result = {"ticket_id": action_id, "title": a.title}
            elif name == "stage_email":
                a = EmailArgs.model_validate(args)
                self.store.db.execute("INSERT INTO outbox VALUES (?,?,?,?,?)", (action_id, user_id, a.to, a.subject, a.body))
                result = {"outbox_id": action_id, "recipient": a.to, "delivery": "local_draft_only"}
            else:
                raise ValueError("Unknown write tool")
            self.store.db.execute("INSERT INTO effects VALUES (?,?,?,?,?)", (action_id, user_id, name, "done", canonical(result)))
        return result

    def export_langfuse(self, payload, client=None):
        owned = client is None
        if client is None:
            if not self.settings.lf_public or not self.settings.lf_secret:
                raise ValueError("Configure Langfuse keys before exporting")
            if payload["destination"] != self.settings.lf_url or payload["project_fingerprint"] != sha256(self.settings.lf_public.encode()).hexdigest()[:12]:
                raise ValueError("Langfuse destination changed since approval; request a new approval")
            from langfuse import Langfuse
            from opentelemetry.sdk.trace import TracerProvider
            client = Langfuse(public_key=self.settings.lf_public, secret_key=self.settings.lf_secret,
                              base_url=payload["destination"], environment="week10-demo", tracer_provider=TracerProvider())
        with client.start_as_current_observation(name="approved-local-trace-export", as_type="span",
                trace_context={"trace_id": payload["trace_id"]},
                metadata={"source": "post-hoc local event log", "contains_original_timestamps": True}) as root:
            for event in payload["events"]:
                data = event["data"]
                generation = event["kind"] == "llm_usage"
                kwargs = {"name": data.get("node", data.get("tool", event["kind"])),
                          "as_type": "generation" if generation else "span",
                          "metadata": {"recorded_at": event["at"], "local_event": event["kind"]},
                          "output": data}
                if generation:
                    kwargs.update(model=self.settings.model,
                                  usage_details={"input": data["input_tokens"], "output": data["output_tokens"] + data["thinking_tokens"]},
                                  cost_details={"total": data["estimated_cost_usd"]})
                with client.start_as_current_observation(**kwargs):
                    pass
        client.flush()
        if owned:
            client.shutdown()
        return {"trace_id": payload["trace_id"], "events_submitted": len(payload["events"]),
                "status": "submitted_not_verified_in_dashboard"}


def action_digest(action):
    return sha256(canonical({k: v for k, v in action.items() if k != "digest"}).encode()).hexdigest()
