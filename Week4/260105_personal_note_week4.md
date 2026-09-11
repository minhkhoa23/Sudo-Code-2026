## sentiment analysis using SVM

Sentiment Analysis bằng SVM là quá trình sử dụng thuật toán Support Vector Machine để phân loại một văn bản vào các nhóm cảm xúc như Positive, Negative hoặc Neutral.

SVM sẽ chuyển văn bản thành các vector số. SVM không thể nhận trực tiếp câu “Sản phẩm rất tốt” làm input mà cần một vector như [0.2, 0, 0.8, ...]. Một trong những phương pháp phổ biến nhất để làm việc này là TF-IDF

Khi dữ liệu đã được vector hóa, mình sẽ bắt đầu huấn luyện mô hình SVM. Ý tưởng chính của SVM là tìm một đường biên quyết định, gọi là decision boundary hay hyperplane, để phân chia các class. Ví dụ, trong bài toán Positive và Negative, SVM cố gắng tìm một ranh giới sao cho các vector của review Positive nằm chủ yếu ở một phía và các vector Negative nằm ở phía còn lại.

SVM không chỉ tìm một đường có thể phân chia dữ liệu mà còn cố gắng tìm đường có khoảng cách giữa hai class lớn nhất. Khoảng cách này được gọi là margin.

Các bước thực hiện sentiment analysis bằng SVM:

-preprocess dataset

-Biểu diễn thành vector

-Huấn luyện SVM

## Sentiment analysis using Naive Bayes

Sở dĩ gọi là Naive Bayes (Bayes ngây thơ) thì ở đây người ta giả định rằng các từ trong câu hoàn toàn độc lập với nhau (Nghĩa là các từ trong câu hoàn toàn không xét đến ngữ cảnh, một điều gần không thể trong ngôn ngữ đời sống → ngây thơ)

Trong khi tính xác xuất thì mình sẽ sử dụng laplacian smoothing để tránh xác suất = 0, Laplacian smoothing có nghĩa là cộng thêm vào tử số +1 để tránh xác suất = 0
Lý do tại sao người ta lại sử dụng laplacian smoothing là do nếu các từ không xuất hiện trong quá trình training thì xác suất các từ đó sẽ = 0, nhưng trong thực tế thì tập training không thể nào bao phủ hết các trường hợp của từ vựng được

Log likelihood: là xác suất được chuyển về dạng log vì tránh xác suất dưới dạng số thập phân sẽ rất là nhỏ và dễ tiến về 0, ngoài ra việc làm này chuyển tích về thành bài toán tổng sẽ dễ đạo hàm hơn

Log prior: ký hiệu là lambda là một dạng regularization, nếu tính ra được log prior thì mình sẽ biết từ đó có thiên hướng positive hay là negative:

Nếu log prior > 0 thì sẽ thiên về positive, < 0 thì sẽ thiên về negative, = 0 thì sẽ thiên về neural

Các bước thực hiện sentiment analysis bằng Naive Bayes:

-preprocess dataset (lowercase, remove punctuation, urls, names, remove stop words, stemming, tokenize sentences)

-đếm số lượng từ và lập bảng tần số

-Tính xác suất có điều kiện và có áp dụng làm mịn Laplacian, từ đó lập ra được bảng xác suất

-Từ bảng xác suất mình sẽ tính và lập thêm một cột log likelihood (Xác suất dựa trên log để tối ưu hơn)

-Tính log prior để biết từ đó có thiên hướng positive hay negative