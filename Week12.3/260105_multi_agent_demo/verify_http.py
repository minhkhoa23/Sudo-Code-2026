"""Real localhost HTTP and process-restart test; never calls Gemini or Langfuse."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from time import perf_counter, sleep

import httpx

from .domain import ROOT


def main():
    port = 8021
    with socket.socket() as probe:
        probe.bind(("127.0.0.1",port))
    checks = []
    destination = ROOT / "artifacts"
    destination.mkdir(exist_ok=True)
    log_path = destination / "http_server.log"
    # Windows may retain WAL handles briefly after process exit. Cleanup must not
    # mask completed assertions; the test port/process is still explicitly stopped.
    with tempfile.TemporaryDirectory(prefix="w10-http-", ignore_cleanup_errors=True) as data_dir, log_path.open("w",encoding="utf-8") as log:
        env = os.environ.copy()
        env.update(DEMO_DATA_DIR=data_dir,GEMINI_API_KEY="",LANGFUSE_PUBLIC_KEY="",LANGFUSE_SECRET_KEY="")
        command = [sys.executable,"-m","uvicorn","week10_multiagent_demo.api:app","--host","127.0.0.1","--port",str(port),"--workers","1"]
        process = None

        def start():
            nonlocal process
            process = subprocess.Popen(command,cwd=ROOT.parent,env=env,stdout=log,stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
            deadline = perf_counter()+35
            while perf_counter()<deadline:
                if process.poll() is not None:
                    raise RuntimeError("HTTP server exited; see log")
                try:
                    if client.get("/health",timeout=1).status_code==200:
                        return
                except httpx.RequestError:
                    pass
                sleep(.2)
            raise TimeoutError("Server not ready; sandbox may block Windows localhost")

        def stop():
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait(timeout=5)

        def request(method,path,token=None,body=None,status=200):
            r=client.request(method,path,headers={"Authorization":"Bearer "+token} if token else {},json=body)
            assert r.status_code==status,(path,r.status_code,r.text[:500])
            checks.append({"path":path,"method":method,"status":r.status_code})
            return r.json()

        def decision(token,thread,view,choice="approve",status=200):
            a=view["approval"]
            return request("POST",f"/api/threads/{thread}/approval",token,
                           {"action_id":a["id"],"digest":a["digest"],"decision":choice},status)

        with httpx.Client(base_url=f"http://127.0.0.1:{port}",timeout=10,trust_env=False) as client:
            try:
                start()
                home=client.get("/")
                assert home.status_code==200 and "Week 10" in home.text
                assert client.get("/docs").status_code==200
                request("GET","/api/inventory",status=401)
                a=request("POST","/api/session",body={})["token"]
                b=request("POST","/api/session",body={})["token"]
                thread=request("POST","/api/threads",a,{})["thread_id"]
                payload={"message":"Giờ mở cửa Chủ nhật?","mode":"offline"}
                view=request("POST",f"/api/threads/{thread}/turn",a,payload)
                assert view["status"]=="completed" and "D01" in {s["doc_id"] for s in view["sources"]}
                request("POST",f"/api/threads/{thread}/turn",a,{"message":"","mode":"offline"},422)
                view=request("POST",f"/api/threads/{thread}/turn",a,{"message":"Ghi nhớ sở thích","action":"remember","args":{"key":"language","value":"Tiếng Việt"},"mode":"offline"})
                assert view["status"]=="awaiting_approval"
                assert not request("GET","/api/inventory",a)["memories"]
                request("POST",f"/api/threads/{thread}/turn",a,payload,409)
                # Terminate actual OS process, start a new one with the same data directory.
                stop(); start()
                restored=request("GET",f"/api/threads/{thread}",a)
                assert restored["approval"]["id"]==view["approval"]["id"]
                decision(b,thread,restored,status=403)
                bad={"action_id":restored["approval"]["id"],"digest":"0"*64,"decision":"approve"}
                request("POST",f"/api/threads/{thread}/approval",a,bad,409)
                done=decision(a,thread,restored)
                assert done["status"]=="completed"
                decision(a,thread,restored,status=409)
                assert len(request("GET","/api/inventory",a)["memories"])==1
                assert not request("GET","/api/inventory",b)["memories"]
                new=request("POST","/api/threads",a,{})["thread_id"]
                recall=request("POST",f"/api/threads/{new}/turn",a,{"message":"Ngôn ngữ đã lưu?","action":"recall","args":{"key":"language"},"mode":"offline"})
                assert "Tiếng Việt" in recall["answer"]
                # Two specialists in the same graph run, gate then reject/approve distinctly.
                compound=request("POST",f"/api/threads/{new}/turn",a,{"message":"Điều kiện gia hạn mượn sách?","action":"research_ticket","args":{"title":"Gia hạn","body":"Nhờ tư vấn"},"mode":"offline"})
                assert not request("GET","/api/inventory",a)["tickets"]
                compound=decision(a,new,compound)
                trace=request("GET","/api/traces/"+compound["trace_id"],a)
                nodes={x["data"].get("node") for x in trace["events"] if x["kind"]=="node_end"}
                assert {"researcher","operations","supervisor"}.issubset(nodes)
                request("GET","/api/traces/"+compound["trace_id"],b,status=404)
                assert client.get("/api/traces/"+compound["trace_id"]+"/download",headers={"Authorization":"Bearer "+a}).status_code==200
                (destination/"actual_http_trace.jsonl").write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in trace["events"])+"\n",encoding="utf-8")
            finally:
                stop()
    result={"status":"passed","http_requests_checked":len(checks),"process_restart":True,"cross_user_isolation":True,
            "checkpoint_resume":True,"trace_source":"real localhost HTTP / offline LangGraph", "checks":checks}
    (destination/"HTTP_CHECKS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="checks"},ensure_ascii=True))


if __name__=="__main__":
    main()
