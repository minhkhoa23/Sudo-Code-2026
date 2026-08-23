# Week 1: Text preprocessing

Trong tuần này, mình sẽ được tìm hiểu về các cách tiền xử lý dữ liệu như tokenizer, vectorization, stopword, lemmatization, normalization

Các bước tiền xử lý thông tin văn bản (Text preprocessing) thông thường bao gồm:

**Tokenization**

tokenization là một loại phân đoạn tách văn bản. Phân đoạn (segmentation) sẽ tách các văn bản thành các đoạn (chunks / segments) nhỏ hơn 

Phân đoạn có thể tách văn bản thành các đoạn văn, đoạn văn thành các câu, các câu thành các cụm từ, các cụm từ thành các token → Ở đây mình sẽ tập trung tách thành các tokens

Tokens có thể là các từ, các dấu câu, chữ tượng hình, ký tự, emojis, emoticons

Các công cụ tokenization:

1 Python—str.split and re.split
2 Natural Language Toolkit (NLTK)—TreebankWordTokenizer and TweetTokenizer
3 SpaCy—Fast and production-ready tokenization
4 Stanford CoreNLP—Linguistically accurate, requiring Java interpreter
5 Hugging Face—BertTokenizer, a WordPiece tokenizer

So về tốc độ thì:

regex > spacy, nltk, các thư viện khác

Token có thể là ký tự văn bản, subword, word, sentence pieces

**Stopword**

Stopword là các từ phổ biến, xuất hiện thường xuyên nhưng mà lại mang ít ngữ nghĩa hay là mang ý nghĩa trung lập trong các ngôn ngữ

Ví dụ:

Trong tiếng Anh: a, an, the, this, and, or, of, on

Trong tiếng Việt: hay không, hay là, hay làm, hay nhỉ, hay nói, hay sao, hay tin, hay đâu

**Case folding**

Bước chuẩn hóa chữ viết hoa / chữ viết thường trong một văn bản về cùng một dạng, thường là chuyển toàn bộ văn bản thành chữ viết thường

Tại sao cần case folding:

-Khắc phục tình trạng ‘denormalized’: các từ trong chữ thường được viết hoa khi đứng ở đầu câu hoặc được viết hoa hết để nhấn mạnh

-Giảm kích thước từ vựng

-Hợp nhất các token đồng nghĩa: Nhờ việc chuẩn hóa về chữ thường giúp các từ giống nhau như ‘good’ & ‘Good’ & ‘GOOD’ về chung một token

Nhược điểm của case folding:

-Mất chữ viết hoa → gây nhầm lẫn đối với danh từ riêng (như tên, chức danh) với các từ thường

-Không có công dụng với các ngôn ngữ không tồn tại chữ viết hoa, viết thường như tiếng Ả Rập, Hindi

**Stemming**

Stemming (tách gốc từ) là một kỹ thuật chuẩn hóa trong NLP để loại bỏ các phần biến đổi ở đuôi từ và đưa từ về một gốc từ chung (stem)

Stemming có thể dùng ở các ngôn ngữ khác như tiếng Anh nhưng không thể dùng trong tiếng Việt

Ví dụ: Các từ như play, plays, playing, played → play

Mục đích của stemming:

-Giảm chiều dữ liệu: nhờ việc gom các từ có chung gốc từ về cùng một dạng giúp giảm kích thước bộ từ vựng

-Cải thiện recall

Nhược điểm của stemming:

-Làm giảm precision

-Không phù hợp với các model deep learning: stemming làm mất đi các thông tin ngữ cảnh và cấu trúc ngữ pháp quan trọng kiến model bị giảm độ chính xác

**Lemmatization**

Giảm inflected (biến từ có trong tiếng anh) và các biến thể của từ về dạng lemma:

Ví dụ: 

am is are về lại be

play plays played playing về lại play

**Synonym substitution**

Bao gồm các bước như:

Typo correction

Spelling correction

Synonym substitution

Contraction expansion

Emoji expansion