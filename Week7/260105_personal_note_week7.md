# Attention mechanism

**Attention là gì?**

Attention là cơ chế giúp model tập trung vào những phần quan trọng của input khi tạo ra output.

Trong NLP, không phải tất cả các từ đều có mức độ quan trọng giống nhau. Khi model cần dự đoán một từ hoặc sinh một câu tóm tắt, nó chỉ cần chú ý nhiều hơn đến những phần có liên quan.

Ví dụ, với một bài báo nói về một công ty công bố sản phẩm mới, khi sinh câu tóm tắt model có thể chú ý nhiều đến:

- Tên công ty

- Tên sản phẩm

- Ngày công bố

- Đặc điểm quan trọng của sản phẩm

Các phần ít liên quan sẽ nhận attention weight thấp hơn.

**Vấn đề của encoder–decoder thông thường**

Trong mô hình encoder–decoder không có attention, encoder thường phải nén toàn bộ input vào một vector có độ dài cố định.

```text
Input sequence
→ Encoder
→ Một context vector
→ Decoder
→ Output sequence
```

Cách này có thể hoạt động với câu ngắn. Tuy nhiên, khi input dài, một vector duy nhất khó giữ được tất cả thông tin.

Ví dụ một paper có hàng nghìn từ nhưng encoder chỉ tạo ra một vector cuối cùng. Một số thông tin ở đầu hoặc giữa paper có thể bị mất trước khi decoder tạo summary.

Attention giúp decoder truy cập lại toàn bộ encoder outputs thay vì chỉ dùng final state.

```text
Encoder output 1 ─┐
Encoder output 2 ─┤
Encoder output 3 ─┼→ Attention → Context vector
...              ─┤
Encoder output n ─┘
```

**Attention hoạt động như thế nào?**

Ở mỗi bước của decoder, attention thường thực hiện các bước:

- So sánh trạng thái hiện tại của decoder với các encoder outputs

- Tạo attention score cho từng vị trí của input

- Dùng softmax để chuyển score thành attention weight

- Nhân mỗi encoder output với weight tương ứng

- Cộng các vector lại để tạo context vector

Attention weight thường nằm từ 0 đến 1 và tổng các weight bằng 1.

Ví dụ:

```text
Token input:      công_ty   công_bố   sản_phẩm   mới   hôm_nay
Attention weight:   0.25      0.15       0.40    0.05    0.15
```

Trong bước này, model chú ý nhiều nhất đến token `sản_phẩm`.

**Query, Key và Value**

Attention thường được giải thích bằng ba thành phần:

- Query: thông tin model đang cần tìm

- Key: thông tin dùng để so sánh với query

- Value: nội dung sẽ được lấy ra nếu key phù hợp với query

Trong encoder–decoder attention:

- Query thường là trạng thái của decoder

- Key thường là các encoder outputs

- Value thường cũng là các encoder outputs

Có thể hiểu đơn giản như việc tìm kiếm:

```text
Query: Tôi đang cần thông tin nào?
Key: Vị trí input này có liên quan không?
Value: Nếu có liên quan thì lấy nội dung ở vị trí này.
```

**Attention score**

Attention score cho biết query và key phù hợp với nhau đến mức nào.

Score lớn có nghĩa là vị trí input đó có liên quan nhiều đến bước output hiện tại.

Sau khi có các score, model dùng softmax:

```text
scores
→ softmax
→ attention weights
```

Softmax giúp chuẩn hóa các score thành một phân phối. Nhờ đó model có thể tập trung mạnh vào một vài vị trí hoặc chia sự chú ý cho nhiều vị trí khác nhau.

**Context vector**

Context vector là tổng có trọng số của các value.

```text
context = weight₁ × value₁
        + weight₂ × value₂
        + ...
        + weightₙ × valueₙ
```

Context vector thay đổi ở từng bước decoder.

Khi decoder sinh từ đầu tiên của summary, nó có thể chú ý đến tiêu đề hoặc phần mở đầu. Khi sinh một con số, nó có thể chuyển attention sang vị trí chứa số liệu trong paper.

**Additive attention**

Additive attention còn thường được gọi là Bahdanau attention.

Nó sử dụng một neural network nhỏ để tính mức độ phù hợp giữa query và key.

Ý tưởng đơn giản:

```text
query + key
→ tanh
→ score
→ softmax
→ attention weight
```

Additive attention thường được dùng với RNN, GRU hoặc LSTM encoder–decoder.

Trong TensorFlow có thể sử dụng:

```python
attention = tf.keras.layers.AdditiveAttention(
    use_scale=True
)

context, attention_scores = attention(
    [decoder_outputs, encoder_outputs],
    return_attention_scores=True
)
```

`decoder_outputs` đóng vai trò query.

`encoder_outputs` đóng vai trò key và value.

`context` chứa thông tin được tổng hợp từ encoder.

`attention_scores` có thể được dùng để vẽ heatmap.

**Dot-product attention**

Dot-product attention tính score bằng tích vô hướng giữa query và key.

```text
score = query · key
```

Cách này đơn giản và có thể tính toán nhanh bằng phép nhân ma trận.

Khi số chiều của vector lớn, score có thể trở nên quá lớn. Scaled dot-product attention chia score cho căn bậc hai của số chiều key trước khi dùng softmax.

```text
score = (query · key) / sqrt(d)
```

Scaled dot-product attention là loại attention quan trọng trong Transformer.

**Attention trong text summarization**

Trong bài toán tóm tắt văn bản:

- Encoder đọc article hoặc paper

- Decoder sinh summary từng token

- Ở mỗi bước, attention chọn các phần input có liên quan

Ví dụ:

```text
Paper
→ Encoder outputs

Decoder sinh "the"
→ attention vào phần mở đầu

Decoder sinh "experiment"
→ attention vào phần mô tả phương pháp

Decoder sinh "improves"
→ attention vào phần kết quả
```

Context vector được nối với decoder output rồi đưa vào Dense layer để dự đoán token tiếp theo.

```python
context = attention([
    decoder_outputs,
    encoder_outputs
])

combined = tf.keras.layers.Concatenate()([
    decoder_outputs,
    context
])

probabilities = tf.keras.layers.Dense(
    vocabulary_size,
    activation="softmax"
)(combined)
```

**Masking**

Các câu trong cùng một batch thường được padding để có cùng độ dài.

Model không nên attention vào token padding. Vì vậy mình cần sử dụng mask.

```text
Token:  paper  presents  results  PAD  PAD
Mask:      1       1        1     0    0
```

Các vị trí có mask bằng 0 sẽ không đóng góp vào context vector.

Trong TensorFlow, `Embedding(mask_zero=True)` có thể tạo mask cho token padding có ID bằng 0.

**Self-attention**

Trong encoder–decoder attention, query thường đến từ decoder còn key và value đến từ encoder.

Trong self-attention, query, key và value cùng được tạo từ một sequence.

```text
Input sequence
 ├→ Query
 ├→ Key
 └→ Value
```

Self-attention giúp mỗi token xem xét các token khác trong cùng câu.

Ví dụ trong câu:

```text
The model processes the paper because it is efficient.
```

Token `it` có thể attention đến `model` để học được mối quan hệ giữa hai từ.

Khác với RNN, self-attention không bắt buộc xử lý token lần lượt từ trái sang phải. Vì vậy việc tính toán có thể được song song hóa tốt hơn.

**Causal attention**

Khi model sinh văn bản, token hiện tại không được nhìn thấy các token tương lai.

Causal mask sẽ chặn các vị trí nằm phía sau:

```text
Token 1 được nhìn token 1
Token 2 được nhìn token 1, 2
Token 3 được nhìn token 1, 2, 3
```

Cách này ngăn data leakage trong quá trình training decoder.

**Multi-head attention**

Thay vì chỉ thực hiện attention một lần, multi-head attention sử dụng nhiều attention head.

Mỗi head có thể học một kiểu quan hệ khác nhau:

- Head chú ý đến chủ thể

- Head chú ý đến động từ

- Head chú ý đến con số

- Head chú ý đến quan hệ giữa các câu

Output của các head được nối lại và biến đổi thành representation cuối cùng.

Multi-head self-attention là thành phần chính của Transformer.

**Attention heatmap**

Attention weight có thể được biểu diễn bằng heatmap.

```text
Trục ngang: token trong input
Trục dọc: token được model sinh ra
Màu sáng hơn: attention weight lớn hơn
```

Heatmap giúp mình quan sát model đang tập trung vào đâu và phát hiện một số vấn đề như:

- Chỉ chú ý vào phần đầu văn bản

- Luôn chú ý vào cùng một token

- Không chú ý đến từ khóa quan trọng

- Attention quá phân tán

Tuy nhiên, attention weight không phải lúc nào cũng là lời giải thích đầy đủ cho quyết định của model. Một vị trí có weight lớn không có nghĩa chắc chắn rằng vị trí đó là nguyên nhân duy nhất tạo ra prediction.

**Ưu điểm của attention**

- Giảm việc phải nén toàn bộ input vào một vector duy nhất

- Học được mối liên hệ giữa các vị trí cách xa nhau

- Hữu ích với sequence-to-sequence task

- Có thể trực quan hóa bằng attention heatmap

- Là nền tảng của Transformer

**Nhược điểm của attention**

- Tốn bộ nhớ khi sequence rất dài

- Attention score không bảo đảm output đúng về mặt sự kiện

- Model vẫn có thể lặp từ hoặc tạo thông tin không có trong input

- Heatmap có thể khó giải thích nếu attention phân tán

- Attention không thay thế cho dữ liệu tốt và quá trình đánh giá model