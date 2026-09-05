**Word embedding**

Word embedding được sử dụng rất nhiều trong các ứng dụng về NLP, word embedding sẽ nhúng các từ thành các con số, có một vài ứng dụng của word embedding mà mình có thể thấy như sau:

Mỗi một từ sẽ đại diện thành một vector của ma trận, và để xây dựng ma trận các con số

Để biểu diễn từ dưới dạng con số thì cách đơn giản nhất mà mình nghĩa ra là đánh số thứ tự theo bảng chữ cái cho từng con số (Intergers), các làm này đơn giản nhưng thứ tự của các chữ cái không có ngữ nghĩa gì với nhau

Tiếp tục mình dùng phương án one-hot vectors, sẽ một vector độ dài n, ở số thứ tự của từ đại diện thì sẽ là 1, các vị trí còn lại là 0

Cách này đơn giản nhưng sẽ rất tốn nếu có quá nhiều từ làm n lớn hơn và cách biểu diễn từ như thế vẫn không mang ngữ nghĩa gì với nhau

→ Word embeddings

Word embedding nhúng các từ thành các vector và các vector này có độ tương đồng ngữ nghĩa so với các vector khác thông qua vị trí của nó.

Đây là ví dụ các từ positive và negative khi được nhúng vào một không gian 2 chiều, trục tung là tính cụ thể hay trừu tượng, trục hoàng là positive hay là negative

Lợi ích của việc word embedding:

-Số chiều thấp (ít hơn số lượng từ vựng)

-Có thể mã hoá ngữ nghĩa

Cách để tạo word embeddings

Để có thể embedding được thì mình cần hai thứ:

-corpus (vocabulary thôi là chưa đủ)

-embedding method (Trong course này sẽ tập trung vào machine learning model)

Ở đây phương pháp thường dùng là self-supervised learning, bao gồm cả supervised và unsupervised luôn

Một vài phương pháp word embeddings:

Phương pháp cổ điển:

-word2vec (deep learning nông)(google, 2013):

+Continuous bag-of-words (CBOW): mô hình học cách dự đoán từ ở trung tâm các từ khác

+Continuous skip-gram / Skip gram with negative sampling (SGNS): mô hình học cách dự đoán từ xung quanh từ đã cho


