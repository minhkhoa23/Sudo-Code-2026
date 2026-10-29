# Eval report — Multi-agent Library

Run UTC: 20261029T090439_594290Z. Mode: **offline**. Kết quả chạy LangGraph thật, không dùng số liệu minh họa.

| Cases | Success rate | Avg steps / evaluated final turn | Avg token cost / run (USD) |
|---:|---:|---:|---:|
| 24 | 95.83% | 5.58 | 0.0 |

Input tokens: 0; output: 0; thinking: 0.

Offline là planner bằng code và trích đoạn tài liệu, không phải chất lượng suy luận của Gemini. Cost 0 chỉ nghĩa không có LLM call; không bao gồm hạ tầng. Gemini eval chưa chạy nếu report ghi offline. Không có chứng cứ trace đã được gửi lên Langfuse Cloud.

Mỗi case là một scenario; chỉ số steps và token cost trong bảng tính trên lượt cuối được chấm, không cộng lượt dựng ngữ cảnh/recall kiểm tra phụ. `outputs.json` và `traces.jsonl` giữ bằng chứng cả các lượt đó. Steps đếm node hoàn tất (gồm supervisor/tool gate), không đếm lần interrupt chưa hoàn tất. Thời gian case gồm setup/kiểm tra và không mô phỏng thời gian con người duyệt.

QA chấm bằng nguồn mong đợi + một thông tin literal có trong câu trả lời, chưa đánh giá đầy đủ tính đúng/ngắn gọn. Offline trả trích đoạn, không dùng làm benchmark so sánh các LLM. Tool case kiểm tra DB trước/sau và trạng thái duyệt; compound kiểm tra cả hai specialist trong trace. Đây là bộ hồi quy nhỏ, chưa chứng minh an toàn trước mọi prompt injection.

Giá Gemini chỉ là ước tính từ usage metadata, gồm thinking tokens ở output, dùng rate trong `.env`; cached input hiện tính theo giá input thường (có thể cao hơn bill). Nếu request lỗi không có usage, cost là unknown, không tự coi là 0. Không bao gồm phí Langfuse hoặc hạ tầng. Xem [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing).

| Case | Nhóm | Kết quả | Steps | Ước tính USD |
|---|---|---|---:|---:|
| Q01 | qa | PASS | 5 | 0.0 |
| Q02 | qa | PASS | 5 | 0.0 |
| Q03 | qa | PASS | 5 | 0.0 |
| Q04 | qa | PASS | 5 | 0.0 |
| Q05 | qa | PASS | 5 | 0.0 |
| Q06 | qa | PASS | 5 | 0.0 |
| Q07 | qa | PASS | 5 | 0.0 |
| Q08 | qa | PASS | 5 | 0.0 |
| Q09 | qa | PASS | 5 | 0.0 |
| Q10 | qa | PASS | 5 | 0.0 |
| Q11 | qa | PASS | 5 | 0.0 |
| Q12 | qa | PASS | 5 | 0.0 |
| Q13 | qa | PASS | 5 | 0.0 |
| Q14 | qa | PASS | 5 | 0.0 |
| Q15 | unknown | FAIL | 5 | 0.0 |
| T16 | fee | PASS | 5 | 0.0 |
| T17 | fee | PASS | 5 | 0.0 |
| M18 | memory | PASS | 8 | 0.0 |
| M19 | memory | PASS | 5 | 0.0 |
| A20 | ticket | PASS | 8 | 0.0 |
| A21 | ticket | PASS | 5 | 0.0 |
| A22 | email | PASS | 8 | 0.0 |
| C23 | compound | PASS | 10 | 0.0 |
| C24 | followup | PASS | 5 | 0.0 |

Chi tiết: `results.csv`, `outputs.json`, `summary.json`, `traces.jsonl` cạnh report này. Decision ghi/gửi local trong eval offline là fixture lập trình sẵn; GUI/API vẫn yêu cầu duyệt từng hành động. Bản chạy Gemini hỏi người dùng trong terminal trước từng lần gửi model.
