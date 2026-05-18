from datetime import datetime,timezone
from flask_login import UserMixin
from extensions import db


# ─────────────────────────────────────────────
# 1. ThuongHieu
# ─────────────────────────────────────────────
class ThuongHieu(db.Model):
    __tablename__ = 'ThuongHieu'

    ThuongHieuID   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenThuongHieu  = db.Column(db.String(100), nullable=False, unique=True)
    QuocGiaXuatXu  = db.Column(db.String(100), nullable=False)
    NamThanhLap    = db.Column(db.Integer, db.CheckConstraint('NamThanhLap > 1800'))
    MoTa           = db.Column(db.String(500))
    Logo           = db.Column(db.String(255))
    TrangThai      = db.Column(db.SmallInteger, default=1)

    san_phams      = db.relationship('SanPham',    back_populates='thuong_hieu', lazy='dynamic')
    ma_giam_gias   = db.relationship('MaGiamGia',  back_populates='thuong_hieu', lazy='dynamic')


# ─────────────────────────────────────────────
# 2. DanhMuc
# ─────────────────────────────────────────────
class DanhMuc(db.Model):
    __tablename__ = 'DanhMuc'

    DanhMucID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenDanhMuc     = db.Column(db.String(100), nullable=False, unique=True)
    DanhMucChaID   = db.Column(db.Integer, db.ForeignKey('DanhMuc.DanhMucID'), nullable=True)
    MoTa           = db.Column(db.String(300))
    TrangThai      = db.Column(db.SmallInteger, default=1)

    danh_muc_con   = db.relationship('DanhMuc', backref=db.backref('danh_muc_cha', remote_side='DanhMuc.DanhMucID'))
    san_phams      = db.relationship('SanPham', back_populates='danh_muc', lazy='dynamic')


# ─────────────────────────────────────────────
# 3. SanPham
# ─────────────────────────────────────────────
class SanPham(db.Model):
    __tablename__ = 'SanPham'

    SanPhamID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    TenSanPham     = db.Column(db.String(200), nullable=False)
    MaSanPham      = db.Column(db.String(50),  nullable=False, unique=True)
    ThuongHieuID   = db.Column(db.Integer, db.ForeignKey('ThuongHieu.ThuongHieuID'), nullable=False)
    DanhMucID      = db.Column(db.Integer, db.ForeignKey('DanhMuc.DanhMucID'),       nullable=False)
    GiaBan         = db.Column(db.Numeric(18, 2), nullable=False)
    GiaGoc         = db.Column(db.Numeric(18, 2), nullable=False)
    ChatLieu       = db.Column(db.String(200))
    XuatXu         = db.Column(db.String(100), nullable=False)
    MoTa           = db.Column(db.Text)
    TrangThai      = db.Column(db.String(20), default='DangBan')

    thuong_hieu    = db.relationship('ThuongHieu',      back_populates='san_phams')
    danh_muc       = db.relationship('DanhMuc',         back_populates='san_phams')
    bien_thes      = db.relationship('BienTheSanPham',  back_populates='san_pham', lazy='dynamic')
    hinh_anhs      = db.relationship('HinhAnhSanPham',  back_populates='san_pham', lazy='dynamic')
    giay_chung_nhans = db.relationship('GiayChungNhan', back_populates='san_pham', lazy='dynamic')
    danh_gias      = db.relationship('DanhGia',         back_populates='san_pham', lazy='dynamic')


# ─────────────────────────────────────────────
# 4. GiayChungNhan
# ─────────────────────────────────────────────
class GiayChungNhan(db.Model):
    __tablename__ = 'GiayChungNhan'

    GiayChungNhanID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SanPhamID       = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    MaChungNhan     = db.Column(db.String(100), nullable=False, unique=True)
    ToChucCap       = db.Column(db.String(200), nullable=False)
    NgayCap         = db.Column(db.Date, nullable=False)
    NgayHetHan      = db.Column(db.Date)
    QRCode          = db.Column(db.String(500))

    san_pham        = db.relationship('SanPham', back_populates='giay_chung_nhans')


# ─────────────────────────────────────────────
# 5. BienTheSanPham
# ─────────────────────────────────────────────
class BienTheSanPham(db.Model):
    __tablename__ = 'BienTheSanPham'

    BienTheID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SanPhamID      = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    SerialNumber   = db.Column(db.String(100), nullable=False, unique=True)
    MauSac         = db.Column(db.String(50),  nullable=False)
    KichThuoc      = db.Column(db.String(20))
    MaVach         = db.Column(db.String(50),  nullable=False, unique=True)
    SoLuongTon     = db.Column(db.Integer, nullable=False, default=0)
    GiaBanRieng    = db.Column(db.Numeric(18, 2))
    HinhAnh        = db.Column(db.String(255))

    san_pham       = db.relationship('SanPham',       back_populates='bien_thes')
    chi_tiet_don_hangs = db.relationship('ChiTietDonHang', back_populates='bien_the', lazy='dynamic')
    bao_hanhs      = db.relationship('BaoHanh',       back_populates='bien_the',  lazy='dynamic')
    gio_hangs      = db.relationship('GioHang',       back_populates='bien_the',  lazy='dynamic')


# ─────────────────────────────────────────────
# 6. HinhAnhSanPham
# ─────────────────────────────────────────────
class HinhAnhSanPham(db.Model):
    __tablename__ = 'HinhAnhSanPham'

    HinhAnhID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SanPhamID      = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'), nullable=False)
    DuongDan       = db.Column(db.String(500), nullable=False)
    LaAnhChinh     = db.Column(db.SmallInteger, default=0)
    ThuTu          = db.Column(db.Integer, default=1)

    san_pham       = db.relationship('SanPham', back_populates='hinh_anhs')


# ─────────────────────────────────────────────
# 7. KhachHang
# ─────────────────────────────────────────────
class KhachHang(UserMixin, db.Model):
    __tablename__ = 'KhachHang'

    KhachHangID    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen          = db.Column(db.String(100), nullable=False)
    Email          = db.Column(db.String(150), nullable=False, unique=True)
    MatKhau        = db.Column(db.String(255), nullable=False)
    SoDienThoai    = db.Column(db.String(15),  unique=True)
    NgaySinh       = db.Column(db.Date)
    HangThanhVien  = db.Column(db.String(20),  default='Standard')
    DiemTichLuy    = db.Column(db.Integer, default=0)
    TongChiTieu    = db.Column(db.Numeric(18, 2), default=0)
    NgayDangKy     = db.Column(db.DateTime, default=datetime.utcnow)

    don_hangs      = db.relationship('DonHang',        back_populates='khach_hang', lazy='dynamic')
    danh_gias      = db.relationship('DanhGia',        back_populates='khach_hang', lazy='dynamic')
    bao_hanhs      = db.relationship('BaoHanh',        back_populates='khach_hang', lazy='dynamic')
    gio_hangs      = db.relationship('GioHang',        back_populates='khach_hang', lazy='dynamic')
    chuong_trinh_vip = db.relationship('ChuongTrinhVIP', back_populates='khach_hang', uselist=False)

    def get_id(self):
        return str(self.KhachHangID)


# ─────────────────────────────────────────────
# 8. ChuongTrinhVIP
# ─────────────────────────────────────────────
class ChuongTrinhVIP(db.Model):
    __tablename__ = 'ChuongTrinhVIP'

    VIPProgramID   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    KhachHangID    = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False, unique=True)
    HangVIP        = db.Column(db.String(20), nullable=False)
    DiemHienTai    = db.Column(db.Integer, default=0)
    NgayLenHang    = db.Column(db.Date, nullable=False)
    NgayHetHan     = db.Column(db.Date)
    UuDaiPhanTram  = db.Column(db.Numeric(5, 2), default=0)

    khach_hang     = db.relationship('KhachHang', back_populates='chuong_trinh_vip')


# ─────────────────────────────────────────────
# 9. DonHang
# ─────────────────────────────────────────────
class DonHang(db.Model):
    __tablename__ = 'DonHang'

    DonHangID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaDonHang      = db.Column(db.String(20),  nullable=False, unique=True)
    KhachHangID    = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    TrangThai      = db.Column(db.String(20),  default='ChoXacNhan')
    TongTienHang   = db.Column(db.Numeric(18, 2), nullable=False)
    GiamGia        = db.Column(db.Numeric(18, 2), default=0)
    ThanhToan      = db.Column(db.Numeric(18, 2), nullable=False)
    DiaChiGiao     = db.Column(db.String(300), nullable=False)
    NgayDat        = db.Column(db.DateTime, default=datetime.utcnow)
    GhiChu         = db.Column(db.String(500))

    khach_hang     = db.relationship('KhachHang',      back_populates='don_hangs')
    chi_tiets      = db.relationship('ChiTietDonHang', back_populates='don_hang', lazy='dynamic')
    thanh_toans    = db.relationship('ThanhToan',      back_populates='don_hang', lazy='dynamic')
    bao_hanhs      = db.relationship('BaoHanh',        back_populates='don_hang', lazy='dynamic')


# ─────────────────────────────────────────────
# 10. ChiTietDonHang
# ─────────────────────────────────────────────
class ChiTietDonHang(db.Model):
    __tablename__ = 'ChiTietDonHang'

    ChiTietID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DonHangID      = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'),         nullable=False)
    BienTheID      = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'),  nullable=False)
    SoLuong        = db.Column(db.Integer, nullable=False)
    DonGia         = db.Column(db.Numeric(18, 2), nullable=False)
    GiamGiaDong    = db.Column(db.Numeric(18, 2), default=0)
    ThanhTienDong  = db.Column(db.Numeric(18, 2), nullable=False)

    don_hang       = db.relationship('DonHang',       back_populates='chi_tiets')
    bien_the       = db.relationship('BienTheSanPham', back_populates='chi_tiet_don_hangs')


# ─────────────────────────────────────────────
# 11. BaoHanh
# ─────────────────────────────────────────────
class BaoHanh(db.Model):
    __tablename__ = 'BaoHanh'

    BaoHanhID          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BienTheID          = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'), nullable=False)
    KhachHangID        = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'),   nullable=False)
    DonHangID          = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'),        nullable=False)
    NgayBatDau         = db.Column(db.Date, nullable=False)
    NgayKetThuc        = db.Column(db.Date, nullable=False)
    DieuKienBaoHanh    = db.Column(db.String(500))
    TrangThaiBaoHanh   = db.Column(db.String(20), default='ConHan')

    bien_the       = db.relationship('BienTheSanPham', back_populates='bao_hanhs')
    khach_hang     = db.relationship('KhachHang',      back_populates='bao_hanhs')
    don_hang       = db.relationship('DonHang',        back_populates='bao_hanhs')


# ─────────────────────────────────────────────
# 12. ThanhToan
# ─────────────────────────────────────────────
class ThanhToan(db.Model):
    __tablename__ = 'ThanhToan'

    ThanhToanID    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DonHangID      = db.Column(db.Integer, db.ForeignKey('DonHang.DonHangID'), nullable=False)
    PhuongThuc     = db.Column(db.String(20), nullable=False)
    SoTien         = db.Column(db.Numeric(18, 2), nullable=False)
    MaGiaoDich     = db.Column(db.String(100), unique=True)
    TrangThai      = db.Column(db.String(20), default='ChoPhanHoi')
    ThoiGian       = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    don_hang       = db.relationship('DonHang', back_populates='thanh_toans')


# ─────────────────────────────────────────────
# 13. DanhGia
# ─────────────────────────────────────────────
class DanhGia(db.Model):
    __tablename__ = 'DanhGia'

    DanhGiaID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SanPhamID      = db.Column(db.Integer, db.ForeignKey('SanPham.SanPhamID'),     nullable=False)
    KhachHangID    = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'), nullable=False)
    MaGiamGiaID    = db.Column(db.Integer, db.ForeignKey('MaGiamGia.MaGiamGiaID'), nullable=True)
    DiemSo         = db.Column(db.SmallInteger, nullable=False)
    NhanXet        = db.Column(db.Text)
    DaXacNhan      = db.Column(db.SmallInteger, default=0)
    NgayDanhGia    = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    san_pham       = db.relationship('SanPham',   back_populates='danh_gias')
    khach_hang     = db.relationship('KhachHang', back_populates='danh_gias')
    ma_giam_gia    = db.relationship('MaGiamGia', back_populates='danh_gias')


# ─────────────────────────────────────────────
# 14. MaGiamGia
# ─────────────────────────────────────────────
class MaGiamGia(db.Model):
    __tablename__ = 'MaGiamGia'

    MaGiamGiaID     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaCode          = db.Column(db.String(50),  nullable=False, unique=True)
    ThuongHieuID    = db.Column(db.Integer, db.ForeignKey('ThuongHieu.ThuongHieuID'), nullable=True)
    LoaiGiam        = db.Column(db.String(20),  nullable=False)
    GiaTri          = db.Column(db.Numeric(10, 2), nullable=False)
    GiamToiDa      = db.Column(db.Numeric(18, 2))
    DonHangToiThieu = db.Column(db.Numeric(18, 2), default=0)
    NgayBatDau      = db.Column(db.Date, nullable=False)
    NgayKetThuc     = db.Column(db.Date, nullable=False)
    SoLuotToiDa     = db.Column(db.Integer)
    SoLuotDaDung    = db.Column(db.Integer, default=0)
    TrangThai       = db.Column(db.SmallInteger, default=1)

    thuong_hieu     = db.relationship('ThuongHieu', back_populates='ma_giam_gias')
    danh_gias       = db.relationship('DanhGia',    back_populates='ma_giam_gia', lazy='dynamic')


# ─────────────────────────────────────────────
# 15. GioHang
# ─────────────────────────────────────────────
class GioHang(db.Model):
    __tablename__ = 'GioHang'

    GioHangID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    KhachHangID    = db.Column(db.Integer, db.ForeignKey('KhachHang.KhachHangID'),   nullable=False)
    BienTheID      = db.Column(db.Integer, db.ForeignKey('BienTheSanPham.BienTheID'), nullable=False)
    SoLuong        = db.Column(db.Integer, nullable=False)
    NgayThem       = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('KhachHangID', 'BienTheID', name='uq_giohang_khachhang_bienthe'),
    )

    khach_hang     = db.relationship('KhachHang',      back_populates='gio_hangs')
    bien_the       = db.relationship('BienTheSanPham', back_populates='gio_hangs')


# ─────────────────────────────────────────────
# 16. NhanVien (Admin)
# ─────────────────────────────────────────────
class NhanVien(UserMixin, db.Model):
    __tablename__ = 'NhanVien'

    NhanVienID     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HoTen          = db.Column(db.String(100), nullable=False)
    Email          = db.Column(db.String(100), nullable=False, unique=True)
    MatKhau        = db.Column(db.String(100), nullable=False)
    SoDienThoai    = db.Column(db.String(15),  unique=True)
    VaiTro         = db.Column(db.String(20),  default='NhanVienBanHang')
    TrangThai      = db.Column(db.SmallInteger, default=1)
    NgayTao        = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    NgayCapNhat    = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def get_id(self):
        return f"nv-{self.NhanVienID}"