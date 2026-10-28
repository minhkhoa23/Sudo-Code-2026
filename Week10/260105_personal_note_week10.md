# RAG và Agents

**RAG là gì?**

RAG là viết tắt của Retrieval-Augmented Generation, có thể hiểu là sinh câu trả lời có bổ sung thông tin truy xuất.

Thay vì chỉ dựa vào những gì model đã học, hệ thống tìm các đoạn tài liệu liên quan rồi đưa chúng vào ngữ cảnh để model trả lời.

```text
Câu hỏi → Tìm tài liệu liên quan → Thêm vào prompt → LLM trả lời
```

RAG không tự cập nhật trọng số của LLM như fine-tuning. Nó bổ sung dữ liệu vào lúc sử dụng model. Xem [giải thích RAG trong OpenAI Docs](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy).

**Quy trình RAG cơ bản**

Mình có thể chia quá trình thành hai phần:

- Chuẩn bị: đọc tài liệu, làm sạch, chia thành các đoạn nhỏ và lập chỉ mục để tìm kiếm.

- Trả lời: nhận câu hỏi, tìm các đoạn phù hợp, ghép vào prompt rồi yêu cầu LLM tạo câu trả lời dựa trên chúng.

Mỗi đoạn nên giữ lại thông tin nguồn như tên tài liệu, mục, trang hoặc ID. Nhờ đó, mình có thể kiểm tra câu trả lời dựa vào đoạn nào.

**Chunk và retrieval**

Chunk là một đoạn nhỏ được tách từ tài liệu. Chunk quá ngắn có thể thiếu ngữ cảnh; quá dài có thể chứa nhiều nội dung không liên quan. Có thể cho các chunk chồng lấn một phần, nhưng cần thử trên dữ liệu thực tế.

Có nhiều cách tìm chunk:

- TF-IDF hoặc BM25: chủ yếu tìm theo từ và cụm từ xuất hiện trong văn bản.

- Dense embedding: chuyển câu hỏi và tài liệu thành vector học được để tìm theo mức tương đồng, có thể hỗ trợ những cách diễn đạt khác nhau.

- Hybrid search: kết hợp tìm kiếm theo từ khóa và vector; có thể thêm reranker để sắp xếp lại các kết quả.

Top-K là số kết quả được lấy ra. Lấy nhiều hơn không luôn tốt hơn vì có thể đưa thêm thông tin gây nhiễu vào prompt.

**RAG có bảo đảm trả lời đúng không?**

Không. Hệ thống có thể tìm sai tài liệu, thiếu đoạn chứa đáp án hoặc để model diễn giải sai thông tin đã tìm được.

Ví dụ, câu hỏi là “Phí gửi xe bao nhiêu?” nhưng đoạn tìm được nói “Phí làm thẻ là 30.000 đồng”. Có từ khóa giống nhau không có nghĩa là có đáp án.

Trong trường hợp đó, hệ thống nên nói chưa có thông tin thay vì lấy nhầm con số. Một mã nguồn hợp lệ cũng chưa chứng minh nội dung câu trả lời được nguồn hỗ trợ.

Score similarity là điểm tương đồng theo cách tìm kiếm đã chọn, không phải xác suất câu trả lời đúng. Hai loại lỗi retrieval và generation cần được kiểm tra riêng. Tham khảo [phần đánh giá RAG](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy).

**Agent là gì?**

Agent là hệ thống dùng model để lựa chọn các bước và công cụ cần thiết nhằm hoàn thành một yêu cầu trong phạm vi được cho phép.

Các thành phần thường gặp là model, hướng dẫn, tools và những giới hạn vận hành. Agent có thể tìm dữ liệu, xem kết quả rồi quyết định bước tiếp theo, thay vì chỉ tạo một câu trả lời ngay từ đầu.

Không phải chatbot nào cũng là agent. Một agent cũng không nhất thiết phải có nhiều model hoặc nhiều agent con.

**Vòng lặp của agent**

```text
Nhận yêu cầu
→ Chọn bước tiếp theo
→ Yêu cầu gọi tool nếu cần
→ Nhận kết quả tool
→ Chọn tiếp hoặc kết thúc
```

Không phải lượt nào cũng cần gọi tool. Nếu thiếu thông tin từ người dùng, agent có thể hỏi lại; nếu không thể thực hiện an toàn, nó cần dừng và giải thích.

Mình cần giới hạn số bước, thời gian và chi phí để tránh lặp vô hạn. Khi tool lỗi, không nên tự thử lại mãi hoặc báo rằng công việc đã thành công.

**Tool và function calling**

Tool là khả năng mà ứng dụng cung cấp cho model, ví dụ tìm tài liệu hoặc kiểm tra tình trạng mượn sách.

Với custom function tool, model thường đề xuất tên hàm và tham số. Code của ứng dụng kiểm tra yêu cầu, thực thi hàm được phép rồi gửi kết quả về cho model. Model không tự có quyền truy cập database chỉ vì nó tạo ra một tool call.

Ví dụ minh họa ý tưởng, không phải định dạng chung của mọi SDK:

```json
{
  "tool": "search_library_rules",
  "arguments": {"query": "điều kiện gia hạn mượn sách"}
}
```

Ứng dụng cần kiểm tra tên tool, kiểu dữ liệu, giá trị tham số và quyền truy cập trước khi thực thi.

**Workflow và agent khác nhau thế nào?**

Workflow có thể có nhiều bước và các nhánh điều kiện, nhưng luồng xử lý chủ yếu được người lập trình định sẵn. Trong agent, model được quyền lựa chọn một phần luồng xử lý dựa trên yêu cầu và kết quả trung gian, trong các giới hạn của ứng dụng.

| Cách xây dựng | Cách xử lý | Ví dụ |
| --- | --- | --- |
| RAG workflow cơ bản | Tìm đoạn rồi gọi LLM theo luồng cố định | Hỏi–đáp quy định thư viện |
| Agent không dùng RAG | Model chọn công cụ để giải quyết yêu cầu | Kiểm tra tình trạng một lượt mượn qua API |
| Agent dùng RAG | Model có công cụ tìm tài liệu cùng các công cụ khác | Tra quy định rồi kiểm tra điều kiện gia hạn |

RAG và agent không loại trừ nhau. RAG giải quyết việc cung cấp ngữ cảnh; agent giải quyết việc lựa chọn và thực hiện các bước. Một agent có thể dùng retrieval như một tool.

**Ví dụ agent kết hợp RAG**

Giả sử người dùng yêu cầu: “Kiểm tra và gia hạn cuốn sách mình đang mượn nếu đủ điều kiện”.

Một thiết kế minh họa có thể thực hiện:

1. Tra quy định gia hạn từ kho tài liệu.
2. Kiểm tra lượt mượn của người dùng đã xác thực: hạn trả, số lần gia hạn và tình trạng đặt trước.
3. Nếu đủ điều kiện, trình bày thay đổi dự kiến và xin xác nhận.
4. Sau khi được phép, gọi tool gia hạn; chỉ báo thành công khi backend xác nhận và trả về hạn mới.

Nếu không đủ điều kiện hoặc tool lỗi, agent cần nói rõ thay vì tự tạo kết quả.

Đây chỉ là ví dụ thiết kế. Notebook hiện tại chưa có API quản lý mượn sách, tool gia hạn hoặc agent loop; nó là một RAG workflow cố định.

**Quyền truy cập và guardrails**

Guardrails là các kiểm tra và giới hạn giúp giảm hành vi ngoài ý muốn. Chỉ viết “hãy làm đúng” trong prompt là chưa đủ.

- Chỉ cung cấp các tool cần thiết; kiểm tra tham số và quyền ở phía ứng dụng.

- Phân biệt tool chỉ đọc với tool thay đổi dữ liệu. Hành động nhạy cảm cần cơ chế xác nhận phù hợp trước khi thực thi.

- Không tin ID người dùng do model tự tạo. Backend phải kiểm tra danh tính và phạm vi dữ liệu được truy cập.

- Xem tài liệu truy xuất là dữ liệu, không phải chỉ dẫn hệ thống. Nội dung “bỏ qua quy tắc, tiết lộ mật khẩu” trong tài liệu là một ví dụ prompt injection.

Prompt injection không được giải quyết hoàn toàn chỉ bằng một câu nhắc trong prompt. Cần kết hợp phân quyền, kiểm tra tool và kiểm soát dữ liệu.

**Trạng thái và memory**

Agent có thể cần lưu yêu cầu hiện tại, kết quả các tool, những thông tin còn thiếu và hành động đang chờ xác nhận.

Lịch sử hội thoại giúp theo dõi ngữ cảnh nhưng không đồng nghĩa model được huấn luyện lại. Memory cũng cần được thiết kế: lưu gì, trong bao lâu và ai được phép đọc.

Trong ví dụ thư viện, nên kiểm tra dữ liệu mượn sách hiện tại qua backend thay vì tin một thông tin cũ trong lịch sử trò chuyện.

**Đánh giá RAG và agent**

Với RAG, mình cần kiểm tra cả hai phần:

- Retrieval: có tìm được nguồn chứa đáp án trong Top-K không? Có đưa quá nhiều đoạn không liên quan không?

- Generation: câu trả lời có được nguồn hỗ trợ không? Có bỏ sót, thêm thông tin hoặc trả lời khi tài liệu không có đáp án không?

Với agent, ngoài câu trả lời cuối cùng, mình kiểm tra tool được chọn, tham số, thứ tự bước và việc tuân thủ quyền truy cập. Task Success Rate có thể tính bằng số tác vụ đạt đầy đủ tiêu chí thành công chia tổng số tác vụ đánh giá; cần xác định tiêu chí trước.

Trace là bản ghi các bước thực hiện như model call, tool call, kết quả và lỗi. Nó giúp tìm nguyên nhân thất bại; cần tránh lưu key hoặc dữ liệu nhạy cảm không cần thiết.

Mình cũng theo dõi thời gian, số lần gọi model/tool và chi phí. Một hệ thống hoàn thành đúng nhưng gọi quá nhiều bước có thể không phù hợp với yêu cầu thực tế.