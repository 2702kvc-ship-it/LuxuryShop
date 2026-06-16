
from extensions import db
from datetime import datetime


# ─────────────────────────────────────────
# 1. THƯƠNG HIỆU
# ─────────────────────────────────────────
class ThuongHieu(db.Model):
    __tablename__ = 'ThuongHieu'
    __table_args__ = {'extend_existing': True}

    ThuongHieuID   = db.Column(db.Integer, primary_key=True)
    TenThuongHieu  = db.Column(db.String(100), nullable=False, unique=True)
    QuocGiaXuatXu  = db.Column(db.String(100), nullable=False)
    NamThanhLap    = db.Column(db.Integer)
    MoTa           = db.Column(db.String(500))
    Logo           = db.Column(db.String(255))
    TrangThai      = db.Column(db.Boolean, default=True)

    # Relationships
    san_phams   = db.relationship('SanPham', backref='thuong_hieu', lazy=True)
    ma_giam_gia = db.relationship('MaGiamGia', backref='thuong_hieu', lazy=True)

    def __repr__(self):
        return f'<ThuongHieu {self.TenThuongHieu}>'


# ─────────────────────────────────────────
# 2. DANH MỤC (tự tham chiếu - danh mục cha/con)
# ─────────────────────────────────────────
class DanhMuc(db.Model):
    __tablename__ = 'DanhMuc'
    __table_args__ = {'extend_existing': True}

    DanhMucID    = db.Column(db.Integer, primary_key=True)
    TenDanhMuc   = db.Column(db.String(100), nullable=False, unique=True)
    DanhMucChaID = db.Column(db.Integer, db.ForeignKey('DanhMuc.DanhMucID'), nullable=True)
    MoTa         = db.Column(db.String(300))
    TrangThai    = db.Column(db.Boolean, default=True)

    # Self-referential relationship
    danh_muc_con = db.relationship('DanhMuc', backref=db.backref('danh_muc_cha', remote_side='DanhMuc.DanhMucID'), lazy=True)
    san_phams    = db.relationship('SanPham', backref='danh_muc', lazy=True)

    def __repr__(self):
        return f'<DanhMuc {self.TenDanhMuc}>'


# ─────────────────────────────────────────
# 3. SẢN PHẨM
# ─────────────────────────────────────────
class SanPham(db.Model):
    __tablename__ = 'SanPham'
    __table_args__ = {'extend_existing': True}

    SanPhamID    = db.Column(db.Integer, primary_key=True)
    TenSanPham   = db.Column(db.String(200), nullable=False)
    MaSanPham    = db.Column(db.String(50), nullable=False, unique=True)
    ThuongHieuID = db.Column(db.Integer, db.ForeignKey('ThuongHieu.ThuongHieuID'), nullable=False)
    DanhMucID    = db.Column(db.Integer, db.ForeignKey('DanhMuc.DanhMucID'), nullable=False)
    GiaBan       = db.Column(db.Numeric(18, 2), nullable=False)
    GiaGoc       = db.Column(db.Numeric(18, 2), nullable=False)
    ChatLieu     = db.Column(db.String(200))
    XuatXu       = db.Column(db.String(100), nullable=False)
    MoTa         = db.Column(db.Text)
    TrangThai    = db.Column(db.String(20), default='DangBan')

    # Relationships
    bien_thes       = db.relationship('BienTheSanPham', backref='san_pham', lazy=True)
    hinh_anhs       = db.relationship('HinhAnhSanPham', backref='san_pham', lazy=True)
    giay_chung_nans = db.relationship('GiayChungNhan', backref='san_pham', lazy=True)
    danh_gias       = db.relationship('DanhGia', backref='san_pham', lazy=True)

    @property
    def anh_chinh(self):
        """Trả về ảnh chính của sản phẩm, dùng trong template."""
        anh = HinhAnhSanPham.query.filter_by(SanPhamID=self.SanPhamID, LaAnhChinh=True).first()
        return anh.DuongDan if anh else 'default.jpg'

    def __repr__(self):
        return f'<SanPham {self.TenSanPham}>'


# ─────────────────────────────────────────
# 4. GIẤY CHỨNG NHẬN
# ─────────────────────────────────────────
class GiayChungNhan(db.Model):
    __tablename__ = 'GiayChungNhan'
    __table_args__ = {'extend_existing': True}

    GiayChungNhanID = db.Column(db.Integer, primary_key=True)
    SanPhamID       = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    MaChungNhan     = db.Column(db.String(100), nullable=False, unique=True)
    ToChucCap       = db.Column(db.String(200), nullable=False)
    NgayCap         = db.Column(db.Date, nullable=False)
    NgayHetHan      = db.Column(db.Date, nullable=True)
    QRCode          = db.Column(db.String(500))

    def __repr__(self):
        return f'<GiayChungNhan {self.MaChungNhan}>'


# ─────────────────────────────────────────
# 5. BIẾN THỂ SẢN PHẨM (màu sắc, kích thước, tồn kho)
# ─────────────────────────────────────────
class BienTheSanPham(db.Model):
    __tablename__ = 'BienTheSanPham'
    __table_args__ = {'extend_existing': True}

    BienTheID    = db.Column(db.Integer, primary_key=True)
    SanPhamID    = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    SerialNumber = db.Column(db.String(100), nullable=False, unique=True)
    MauSac       = db.Column(db.String(50), nullable=False)
    KichThuoc    = db.Column(db.String(20))
    MaVach       = db.Column(db.String(50), nullable=False, unique=True)
    SoLuongTon   = db.Column(db.Integer, nullable=False, default=0)
    GiaBanRieng  = db.Column(db.Numeric(18, 2), nullable=True)
    HinhAnh      = db.Column(db.String(255))

    # Relationships
    gio_hangs       = db.relationship('GioHang', backref='bien_the', lazy=True)
    chi_tiet_dh     = db.relationship('ChiTietDonHang', backref='bien_the', lazy=True)
    bao_hanhs       = db.relationship('BaoHanh', backref='bien_the', lazy=True)

    def gia_hien_tai(self):
        """Trả về giá riêng nếu có, không thì dùng giá sản phẩm."""
        return self.GiaBanRieng if self.GiaBanRieng else self.san_pham.GiaBan

    def __repr__(self):
        return f'<BienThe {self.MauSac} - {self.KichThuoc}>'


# ─────────────────────────────────────────
# 6. HÌNH ẢNH SẢN PHẨM
# ─────────────────────────────────────────
class HinhAnhSanPham(db.Model):
    __tablename__ = 'HinhAnhSanPham'
    __table_args__ = {'extend_existing': True}

    HinhAnhID  = db.Column(db.Integer, primary_key=True)
    SanPhamID  = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    DuongDan   = db.Column(db.String(500), nullable=False)
    LaAnhChinh = db.Column(db.Boolean, default=False)
    ThuTu      = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<HinhAnh {self.DuongDan}>'


# ─────────────────────────────────────────
# 7. KHÁCH HÀNG
# ─────────────────────────────────────────
class KhachHang(db.Model):
    __tablename__ = 'KhachHang'
    __table_args__ = {'extend_existing': True}

    KhachHangID   = db.Column(db.Integer, primary_key=True)
    HoTen         = db.Column(db.String(100), nullable=False)
    Email         = db.Column(db.String(150), nullable=False, unique=True)
    MatKhau       = db.Column(db.String(255), nullable=False)
    SoDienThoai   = db.Column(db.String(15), unique=True)
    NgaySinh      = db.Column(db.Date, nullable=True)
    HangThanhVien = db.Column(db.String(20), default='Standard')
    DiemTichLuy   = db.Column(db.Integer, default=0)
    TongChiTieu   = db.Column(db.Numeric(18, 2), default=0)
    NgayDangKy    = db.Column(db.DateTime, default=datetime.now)

    # Relationships
    don_hangs  = db.relationship('DonHang', backref='khach_hang', lazy=True)
    gio_hangs  = db.relationship('GioHang', backref='khach_hang', lazy=True)
    danh_gias  = db.relationship('DanhGia', backref='khach_hang', lazy=True)
    chuong_trinh_vip = db.relationship('ChuongTrinhVIP', backref='khach_hang', uselist=False)

    # Flask-Login interface (nếu dùng flask-login sau này)
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.KhachHangID)

    def __repr__(self):
        return f'<KhachHang {self.Email}>'


# ─────────────────────────────────────────
# 8. CHƯƠNG TRÌNH VIP
# ─────────────────────────────────────────
class ChuongTrinhVIP(db.Model):
    __tablename__ = 'ChuongTrinhVIP'
    __table_args__ = {'extend_existing': True}

    VIPProgramID  = db.Column(db.Integer, primary_key=True)
    KhachHangID   = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False, unique=True)
    HangVIP       = db.Column(db.String(20), nullable=False)
    DiemHienTai   = db.Column(db.Integer, default=0)
    NgayLenHang   = db.Column(db.Date, nullable=False)
    NgayHetHan    = db.Column(db.Date, nullable=True)
    UuDaiPhanTram = db.Column(db.Numeric(5, 2), default=0)

    def __repr__(self):
        return f'<VIP {self.HangVIP} - KH {self.KhachHangID}>'


# ─────────────────────────────────────────
# 9. MÃ GIẢM GIÁ
# ─────────────────────────────────────────
class MaGiamGia(db.Model):
    __tablename__ = 'MaGiamGia'
    __table_args__ = {'extend_existing': True}

    MaGiamGiaID     = db.Column(db.Integer, primary_key=True)
    MaCode          = db.Column(db.String(50), nullable=False, unique=True)
    ThuongHieuID    = db.Column(db.Integer, db.ForeignKey('ThuongHieu.ThuongHieuID'), nullable=True)
    LoaiGiam        = db.Column(db.String(30), nullable=False)   # 'PhanTram' | 'SoTienCoDinh'
    GiaTri          = db.Column(db.Numeric(10, 2), nullable=False)
    GiamToiDa       = db.Column(db.Numeric(18, 2), nullable=True)
    DonHangToiThieu = db.Column(db.Numeric(18, 2), default=0)
    NgayBatDau      = db.Column(db.Date, nullable=False)
    NgayKetThuc     = db.Column(db.Date, nullable=False)
    SoLuotToiDa     = db.Column(db.Integer, nullable=True)
    SoLuotDaDung    = db.Column(db.Integer, default=0)
    TrangThai       = db.Column(db.Boolean, default=True)

    # Relationships
    don_hangs = db.relationship('DonHang', backref='ma_giam_gia', lazy=True)

    def con_hieu_luc(self):
        """Kiểm tra mã còn dùng được không."""
        from datetime import date
        hom_nay = date.today()
        het_luot = self.SoLuotToiDa and self.SoLuotDaDung >= self.SoLuotToiDa
        return (self.TrangThai and
                self.NgayBatDau <= hom_nay <= self.NgayKetThuc and
                not het_luot)

    def __repr__(self):
        return f'<MaGiamGia {self.MaCode}>'


# ─────────────────────────────────────────
# 10. ĐƠN HÀNG
# ─────────────────────────────────────────
class DonHang(db.Model):
    __tablename__ = 'DonHang'
    __table_args__ = {'extend_existing': True}

    DonHangID    = db.Column(db.Integer, primary_key=True)
    MaDonHang    = db.Column(db.String(20), nullable=False, unique=True)
    KhachHangID  = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    MaGiamGiaID  = db.Column(db.Integer, db.ForeignKey('MaGiamGia.MaGiamGiaID'), nullable=True)
    TrangThai    = db.Column(db.String(30), default='ChoXacNhan')
    TongTienHang = db.Column(db.Numeric(18, 2), nullable=False)
    GiamGia      = db.Column(db.Numeric(18, 2), default=0)
    ThanhToan    = db.Column(db.Numeric(18, 2), nullable=False)
    DiaChiGiao   = db.Column(db.String(300), nullable=False)
    NgayDat      = db.Column(db.DateTime, default=datetime.now)
    GhiChu       = db.Column(db.String(500))

    # Relationships
    chi_tiets  = db.relationship('ChiTietDonHang', backref='don_hang', lazy=True)
    thanh_toan = db.relationship('ThanhToan', backref='don_hang', lazy=True)
    bao_hanhs  = db.relationship('BaoHanh', backref='don_hang', lazy=True)

    def __repr__(self):
        return f'<DonHang {self.MaDonHang}>'


# ─────────────────────────────────────────
# 11. CHI TIẾT ĐƠN HÀNG
# ─────────────────────────────────────────
class ChiTietDonHang(db.Model):
    __tablename__ = 'ChiTietDonHang'
    __table_args__ = {'extend_existing': True}

    ChiTietID    = db.Column(db.Integer, primary_key=True)
    DonHangID    = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'), nullable=False)
    BienTheID    = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'), nullable=False)
    SoLuong      = db.Column(db.Integer, nullable=False)
    DonGia       = db.Column(db.Numeric(18, 2), nullable=False)
    GiamGiaDong  = db.Column(db.Numeric(18, 2), default=0)
    ThanhTienDong = db.Column(db.Numeric(18, 2), nullable=False)

    def __repr__(self):
        return f'<ChiTiet DH={self.DonHangID} BT={self.BienTheID}>'


# ─────────────────────────────────────────
# 12. BẢO HÀNH
# ─────────────────────────────────────────
class BaoHanh(db.Model):
    __tablename__ = 'BaoHanh'
    __table_args__ = {'extend_existing': True}

    BaoHanhID          = db.Column(db.Integer, primary_key=True)
    BienTheID          = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'), nullable=False)
    KhachHangID        = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    DonHangID          = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'), nullable=False)
    NgayBatDau         = db.Column(db.Date, nullable=False)
    NgayKetThuc        = db.Column(db.Date, nullable=False)
    DieuKienBaoHanh    = db.Column(db.String(500))
    TrangThaiBaoHanh   = db.Column(db.String(20), default='ConHan')

    def __repr__(self):
        return f'<BaoHanh {self.BaoHanhID} - {self.TrangThaiBaoHanh}>'


# ─────────────────────────────────────────
# 13. THANH TOÁN
# ─────────────────────────────────────────
class ThanhToan(db.Model):
    __tablename__ = 'ThanhToan'
    __table_args__ = {'extend_existing': True}

    ThanhToanID  = db.Column(db.Integer, primary_key=True)
    DonHangID    = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'), nullable=False)
    PhuongThuc   = db.Column(db.String(30), nullable=False)
    SoTien       = db.Column(db.Numeric(18, 2), nullable=False)
    MaGiaoDich   = db.Column(db.String(100), unique=True)
    TrangThai    = db.Column(db.String(20), default='ChoPhanHoi')
    ThoiGian     = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<ThanhToan {self.PhuongThuc} - {self.TrangThai}>'


# ─────────────────────────────────────────
# 14. ĐÁNH GIÁ
# ─────────────────────────────────────────
class DanhGia(db.Model):
    __tablename__ = 'DanhGia'
    __table_args__ = {'extend_existing': True}

    DanhGiaID   = db.Column(db.Integer, primary_key=True)
    SanPhamID   = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    KhachHangID = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    MaGiamGiaID = db.Column(db.Integer, db.ForeignKey('MaGiamGia.MaGiamGiaID'), nullable=True)
    DiemSo      = db.Column(db.SmallInteger, nullable=False)
    NhanXet     = db.Column(db.Text)
    DaXacNhan   = db.Column(db.Boolean, default=False)
    NgayDanhGia = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<DanhGia SP={self.SanPhamID} KH={self.KhachHangID} Diem={self.DiemSo}>'


# ─────────────────────────────────────────
# 15. GIỎ HÀNG
# ─────────────────────────────────────────
class GioHang(db.Model):
    __tablename__ = 'GioHang'
    __table_args__ = {'extend_existing': True}

    GioHangID   = db.Column(db.Integer, primary_key=True)
    KhachHangID = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    BienTheID   = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'), nullable=False)
    SoLuong     = db.Column(db.Integer, nullable=False)
    NgayThem    = db.Column(db.DateTime, default=datetime.now)

    def thanh_tien(self):
        """Tính thành tiền cho dòng giỏ hàng này."""
        return self.SoLuong * float(self.bien_the.gia_hien_tai())

    def __repr__(self):
        return f'<GioHang KH={self.KhachHangID} BT={self.BienTheID} SL={self.SoLuong}>'


# ─────────────────────────────────────────
# 16. NHÂN VIÊN
# ─────────────────────────────────────────
class NhanVien(db.Model):
    __tablename__ = 'NhanVien'
    __table_args__ = {'extend_existing': True}

    NhanVienID  = db.Column(db.Integer, primary_key=True)
    HoTen       = db.Column(db.String(100), nullable=False)
    Email       = db.Column(db.String(100), nullable=False, unique=True)
    MatKhau     = db.Column(db.String(255), nullable=False)
    SoDienThoai = db.Column(db.String(15), unique=True)
    VaiTro      = db.Column(db.String(30), default='NhanVienBanHang')
    TrangThai   = db.Column(db.Boolean, default=True)
    NgayTao     = db.Column(db.DateTime, default=datetime.now)
    NgayCapNhat = db.Column(db.DateTime, default=datetime.now)

    # Flask-Login interface cho nhân viên
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.TrangThai

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return f'nv_{self.NhanVienID}'

    def is_admin(self):
        return self.VaiTro in ('Admin', 'SuperAdmin')

    def __repr__(self):
        return f'<NhanVien {self.Email} - {self.VaiTro}>'