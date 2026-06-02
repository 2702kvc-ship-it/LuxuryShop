API = endpoint/?parameters/!query

# Authentication
1. - REGISTERED --> Check == "mail" --> Mail exist | not exist --> Raise "This email has been registered"  | Run query create new user (ORM)
   - Password encrypted / your password needs longer than 8 strings.
   - Update Information about individual / called query (ORM).
2. - LOGIN --> Check =="mail" -->  Right | Wrong --> Password encrypted | Raise "Pls fill the correct password" --> True password | Back to enter password --> Raise "Login success" --> Load to insight web / user interface.
3. - LOGOUT --> Return Exact LOGIN INTERFACE / Out of session. 

# Thuong hieu
1. - Take "Thuonghieu" information / called query thuonghieu by "tenthuonghieu"(lower)(ORM).

# Danh muc 
1. - Take "Danhmuc"/"Thuonghieu" information / called query Danhmuc by "tenDanhmuc" (ORM). 

# Sanpham 
1. - Take "Sanpham"/"Danhmuc"/"Thuonghieu" / called query by "Tensanpham"(ORM). 

# Bien the san pham 
1. - Take "Bienthesanpham"/"sanpham"/"Danhmuc"/"Thuonghieu" / called query by "TenBienthesanpham"(ORM). 
   - Switch color / query "hinhanhsanpham".

# Gio Hang 
1. - Start with White Table --> Add "bienthesanpham" --> Endpoint of that "bienthesanpham" has been included in this table / every "bienthesanpham" has seperate endpoint with id "bienthesanpham" in query/ but just render as 1 product. --> click to anylink of "bienthesanpham" --> return Take "Bienthesanpham".
   - Auto update numer of product has exist in blanket / Number above 1.
   - Render price of these product under each .

# Hinh anh + chung nhan san pham
1. - Get these by using query (ORM), located at Bienthesanpham 

# Don hang 
1. - Stand here is how many product you choose --> Count price of these product/ price = linear sum of each product *  number of product (same) .
   - Calling MaGiamGia --> Matching LoaiGiam(what product can have reducation) --> Matching "Price of these product" --> Cal money can be reduced Price*GiaTri(%)-->Belove than GiaToiDa(VND) 
   -  Status : ("Choxacnhan"/"Daxacnhan"/"Danggiao"/"Dagiao")| Admin can update these just by update query (ORM).
   - Add Magiam/CHuongtrinhvip.

# Chi tiet don hang

1. - Take each amount --> Take price --> Take GiamGia from "Donhang" --> Cal Thanhtien.

# Ma Giam Gia 
1. - Setup Again when it on expire time.
   - Circle (every 3 months) shop will have 1000 voucher each "Thuonghieu" can apply for every product of this "Thuonghieu".
   - Giatri(%)/Magiamgia random for 10% -> 35% (must be |5 ).
   - Always get Giamtoida(vnd) about 8% of highest price/product/Thuonghieu.
   - From above 20% will apply for the product with price > 2tr vnd| other will opposed.

# Chuongtrinhvip 
1. - For 1000vnd you an get 1xp.
   - Rank/ "Iron"(1000xp)/"Bronze"(3000xp)/"Silver"(7000xp)/"Gold"(15000xp)/"Platinum"(31000xp)/"Diamond"(50000xp)/"Saphire"(70000xp).
   - Update when "Thanhtoan"/ "Diem"|"Hanghientai".
   - Pri/For each rank can gain 5% scale up to 35%.Every body has 1 voucher for 3 months(exist for 1 months).

# Thanh toan
   - Set Payment (VN PAY QR) for each bill, just pay online.

# Bao hanh
   - 1 product under 2 tr vnd can have 3 months protect, above 2 tr vnd can have 6 months protect 
# Danh gia
1. - Thanh toan / Danh gia cac san pham 1-> 5 sao + comment.

# Nhan vien.
1. - Set up status of order ("Choxacnhan/Daxacnhan/Danggiaohang/Dagiaohang").
   - 