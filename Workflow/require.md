## ĐỀ TÀI PROJECT/ TẠO 1 SHOP lUXURY
- Data structure : file docx có chi tiết 
1.Bảng ThuongHieu	
2.Bảng DanhMuc	
3.Bảng SanPham	
4.Bảng GiayChungNhan	
5.Bảng BienTheSanPham	
6.Bảng HinhAnhSanPham	
7.Bảng KhachHang	
8.Bảng ChuongTrinhVIP	
9.Bảng DonHang	
10.Bảng ChiTietDonHang	
11.Bảng BaoHanh	
12.Bảng ThanhToan	
13.Bảng DanhGia	
14.Bảng MaGiamGia	
15.Bảng GioHang (Giỏ hàng)	
16.Bảng NhanVien (Admin)	
- Yêu cầu : Thực hiện logic backend cho bài trên 
- Backend: datalayer.py(orm hứng dữ liệu từ database), service.py(thực hiện các luồng logic liên quan ví dụ như đăng nhập, tạo tài khoản, thêm hàng vào giỏ, áp mã giảm giá, xuất đơn hàng, xuất chi tiết đơn hàng, tặng mã bảo hành dựa trên,nhân viên có quyền truy cập vào làm admin của shop(cái này tôi ko rõ chịu) , chắc chắn còn xót nhưng tôi chưa tìm ra ), schema.py (cung cấp dạng dữ liệu json khi reponse trước các lệnh request), route.py() trả về api truy cập chuẩn cho web giúp web dễ truy cập hơn các url cũng gọn hơn , app.py() nơi mà thực hiện add toàn bộ các route vào app
- frontend : tất cả thao tác xem hình ảnh, khách hàng ,sản phẩm, giấy chứng nhận vv..... do javascript làm hết (tôi ko thuộc phận sự frontend chỉ nói lên để tránh nhầm lẫn với backend có thể tôi đúng hoặc sai)
- Kiến thức yêu cầu : Khả năng code bằng PYTHON,SQL,JAVASCRIPT,HTML,CSS 
- Kỹ thuật yêu cầu : thư viện python như flask,sqlalchemy(cho sql server), addlistener(js), basemodel, httpError ....