# Neural network for NLP bằng TensorFlow

Neural network có thể được sử dụng để phân loại văn bản, ví dụ như phân loại chủ đề bài báo, phân loại email spam hoặc phân tích cảm xúc.

Máy tính không thể hiểu trực tiếp một câu chữ nên trước khi đưa dữ liệu vào neural network, mình cần chuyển văn bản thành các con số.

Quy trình cơ bản:

- Đọc và tiền xử lý dữ liệu

- Chia dữ liệu thành train, validation và test

- Chuyển văn bản thành các token

- Chuyển token thành vector bằng embedding

- Huấn luyện neural network

- Đánh giá kết quả

**Text vectorization**

Trong TensorFlow, mình có thể dùng `TextVectorization` để chuyển văn bản thành một chuỗi số nguyên.

Ví dụ câu:

```text
hôm nay thời tiết đẹp
```

có thể được chuyển thành:

```text
[25, 84, 36, 102]
```

Mỗi số đại diện cho một token trong vocabulary.

Trước khi sử dụng, mình gọi `adapt()` trên tập train để layer học vocabulary. Không nên gọi `adapt()` trên tập test vì như vậy model sẽ biết trước thông tin của dữ liệu dùng để đánh giá.

Các câu thường có độ dài khác nhau nên mình cần chọn một độ dài cố định. Câu ngắn sẽ được thêm padding, còn câu quá dài sẽ bị cắt bớt.

**Word embedding**

Sau khi token được đổi thành số nguyên, mình dùng layer `Embedding` để chuyển mỗi token thành một vector.

Nếu chỉ dùng số thứ tự thì các con số không thể hiện được ý nghĩa của từ. Ví dụ token 100 không có nghĩa là quan trọng hơn token 10.

Embedding sẽ được học trong quá trình training. Những từ được sử dụng trong ngữ cảnh gần giống nhau có thể học được các vector gần nhau hơn.

Ưu điểm của embedding:

- Số chiều nhỏ hơn one-hot vector

- Có thể học được một phần ý nghĩa và mối quan hệ giữa các từ

- Phù hợp với neural network

**Mô hình neural network đơn giản**

Mô hình mình sử dụng có dạng:

```text
TextVectorization
→ Embedding
→ GlobalAveragePooling1D
→ Dense
→ Dropout
→ Dense + Softmax
```

`Embedding` chuyển các token thành vector.

`GlobalAveragePooling1D` lấy trung bình các vector trong câu để tạo thành một vector có độ dài cố định. Cách này đơn giản và chạy nhanh nhưng sẽ làm mất thứ tự của từ.

`Dense` học cách kết hợp các đặc trưng để phân loại văn bản.

`Dropout` tạm thời bỏ ngẫu nhiên một số neuron trong lúc training để hạn chế overfitting.

Layer cuối dùng `softmax` để tạo xác suất cho từng class. Class có xác suất cao nhất sẽ là dự đoán của model.

**Training**

Trong quá trình training, model thực hiện các bước:

- Nhận một batch văn bản

- Dự đoán class

- So sánh dự đoán với nhãn thật bằng loss

- Dùng backpropagation để tính gradient

- Optimizer cập nhật các weight

Quá trình này được lặp lại qua nhiều epoch.

Mình dùng `SparseCategoricalCrossentropy` vì nhãn của mỗi văn bản là một số nguyên và bài toán có nhiều class.

Optimizer được sử dụng là Adam. Learning rate quyết định mức độ thay đổi weight sau mỗi lần cập nhật. Learning rate quá lớn có thể làm model học không ổn định, còn quá nhỏ sẽ làm model học rất chậm.

**Train, validation và test**

Train set được dùng để cập nhật weight của model.

Validation set được dùng để theo dõi quá trình training và chọn model tốt nhất.

Test set chỉ được dùng sau khi đã hoàn thành việc chọn model để đánh giá kết quả cuối cùng.

Nếu accuracy trên tập train tiếp tục tăng nhưng accuracy trên validation không tăng hoặc giảm xuống thì model có thể đang bị overfitting.

Mình có thể dùng `EarlyStopping` để dừng training khi validation loss không còn cải thiện và khôi phục lại weight tốt nhất.

**Đánh giá model**

Accuracy là tỷ lệ số mẫu được dự đoán đúng trên tổng số mẫu.

Tuy nhiên, accuracy chưa đủ nếu số lượng dữ liệu của các class không cân bằng. Vì vậy mình có thể xem thêm:

- Precision

- Recall

- F1-score

- Confusion matrix

Macro F1 tính F1 riêng cho từng class rồi lấy trung bình, vì vậy mỗi class đều có mức độ quan trọng như nhau.

Confusion matrix giúp mình biết model thường nhầm class nào với class nào. Từ đó mình có thể xem lại dữ liệu và cải thiện bước tiền xử lý hoặc mô hình.

**Kết quả thử nghiệm với VNTC**

Mình đã thử mô hình neural network đơn giản trên bộ dữ liệu phân loại văn bản tiếng Việt VNTC.

Trong lần chạy nhanh, kết quả trên tập test là:

- Accuracy: khoảng 87.6%

- Macro F1: khoảng 87.38%

- Validation accuracy tốt nhất: khoảng 89.51%

Kết quả này cho thấy mô hình đơn giản vẫn có thể tạo ra một baseline tương đối tốt. Tuy nhiên, đây chưa phải kết quả tối ưu vì lần thử chỉ dùng một phần dữ liệu test và số epoch giới hạn.
