# Week 10 → Multi-agent Library bằng LangGraph

Project demo chạy bằng **FastAPI + GUI web**, dùng lại dữ liệu thư viện giả định từ bài RAG. Có supervisor, hai specialist, 7 tool, memory lâu dài, checkpoint SQLite và approval trước tác vụ ghi/gửi. Xem [kiến trúc](ARCHITECTURE.md).

**Chạy ngay trên máy hiện tại**

Trong PowerShell:

```powershell
cd "D:\Sudo code 2026"
& ".\tmp\multiagent_venv\Scripts\python.exe" -m uvicorn week10_multiagent_demo.api:app --host 127.0.0.1 --port 8010 --workers 1
```

Mở [GUI](http://127.0.0.1:8010/) hoặc [API docs](http://127.0.0.1:8010/docs). Dừng bằng `Ctrl+C`. Chưa có Gemini key thì ứng dụng ghi rõ đang chạy offline. CPU đủ cho chế độ này.

Cũng có thể chạy `week10_multiagent_demo/start_demo.ps1` nếu PowerShell cho phép script; không cần thay đổi execution policy để dùng lệnh Python ở trên.

**Cài ở môi trường mới**

Python 3.12 đã được kiểm tra. Giữ nguyên cấu trúc thư mục package khi copy project.

```powershell
cd "D:\Sudo code 2026"
py -3.12 -m venv week10_multiagent_demo\.venv
& ".\week10_multiagent_demo\.venv\Scripts\python.exe" -m pip install -r week10_multiagent_demo\requirements.txt
& ".\week10_multiagent_demo\.venv\Scripts\python.exe" -m uvicorn week10_multiagent_demo.api:app --host 127.0.0.1 --port 8010 --workers 1
```

`requirements-lock.txt` ghi đầy đủ version môi trường Windows đã kiểm tra. Các lệnh eval bên dưới dùng `tmp/multiagent_venv`; thay bằng `.venv` mới nếu cần.

**Bật Gemini**

Copy `.env.example` thành `.env` trong thư mục project, nhập `GEMINI_API_KEY` ở máy bạn rồi khởi động lại server. Không gửi key qua chat, không nhập key vào câu hỏi, không commit `.env`.

Model mặc định `gemini-3.1-flash-lite`. Nếu đổi model, cập nhật rate input/output trong `.env`. Rate mặc định tham khảo giá text standard paid tại ngày 2026-10-29: 0,25 USD / 1 triệu input token và 1,50 USD / 1 triệu output token. Kiểm tra lại [model](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite) và [pricing](https://ai.google.dev/gemini-api/docs/pricing) theo tài khoản/tier thực tế.

Chọn Gemini/Auto trong GUI. **Mỗi lần gửi model đều có bước duyệt**, cho bạn xem system prompt, nội dung chứa câu hỏi/history/memory/nguồn và model được dùng. Sau đó, nếu cần ghi memory hoặc tạo ticket, hệ lại hỏi duyệt riêng. Từ chối thì hành động đang chờ không chạy. Đây là cách thực hiện yêu cầu duyệt trước mọi lần gửi ra ngoài.

Nếu không có key, hệ dùng offline và ghi lý do. Nếu Gemini request lỗi, hệ ghi fallback offline; cost có thể là unknown vì request lỗi vẫn có thể phát sinh phí. Không coi fallback là Gemini thành công.

**Cách dùng GUI**

1. Chọn chế độ và tác vụ. Tác vụ xác định quyền được cấp cho lượt đó.
2. Nhập yêu cầu; tham số JSON của tool có mẫu tự điền.
3. Bấm **Chạy lượt này**. Nếu có approval, kiểm tra toàn bộ preview rồi duyệt hoặc từ chối.
4. Xem kết quả, nguồn, số bước và token/cost. Bấm **Xem trace** hoặc **Tải JSONL**.
5. Chọn **Thread mới, cùng người dùng** để thử long-term memory qua phiên khác.

Ví dụ memory: `{"key":"language","value":"Tiếng Việt"}`. Sau khi duyệt, tạo thread mới và chọn đọc memory với `{"key":"language"}`. Mỗi trình duyệt được một demo session token riêng, lưu localStorage; token được hash trong DB. Giữ token nếu muốn dùng lại dữ liệu của session đó. Đây chưa phải hệ đăng nhập production.

Tác vụ `Tra cứu + tạo ticket` gọi cả hai specialist. Tác vụ email chỉ lưu nháp trong outbox local, không dùng SMTP và không gửi email thật. Đích demo có đuôi `.example`.

**Gọi API**

- `POST /api/session` lấy token demo.
- Gửi header `Authorization: Bearer <token>` ở các endpoint còn lại.
- `POST /api/threads` tạo thread; `POST /api/threads/{id}/turn` bắt đầu lượt.
- `GET /api/threads/{id}` khôi phục trạng thái, kể cả interrupt sau khi restart.
- `POST /api/threads/{id}/approval` duyệt bằng action ID và digest đang chờ.
- `GET /api/inventory` xem memory/ticket/outbox của session.
- `GET /api/traces` và `GET /api/traces/{id}/download` xem/tải log.

Body ví dụ của một lượt:

```json
{"message":"Tính phí 2 cuốn quá hạn 3 ngày.","action":"fee","args":{"books":2,"days":3},"mode":"offline"}
```

Code API không nhận `user_id` tùy ý từ model. Không dùng token của người khác để truy cập thread/trace. Input sai schema trả 422; thao tác xung đột như duyệt lại hoặc gửi thêm khi đang chờ thường trả 409.

**Memory và checkpoint**

Mặc định dữ liệu ở `runtime/application.sqlite3` và `runtime/checkpoints.sqlite3`, không xóa khi server dừng. Có thể đổi `DEMO_DATA_DIR` sang thư mục riêng. Memory được lưu theo user và dùng xuyên thread; lịch sử ngắn hạn và vị trí graph nằm trong checkpoint.

Restart server cùng thư mục dữ liệu rồi tải lại GUI để tiếp tục duyệt. Không đổi model/đích Langfuse giữa lúc có hành động đang chờ nếu chưa kiểm tra preview; đích xuất Langfuse thay đổi sẽ bị chặn.

**Langfuse**

Hiện chưa có project/key Langfuse nên trace thực tế được giữ local. Để xuất sau này:

1. Tạo project Langfuse của bạn, điền `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` đúng region vào `.env`, restart server.
2. Chạy một lượt, chọn tác vụ **Gửi trace sang Langfuse**. JSON mẫu lấy trace ID của lượt đang xem.
3. Duyệt đúng payload và đích. Chỉ sau bước này SDK mới gửi. Kiểm tra dashboard để xác nhận đã nhận; trạng thái API chỉ nói đã submit, không tự chứng minh dashboard có dữ liệu.

Đây là export sau khi chạy; event metadata giữ timestamp gốc, không giả là realtime trace. Không có tự động upload khi khởi động, khi eval offline hoặc khi chưa duyệt. Tài liệu: [Langfuse](https://langfuse.com/docs).

**Eval và kiểm tra**

```powershell
& ".\tmp\multiagent_venv\Scripts\python.exe" -m week10_multiagent_demo.evaluate --mode offline
& ".\tmp\multiagent_venv\Scripts\python.exe" -m week10_multiagent_demo.verify_system
& ".\tmp\multiagent_venv\Scripts\python.exe" -m week10_multiagent_demo.verify_http
```

Eval có **25 case** trong `data/eval_cases.json`: QA có nguồn, câu ngoài miền, tính phí, memory duyệt/từ chối, ticket, outbox, hai specialist và follow-up sau reopen. Có case bổ sung từ luồng GUI để kiểm tra truy vấn compound. Kết quả CSV/JSON, trace JSONL và report ở `artifacts/evals/<timestamp>/`; bản report gần nhất ở `EVAL_REPORT.md`.

`verify_system` kiểm tra phân quyền, người dùng khác, digest sai, replay, memory/checkpoint và cost. Các bài Gemini dùng stub/HTTP mock; Langfuse dùng SDK thật với in-memory exporter. Đây không phải bằng chứng đã gọi dịch vụ thật.

`verify_http` mở localhost 8021, gọi HTTP thật, dừng và bật lại process để thử checkpoint/approval, sau đó dừng server test. Nếu Windows sandbox không cho mở localhost thì cần chạy ở terminal thông thường. Log/check report ở `artifacts/`.

Để đo Gemini thật sau khi nhập key:

```powershell
& ".\tmp\multiagent_venv\Scripts\python.exe" -m week10_multiagent_demo.evaluate --mode gemini
```

Terminal sẽ yêu cầu duyệt từng lần gửi model. Không autoapprove external send. Bộ grader literal nhỏ chỉ là kiểm tra hồi quy; cần đánh giá thêm tính đúng/ngắn gọn nếu dùng như benchmark chất lượng. Test offline không phải security ASR, không phải Gemini benchmark.

**Cost và số bước**

Steps là số node hoàn tất, gồm supervisor và approval sau khi resume; lần node vừa interrupt chưa hoàn tất không được đếm. Eval cộng toàn bộ lượt của một scenario, kể cả dựng ngữ cảnh/recall, từ trace thực tế.

Gemini token dùng `usage_metadata`, gồm input, output, thinking. Rate input thường được áp dụng cả cached input trong ước tính, nên có thể cao hơn bill thực; không tính cache discount, thuế, Langfuse và hạ tầng. Thiếu usage thì cost unknown. Offline có 0 model token và 0 token cost; không có nghĩa hạ tầng miễn phí.

**File nên xem**

- `ARCHITECTURE.md`: sơ đồ và trust boundary.
- `DEMO_5_MINUTES.md`: kịch bản demo 5 phút.
- `EVAL_REPORT.md`: bảng kết quả thực tế.
- `artifacts/actual_http_trace.jsonl`: trace từ lượt HTTP chạy thật.
- `artifacts/SYSTEM_CHECKS.json`, `artifacts/HTTP_CHECKS.json`: bằng chứng kiểm tra.

API bind localhost để demo. Session auth, SQLite, lexical search và khóa một worker chưa đủ cho production. User memory, model output và tài liệu vẫn là dữ liệu không đáng tin; quyền tool và approval nằm trong code.
