"""
schema.py
Chuyển đổi ORM objects → dict (JSON-serializable).
Không chứa logic nghiệp vụ, chỉ định dạng dữ liệu trả về.
"""

from decimal import Decimal


def _decimal(val):
    return float(val) if isinstance(val, Decimal) else val


def _date(val):
    return val.isoformat() if val else None


def _datetime(val):
    return val.isoformat() if val else None


# ══════════════════════════════════════════════
# ThuongHieu
# ══════════════════════════════════════════════
def thuong_hieu_schema(obj):
    return {
        'thuong_hieu_id': obj.ThuongHieuID,
        'ten_thuong_hieu': obj.TenThuongHieu,
        'quoc_gia_xuat_xu': obj.QuocGiaXuatXu,
        'nam_thanh_lap': obj.NamThanhLap,
        'mo_ta': obj.MoTa,
        'logo': obj.Logo,
        'trang_thai': obj.TrangThai,
    }


def thuong_hieu_list_schema(objs):
    return [thuong_hieu_schema(o) for o in objs]


# ══════════════════════════════════════════════
# DanhMuc
# ══════════════════════════════════════════════
def danh_muc_schema(obj):
    return {
        'danh_muc_id': obj.DanhMucID,
        'ten_danh_muc': obj.TenDanhMuc,
        'danh_muc_cha_id': obj.DanhMucChaID,
        'mo_ta': obj.MoTa,
        'trang_thai': obj.TrangThai,
    }


def danh_muc_list_schema(objs):
    return [danh_muc_schema(o) for o in objs]


# ══════════════════════════════════════════════
# HinhAnhSanPham
# ══════════════════════════════════════════════
def hinh_anh_schema(obj):
    return {
        'hinh_anh_id': obj.HinhAnhID,
        'duong_dan': obj.DuongDan,
        'la_anh_chinh': bool(obj.LaAnhChinh),
        'thu_tu': obj.ThuTu,
    }


# ══════════════════════════════════════════════
# GiayChungNhan
# ══════════════════════════════════════════════
def giay_chung_nhan_schema(obj):
    return {
        'giay_chung_nhan_id': obj.GiayChungNhanID,
        'ma_chung_nhan': obj.MaChungNhan,
        'to_chuc_cap': obj.ToChucCap,
        'ngay_cap': _date(obj.NgayCap),
        'ngay_het_han': _date(obj.NgayHetHan),
        'qr_code': obj.QRCode,
    }


# ══════════════════════════════════════════════
# BienTheSanPham
# ══════════════════════════════════════════════
def bien_the_schema(obj, include_san_pham=False):
    data = {
        'bien_the_id': obj.BienTheID,
        'san_pham_id': obj.SanPhamID,
        'serial_number': obj.SerialNumber,
        'mau_sac': obj.MauSac,
        'kich_thuoc': obj.KichThuoc,
        'ma_vach': obj.MaVach,
        'so_luong_ton': obj.SoLuongTon,
        'gia_ban_rieng': _decimal(obj.GiaBanRieng),
        'hinh_anh': obj.HinhAnh,
    }
    if include_san_pham and obj.san_pham:
        data['san_pham'] = san_pham_short_schema(obj.san_pham)
    return data


def bien_the_list_schema(objs, include_san_pham=False):
    return [bien_the_schema(o, include_san_pham) for o in objs]


# ══════════════════════════════════════════════
# SanPham
# ══════════════════════════════════════════════
def san_pham_short_schema(obj):
    """Dùng trong nested response (ví dụ: giỏ hàng, chi tiết đơn hàng)."""
    return {
        'san_pham_id': obj.SanPhamID,
        'ten_san_pham': obj.TenSanPham,
        'ma_san_pham': obj.MaSanPham,
        'gia_ban': _decimal(obj.GiaBan),
        'trang_thai': obj.TrangThai,
    }


def san_pham_schema(obj):
    """Full schema — dùng ở trang chi tiết sản phẩm."""
    return {
        'san_pham_id': obj.SanPhamID,
        'ten_san_pham': obj.TenSanPham,
        'ma_san_pham': obj.MaSanPham,
        'thuong_hieu': thuong_hieu_schema(obj.thuong_hieu) if obj.thuong_hieu else None,
        'danh_muc': danh_muc_schema(obj.danh_muc) if obj.danh_muc else None,
        'gia_ban': _decimal(obj.GiaBan),
        'gia_goc': _decimal(obj.GiaGoc),
        'chat_lieu': obj.ChatLieu,
        'xuat_xu': obj.XuatXu,
        'mo_ta': obj.MoTa,
        'trang_thai': obj.TrangThai,
        'hinh_anhs': [hinh_anh_schema(h) for h in obj.hinh_anhs],
        'bien_thes': [bien_the_schema(b) for b in obj.bien_thes],
        'giay_chung_nhans': [giay_chung_nhan_schema(g) for g in obj.giay_chung_nhans],
    }


def san_pham_list_schema(objs):
    """Danh sách sản phẩm — không kèm nested detail để tránh nặng."""
    result = []
    for obj in objs:
        anh_chinh = obj.hinh_anhs.filter_by(LaAnhChinh=1).first()
        result.append({
            'san_pham_id': obj.SanPhamID,
            'ten_san_pham': obj.TenSanPham,
            'ma_san_pham': obj.MaSanPham,
            'thuong_hieu': obj.thuong_hieu.TenThuongHieu if obj.thuong_hieu else None,
            'danh_muc': obj.danh_muc.TenDanhMuc if obj.danh_muc else None,
            'gia_ban': _decimal(obj.GiaBan),
            'trang_thai': obj.TrangThai,
            'anh_chinh': anh_chinh.DuongDan if anh_chinh else None,
        })
    return result


# ══════════════════════════════════════════════
# KhachHang
# ══════════════════════════════════════════════
def khach_hang_schema(obj):
    return {
        'khach_hang_id': obj.KhachHangID,
        'ho_ten': obj.HoTen,
        'email': obj.Email,
        'so_dien_thoai': obj.SoDienThoai,
        'ngay_sinh': _date(obj.NgaySinh),
        'hang_thanh_vien': obj.HangThanhVien,
        'diem_tich_luy': obj.DiemTichLuy,
        'tong_chi_tieu': _decimal(obj.TongChiTieu),
        'ngay_dang_ky': _datetime(obj.NgayDangKy),
    }


# ══════════════════════════════════════════════
# ChuongTrinhVIP
# ══════════════════════════════════════════════
def vip_schema(obj):
    return {
        'vip_program_id': obj.VIPProgramID,
        'khach_hang_id': obj.KhachHangID,
        'hang_vip': obj.HangVIP,
        'diem_hien_tai': obj.DiemHienTai,
        'ngay_len_hang': _date(obj.NgayLenHang),
        'ngay_het_han': _date(obj.NgayHetHan),
        'uu_dai_phan_tram': _decimal(obj.UuDaiPhanTram),
    }


# ══════════════════════════════════════════════
# GioHang
# ══════════════════════════════════════════════
def gio_hang_item_schema(obj):
    bt = obj.bien_the
    gia = bt.GiaBanRieng or bt.san_pham.GiaBan
    return {
        'gio_hang_id': obj.GioHangID,
        'bien_the_id': bt.BienTheID,
        'ten_san_pham': bt.san_pham.TenSanPham,
        'thuong_hieu': bt.san_pham.thuong_hieu.TenThuongHieu if bt.san_pham.thuong_hieu else None,
        'mau_sac': bt.MauSac,
        'kich_thuoc': bt.KichThuoc,
        'serial_number': bt.SerialNumber,
        'hinh_anh': bt.HinhAnh,
        'gia_don_vi': _decimal(gia),
        'so_luong': obj.SoLuong,
        'thanh_tien': _decimal(gia * obj.SoLuong),
        'ngay_them': _datetime(obj.NgayThem),
        'ton_kho': bt.SoLuongTon,
    }


def gio_hang_schema(items):
    from decimal import Decimal as D
    data = [gio_hang_item_schema(i) for i in items]
    tong = sum(i['thanh_tien'] for i in data)
    return {
        'items': data,
        'so_luong_loai': len(data),
        'tong_tien': tong,
    }


# ══════════════════════════════════════════════
# MaGiamGia
# ══════════════════════════════════════════════
def ma_giam_gia_schema(obj):
    return {
        'ma_giam_gia_id': obj.MaGiamGiaID,
        'ma_code': obj.MaCode,
        'thuong_hieu_id': obj.ThuongHieuID,
        'loai_giam': obj.LoaiGiam,
        'gia_tri': _decimal(obj.GiaTri),
        'giam_toi_da': _decimal(obj.GiamToiDa),
        'don_hang_toi_thieu': _decimal(obj.DonHangToiThieu),
        'ngay_bat_dau': _date(obj.NgayBatDau),
        'ngay_ket_thuc': _date(obj.NgayKetThuc),
        'so_luot_toi_da': obj.SoLuotToiDa,
        'so_luot_da_dung': obj.SoLuotDaDung,
        'trang_thai': obj.TrangThai,
    }


# ══════════════════════════════════════════════
# ChiTietDonHang
# ══════════════════════════════════════════════
def chi_tiet_don_hang_schema(obj):
    bt = obj.bien_the
    return {
        'chi_tiet_id': obj.ChiTietID,
        'bien_the_id': obj.BienTheID,
        'ten_san_pham': bt.san_pham.TenSanPham if bt and bt.san_pham else None,
        'serial_number': bt.SerialNumber if bt else None,
        'mau_sac': bt.MauSac if bt else None,
        'kich_thuoc': bt.KichThuoc if bt else None,
        'hinh_anh': bt.HinhAnh if bt else None,
        'so_luong': obj.SoLuong,
        'don_gia': _decimal(obj.DonGia),
        'giam_gia_dong': _decimal(obj.GiamGiaDong),
        'thanh_tien_dong': _decimal(obj.ThanhTienDong),
    }


# ══════════════════════════════════════════════
# ThanhToan
# ══════════════════════════════════════════════
def thanh_toan_schema(obj):
    return {
        'thanh_toan_id': obj.ThanhToanID,
        'don_hang_id': obj.DonHangID,
        'phuong_thuc': obj.PhuongThuc,
        'so_tien': _decimal(obj.SoTien),
        'ma_giao_dich': obj.MaGiaoDich,
        'trang_thai': obj.TrangThai,
        'thoi_gian': _datetime(obj.ThoiGian),
    }


# ══════════════════════════════════════════════
# BaoHanh
# ══════════════════════════════════════════════
def bao_hanh_schema(obj):
    bt = obj.bien_the
    return {
        'bao_hanh_id': obj.BaoHanhID,
        'bien_the_id': obj.BienTheID,
        'serial_number': bt.SerialNumber if bt else None,
        'ten_san_pham': bt.san_pham.TenSanPham if bt and bt.san_pham else None,
        'don_hang_id': obj.DonHangID,
        'ngay_bat_dau': _date(obj.NgayBatDau),
        'ngay_ket_thuc': _date(obj.NgayKetThuc),
        'dieu_kien_bao_hanh': obj.DieuKienBaoHanh,
        'trang_thai_bao_hanh': obj.TrangThaiBaoHanh,
    }


def bao_hanh_list_schema(objs):
    return [bao_hanh_schema(o) for o in objs]


# ══════════════════════════════════════════════
# DonHang
# ══════════════════════════════════════════════
def don_hang_short_schema(obj):
    """Dùng trong danh sách đơn hàng."""
    return {
        'don_hang_id': obj.DonHangID,
        'ma_don_hang': obj.MaDonHang,
        'trang_thai': obj.TrangThai,
        'tong_tien_hang': _decimal(obj.TongTienHang),
        'giam_gia': _decimal(obj.GiamGia),
        'thanh_toan': _decimal(obj.ThanhToan),
        'ngay_dat': _datetime(obj.NgayDat),
        'dia_chi_giao': obj.DiaChiGiao,
    }


def don_hang_schema(obj, chi_tiets=None, thanh_toans=None, bao_hanhs=None):
    """Full schema — dùng ở trang chi tiết đơn hàng."""
    data = don_hang_short_schema(obj)
    data['ghi_chu'] = obj.GhiChu
    data['khach_hang_id'] = obj.KhachHangID
    if chi_tiets is not None:
        data['chi_tiets'] = [chi_tiet_don_hang_schema(c) for c in chi_tiets]
    if thanh_toans is not None:
        data['thanh_toans'] = [thanh_toan_schema(t) for t in thanh_toans]
    if bao_hanhs is not None:
        data['bao_hanhs'] = [bao_hanh_schema(b) for b in bao_hanhs]
    return data


def don_hang_list_schema(objs):
    return [don_hang_short_schema(o) for o in objs]


# ══════════════════════════════════════════════
# DanhGia
# ══════════════════════════════════════════════
def danh_gia_schema(obj):
    return {
        'danh_gia_id': obj.DanhGiaID,
        'san_pham_id': obj.SanPhamID,
        'khach_hang_id': obj.KhachHangID,
        'ho_ten_khach': obj.khach_hang.HoTen if obj.khach_hang else None,
        'diem_so': obj.DiemSo,
        'nhan_xet': obj.NhanXet,
        'da_xac_nhan': bool(obj.DaXacNhan),
        'ngay_danh_gia': _datetime(obj.NgayDanhGia),
    }


def danh_gia_list_schema(objs):
    return [danh_gia_schema(o) for o in objs]


# ══════════════════════════════════════════════
# NhanVien
# ══════════════════════════════════════════════
def nhan_vien_schema(obj):
    return {
        'nhan_vien_id': obj.NhanVienID,
        'ho_ten': obj.HoTen,
        'email': obj.Email,
        'so_dien_thoai': obj.SoDienThoai,
        'vai_tro': obj.VaiTro,
        'trang_thai': obj.TrangThai,
        'ngay_tao': _datetime(obj.NgayTao),
        'ngay_cap_nhat': _datetime(obj.NgayCapNhat),
    }


def nhan_vien_list_schema(objs):
    return [nhan_vien_schema(o) for o in objs]


# ══════════════════════════════════════════════
# Response helpers
# ══════════════════════════════════════════════
def success(data=None, message="Thành công"):
    return {'success': True, 'message': message, 'data': data}


def error(message="Có lỗi xảy ra", code=400):
    return {'success': False, 'message': message, 'data': None}, code