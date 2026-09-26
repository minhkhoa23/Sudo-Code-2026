# Sequence model và LSTM

**Sequence model**

Sequence model là mô hình được thiết kế để xử lý dữ liệu có thứ tự.

Ví dụ về dữ liệu dạng chuỗi:

- Các từ trong một câu

- Các câu trong một đoạn văn

- Các khung hình trong video

- Dữ liệu âm thanh theo thời gian

- Giá cổ phiếu qua từng ngày

Trong NLP, thứ tự của từ rất quan trọng. Hai câu có cùng các từ nhưng thứ tự khác nhau có thể mang ý nghĩa khác nhau.

Ví dụ:

```text
Tôi gửi tài liệu cho anh Nam.
Anh Nam gửi tài liệu cho tôi.
```

Nếu mình chỉ lấy trung bình các word embedding thì hai câu có thể được biểu diễn gần giống nhau. Sequence model sẽ đọc các token theo đúng thứ tự để giữ lại thông tin này.

**Recurrent Neural Network**

RNN là một loại sequence model. RNN đọc từng phần tử của chuỗi và truyền thông tin từ bước trước sang bước sau.

Ở thời điểm `t`, RNN nhận:

- Input hiện tại `x_t`

- Hidden state của bước trước `h_(t-1)`

Sau đó RNN tạo ra hidden state mới `h_t`.

Hidden state có thể được hiểu là bộ nhớ tóm tắt những gì model đã đọc trước đó.

Ví dụ khi đọc câu:

```text
hôm nay trời rất đẹp
```

RNN sẽ đọc lần lượt `hôm` → `nay` → `trời` → `rất` → `đẹp`. Sau mỗi từ, hidden state được cập nhật và truyền sang từ tiếp theo.

RNN dùng lại cùng một bộ weight ở mọi bước. Vì vậy model có thể xử lý các câu có độ dài khác nhau.

**Các dạng sequence model**

Sequence model có thể được dùng theo nhiều cách:

- Many-to-one: nhận một câu và trả về một nhãn, ví dụ phân loại chủ đề văn bản

- One-to-many: nhận một input và tạo ra một chuỗi, ví dụ tạo mô tả cho hình ảnh

- Many-to-many: nhận một chuỗi và trả về một chuỗi, ví dụ dịch máy hoặc gắn nhãn cho từng token

Trong bài toán phân loại văn bản VNTC, mình sử dụng dạng many-to-one vì toàn bộ văn bản chỉ cần dự đoán một chủ đề.

**Vấn đề của RNN thông thường**

RNN có thể ghi nhớ thông tin gần khá tốt nhưng thường gặp khó khăn khi thông tin quan trọng nằm quá xa.

Ví dụ:

```text
Tôi lớn lên ở Việt Nam ... Tôi nói thành thạo tiếng Việt.
```

Để dự đoán từ `Việt`, model cần nhớ thông tin `Việt Nam` đã xuất hiện từ trước đó.

Khi train RNN, gradient được truyền ngược qua nhiều bước thời gian. Gradient có thể trở nên rất nhỏ hoặc rất lớn.

- Vanishing gradient: gradient ngày càng nhỏ, model khó học được quan hệ dài hạn

- Exploding gradient: gradient trở nên quá lớn, quá trình training không ổn định

Gradient clipping có thể giúp hạn chế exploding gradient. Tuy nhiên, RNN thông thường vẫn khó xử lý long-term dependency.

**LSTM**

LSTM là viết tắt của Long Short-Term Memory. Đây là một loại RNN được thiết kế để học các mối quan hệ dài hạn tốt hơn.

Điểm quan trọng của LSTM là `cell state`. Cell state giống như một đường truyền bộ nhớ chạy qua các bước của chuỗi.

LSTM có thể quyết định:

- Thông tin nào cần quên

- Thông tin mới nào cần ghi nhớ

- Thông tin nào cần đưa ra output

Các quyết định này được điều khiển bằng các gate.

**Sigmoid và tanh**

Các gate thường sử dụng hàm sigmoid. Sigmoid tạo ra giá trị từ 0 đến 1.

- Giá trị gần 0: chặn hoặc bỏ thông tin

- Giá trị gần 1: cho thông tin đi qua

Hàm `tanh` tạo ra giá trị từ -1 đến 1. Nó thường được dùng để tạo thông tin mới hoặc điều chỉnh nội dung của cell state.

**Forget gate**

Forget gate quyết định phần nào của cell state cũ cần được giữ lại hoặc loại bỏ.

Ví dụ, khi model gặp một chủ thể mới trong câu, thông tin về chủ thể cũ có thể không còn cần thiết. Forget gate có thể giảm ảnh hưởng của thông tin cũ đó.

Có thể hiểu đơn giản:

```text
Thông tin cũ × mức độ cần giữ
```

Nếu gate trả về gần 1 thì thông tin được giữ lại. Nếu trả về gần 0 thì thông tin bị quên đi.

**Input gate**

Input gate quyết định thông tin mới nào cần được ghi vào cell state.

Bước này gồm hai ý:

- Chọn phần thông tin cần cập nhật

- Tạo ra các giá trị mới có thể được thêm vào bộ nhớ

Cell state mới là sự kết hợp giữa phần thông tin cũ được giữ lại và phần thông tin mới được thêm vào.

**Output gate**

Output gate quyết định phần nào của cell state sẽ được đưa ra hidden state hiện tại.

Hidden state là thông tin LSTM gửi sang bước tiếp theo và cũng có thể được sử dụng để tạo prediction.

Như vậy, ba gate có thể được nhớ đơn giản như sau:

```text
Forget gate: cần quên gì?
Input gate: cần nhớ thêm gì?
Output gate: cần đưa thông tin gì ra ngoài?
```

**Cell state và hidden state**

LSTM có hai trạng thái chính:

- Cell state `C_t`: bộ nhớ dài hạn

- Hidden state `h_t`: thông tin đầu ra ngắn hạn tại bước hiện tại

Cell state giúp thông tin đi qua nhiều bước với ít thay đổi hơn. Các gate chỉ thêm hoặc loại bỏ những phần cần thiết nên LSTM có khả năng giữ thông tin dài hạn tốt hơn RNN thông thường.

**LSTM trong TensorFlow**

Một mô hình phân loại văn bản đơn giản có thể được tạo như sau:

```python
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 128, mask_zero=True),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(num_classes, activation="softmax")
])
```

`Embedding` chuyển token thành vector.

`LSTM` đọc chuỗi vector theo thứ tự và trả về hidden state cuối cùng.

`Dense` dùng hidden state đó để dự đoán class của văn bản.

`mask_zero=True` giúp model bỏ qua các token padding có giá trị 0.

Nếu mình muốn LSTM trả về output ở mọi bước thời gian thì dùng:

```python
tf.keras.layers.LSTM(64, return_sequences=True)
```

Điều này cần thiết khi mình muốn nối thêm một LSTM khác hoặc cần dự đoán cho từng token.

**Bidirectional LSTM**

LSTM thông thường đọc câu từ trái sang phải. Bidirectional LSTM đọc theo cả hai hướng:

```text
trái → phải
trái ← phải
```

Nhờ đó, biểu diễn của một từ có thể sử dụng cả thông tin đứng trước và đứng sau nó.

Ví dụ trong TensorFlow:

```python
tf.keras.layers.Bidirectional(
    tf.keras.layers.LSTM(64)
)
```

Bidirectional LSTM thường hữu ích cho phân loại văn bản hoặc gắn nhãn chuỗi khi toàn bộ câu đã có sẵn. Nó không phù hợp với trường hợp chỉ được phép sử dụng thông tin trong quá khứ để dự đoán tương lai.

**Ưu điểm và nhược điểm của LSTM**

Ưu điểm:

- Giữ thứ tự của token

- Học long-term dependency tốt hơn RNN thông thường

- Có thể xử lý chuỗi có độ dài khác nhau

- Phù hợp với phân loại văn bản, dự đoán chuỗi và gắn nhãn token

Nhược điểm:

- Training chậm vì phải xử lý chuỗi theo từng bước

- Có nhiều tham số hơn RNN thông thường

- Khó song song hóa hơn CNN và Transformer

- Với chuỗi rất dài, LSTM vẫn có thể bỏ sót thông tin

**LSTM và GRU**

GRU là một biến thể đơn giản hơn của LSTM.

GRU kết hợp một số gate và không tách riêng cell state với hidden state. Vì vậy GRU thường có ít tham số hơn và có thể train nhanh hơn.

Không có mô hình nào luôn tốt hơn trong mọi bài toán. Mình nên thử cả LSTM và GRU rồi so sánh trên validation set.
