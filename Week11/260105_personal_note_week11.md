# WEB SCRAPING / API

**Web scraping là gì?**

Web scraping là việc lấy dữ liệu từ website bằng chương trình rồi chuyển thành dạng dễ sử dụng, như một bảng dữ liệu hoặc danh sách bản ghi.

Ví dụ, từ trang danh sách sách, mình lấy tên, giá, rating và đường dẫn sản phẩm thay vì sao chép từng dòng bằng tay.

Quy trình cơ bản:

```text
Chọn nguồn → Gửi HTTP request → Đọc response → Trích xuất → Làm sạch → Lưu dữ liệu
```

**API là gì?**

API là giao diện để các chương trình trao đổi dữ liệu hoặc sử dụng chức năng của nhau. Trong note này, mình tập trung vào web API qua HTTP.

API có thể trả về dữ liệu có cấu trúc như JSON, nên mình thường không cần tìm tên sản phẩm trong các thẻ HTML. Tuy nhiên, không phải API nào cũng trả JSON hoặc yêu cầu API key; cần đọc tài liệu của từng dịch vụ.

Nếu website có API chính thức phù hợp và mình được phép sử dụng, mình nên cân nhắc API trước khi scrape giao diện HTML.

**Scraping và API khác nhau thế nào?**

| Điểm so sánh | Scraping HTML | Gọi web API |
| --- | --- | --- |
| Dữ liệu nhận được | HTML, cần tìm phần tử chứa dữ liệu | Thường là JSON/XML theo schema của dịch vụ |
| Cách trích xuất | CSS selector, XPath hoặc duyệt DOM | Đọc trường trong response |
| Thay đổi cần theo dõi | Cấu trúc HTML và cách trang tải dữ liệu | Endpoint, phiên bản và schema |
| Giới hạn | Quyền truy cập, điều khoản và mức tải gây ra cho website | Quyền, quota/rate limit và phí nếu có |

Gọi API không có nghĩa là luôn nhanh, miễn phí hoặc không bao giờ thay đổi. Mình vẫn cần kiểm tra response và dữ liệu thu được.

**HTTP request và response**

Request thường có URL, method, headers và có thể có query parameters hoặc body.

`GET` thường dùng để đọc dữ liệu. `POST` thường dùng để gửi dữ liệu hoặc yêu cầu xử lý. Ý nghĩa cụ thể phụ thuộc API, nên không tự gửi thử những request có thể thay đổi dữ liệu.

Response có status code, headers và body. Body có thể là HTML, JSON hoặc định dạng khác. Với Requests, mình thường dùng `response.content` để lấy bytes, `response.text` để lấy text và `response.json()` để đọc JSON. Xem [Requests Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/).

**BeautifulSoup dùng để làm gì?**

BeautifulSoup là thư viện giúp phân tích HTML/XML và tìm dữ liệu trong cấu trúc đó. Nó không tự tải website như một HTTP client và không tự chạy JavaScript.

Trong bài thực hành của mình, Requests tải HTML, còn BeautifulSoup đọc HTML để tìm các thẻ cần lấy dữ liệu.

Một số cách tìm thường dùng:

- `find()` / `find_all()`: tìm một hoặc nhiều phần tử theo điều kiện.

- `select_one()` / `select()`: tìm bằng CSS selector.

- `get_text()`: lấy nội dung văn bản.

- `get("href")`, `get("title")`: lấy giá trị thuộc tính.

Tham khảo [BeautifulSoup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

**Ví dụ trích xuất HTML**

Ví dụ dưới dùng HTML tự tạo, không gửi request tới website:

```python
from bs4 import BeautifulSoup

html_doc = """
<article class="product_pod">
  <h3><a title="Sách minh họa đầy đủ" href="/books/1">Sách minh họa...</a></h3>
  <p class="price_color">£12.50</p>
</article>
"""

soup = BeautifulSoup(html_doc, "html.parser")
book = soup.select_one("article.product_pod")
title = book.select_one("h3 a").get("title")
price = float(book.select_one("p.price_color").get_text(strip=True).replace("£", ""))

print(title)  # Sách minh họa đầy đủ
print(price)  # 12.5
```

`h3 a` chọn thẻ `a` nằm trong `h3`. Thuộc tính `title` ở ví dụ này chứa tên đầy đủ, còn text đang được rút gọn. Không nên cho rằng mọi website đều có cấu trúc giống ví dụ.

**Đọc dữ liệu JSON từ API**

Nếu response là JSON, mình đọc các trường dữ liệu thay vì dùng selector HTML. Ví dụ minh họa phần xử lý JSON, không gọi một API thật:

```python
import json

response_body = '{"books": [{"title": "Sách A", "price": 12.5}]}'
data = json.loads(response_body)

for book in data["books"]:
    print(book["title"], book["price"])
```

Khi gọi API thật, cần kiểm tra status code và định dạng trước. Đọc được JSON chưa có nghĩa request thành công: response JSON cũng có thể chứa thông báo lỗi. Cần kiểm tra schema của dịch vụ. Xem [cách xử lý response JSON bằng Requests](https://requests.readthedocs.io/en/latest/user/quickstart/#json-response-content).

**Scrapy là gì?**

Scrapy là framework hỗ trợ xây dựng quá trình crawl và trích xuất dữ liệu. Ngoài parser, nó còn có các phần như xếp lịch request, tải trang, xử lý dữ liệu và xuất kết quả.

Spider là phần mình viết để xác định URL bắt đầu, cách đọc response và các liên kết cần đi tiếp. Spider có thể dùng CSS hoặc XPath để lấy dữ liệu.

Pipeline có thể kiểm tra, làm sạch và lưu các bản ghi được spider tạo ra. Scrapy cũng hỗ trợ xuất dữ liệu như JSON hoặc CSV. Xem [Scrapy](https://www.scrapy.org/) và [tutorial chính thức](https://docs.scrapy.org/en/latest/intro/tutorial.html).

Với bài tập chỉ lấy một vài trang, Requests + BeautifulSoup là cách bắt đầu gọn. Khi có nhiều URL, nhiều bước xử lý hoặc cần quản lý crawl có hệ thống, mình có thể cân nhắc Scrapy. Dùng framework không thay thế việc chọn đúng selector và kiểm tra dữ liệu.

**Pagination và URL tương đối**

Một trang chỉ chứa một phần dữ liệu nên mình cần xử lý pagination, tức phân trang.

Với website, có thể tìm liên kết “Next” rồi ghép URL tương đối bằng `urljoin`. Với API, phân trang có thể dùng số trang, offset hoặc cursor; phải theo quy định của API.

Mình cần giới hạn số trang, kiểm tra URL đã thăm và dừng khi hết trang. Không nên chỉ thay số trong URL nếu chưa hiểu cấu trúc phân trang. Cách theo liên kết được minh họa trong [Scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html).

**Website có JavaScript**

Đôi khi trình duyệt hiển thị dữ liệu nhưng HTML tải bằng Requests không có phần đó. Dữ liệu có thể được tải thêm sau khi JavaScript chạy.

Mình cần kiểm tra nguồn dữ liệu bằng DevTools/Network, xem có API hoặc dữ liệu nhúng phù hợp được phép sử dụng không. BeautifulSoup và Scrapy mặc định không phải trình duyệt chạy JavaScript. Nếu cần browser rendering thì phải bổ sung công cụ thích hợp, không chỉ đổi selector. Xem [hướng dẫn xử lý nội dung động của Scrapy](https://docs.scrapy.org/en/latest/topics/dynamic-content.html).

**Lỗi HTTP và giới hạn request**

Một số status code thường gặp:

- `200`: request thành công về HTTP, vẫn cần kiểm tra body có đúng dữ liệu mong muốn không.

- `401` / `403`: cần kiểm tra xác thực hoặc quyền truy cập, không tìm cách vượt chặn.

- `404`: tài nguyên không tìm thấy.

- `429`: quá nhiều request theo giới hạn áp dụng.

- `5xx`: nhóm lỗi phía server.

Mình nên đặt timeout, ghi log và giới hạn số lần thử lại. Không retry liên tục hoặc tự gửi lại thao tác ghi có thể gây tác dụng lặp. Tra cứu [HTTP status codes trên MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status).

**Làm sạch và kiểm tra dữ liệu**

Sau khi trích xuất, mình cần bỏ khoảng trắng dư, chuyển giá sang số, xử lý encoding và kiểm tra trường bị thiếu.

Nên chọn khóa phù hợp để loại trùng, ví dụ URL sản phẩm. Không tự gán giá hoặc rating giả khi parser không tìm thấy dữ liệu.

Mỗi bản ghi nên giữ nguồn và thời điểm lấy. Lưu HTML hoặc response cần thiết giúp mình kiểm tra lại mà không phải tải website nhiều lần. Dữ liệu lưu thành công không có nghĩa là dữ liệu đã đầy đủ hoặc chính xác.

**Thu thập có trách nhiệm**

Mình cần kiểm tra điều khoản, quyền sử dụng và `robots.txt`; chỉ lấy dữ liệu trong phạm vi được phép. Không vượt xác thực/CAPTCHA và không thu thập dữ liệu nhạy cảm khi chưa có quyền phù hợp.

Nên đặt User-Agent rõ ràng, khoảng nghỉ và số request đồng thời phù hợp. Scrapy có cấu hình như `ROBOTSTXT_OBEY` và `DOWNLOAD_DELAY`, nhưng mình vẫn phải hiểu và đặt cấu hình đúng. Xem [Scrapy settings](https://docs.scrapy.org/en/latest/topics/settings.html).

Không có `robots.txt` không có nghĩa là được scrape mọi thứ. Với API key, nên dùng Secrets hoặc biến môi trường, không đưa key vào notebook chia sẻ hay log.

**Những gì mình học từ notebook Books to Scrape**

[Notebook BeautifulSoup](<D:/Sudo code 2026/Books_to_Scrape_BeautifulSoup.ipynb>) đã có một lần chạy lấy 60 sách từ 3 trang danh sách, không có dòng trùng hoặc card bị bỏ do lỗi trích xuất.

Mỗi sách được chọn bằng `article.product_pod`. Tên đầy đủ lấy từ `h3 a[title]`, giá từ `p.price_color`, rating từ class của `p.star-rating`. Trang tiếp theo được tìm qua `li.next a`.

Điều mình cần nhớ là chọn đúng thuộc tính, chuẩn hóa kiểu dữ liệu và kiểm tra kết quả, không chỉ viết vòng lặp tải trang.

Đây chỉ là mẫu 3 trang, không phải toàn bộ website. Giá và rating của Books to Scrape là dữ liệu demo, không dùng để suy ra chất lượng sách hoặc đưa ra quyết định mua. Số liệu nằm trong [báo cáo của lần chạy](<D:/Sudo code 2026/books_scraping_outputs/20261028T032745_044129Z/scraping_report.md>).
