# LLM — Large Language Model

**LLM là gì?**

LLM là viết tắt của Large Language Model, nghĩa là mô hình ngôn ngữ lớn.

Đây là neural network được huấn luyện trên lượng dữ liệu lớn để học các quy luật của ngôn ngữ. Model có thể dùng cho nhiều tác vụ như trả lời câu hỏi, tóm tắt, dịch và viết code, thay vì chỉ dự đoán một nhãn phân loại.

Một câu trả lời nghe tự nhiên không có nghĩa là nội dung chắc chắn đúng. Mình vẫn cần kiểm tra output, nhất là tên riêng, số liệu và nguồn tham khảo.

**Liên hệ với Transformer**

Nhiều LLM sinh văn bản sử dụng kiến trúc Transformer. Self-attention giúp model kết hợp thông tin giữa các token trong ngữ cảnh.

Với model sinh văn bản theo kiểu autoregressive, quá trình cơ bản là:

```text
Prompt → Tokenization → Model → Dự đoán token tiếp theo
                                  ↓
                         Nối token vào ngữ cảnh
                                  ↓
                         Tiếp tục sinh hoặc dừng
```

Model không nhất thiết tạo toàn bộ câu trong một bước. Nó sinh tiếp dựa trên input và những token đã có. Phần kiến trúc được ghi lại trong [note Transformer](<D:/Sudo code 2026/transformer-model-notes.md>).

**Pretraining, fine-tuning và inference**

Pretraining là giai đoạn model học từ dữ liệu lớn. Với nhiều model sinh văn bản, một mục tiêu quan trọng là dự đoán token tiếp theo từ các token trước đó.

Sau đó, model có thể trải qua các bước huấn luyện bổ sung để làm theo hướng dẫn và đáp ứng yêu cầu tốt hơn. Fine-tuning cập nhật trọng số của model trên dữ liệu huấn luyện bổ sung.

Inference là lúc mình sử dụng model để tạo câu trả lời. Gửi một prompt thông thường không có nghĩa là mình đang fine-tune hoặc trực tiếp cập nhật trọng số của model.

**Token và context window**

Model xử lý văn bản dưới dạng token. Một token có thể là một phần của từ, dấu câu hoặc một chuỗi ký tự; không nên hiểu một token luôn bằng một từ. Hai tokenizer khác nhau có thể đếm cùng đoạn văn ra số token khác nhau. Xem [khái niệm token của OpenAI](https://developers.openai.com/api/docs/concepts).

Context window là giới hạn ngữ cảnh model có thể xử lý trong một lần làm việc. Khi chuẩn bị input, mình cần chừa chỗ cho output và các token nội bộ theo giới hạn của model. Context lớn không bảo đảm model sẽ sử dụng đúng mọi chi tiết trong tài liệu dài. Xem [cách tính token của Gemini](https://ai.google.dev/gemini-api/docs/tokens?hl=vi).

**Prompt là gì?**

Prompt là nội dung mình đưa cho model, gồm yêu cầu, dữ liệu và những ràng buộc cần tuân theo.

Ví dụ prompt tóm tắt:

```text
Tóm tắt đoạn văn dưới đây bằng tiếng Việt trong đúng 2 câu.
Giữ các số liệu quan trọng. Không thêm thông tin ngoài đoạn văn.

Đoạn văn:
[Nội dung cần tóm tắt]
```

Với QA, mình có thể yêu cầu: “Chỉ dựa vào đoạn văn để trả lời. Nếu không có đáp án, hãy nói không có thông tin”.

Prompt rõ giúp định hướng output nhưng không bảo đảm model luôn làm đúng. Mình nên tách yêu cầu khỏi phần dữ liệu, chỉ rõ độ dài và định dạng mong muốn. Tham khảo [hướng dẫn viết prompt của OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering).

**Dùng LLM qua API**

Khi dùng API, code của mình gửi yêu cầu đến dịch vụ đang phục vụ model rồi nhận phản hồi. Mình không phải tự train hoặc tải toàn bộ model về máy.

Các phần thường cần chuẩn bị là API key, tên model, prompt và cấu hình sinh output.

OpenAI có Responses API để tạo phản hồi từ prompt. Cách gọi và đọc output được hướng dẫn trong [tài liệu tạo văn bản OpenAI](https://developers.openai.com/api/docs/guides/text).

Google cung cấp Gemini API để sử dụng các model Gemini. Khả năng xử lý văn bản, hình ảnh, âm thanh hoặc tài liệu phụ thuộc model và API cụ thể; không phải model nào cũng hỗ trợ giống nhau. Xem [tài liệu Gemini tiếng Việt](https://ai.google.dev/gemini-api/docs?hl=vi).

ChatGPT là ứng dụng, còn OpenAI API là cách tích hợp model vào chương trình của mình. Trong notebook so sánh, tên “ChatGPT” là nhãn dễ đọc cho model được gọi qua OpenAI API, không phải thao tác trên website ChatGPT.

**Một số cấu hình cần chú ý**

- Tên model: quyết định model được sử dụng; cần kiểm tra quyền truy cập của tài khoản.

- Giới hạn output: giới hạn số token được sinh. Giới hạn quá thấp có thể khiến câu trả lời bị cắt.

- Temperature: với model hỗ trợ, tham số này ảnh hưởng cách lấy mẫu token. Không nên coi temperature thấp là bảo đảm đúng hoặc luôn tái lập được output.

- Thinking hoặc reasoning: một số model có cấu hình dành cho suy luận, có thể ảnh hưởng số token, thời gian và chi phí.

Tên tham số và khả năng hỗ trợ khác nhau giữa các model/API. Mình cần xem tài liệu thay vì chuyển nguyên cấu hình từ bên này sang bên kia. Tham khảo [tạo văn bản với Gemini](https://ai.google.dev/gemini-api/docs/text-generation?hl=vi).

**Hallucination**

Hallucination là khi model tạo thông tin sai hoặc không được dữ liệu nguồn hỗ trợ nhưng trình bày như một điều đúng.

Ví dụ lỗi giả định: nguồn chỉ nói điểm trung bình tăng sau khi dùng ứng dụng, nhưng model lại kết luận ứng dụng chắc chắn là nguyên nhân làm điểm tăng, dù nghiên cứu không có nhóm đối chứng.

Khi tóm tắt, mình cần kiểm tra cả thông tin được giữ lại lẫn thông tin model thêm vào. Đếm đủ từ khóa chưa chứng minh bản tóm tắt đúng nghĩa.

**Prompting, RAG và fine-tuning khác nhau thế nào?**

- Prompting: thay đổi hướng dẫn, ví dụ hoặc dữ liệu đưa vào ngữ cảnh, không trực tiếp cập nhật trọng số.

- RAG: tìm các đoạn tài liệu liên quan rồi đưa vào ngữ cảnh để model trả lời dựa trên chúng.

- Fine-tuning: huấn luyện bổ sung để cập nhật trọng số model.

RAG giúp cung cấp tài liệu nhưng vẫn có thể lấy nhầm nguồn hoặc model diễn giải sai. Fine-tuning cũng không thay thế việc kiểm chứng câu trả lời.

**Đánh giá độ chính xác**

Với QA, mình chuẩn bị đáp án trước rồi đối chiếu output. Exact Match kiểm tra câu trả lời có khớp đáp án sau chuẩn hóa không; cách diễn đạt đúng nhưng khác đáp án mẫu có thể vẫn bị chấm sai.

Với tóm tắt, mình kiểm tra ý chính, số liệu, phủ định, thông tin bị bỏ sót và thông tin được thêm vào. Độ phủ ý chính hoặc ROUGE chỉ phản ánh một phần chất lượng, không phải phép đo đầy đủ về độ đúng sự kiện.

Mình nên dùng nhiều ví dụ và kết hợp chấm tự động với đọc thủ công. Chỉ một câu đúng chưa chứng minh model tốt trên mọi tác vụ. Xem [hướng dẫn đánh giá của OpenAI](https://developers.openai.com/api/docs/guides/evaluation-best-practices).

**Tốc độ và chi phí**

Trong notebook, tốc độ được đo bằng thời gian từ lúc gửi request đến khi nhận toàn bộ phản hồi. Số đo này có cả độ trễ mạng, không chỉ thời gian tính toán của model.

Chi phí text thường phụ thuộc số token input và output cùng đơn giá của model. Với bảng giá có cached input, cách tính cơ bản là:

```text
Chi phí ≈ ((input - cached) × giá input
          + cached × giá cached
          + output tính phí × giá output) / 1.000.000
```

Công thức trên dùng giá theo một triệu token, chưa gồm phí khác nếu có. Mình lấy usage từ API, không ước lượng hóa đơn bằng số từ. Output tính phí có thể gồm token không hiển thị; không tự cộng reasoning lần nữa nếu đã nằm trong bộ đếm output. Xem [cách đọc token usage OpenAI](https://developers.openai.com/api/docs/guides/token-counting).

Giá/model có thể thay đổi; cần kiểm tra [bảng giá OpenAI](https://developers.openai.com/api/docs/pricing) và [bảng giá Gemini](https://ai.google.dev/gemini-api/docs/pricing?hl=vi). Ước tính theo giá niêm yết không nhất thiết bằng hóa đơn sau free tier, credits hoặc thuế.