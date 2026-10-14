# Transformer model

**Transformer là gì?**

Transformer là một kiến trúc neural network dùng attention để xử lý dữ liệu dạng chuỗi.

Trong NLP, Transformer có thể được dùng cho dịch máy, phân loại văn bản, tóm tắt và sinh văn bản.

Kiến trúc Transformer ban đầu được giới thiệu trong paper [Attention Is All You Need](https://arxiv.org/abs/1706.03762) năm 2017. Nó sử dụng attention để trao đổi thông tin giữa các token, thay cho việc truyền hidden state lần lượt như RNN.

**Transformer và LSTM**

LSTM đọc chuỗi theo từng bước:

```text
Token 1 → Token 2 → Token 3 → Token 4
```

Thông tin từ token trước được truyền sang token sau qua hidden state và cell state.

Transformer dùng self-attention để mỗi token kết hợp thông tin từ các vị trí được phép nhìn trong chuỗi. Khi training, nhiều vị trí có thể được tính song song nên phù hợp với GPU.

Tuy nhiên, khi sinh văn bản theo kiểu autoregressive, Transformer vẫn cần tạo token tiếp theo dựa trên các token đã sinh. Vì vậy, sinh một câu không hoàn toàn song song như lúc training.

**Encoder và decoder**

Transformer ban đầu có hai phần chính:

- Encoder: đọc câu nguồn và tạo biểu diễn theo ngữ cảnh cho từng token.

- Decoder: dùng biểu diễn của encoder và các token đích trước đó để sinh câu đích.

Ví dụ dịch Anh → Việt:

```text
I like learning.
       ↓
Tokenizer → Embedding + thông tin vị trí
       ↓
Encoder → Biểu diễn của câu tiếng Anh
       ↓
Decoder → Dự đoán token tiếng Việt tiếp theo
       ↓
Tôi thích học.
```

Đây là dạng sequence-to-sequence: input và output đều là chuỗi, nhưng độ dài không cần giống nhau.

**Tokenization và embedding**

Trước khi đưa câu vào model, mình chuyển văn bản thành token rồi thành token ID.

Token có thể là từ, ký tự hoặc subword. Một từ ít gặp có thể được chia thành nhiều subword để model xử lý dễ hơn.

Embedding chuyển mỗi token ID thành một vector được học trong quá trình training.

Ví dụ, `d_model = 96` có nghĩa là mỗi vị trí được biểu diễn bằng một vector 96 chiều trong các block của model.

**Positional encoding**

Self-attention thông thường không tự biết thứ tự của token nếu không có thông tin vị trí.

Hai câu có cùng các từ nhưng khác ý nghĩa. Model cần biết từ nào đứng trước và từ nào đứng sau.

Positional encoding đưa thông tin vị trí vào biểu diễn token:

```text
Biểu diễn đầu vào = token embedding + positional encoding
```

Transformer ban đầu dùng các hàm sin và cos. Một số model khác học positional embedding hoặc sử dụng cách biểu diễn vị trí khác.

**Self-attention**

Self-attention giúp một token kết hợp thông tin từ các token khác trong cùng chuỗi.

Ví dụ trong câu `Lan đọc sách vì cô ấy thích học`, biểu diễn của `cô ấy` có thể sử dụng thông tin từ `Lan` để học mối liên hệ giữa hai phần của câu.

Query, Key và Value được tạo bằng các phép biến đổi có tham số học được:

- Query: token hiện tại cần tìm thông tin gì?

- Key: token khác có phù hợp với query không?

- Value: nội dung được tổng hợp từ vị trí đó.

Trong self-attention, Q, K và V cùng xuất phát từ một chuỗi, nhưng không nhất thiết là các vector giống nhau.

**Scaled dot-product attention**

Công thức chính:

```text
Attention(Q, K, V) = softmax(QKᵀ / sqrt(d_k))V
```

`QKᵀ` tạo score giữa các query và key. Chia cho `sqrt(d_k)` giúp kiểm soát độ lớn của score khi chiều vector tăng.

Softmax chuyển score thành attention weight. Model dùng các weight này để lấy tổng có trọng số của Value.

**Multi-head attention**

Multi-head attention thực hiện attention qua nhiều head với các phép chiếu Q, K, V riêng.

Các head có thể học những mối quan hệ khác nhau. Mình không quy định sẵn head nào phải học chủ ngữ, động từ hay số liệu.

Output của các head được nối lại rồi biến đổi về biểu diễn đầu ra.

Ví dụ khi `d_model = 96` và có 4 head, mỗi head có thể dùng key dimension bằng `96 / 4 = 24`.

**Encoder block**

Một encoder block theo cấu trúc ban đầu gồm:

```text
Input
→ Multi-head self-attention
→ Residual connection + Layer normalization
→ Feed-forward network
→ Residual connection + Layer normalization
→ Output
```

Feed-forward network thường có hai Dense layer, có activation ở giữa. Cùng một mạng được áp dụng riêng cho từng vị trí của chuỗi.

Residual connection cộng input của một sublayer vào output của nó, giúp thông tin và gradient đi qua nhiều layer dễ hơn.

Layer normalization chuẩn hóa các chiều đặc trưng ở mỗi vị trí. Dropout giúp hạn chế overfitting.

Stack nhiều encoder block giúp model học biểu diễn qua nhiều mức xử lý.

**Decoder block và cross-attention**

Decoder có ba phần xử lý chính: causal self-attention, cross-attention và feed-forward network. Các phần này cũng đi cùng residual connection và layer normalization.

Causal self-attention dùng các token đích đã có. Cross-attention kết nối decoder với câu nguồn:

```text
Query: biểu diễn từ decoder
Key:   encoder outputs
Value: encoder outputs
```

Ví dụ khi sinh từ `học`, decoder có thể chú ý đến phần câu nguồn chứa `learning`.

**Padding mask**

Các câu trong một batch thường có độ dài khác nhau. Câu ngắn được thêm PAD để có cùng kích thước tensor.

```text
Token: tôi  thích  học  PAD  PAD
Mask:   1     1     1    0    0
```

Padding mask ngăn attention lấy thông tin từ các key PAD. Khi tính loss và accuracy, mình cũng cần bỏ các vị trí label PAD.

Nếu tính cả PAD, accuracy có thể cao vì model dự đoán đúng nhiều token padding, trong khi các token thật vẫn sai.

**Causal mask**

Khi dự đoán token tiếp theo, decoder không được nhìn token đích tương lai.

```text
Vị trí 1 được nhìn vị trí 1
Vị trí 2 được nhìn vị trí 1, 2
Vị trí 3 được nhìn vị trí 1, 2, 3
```

Causal mask giữ quy tắc này cả lúc training. Nếu không có mask, decoder có thể nhìn đáp án tương lai và kết quả training sẽ gây hiểu nhầm.

Encoder trong bài toán dịch thường được nhìn toàn bộ câu nguồn vì câu nguồn đã có sẵn.

**Multi-head attention trong TensorFlow**

Ví dụ dưới chỉ minh họa một lớp self-attention trên các vector đầu vào:

```python
import tensorflow as tf

x = tf.random.normal(shape=(2, 5, 64))

attention = tf.keras.layers.MultiHeadAttention(
    num_heads=4,
    key_dim=16,
    dropout=0.1,
)

output, scores = attention(
    query=x,
    value=x,
    return_attention_scores=True,
    training=False,
)

print(output.shape)  # (2, 5, 64)
print(scores.shape)  # (2, 4, 5, 5)
```

`key_dim` là số chiều key/query của mỗi head. `scores` có thứ tự chiều: batch, head, query position, key position.

Với decoder self-attention, có thể truyền thêm `use_causal_mask=True`. Padding mask được truyền qua `attention_mask`; giá trị `True` nghĩa là được phép attention.

Transformer đầy đủ còn cần embedding, thông tin vị trí, feed-forward, normalization và các lớp đầu ra. Xem [TensorFlow MultiHeadAttention](https://www.tensorflow.org/api_docs/python/tf/keras/layers/MultiHeadAttention).

**Training bằng teacher forcing**

Trong bài toán dịch, model học dự đoán token đích tiếp theo từ câu nguồn và prefix đích đúng.

```text
Target:        BOS  Tôi    thích  học  EOS
Decoder input: BOS  Tôi    thích  học
Label:         Tôi  thích  học    EOS
```

Input và label của decoder lệch nhau một vị trí. Causal mask giúp model chỉ nhìn prefix được phép, dù nhiều vị trí được tính cùng lúc.

Dense layer cuối trả logits cho vocabulary đích. Cross-entropy so sánh logits với label, bỏ qua PAD. Các bước này được minh họa trong [TensorFlow Transformer tutorial](https://www.tensorflow.org/text/tutorials/transformer).

**Sinh bản dịch khi inference**

Lúc inference, model không có reference để dùng làm prefix.

```text
BOS
→ Tôi
→ thích
→ học
→ EOS
```

Mỗi token mới được nối vào prefix. Model dừng khi sinh EOS hoặc đạt giới hạn độ dài.

Greedy decoding chọn token có xác suất cao nhất ở từng bước. Beam search giữ nhiều chuỗi ứng viên để tìm một bản dịch tốt hơn theo cách chấm điểm đã chọn.

Beam search không bảo đảm bản dịch đúng nghĩa nếu model chưa học tốt.

**Các dạng Transformer**

Không phải Transformer nào cũng có cả encoder và decoder:

| Kiến trúc | Vai trò thường gặp | Ví dụ |
| --- | --- | --- |
| Encoder-only | Tạo biểu diễn để phân loại, gắn nhãn hoặc trích xuất câu trả lời | BERT |
| Decoder-only | Sinh token tiếp theo từ prefix | GPT |
| Encoder–decoder | Nhận chuỗi nguồn và sinh chuỗi đích | Transformer dịch máy, T5 |

[BERT](https://arxiv.org/abs/1810.04805) học biểu diễn dùng ngữ cảnh hai phía. [GPT-2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) dùng Transformer để sinh văn bản theo prefix. [T5](https://arxiv.org/abs/1910.10683) biểu diễn nhiều bài toán NLP dưới dạng text-to-text.

**Train từ đầu và fine-tuning**

Train từ đầu nghĩa là bắt đầu với các weight chưa được học từ corpus khác. Model phải học cả biểu diễn ngôn ngữ và bài toán của mình từ dữ liệu training.

Fine-tuning bắt đầu từ một model đã được pretrain, rồi cập nhật weight trên dữ liệu của bài toán mới.

Notebook EVBCorpus của mình train từ đầu. Vì vậy, một cấu hình nhỏ không có sẵn khả năng ngôn ngữ như một model pretrained lớn.

**Đánh giá chất lượng dịch**

Training loss và token accuracy dùng teacher forcing. Lúc dịch thật, model sử dụng các token do chính nó sinh ra nên một lỗi có thể ảnh hưởng đến các bước sau.

Mình cần sinh bản dịch trên test rồi so với reference bằng BLEU, chrF và đọc câu mẫu. Đặc biệt cần kiểm tra tên riêng, số liệu, phủ định, nội dung bị bỏ sót và lặp từ.

Tokenizer chỉ học từ train. Validation dùng để chọn checkpoint hoặc cấu hình; test dùng để đánh giá sau khi đã chốt lựa chọn.

**Những gì mình học từ notebook EVBCorpus**

Lần chạy QUICK_RUN đính kèm dùng 5.918 cặp train, 400 validation và 300 test, trong 12 epoch.

Model có 2 encoder block và 2 decoder block, `d_model = 96`, 4 attention head. Kết quả là BLEU khoảng 2,30 và chrF khoảng 18,71.

Loss giảm nhưng bản dịch vẫn có lỗi sai nghĩa, sai tên riêng, số liệu và lặp từ. Điều mình cần nhớ là xây đúng kiến trúc và train chạy được chưa đủ để có chất lượng dịch tốt.

Đây là thí nghiệm nhỏ trên phần EVBNews v1.0 công khai, không đại diện cho toàn bộ EVBCorpus hoặc mọi Transformer. Số liệu đầy đủ nằm trong [báo cáo của lần chạy](./evb_transformer_outputs/en_to_vi_30a44431fc/translation_quality_report.md).

**Ưu điểm và hạn chế**

Transformer cho phép trao đổi thông tin trực tiếp giữa các vị trí cách xa nhau và tính nhiều vị trí song song khi training.

Tuy nhiên, full self-attention tạo các score cho từng cặp vị trí. Với chuỗi dài `n`, số score tăng theo `n²`, khiến việc tính toán và lưu attention trở nên tốn kém.

Chất lượng còn phụ thuộc dữ liệu, tokenizer, số bước training và cách decoding. Attention không bảo đảm output đúng sự kiện; model vẫn có thể bịa thông tin hoặc lặp nội dung.