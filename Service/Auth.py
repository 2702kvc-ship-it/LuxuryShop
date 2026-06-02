"""
service.py
Tầng logic nghiệp vụ — gọi datalayer, KHÔNG truy vấn DB trực tiếp.
Trả về (data, None) khi thành công, (None, "thông báo lỗi") khi thất bại.
"""

from datetime import date, timedelta
from decimal import Decimal
import uuid

from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user

from Model.Datalayer import (
    # KhachHang
    get_khach_hang_by_email, get_khach_hang_by_id, create_khach_hang,
    update_khach_hang,
    # NhanVien
    get_nhan_vien_by_email, get_nhan_vien_by_id,
    # GioHang
    get_gio_hang_by_khach_hang, add_to_gio_hang, update_so_luong_gio_hang,
    remove_from_gio_hang, clear_gio_hang, get_gio_hang_item,
    # BienTheSanPham
    get_bien_the_by_id, update_ton_kho,
    # DonHang
    create_don_hang, get_don_hang_by_id, get_don_hang_by_khach_hang,
    get_don_hang_by_ma, update_trang_thai_don_hang, get_all_don_hang,
    # ChiTietDonHang
    bulk_create_chi_tiet, get_chi_tiet_by_don_hang,
    # ThanhToan
    create_thanh_toan, get_thanh_toan_by_don_hang, update_trang_thai_thanh_toan,
    # MaGiamGia
    get_ma_giam_gia_by_code, tang_luot_su_dung,
    # BaoHanh
    create_bao_hanh, get_bao_hanh_by_don_hang,
    # DanhGia
    get_danh_gia_by_khach_va_san_pham, create_danh_gia,
    # VIP
    get_vip_by_khach_hang, create_or_update_vip,
    # SanPham
    get_san_pham_by_id,
)

bcrypt = Bcrypt()


# ══════════════════════════════════════════════
# AUTH — KhachHang
# ══════════════════════════════════════════════

def dang_ky_khach_hang(ho_ten, email, mat_khau, so_dien_thoai=None, ngay_sinh=None):
    """Tạo tài khoản khách hàng mới."""
    if get_khach_hang_by_email(email):
        return None, "Email đã được đăng ký."

    ma_hoa = bcrypt.generate_password_hash(mat_khau).decode('utf-8')
    kh = create_khach_hang({
        'HoTen': ho_ten,
        'Email': email.strip().lower(),
        'MatKhau': ma_hoa,
        'SoDienThoai': so_dien_thoai,
        'NgaySinh': ngay_sinh,
        'HangThanhVien': None,   # chưa xác nhận
    })
    return kh, None


def dang_nhap_khach_hang(email, mat_khau, remember=False):
    """Xác thực và đăng nhập khách hàng."""
    kh = get_khach_hang_by_email(email)
    if not kh:
        return None, "Email không tồn tại."
    if kh.HangThanhVien is None:
        return None, "Tài khoản chưa được xác nhận."
    if not bcrypt.check_password_hash(kh.MatKhau, mat_khau):
        return None, "Mật khẩu không đúng."
    login_user(kh, remember=remember)
    return kh, None


def dang_xuat():
    logout_user()


def doi_mat_khau_khach_hang(khach_hang_id, mat_khau_cu, mat_khau_moi):
    kh = get_khach_hang_by_id(khach_hang_id)
    if not kh:
        return None, "Không tìm thấy tài khoản."
    if not bcrypt.check_password_hash(kh.MatKhau, mat_khau_cu):
        return None, "Mật khẩu cũ không đúng."
    ma_hoa = bcrypt.generate_password_hash(mat_khau_moi).decode('utf-8')
    update_khach_hang(khach_hang_id, {'MatKhau': ma_hoa})
    return kh, None


# ══════════════════════════════════════════════
# AUTH — NhanVien (Admin)
# ══════════════════════════════════════════════

def dang_nhap_nhan_vien(email, mat_khau, remember=False):
    """Xác thực và đăng nhập nhân viên/admin."""
    nv = get_nhan_vien_by_email(email)
    if not nv:
        return None, "Email không tồn tại hoặc tài khoản đã bị vô hiệu hóa."
    if not bcrypt.check_password_hash(nv.MatKhau, mat_khau):
        return None, "Mật khẩu không đúng."
    login_user(nv, remember=remember)
    return nv, None
