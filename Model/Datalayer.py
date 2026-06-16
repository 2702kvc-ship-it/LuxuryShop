"""
datalayer.py
Tầng truy vấn dữ liệu thuần ORM — KHÔNG chứa logic nghiệp vụ.
Mọi hàm chỉ đọc/ghi DB, trả về object hoặc None/list.
"""

from extensions import db
from Model.Models import (
    ThuongHieu, DanhMuc, SanPham, GiayChungNhan,
    BienTheSanPham, HinhAnhSanPham, KhachHang,
    ChuongTrinhVIP, DonHang, ChiTietDonHang,
    BaoHanh, ThanhToan, DanhGia, MaGiamGia,
    GioHang, NhanVien,
)


# ══════════════════════════════════════════════
# ThuongHieu
# ══════════════════════════════════════════════
def get_all_thuong_hieu():
    return ThuongHieu.query.filter_by(TrangThai=1).all()

def get_thuong_hieu_by_id(thuong_hieu_id):
    return db.session.get(ThuongHieu, thuong_hieu_id)

def create_thuong_hieu(data: dict):
    obj = ThuongHieu(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_thuong_hieu(thuong_hieu_id, data: dict):
    obj = db.session.get(ThuongHieu, thuong_hieu_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj

def delete_thuong_hieu(thuong_hieu_id):
    obj = db.session.get(ThuongHieu, thuong_hieu_id)
    if not obj:
        return False
    obj.TrangThai = 0
    db.session.commit()
    return True


# ══════════════════════════════════════════════
# DanhMuc
# ══════════════════════════════════════════════
def get_all_danh_muc():
    return DanhMuc.query.filter_by(TrangThai=1).all()

def get_danh_muc_by_id(danh_muc_id):
    return db.session.get(DanhMuc, danh_muc_id)

def get_danh_muc_con(danh_muc_cha_id):
    return DanhMuc.query.filter_by(DanhMucChaID=danh_muc_cha_id, TrangThai=1).all()

def create_danh_muc(data: dict):
    obj = DanhMuc(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_danh_muc(danh_muc_id, data: dict):
    obj = db.session.get(DanhMuc, danh_muc_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# SanPham
# ══════════════════════════════════════════════
def get_all_san_pham(trang_thai='DangBan'):
    return SanPham.query.filter_by(TrangThai=trang_thai).all()

def get_san_pham_by_id(san_pham_id):
    return db.session.get(SanPham, san_pham_id)

def get_san_pham_by_thuong_hieu(thuong_hieu_id):
    return SanPham.query.filter_by(ThuongHieuID=thuong_hieu_id, TrangThai='DangBan').all()

def get_san_pham_by_danh_muc(danh_muc_id):
    return SanPham.query.filter_by(DanhMucID=danh_muc_id, TrangThai='DangBan').all()

def search_san_pham(keyword: str):
    pattern = f'%{keyword}%'
    return SanPham.query.filter(
        SanPham.TenSanPham.like(pattern) | SanPham.MaSanPham.like(pattern)
    ).all()

def create_san_pham(data: dict):
    obj = SanPham(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_san_pham(san_pham_id, data: dict):
    obj = db.session.get(SanPham, san_pham_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# GiayChungNhan
# ══════════════════════════════════════════════
def get_giay_chung_nhan_by_san_pham(san_pham_id):
    return GiayChungNhan.query.filter_by(SanPhamID=san_pham_id).all()

def get_giay_chung_nhan_by_ma(ma_chung_nhan: str):
    return GiayChungNhan.query.filter_by(MaChungNhan=ma_chung_nhan).first()

def create_giay_chung_nhan(data: dict):
    obj = GiayChungNhan(**data)
    db.session.add(obj)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# BienTheSanPham
# ══════════════════════════════════════════════
def get_bien_the_by_san_pham(san_pham_id):
    return BienTheSanPham.query.filter_by(SanPhamID=san_pham_id).all()

def get_bien_the_by_id(bien_the_id):
    return db.session.get(BienTheSanPham, bien_the_id)

def get_bien_the_by_serial(serial_number: str):
    return BienTheSanPham.query.filter_by(SerialNumber=serial_number).first()

def update_ton_kho(bien_the_id, delta: int):
    """delta dương = nhập kho, âm = xuất kho"""
    obj = db.session.get(BienTheSanPham, bien_the_id)
    if not obj:
        return None
    obj.SoLuongTon += delta
    db.session.commit()
    return obj

def create_bien_the(data: dict):
    obj = BienTheSanPham(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_bien_the(bien_the_id, data: dict):
    obj = db.session.get(BienTheSanPham, bien_the_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# HinhAnhSanPham
# ══════════════════════════════════════════════
def get_hinh_anh_by_san_pham(san_pham_id):
    return HinhAnhSanPham.query.filter_by(SanPhamID=san_pham_id).order_by(HinhAnhSanPham.ThuTu).all()

def get_anh_chinh(san_pham_id):
    return HinhAnhSanPham.query.filter_by(SanPhamID=san_pham_id, LaAnhChinh=1).first()

def create_hinh_anh(data: dict):
    obj = HinhAnhSanPham(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def delete_hinh_anh(hinh_anh_id):
    obj = db.session.get(HinhAnhSanPham, hinh_anh_id)
    if not obj:
        return False
    db.session.delete(obj)
    db.session.commit()
    return True


# ══════════════════════════════════════════════
# KhachHang
# ══════════════════════════════════════════════
def get_khach_hang_by_id(khach_hang_id):
    return db.session.get(KhachHang, khach_hang_id)

def get_khach_hang_by_email(email: str):
    return KhachHang.query.filter_by(Email=email.strip().lower()).first()

def get_all_khach_hang():
    return KhachHang.query.all()

def create_khach_hang(data: dict):
    obj = KhachHang(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_khach_hang(khach_hang_id, data: dict):
    obj = db.session.get(KhachHang, khach_hang_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# ChuongTrinhVIP
# ══════════════════════════════════════════════
def get_vip_by_khach_hang(khach_hang_id):
    return ChuongTrinhVIP.query.filter_by(KhachHangID=khach_hang_id).first()

def get_giamgia_vip(khach_hang_id):
    vip = get_vip_by_khach_hang(khach_hang_id)
    if not vip:
        return 0
    return vip.UuDaiPhanTram or 0
def create_or_update_vip(khach_hang_id, data: dict):
    obj = get_vip_by_khach_hang(khach_hang_id)
    if obj:
        for k, v in data.items():
            setattr(obj, k, v)
    else:
        obj = ChuongTrinhVIP(KhachHangID=khach_hang_id, **data)
        db.session.add(obj)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# DonHang
# ══════════════════════════════════════════════
def get_don_hang_by_id(don_hang_id):
    return db.session.get(DonHang, don_hang_id)

def get_don_hang_by_ma(ma_don_hang: str):
    return DonHang.query.filter_by(MaDonHang=ma_don_hang).first()

def get_don_hang_by_khach_hang(khach_hang_id):
    return DonHang.query.filter_by(KhachHangID=khach_hang_id).order_by(DonHang.NgayDat.desc()).all()

def get_all_don_hang(trang_thai=None):
    q = DonHang.query
    if trang_thai:
        q = q.filter_by(TrangThai=trang_thai)
    return q.order_by(DonHang.NgayDat.desc()).all()

def create_don_hang(data: dict):
    obj = DonHang(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_trang_thai_don_hang(don_hang_id, trang_thai: str):
    obj = db.session.get(DonHang, don_hang_id)
    if not obj:
        return None
    obj.TrangThai = trang_thai
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# ChiTietDonHang
# ══════════════════════════════════════════════
def get_chi_tiet_by_don_hang(don_hang_id):
    return ChiTietDonHang.query.filter_by(DonHangID=don_hang_id).all()

def create_chi_tiet(data: dict):
    obj = ChiTietDonHang(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def bulk_create_chi_tiet(list_data: list):
    objs = [ChiTietDonHang(**d) for d in list_data]
    db.session.bulk_save_objects(objs)
    db.session.commit()
    return objs


# ══════════════════════════════════════════════
# BaoHanh
# ══════════════════════════════════════════════
def get_bao_hanh_by_khach_hang(khach_hang_id):
    return BaoHanh.query.filter_by(KhachHangID=khach_hang_id).all()

def get_bao_hanh_by_don_hang(don_hang_id):
    return BaoHanh.query.filter_by(DonHangID=don_hang_id).all()

def get_bao_hanh_by_serial(serial_number: str):
    bien_the = get_bien_the_by_serial(serial_number)
    if not bien_the:
        return None
    return BaoHanh.query.filter_by(BienTheID=bien_the.BienTheID).first()

def create_bao_hanh(data: dict):
    obj = BaoHanh(**data)
    db.session.add(obj)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# ThanhToan
# ══════════════════════════════════════════════
def get_thanh_toan_by_don_hang(don_hang_id):
    return ThanhToan.query.filter_by(DonHangID=don_hang_id).all()

def create_thanh_toan(data: dict):
    obj = ThanhToan(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_trang_thai_thanh_toan(thanh_toan_id, trang_thai: str):
    obj = db.session.get(ThanhToan, thanh_toan_id)
    if not obj:
        return None
    obj.TrangThai = trang_thai
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# DanhGia
# ══════════════════════════════════════════════
def get_danh_gia_by_san_pham(san_pham_id):
    return DanhGia.query.filter_by(SanPhamID=san_pham_id, DaXacNhan=1).all()

def get_danh_gia_by_khach_hang(khach_hang_id):
    return DanhGia.query.filter_by(KhachHangID=khach_hang_id).all()

def get_danh_gia_by_khach_va_san_pham(khach_hang_id, san_pham_id):
    return DanhGia.query.filter_by(KhachHangID=khach_hang_id, SanPhamID=san_pham_id).first()

def create_danh_gia(data: dict):
    obj = DanhGia(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def xac_nhan_danh_gia(danh_gia_id):
    obj = db.session.get(DanhGia, danh_gia_id)
    if not obj:
        return None
    obj.DaXacNhan = 1
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# MaGiamGia
# ══════════════════════════════════════════════
def get_ma_giam_gia_by_code(ma_code: str):
    return MaGiamGia.query.filter_by(MaCode=ma_code.strip().upper(), TrangThai=1).first()

def get_ma_giam_gia_by_id(ma_giam_gia_id):
    return db.session.get(MaGiamGia, ma_giam_gia_id)

def tang_luot_su_dung(ma_giam_gia_id):
    obj = db.session.get(MaGiamGia, ma_giam_gia_id)
    if not obj:
        return None
    obj.SoLuotDaDung += 1
    db.session.commit()
    return obj

def create_ma_giam_gia(data: dict):
    obj = MaGiamGia(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_ma_giam_gia(ma_giam_gia_id, data: dict):
    obj = db.session.get(MaGiamGia, ma_giam_gia_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


# ══════════════════════════════════════════════
# GioHang
# ══════════════════════════════════════════════
def get_gio_hang_by_khach_hang(khach_hang_id):
    return GioHang.query.filter_by(KhachHangID=khach_hang_id).all()

def get_gio_hang_item(khach_hang_id, bien_the_id):
    return GioHang.query.filter_by(KhachHangID=khach_hang_id, BienTheID=bien_the_id).first()

def add_to_gio_hang(khach_hang_id, bien_the_id, so_luong: int):
    item = get_gio_hang_item(khach_hang_id, bien_the_id)
    if item:
        item.SoLuong += so_luong
    else:
        item = GioHang(KhachHangID=khach_hang_id, BienTheID=bien_the_id, SoLuong=so_luong)
        db.session.add(item)
    db.session.commit()
    return item

def update_so_luong_gio_hang(khach_hang_id, bien_the_id, so_luong: int):
    item = get_gio_hang_item(khach_hang_id, bien_the_id)
    if not item:
        return None
    if so_luong <= 0:
        db.session.delete(item)
    else:
        item.SoLuong = so_luong
    db.session.commit()
    return item

def remove_from_gio_hang(khach_hang_id, bien_the_id):
    item = get_gio_hang_item(khach_hang_id, bien_the_id)
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True

def clear_gio_hang(khach_hang_id):
    GioHang.query.filter_by(KhachHangID=khach_hang_id).delete()
    db.session.commit()


# ══════════════════════════════════════════════
# NhanVien
# ══════════════════════════════════════════════
def get_nhan_vien_by_id(nhan_vien_id):
    return db.session.get(NhanVien, nhan_vien_id)

def get_nhan_vien_by_email(email: str):
    return NhanVien.query.filter_by(Email=email.strip().lower(), TrangThai=1).first()

def get_all_nhan_vien():
    return NhanVien.query.filter_by(TrangThai=1).all()

def create_nhan_vien(data: dict):
    obj = NhanVien(**data)
    db.session.add(obj)
    db.session.commit()
    return obj

def update_nhan_vien(nhan_vien_id, data: dict):
    obj = db.session.get(NhanVien, nhan_vien_id)
    if not obj:
        return None
    for k, v in data.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj

def deactivate_nhan_vien(nhan_vien_id):
    obj = db.session.get(NhanVien, nhan_vien_id)
    if not obj:
        return False
    obj.TrangThai = 0
    db.session.commit()
    return True