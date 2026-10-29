# Bảo mật cho hệ thống RAG và Agent

**Bài toán cốt lõi là gì?**

Khi xây hệ thống RAG hoặc agent, model thường nhận cùng lúc nhiều nguồn văn bản: hướng dẫn của người phát triển (`SYSTEM_PROMPT`), câu hỏi của người dùng và dữ liệu bên ngoài như tài liệu truy xuất hoặc kết quả từ tool.

Nếu hệ thống không kiểm soát ranh giới giữa các nguồn này, nội dung trong dữ liệu có thể bị model diễn giải nhầm thành mệnh lệnh cần thực hiện. Đây là bài toán lẫn lộn giữa dữ liệu và chỉ thị (*data vs. instruction confusion*).

```text
System prompt + Câu hỏi người dùng + Tài liệu RAG → Chung một ngữ cảnh token → LLM xử lý
```

**SQLi, XSS và prompt injection giống và khác nhau ở đâu?**

Trong ứng dụng web truyền thống:

- SQL Injection (SQLi) xảy ra khi chuỗi người dùng nhập được ghép thẳng vào câu lệnh SQL, làm thay đổi cấu trúc truy vấn.
- Cross-Site Scripting (XSS) xảy ra khi dữ liệu không tin cậy được đưa thẳng vào HTML trên trình duyệt mà không qua mã hóa phù hợp, khiến trình duyệt chạy nhầm script.

Điểm giống nhau giữa SQLi, XSS và prompt injection là cả ba đều trộn dữ liệu không đáng tin cậy vào kênh điều khiển của bộ thông dịch.

Tuy nhiên, cách vá kinh điển lại không áp dụng nguyên xi sang LLM được:

| Tiêu chí | SQLi / XSS | Prompt injection trên LLM |
| --- | --- | --- |
| Ranh giới cú pháp | Có ngữ pháp hình thức rõ ràng, tách được cây cú pháp lệnh và vùng dữ liệu | Không có ranh giới cú pháp cứng; mọi thành phần đều thành chuỗi token đưa vào cơ chế attention |
| Cách vá chuẩn | Parameterized query (`?`) cho SQL; escape theo ngữ cảnh (`html.escape`) cho HTML | Không có "parameterized prompt" tuyệt đối ở tầng model |
| Cách tiếp cận | Xử lý triệt để tại nơi tạo truy vấn hoặc render giao diện | Kết hợp phòng thủ nhiều lớp ở kiến trúc ứng dụng xung quanh model |

Hiểu điều này giúp mình không chủ quan rằng chỉ cần viết thêm một câu dặn trong `SYSTEM_PROMPT` là hệ thống đã an toàn. Xem thêm loạt bài của [Simon Willison về Prompt Injection](https://simonwillison.net/tags/prompt-injection/).

**Direct và indirect prompt injection**

Mình có thể chia prompt injection thành hai hướng chính:

- Direct prompt injection: chính người dùng gõ các câu yêu cầu model bỏ qua quy tắc ban đầu, đóng vai khác (*jailbreak / roleplay*) hoặc in lại hướng dẫn hệ thống.
- Indirect prompt injection: người dùng chỉ hỏi một câu hoàn toàn bình thường, nhưng tài liệu được RAG lấy ra (hoặc dữ liệu đọc từ web, email, ticket) lại chứa văn bản giả dạng chỉ thị hệ thống.

Trong demo Thư viện Bình Minh, nếu kho tài liệu có một thông báo sự kiện bị chèn câu yêu cầu trợ lý tự gọi hàm gia hạn sách hoặc báo sai quy định phí phạt, người dùng chỉ cần hỏi *"Thư viện có sự kiện gì mới không?"* là đoạn văn bản đó đã đi vào prompt của model.

Ngoài ra, trên hệ RAG dùng TF-IDF với ngưỡng `MIN_SCORE = 0.12`, những câu hỏi không có từ vựng liên quan đến thư viện sẽ bị chặn ngay từ bước tìm chunk (`no_context`) trước khi gọi API. Những câu kiểm thử có chứa từ khóa thư viện mới thực sự đi tới bước sinh câu trả lời của LLM.

**Vì sao chặn bằng regex blocklist không đủ?**

Một phản xạ thường gặp là lập danh sách từ cấm bằng biểu thức chính quy, ví dụ chặn `"ignore previous"`, `"bỏ qua quy định"`, `"system prompt"`.

Cách này chỉ bắt được một số mẫu cố định trên câu hỏi trực tiếp và rất dễ bị vượt qua:

- Ngôn ngữ tự nhiên có vô số cách diễn đạt tương đương, viết tắt, chèn dấu gạch nối hoặc chuyển sang ngôn ngữ khác.
- Nếu chặn quá rộng, hệ thống dễ từ chối nhầm cả câu hỏi hợp lệ của người dùng thật.
- Quan trọng nhất, nếu chỉ kiểm tra regex trên câu hỏi người dùng thì hệ thống hoàn toàn bỏ sót indirect prompt injection nằm sẵn bên trong tài liệu RAG.

Regex vẫn có ích để kiểm tra định dạng chặt như mã phiếu mượn `L001` hay mã nguồn `[D03-C01]`, nhưng không thể dùng làm lớp bảo vệ chính để hiểu ý định trong ngôn ngữ tự nhiên.

**Ánh xạ rủi ro theo OWASP Top 10 cho ứng dụng LLM**

Khi rà soát một hệ RAG/Agent có kết nối database và hiển thị giao diện web, bốn nhóm rủi ro mình cần chú ý nhất là:

| Mã tham chiếu | Nhóm rủi ro | Biểu hiện trong hệ RAG / Agent |
| --- | --- | --- |
| LLM01 | Prompt Injection | Câu hỏi hoặc tài liệu truy xuất làm model trả lời sai quy tắc hoặc kích hoạt hành động ngoài ý muốn |
| LLM05 | Improper Output Handling | Đưa thẳng text của model vào HTML gây XSS, hoặc ghép thẳng tham số model sinh ra vào câu SQL |
| LLM06 | Excessive Agency | Cấp cho agent các tool có quyền quá rộng, tự sửa dữ liệu hoặc đọc dữ liệu của tài khoản khác mà không kiểm tra |
| LLM07 | System Prompt Leakage | Lộ cấu hình, quy tắc nội bộ hoặc thông tin nhạy cảm đặt nhầm trong `SYSTEM_PROMPT` |

Tham khảo danh sách đầy đủ tại [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/).

**Xử lý output và giới hạn quyền của tool**

Model không nên được tin tưởng như một thành phần đã xác thực quyền. Ngay cả khi prompt injection xảy ra ở tầng model, hệ thống bên dưới vẫn phải giữ được an toàn cho dữ liệu.

Hai điểm dễ sai khi nối LLM với phần còn lại của ứng dụng:

- Đưa thẳng câu trả lời của model vào `HTML()` hoặc `innerHTML`: nếu model bị ép sinh thẻ HTML hoặc link ảnh ngoài (`![img](https://...)`), giao diện có thể bị lỗi hiển thị, chạy script hoặc rò rỉ thông tin qua request tải ảnh. Khi hiển thị văn bản thuần, cần dùng `html.escape(text, quote=True)`.
- Cho model tự điền `user_id` hoặc câu SQL khi gọi tool: ví dụ người đang đăng nhập là `reader_01` nhưng nhờ agent tra cứu phiếu mượn của `reader_02`. Định danh người dùng phải được backend lấy từ session đăng nhập, kết hợp truy vấn có tham số (`WHERE user_id = ?`).

```python
# Không nhận user_id từ LLM; khóa chặt theo tài khoản đang đăng nhập ở backend
cursor.execute(
    "SELECT loan_id, book_title, due_date FROM loans WHERE user_id = ?",
    (authenticated_user_id,),
)
```

**Phòng thủ nhiều lớp (Defense-in-Depth) và Approval Gate**

Thay vì trông chờ vào một chốt chặn duy nhất, mình chia trách nhiệm bảo vệ thành nhiều lớp nối tiếp nhau:

```text
Input kiểm tra độ dài
→ Tách biệt dữ liệu RAG (untrusted_passages)
→ Ép schema đầu ra (Pydantic JSON) & đối chiếu mã trích dẫn
→ Tool chỉ đọc / khóa theo session + Approval Gate cho tác vụ ghi
→ Kiểm tra rò rỉ & escape HTML trước khi hiển thị
```

Các nguyên tắc thực hành chính:

- Không đặt API key, mật khẩu DB hay bí mật hệ thống vào trong `SYSTEM_PROMPT`.
- Đóng khung tài liệu truy xuất dưới dạng trường dữ liệu rõ ràng (như `untrusted_passages`) và kiểm tra các `chunk_id` trích dẫn có thực sự nằm trong danh sách vừa truy xuất hay không.
- Tách riêng tool chỉ đọc (*read-only*, như xem phiếu mượn của chính mình) và tool làm thay đổi dữ liệu (*state-changing*, như gia hạn sách, xóa bản ghi, gửi email).
- Đặt **Approval Gate (Human-in-the-Loop)** cho các tool nhạy cảm: khi model đề xuất gọi `renew_loan`, code điều phối dừng lại ở trạng thái chờ (`PENDING_USER_APPROVAL`), hiển thị rõ tham số dự kiến và chỉ thực thi sau khi người dùng bấm xác nhận.

**Đo lường bằng Attack Success Rate (ASR)**

Để biết các lớp bảo vệ có thực sự giảm rủi ro hay không, mình cần xây dựng bộ test cố định (hoặc dùng các công cụ đánh giá tự động như `promptfoo`, `garak`) và đo trước/sau khi sửa.

$$\text{ASR} = \frac{\text{Số kịch bản khiến hệ thống vi phạm chính sách}}{\text{Tổng số kịch bản kiểm thử}} \times 100\%$$

Trước khi chạy đánh giá, cần định nghĩa rõ thế nào là một lần vi phạm thành công: ví dụ trả lời sai sự kiện trong tài liệu, lộ chuỗi cấu hình nội bộ, chèn lọt thẻ HTML chưa escape, đọc được dữ liệu của `user_id` khác, hoặc tự động cập nhật database khi chưa có xác nhận.

Một điểm cần nhớ là `ASR = 0%` trên bộ 15–20 kịch bản tự soạn chỉ chứng minh hệ thống đã chặn được các mẫu trong phạm vi kiểm thử đó, không có nghĩa hệ thống miễn nhiễm với mọi biến thể mới. Khi thêm tài liệu mới hoặc mở thêm tool cho agent, mình cần cập nhật lại bộ test tương ứng.
