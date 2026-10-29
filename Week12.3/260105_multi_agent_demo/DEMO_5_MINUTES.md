# Kịch bản demo 5 phút

Chuẩn bị: chạy server theo README, mở `http://127.0.0.1:8010`, mở thêm `ARCHITECTURE.md` và `EVAL_REPORT.md`. Chọn **Offline** cho bản demo không cần key; nói rõ đây là mô phỏng quyết định và trích đoạn, chạy trên LangGraph thật.

| Thời gian | Thao tác | Điểm cần trình bày |
|---|---|---|
| 0:00–0:40 | Giới thiệu sơ đồ và 7 tool | Supervisor điều phối, researcher tra cứu, operations xử lý tác vụ; quyền khác nhau |
| 0:40–1:25 | Hỏi “Thư viện có mở cửa Chủ nhật không?”, rồi “Còn thứ Bảy?” | Nguồn D01; history trong cùng thread; câu trả lời offline được gắn nhãn |
| 1:25–2:15 | Chọn lưu memory `language=Tiếng Việt`, bấm chạy rồi **Từ chối**. Thử lại và **Duyệt** | Xem inventory: trước duyệt không ghi; từ chối không ghi; chấp thuận mới có memory |
| 2:15–2:50 | Tạo thread mới, chọn đọc memory `language` | Long-term memory tách khỏi history của thread |
| 2:50–3:50 | Chọn “Tra cứu + tạo ticket”, hỏi điều kiện gia hạn, duyệt ticket | Một lượt đi qua cả hai specialist; nội dung ghi được hiển thị cụ thể |
| 3:50–4:25 | Xem/tải trace và inventory | Node, tool read/write, approval digest và bản ghi ticket thật; không chỉ lời model nói |
| 4:25–5:00 | Mở bảng eval và nói giới hạn | 25 case; success rate, avg steps, token cost offline; chưa có Gemini benchmark hay Langfuse Cloud trace |

Nếu có Gemini key: dành một lượt hỏi đơn giản để cho thấy gate trước mỗi request supervisor/researcher. Không nhấn duyệt nếu chưa xem dữ liệu. Giới thiệu usage input/output/thinking sau khi có phản hồi thật. Nếu lỗi/rate limit thì chỉ ra nhãn fallback và cost unknown; không lấy số offline thay số Gemini.

Demo checkpoint tùy chọn: tạo một hành động đang chờ, dừng server bằng Ctrl+C, chạy lại cùng data directory, tải lại GUI rồi duyệt. Có kiểm tra process restart tự động và log trong `artifacts/HTTP_CHECKS.json` để đối chiếu nếu không kịp biểu diễn trong 5 phút.

Demo Langfuse tùy chọn: sau khi có project/key, xuất một trace và duyệt payload, rồi kiểm tra dashboard. Chưa có key thì chỉ trình bày log local và điểm tích hợp; không khẳng định đã upload.

Kết quả eval lưu trong `artifacts/evals/`. Các trace được tạo thật từ graph offline. File `artifacts/actual_http_trace.jsonl` giữ một lượt compound qua API thật. Đây là kịch bản trình diễn, không phải video đã quay.
