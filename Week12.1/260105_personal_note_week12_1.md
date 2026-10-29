# Deploy model bằng Flask / FastAPI

**Deploy model là gì?**

Deploy model là đưa model đã huấn luyện vào một chương trình để có thể sử dụng nó. Trong bài này, mình đưa model thành một web API: chương trình khác gửi văn bản và nhận kết quả phân loại.

Ví dụ, model VNTC đã học cách phân loại tin tức. Sau khi deploy, mình gửi một bài báo đến API và nhận chủ đề như `The thao`, `Suc khoe` hoặc `Vi tinh`.

Deploy có thể bắt đầu ngay trên máy cá nhân. Muốn người khác truy cập qua Internet thì cần thêm môi trường chạy và cấu hình mạng phù hợp.

**Training, inference và deployment**

| Khái niệm | Mình làm gì? |
| --- | --- |
| Training | Dùng dữ liệu để học trọng số của model |
| Inference | Dùng model đã học để dự đoán input mới |
| Deployment | Chuẩn bị model, code và môi trường để phục vụ dự đoán |

Trong bài thực hành, server không train lại mỗi khi nhận câu hỏi. Nó nạp model đã lưu và chạy inference.

**Quy trình cơ bản**

```text
Train → Lưu model → Viết API → Chạy server → Gửi request → Kiểm tra kết quả
```

Khi API nhận văn bản, luồng xử lý là:

```text
Văn bản → Kiểm tra input → Tiền xử lý → Model → Chọn nhãn → JSON response
```

API giúp mình sử dụng model từ notebook, website hoặc ứng dụng khác mà không phải chép toàn bộ code training vào từng nơi.

**Cần lưu những gì sau khi train?**

Mình cần lưu trọng số, cấu hình model và các thành phần dùng để xử lý input/output, như vocabulary, tokenizer và danh sách nhãn.

Nếu model dự đoán class có ID 7 nhưng mình đọc sai thứ tự nhãn thì kết quả hiển thị vẫn có thể sai, dù trọng số được nạp đúng.

Trong bài VNTC, TensorFlow SavedModel giữ graph, trọng số và TextVectorization. `labels.json` giữ danh sách nhãn theo đúng thứ tự training. Model được nạp bằng `tf.saved_model.load()` rồi gọi endpoint `serve`.

Mình không gọi lại `adapt()` trên văn bản người dùng. Thay đổi vocabulary hoặc cách chuẩn hóa có thể làm input khác với lúc model được huấn luyện.

**Flask và FastAPI**

Flask là framework để viết ứng dụng web bằng Python. Mình có thể viết route nhận dữ liệu, gọi model và trả JSON. Flask là ứng dụng WSGI và cần server WSGI phù hợp khi triển khai production. 

FastAPI hỗ trợ xây API bằng type hints, kiểm tra dữ liệu với Pydantic và tạo tài liệu API tương tác. Trong bài thực hành, mình dùng FastAPI để khai báo input và thử request tại `/docs`.

| Điểm so sánh | Flask | FastAPI |
| --- | --- | --- |
| Viết endpoint | Khai báo route | Khai báo path operation |
| Kiểm tra input | Tự xử lý hoặc bổ sung thư viện | Tích hợp schema bằng Pydantic |
| Tài liệu API | Cần thiết lập thêm | Có tài liệu tương tác tự động |
| Server thường dùng | Server WSGI, ví dụ Waitress | Server ASGI, ví dụ Uvicorn |

Cả hai đều có thể phục vụ NLP model. Chọn FastAPI không tự làm phép tính của neural network nhanh hơn; mình vẫn cần đo thời gian thực tế. Các lựa chọn server được giới thiệu trong [Flask deployment](https://flask.palletsprojects.com/en/stable/deploying/) và [FastAPI: chạy server](https://fastapi.tiangolo.com/deployment/manually/).

**Request và response**

Endpoint là một địa chỉ để sử dụng chức năng của API. Trong demo của mình:

- `GET /health`: kiểm tra model đã sẵn sàng.
- `GET /labels`: xem danh sách nhãn.
- `POST /predict`: gửi văn bản để phân loại.

Ví dụ JSON gửi đến `/predict`:

```json
{
  "text": "Đội tuyển bóng đá Việt Nam giành chiến thắng trong trận chung kết.",
  "top_k": 3
}
```

Response của demo có `label`, `score`, danh sách `top_k`, `inference_ms` và `model_id`. `top_k` là các chủ đề có điểm cao nhất, không phải số câu hỏi gửi đi.

`score` là điểm softmax. Điểm cao không bảo đảm dự đoán đúng, nhất là khi văn bản khác loại dữ liệu training.

**Kiểm tra input**

API cần kiểm tra kiểu dữ liệu, trường bắt buộc và độ dài văn bản trước khi gọi model. Điều này giúp phát hiện lỗi sớm và tránh xử lý input quá lớn.

Trong demo VNTC, `text` phải có chữ hoặc số, tối đa 20.000 ký tự; `top_k` phải là số nguyên từ 1 đến 10. Input sai schema trả HTTP 422, lỗi chạy model trả HTTP 500. Đây là quy định của API mình viết. FastAPI hỗ trợ khai báo các điều kiện qua schema;

Giới hạn ký tự của API khác giới hạn token của model. TextVectorization trong model VNTC chỉ dùng 400 token đầu, nên văn bản được API chấp nhận vẫn có thể bị cắt khi đưa vào model.

**Nạp model một lần**

Đọc model từ ổ đĩa ở mỗi request sẽ làm tăng thời gian xử lý. Với FastAPI, mình dùng `lifespan` để nạp và warm-up model trước khi server nhận request, sau đó dùng lại model cho các lần dự đoán.

Warm-up là chạy thử một input để model sẵn sàng và phát hiện lỗi nạp model. Nếu thiếu artifact, server nên báo lỗi rõ ràng khi khởi động.

Việc nạp một lần ở đây là **mỗi worker process**. Nếu chạy nhiều worker, mỗi process thường có bộ nhớ riêng và có thể nạp thêm một bản model, làm tăng RAM.
**Chạy API trên máy**

Sau khi cài dependency theo [hướng dẫn của demo](<D:/Sudo code 2026/nlp_fastapi_deployment/README.md>), mình chạy lệnh sau trong thư mục chứa project bằng môi trường Python đã chuẩn bị:

```shell
python -m uvicorn main:app --app-dir nlp_fastapi_deployment --host 127.0.0.1 --port 8000
```

`main:app` chỉ object `app` trong file `main.py`. `--app-dir` cho Uvicorn biết nơi tìm file này. Uvicorn chạy ứng dụng FastAPI và phục vụ request HTTP.

Khi server sẵn sàng, mình có thể mở `/docs` để thử API trên máy đang chạy server. Địa chỉ `127.0.0.1` là localhost của môi trường đó, không tự tạo đường dẫn công khai cho người khác.

**Development và production**

Development là giai đoạn viết, sửa và thử code. Production là môi trường phục vụ ứng dụng để sử dụng thực tế, kể cả khi chỉ dùng trong nội bộ.

Flask ghi rõ không dùng development server cho production. Khi triển khai cần chọn server phù hợp, thay vì coi `flask run` là cấu hình phục vụ lâu dài.

Với FastAPI, `--reload` tiện khi sửa code vì server tự khởi động lại, nhưng không nên dùng trong production.

Khi đưa API lên máy chủ, mình cần quan tâm HTTPS, quyền truy cập, giới hạn tải, RAM và cách khởi động lại khi process lỗi. Ghi lại version thư viện và model giúp việc chạy lại hoặc quay về bản trước dễ hơn.

**Đánh giá sau khi deploy**

Mình cần kiểm tra cả chức năng API và chất lượng dự đoán:

- API có nhận và trả đúng dữ liệu không? Input sai có được xử lý rõ không?
- Cùng một input, API có trả kết quả giống khi gọi trực tiếp model không?
- Accuracy và macro-F1 trên dữ liệu có nhãn là bao nhiêu?
- Request mất bao lâu? Server dùng bao nhiêu RAM khi có nhiều request?

Accuracy đo tỷ lệ dự đoán đúng. Latency đo thời gian phản hồi. Hai giá trị này nói về hai mặt khác nhau của hệ thống.

`inference_ms` trong demo chỉ đo gọi model và xếp hạng. HTTP round trip còn có validation, chờ xử lý, truyền dữ liệu và đọc JSON, nên không nên dùng hai phép đo thay cho nhau.

**Những gì mình học từ bài VNTC**

Trong [notebook triển khai](<D:/Sudo code 2026/Deploy_NLP_FastAPI.ipynb>), mình dùng lại model TensorFlow đã train và chạy FastAPI trên CPU ở máy local.

Theo [báo cáo triển khai](<D:/Sudo code 2026/nlp_fastapi_deployment/DEPLOYMENT_REPORT.md>), 20 kiểm tra HTTP đều đạt. Trên tập con 100 mẫu test, accuracy qua API là 87%, macro-F1 khoảng 0,8637; cả 100 dự đoán đều trùng với khi gọi trực tiếp SavedModel.

Với 30 request tuần tự sau warm-up, HTTP round trip trung bình khoảng 1,97 ms trên localhost. Đây không phải kết quả load test nhiều người dùng hoặc độ trễ khi chạy trên cloud.

Kết quả 87,6% accuracy trên 8.000 mẫu thuộc lần đánh giá model trước đó. Tập 100 mẫu khi kiểm tra deployment khác phạm vi, nên mình không kết luận model bị giảm chất lượng chỉ từ hai số này.

**Demo trên Colab**

Trên Colab, mình cần upload cả code lẫn artifact và kiểm tra dependency của runtime. `127.0.0.1` khi gọi từ notebook trỏ tới máy chạy runtime, nên link đó không trực tiếp mở API trên trình duyệt máy cá nhân.

Runtime có thể bị ngắt và tài nguyên không được giữ vô thời hạn. Mình nên dùng Colab cho phần thực hành trong notebook và lưu kết quả cần thiết; không coi đó là một API luôn hoạt động.