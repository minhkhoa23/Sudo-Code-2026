**Bag of word**

Bag of Words, viết tắt là **BoW**, là cách biểu diễn văn bản bằng cách **đếm số lần xuất hiện của từng từ**.

Nó không quan tâm thứ tự từ, chỉ quan tâm từ nào xuất hiện và xuất hiện bao nhiêu lần.

Ưu điểm: đơn giản, dễ hiểu, dễ dùng.

Nhược điểm: mất thứ tự và ngữ cảnh của câu.

**TF-IDF**

TF-IDF là cách biểu diễn văn bản bằng trọng số, không chỉ đếm từ đơn giản như Bag of Words.

TF-IDF gồm 2 phần:

```
TF = Term Frequency
```

Từ xuất hiện càng nhiều trong một văn bản thì TF càng cao.

```
IDF = Inverse Document Frequency
```

Từ xuất hiện ở quá nhiều văn bản thì bị giảm trọng số.

**Unigram**

Unigram là đặc trưng gồm **1 từ/token**

Nếu mình dùng `CountVectorizer(ngram_range=(1, 1))`, tức là mình đang dùng unigram.

Thực tế, Bag of Words mặc định thường chính là Bag of Unigrams.

**Bigram**

Bigram là đặc trưng gồm **2 từ/token liên tiếp**.

Unigram và Bigram trả lời câu hỏi: lấy đặc trưng theo cụm mấy từ?
Bag of Words và TF-IDF trả lời câu hỏi: biểu diễn đặc trưng đó bằng cách nào?