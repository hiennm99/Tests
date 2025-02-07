Yêu cầu: Thiết kế 1 hệ thống API với 2 endpoint
- Endpoint 1: thêm/cập nhật record. Nếu record chưa có thì thêm vào và trả output là "Inserted", nếu record đã có thì cập nhật nó và trả output là "Appended"
- Endpoint 2: truy vấn 1 record và tính toán phân vị. Output trả về bao gồm giá trị phân vị được tính toán & tổng số phần tử trong nhóm

* Lưu ý:
- Không sử dụng thư viện để tính phân vị nếu nhóm có ít hơn 100 giá trị
- Chú ý vào hiệu suất cao & khả năng phục hồi
- Lý luận về tính khá dụng cao & khả năng mở rộng
- KHÔNG dùng cơ sở dữ liệu. Keep it simple
- Ngôn ngữ được chọn tùy ý

Ví dụ:
+ Endpoint 1: 
input: {"poolId": 123456, "poolValues": [1,7,2,6]} -> output: "Inserted"/"Appended"

+ Endpoint 2:
input: {"poolId": 123456, "percentile": 99.5} -> output: {"quantile": 6,984, "count": 4}

-----------------------------------------------------------------------------------------------------------------------------------------------
Ý tưởng xây dựng cơ bản:
- Dùng FastAPI để xây dựng nhanh hệ thống API
- Vì không được dùng Database vậy nên sẽ chọn: global variable để lưu các giá trị trong session, và dùng file json để lưu các giá trị khi đóng session -> điều này giúp hệ thống có khả năng phục hồi nếu chẳng may xảy ra sự cố.
- Đối với nhóm có ít hơn 100 giá trị thì sẽ tự viết hàm để tính phân vị

-----------------------------------------------------------------------------------------------------------------------------------------------
Chi tiết xây dựng hệ thống:
-  Dự án sẽ được chia thành các phần nhỏ để dễ quản lý: 
   + /data: chứa data trong session và file json lưu data
   + /models: chứa các models của Pool và Pool Manager
   + /routers: chứa các route đến các API
   + /schemas: chứa các model quy định format cho các input của các API
   + /utils: chứa các hàm phụ trợ như đọc/ghi file, tính phân vị,...
   + file main.py: file thực thi của dự án

- Mô tả hoạt động:
B1: khi chương trình chạy thì sự kiện "startup" sẽ đọc file json để load data đã lưu -> lưu vào biến global là pools
B2: 
   B2.1: endpoint /add có chức năng thêm/cập nhật các giá trị
      + Nếu giá trị chưa có tồn tại trong biến pools thì thêm vào và trả output là "Inserted". Lưu ý: để tối ưu tốc độ tìm kiếm thì sẽ biến đổi 1 chút ở input. Cụ thể thì giá trị của trường "poolId" sẽ trực tiếp là key, còn value là giá trị của trường "poolValues"
      VD: {"poolId": 123, "poolValues": [0,4,6]} -> {123: [0,4,6]}
      ==> Điều này giúp cho việc tìm kiếm/cập nhật giá trị nhanh hơn.
      + Nếu giá trị đã tồn tại trong biến pools thì nó sẽ cập nhật value của giá trị có key = poolId và trả ra output là "Appened"
   
   B2.2: endpoint /query có chức năng tính toán phân vị với giá trị được nhập vào
      + Nếu giá trị chưa tồn tại trong biến pools thì trả về lỗi 404
      + Nếu giá trị tồn tại trong biến pools thì tính toán phân vị. Lưu ý: xét xem tổng số phần tử có bé 100 hay không, nếu < 100 thì dùng hàm tự viết, còn nếu >=100 thì dùng built-in function của thư viện numpy (có thể chỉ dùng hàm tự viết)
      ==> Output trả về là; {"quantile": ...., "count": ....}
B3: khi chương trình dừng thì biến global pools sẽ được ghi vào file json nhằm khôi phục lại khi chương trình chạy lại.

------------------------------------------------------------------------------------------------------------------------------------------------
Khả năng mở rộng & tính sẵn sàng

- Thiết kế hệ thống như trên khá đơn giản và nhanh nhưng có khá nhiều bất cập.
  + Đầu tiên là biến toàn cục gây ra vấn đề bất đồng bộ hóa khi có nhiều request cùng lúc
  + Thứ hai, ghi file json sẽ gây ra bottleneck vì json không hỗ trợ ghi đồng thời và ghi lượng dữ liệu lớn thì việc đọc ghi rất chậm
  + Thứ ba, việc chỉ lưu dữ liệu khi app tắt có thể gây mất dữ liệu khi app crash

- Các cải tiến:
  + Đầu tiên, thay vì dùng biến toàn cục thì dùng Singleton Pattern với 1 class Pool Manager chứa các Pool -> đảm bảo duy nhất 1 instance được khởi tạo trong chương trình, truy xuất nhanh chóng theo poolId
  + Thứ hai, thay vì lưu file JSON thì lưu file pickle dạng binary -> tốc độ đọc, ghi nhanh hơn json
  + Cuối cùng, thay vì chỉ lưu data khi app shutdown thì thêm Background Task để lưu data mỗi 10 giây (tùy chỉnh) -> tránh việc mất dữ liệu do app tắt đột ngột

==> Tuy đã cải thiện đáng kể nhưng để mở rộng hệ thống này thì vẫn cần phải kết nối với Database vì asyncio chỉ hoạt động tốt trên 1 worker, nếu có nhiều worker thì sẽ xảy ra vấn đề đồng bộ dữ liệu giữa các worker


================================================================================================================================================
HOW TO RUN 
1. Clone this repository
2. Run: pip install -r requirements.txt (Python is required)
3. Run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
4. Access http://localhost:8000/docs to test API Endpoints