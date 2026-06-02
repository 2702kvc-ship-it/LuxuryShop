"""
routes.py
Flask Blueprint API — nhận request, gọi service, trả JSON.
Không chứa logic nghiệp vụ, không truy vấn DB trực tiếp.

Blueprints:
  /auth        — đăng ký, đăng nhập, đăng xuất
  /khachhang   — thông tin cá nhân, VIP
  /sanpham     — danh sách, chi tiết sản phẩm
  /giohang     — giỏ hàng
  /donhang     — đặt hàng, lịch sử đơn hàng
  /baohang     — xem bảo hành
  /danhgia     — đánh giá sản phẩm
  /admin       — quản lý đơn hàng, nhân viên (yêu cầu quyền admin)
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

import Service.Auth as service
import Service.Logic as logic
import Model.Schema as schema
import Model.Datalayer as datalayer

# ──────────────────────────────────────────────
# Blueprints
# ──────────────────────────────────────────────
auth_bp       = Blueprint('auth',       __name__)
khachhang_bp  = Blueprint('khachhang',  __name__)
sanpham_bp    = Blueprint('sanpham',    __name__)
giohang_bp    = Blueprint('giohang',   __name__)
donhang_bp    = Blueprint('donhang',   __name__)
baohang_bp    = Blueprint('baohang',   __name__)
danhgia_bp    = Blueprint('danhgia',   __name__)
admin_bp      = Blueprint('admin',      __name__)


# ──────────────────────────────────────────────
# Decorators
# ──────────────────────────────────────────────
def khach_hang_required(f):
    """Chỉ cho phép KhachHang đã đăng nhập (không phải NhanVien)."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        from models import KhachHang
        if not isinstance(current_user._get_current_object(), KhachHang):
            return jsonify(schema.error("Chỉ dành cho khách hàng.", 403)[0]), 403
        return f(*args, **kwargs)
    return decorated


def nhan_vien_required(f):
    """Chỉ cho phép NhanVien đã đăng nhập."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        from models import NhanVien
        if not isinstance(current_user._get_current_object(), NhanVien):
            return jsonify(schema.error("Chỉ dành cho nhân viên.", 403)[0]), 403
        return f(*args, **kwargs)
    return decorated


def admin_required(vai_tros=('Admin', 'SuperAdmin')):
    """Chỉ cho phép NhanVien có vai trò trong danh sách."""
    def decorator(f):
        @wraps(f)
        @nhan_vien_required
        def decorated(*args, **kwargs):
            if current_user.VaiTro not in vai_tros:
                return jsonify(schema.error("Không đủ quyền hạn.", 403)[0]), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def _json():
    """Lấy JSON body, trả {} nếu không có."""
    return request.get_json(silent=True) or {}


# ══════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════

@auth_bp.post('/dang-ky')
def dang_ky():
    d = _json()
    kh, err = service.dang_ky_khach_hang(
        ho_ten=d.get('ho_ten', '').strip(),
        email=d.get('email', '').strip(),
        mat_khau=d.get('mat_khau', ''),
        so_dien_thoai=d.get('so_dien_thoai'),
        ngay_sinh=d.get('ngay_sinh'),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.khach_hang_schema(kh), "Đăng ký thành công.")), 201


@auth_bp.post('/dang-nhap')
def dang_nhap():
    d = _json()
    kh, err = service.dang_nhap_khach_hang(
        email=d.get('email', '').strip(),
        mat_khau=d.get('mat_khau', ''),
        remember=d.get('remember', False),
    )
    if err:
        return jsonify(schema.error(err)[0]), 401
    return jsonify(schema.success(schema.khach_hang_schema(kh), "Đăng nhập thành công."))


@auth_bp.post('/admin/dang-nhap')
def admin_dang_nhap():
    d = _json()
    nv, err = service.dang_nhap_nhan_vien(
        email=d.get('email', '').strip(),
        mat_khau=d.get('mat_khau', ''),
        remember=d.get('remember', False),
    )
    if err:
        return jsonify(schema.error(err)[0]), 401
    return jsonify(schema.success(schema.nhan_vien_schema(nv), "Đăng nhập thành công."))


@auth_bp.post('/dang-xuat')
@login_required
def dang_xuat():
    service.dang_xuat()
    return jsonify(schema.success(message="Đăng xuất thành công."))


@auth_bp.post('/doi-mat-khau')
@khach_hang_required
def doi_mat_khau():
    d = _json()
    kh, err = service.doi_mat_khau_khach_hang(
        khach_hang_id=current_user.KhachHangID,
        mat_khau_cu=d.get('mat_khau_cu', ''),
        mat_khau_moi=d.get('mat_khau_moi', ''),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(message="Đổi mật khẩu thành công."))


# ══════════════════════════════════════════════
# KHÁCH HÀNG
# ══════════════════════════════════════════════

@khachhang_bp.get('/ho-so')
@khach_hang_required
def xem_ho_so():
    kh = datalayer.get_khach_hang_by_id(current_user.KhachHangID)
    return jsonify(schema.success(schema.khach_hang_schema(kh)))


@khachhang_bp.put('/ho-so')
@khach_hang_required
def cap_nhat_ho_so():
    d = _json()
    kh, err = service.cap_nhat_thong_tin_ca_nhan(current_user.KhachHangID, d)
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.khach_hang_schema(kh), "Cập nhật thành công."))


@khachhang_bp.get('/vip')
@khach_hang_required
def xem_vip():
    vip, err = service.xem_thong_tin_vip(current_user.KhachHangID)
    if err:
        return jsonify(schema.error(err, 404)[0]), 404
    return jsonify(schema.success(schema.vip_schema(vip)))


# ══════════════════════════════════════════════
# SẢN PHẨM
# ══════════════════════════════════════════════

@sanpham_bp.get('/')
def danh_sach_san_pham():
    thuong_hieu_id = request.args.get('thuong_hieu_id', type=int)
    danh_muc_id    = request.args.get('danh_muc_id',    type=int)
    keyword        = request.args.get('q', '').strip()

    if keyword:
        san_phams = datalayer.search_san_pham(keyword)
    elif thuong_hieu_id:
        san_phams = datalayer.get_san_pham_by_thuong_hieu(thuong_hieu_id)
    elif danh_muc_id:
        san_phams = datalayer.get_san_pham_by_danh_muc(danh_muc_id)
    else:
        san_phams = datalayer.get_all_san_pham()

    return jsonify(schema.success(schema.san_pham_list_schema(san_phams)))


@sanpham_bp.get('/<int:san_pham_id>')
def chi_tiet_san_pham(san_pham_id):
    sp = datalayer.get_san_pham_by_id(san_pham_id)
    if not sp:
        return jsonify(schema.error("Sản phẩm không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.san_pham_schema(sp)))


@sanpham_bp.get('/<int:san_pham_id>/danh-gia')
def danh_gia_san_pham(san_pham_id):
    dgs = datalayer.get_danh_gia_by_san_pham(san_pham_id)
    return jsonify(schema.success(schema.danh_gia_list_schema(dgs)))


@sanpham_bp.get('/<int:san_pham_id>/giay-chung-nhan')
def giay_chung_nhan_san_pham(san_pham_id):
    gcns = datalayer.get_giay_chung_nhan_by_san_pham(san_pham_id)
    return jsonify(schema.success([schema.giay_chung_nhan_schema(g) for g in gcns]))


@sanpham_bp.get('/thuong-hieu/')
def danh_sach_thuong_hieu():
    ths = datalayer.get_all_thuong_hieu()
    return jsonify(schema.success(schema.thuong_hieu_list_schema(ths)))


@sanpham_bp.get('/danh-muc/')
def danh_sach_danh_muc():
    dms = datalayer.get_all_danh_muc()
    return jsonify(schema.success(schema.danh_muc_list_schema(dms)))


# ══════════════════════════════════════════════
# GIỎ HÀNG
# ══════════════════════════════════════════════

@giohang_bp.get('/')
@khach_hang_required
def xem_gio_hang():
    items = datalayer.get_gio_hang_by_khach_hang(current_user.KhachHangID)
    return jsonify(schema.success(schema.gio_hang_schema(items)))


@giohang_bp.post('/them')
@khach_hang_required
def them_san_pham():
    d = _json()
    item, err = service.them_vao_gio_hang(
        khach_hang_id=current_user.KhachHangID,
        bien_the_id=d.get('bien_the_id'),
        so_luong=d.get('so_luong', 1),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(message="Đã thêm vào giỏ hàng.")), 201


@giohang_bp.put('/cap-nhat')
@khach_hang_required
def cap_nhat_gio_hang():
    d = _json()
    item, err = service.cap_nhat_gio_hang(
        khach_hang_id=current_user.KhachHangID,
        bien_the_id=d.get('bien_the_id'),
        so_luong_moi=d.get('so_luong', 0),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(message="Đã cập nhật giỏ hàng."))


@giohang_bp.delete('/xoa/<int:bien_the_id>')
@khach_hang_required
def xoa_san_pham(bien_the_id):
    ok, err = service.xoa_khoi_gio_hang(current_user.KhachHangID, bien_the_id)
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(message="Đã xóa khỏi giỏ hàng."))


# ══════════════════════════════════════════════
# ĐƠN HÀNG
# ══════════════════════════════════════════════

@donhang_bp.post('/dat-hang')
@khach_hang_required
def dat_hang():
    d = _json()
    dh, err = service.dat_hang(
        khach_hang_id=current_user.KhachHangID,
        dia_chi_giao=d.get('dia_chi_giao', '').strip(),
        phuong_thuc_thanh_toan=d.get('phuong_thuc_thanh_toan', 'TienMat'),
        ma_giam_gia_code=d.get('ma_giam_gia'),
        ghi_chu=d.get('ghi_chu'),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.don_hang_short_schema(dh), "Đặt hàng thành công.")), 201


@donhang_bp.get('/')
@khach_hang_required
def lich_su_don_hang():
    don_hangs, _ = service.xem_don_hang_khach(current_user.KhachHangID)
    return jsonify(schema.success(schema.don_hang_list_schema(don_hangs)))


@donhang_bp.get('/<int:don_hang_id>')
@khach_hang_required
def chi_tiet_don_hang(don_hang_id):
    result, err = service.xem_chi_tiet_don_hang(don_hang_id, current_user.KhachHangID)
    if err:
        return jsonify(schema.error(err, 404)[0]), 404
    return jsonify(schema.success(schema.don_hang_schema(
        result['don_hang'],
        chi_tiets=result['chi_tiets'],
        thanh_toans=result['thanh_toans'],
        bao_hanhs=result['bao_hanhs'],
    )))


@donhang_bp.post('/<int:don_hang_id>/huy')
@khach_hang_required
def huy_don_hang(don_hang_id):
    dh, err = service.huy_don_hang(don_hang_id, current_user.KhachHangID)
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.don_hang_short_schema(dh), "Đã hủy đơn hàng."))


@donhang_bp.post('/kiem-tra-ma-giam-gia')
@khach_hang_required
def kiem_tra_ma_giam_gia():
    d = _json()
    ma_code = d.get('ma_code', '').strip()
    tong_tien = d.get('tong_tien', 0)

    from decimal import Decimal
    giam, mgg, err = service.ap_ma_giam_gia(ma_code, Decimal(str(tong_tien)))
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success({
        'ma_code': ma_code,
        'so_tien_giam': float(giam),
        'thanh_toan': float(Decimal(str(tong_tien)) - giam),
        'chi_tiet_ma': schema.ma_giam_gia_schema(mgg),
    }))


# ══════════════════════════════════════════════
# BẢO HÀNH
# ══════════════════════════════════════════════

@baohang_bp.get('/')
@khach_hang_required
def xem_bao_hanh():
    bhs, _ = service.kiem_tra_bao_hanh_cua_khach(current_user.KhachHangID)
    return jsonify(schema.success(schema.bao_hanh_list_schema(bhs)))


@baohang_bp.get('/don-hang/<int:don_hang_id>')
@khach_hang_required
def bao_hanh_theo_don(don_hang_id):
    bhs, err = service.kiem_tra_bao_hanh(don_hang_id, current_user.KhachHangID)
    if err:
        return jsonify(schema.error(err, 404)[0]), 404
    return jsonify(schema.success(schema.bao_hanh_list_schema(bhs)))


# ══════════════════════════════════════════════
# ĐÁNH GIÁ
# ══════════════════════════════════════════════

@danhgia_bp.post('/gui')
@khach_hang_required
def gui_danh_gia():
    d = _json()
    dg, err = service.gui_danh_gia(
        khach_hang_id=current_user.KhachHangID,
        san_pham_id=d.get('san_pham_id'),
        diem_so=d.get('diem_so'),
        nhan_xet=d.get('nhan_xet'),
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.danh_gia_schema(dg), "Gửi đánh giá thành công.")), 201


# ══════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════

# --- Đơn hàng ---
@admin_bp.get('/don-hang')
@nhan_vien_required
def admin_xem_don_hang():
    trang_thai = request.args.get('trang_thai')
    don_hangs, _ = service.admin_xem_tat_ca_don_hang(trang_thai)
    return jsonify(schema.success(schema.don_hang_list_schema(don_hangs)))


@admin_bp.get('/don-hang/<int:don_hang_id>')
@nhan_vien_required
def admin_chi_tiet_don_hang(don_hang_id):
    result, err = service.xem_chi_tiet_don_hang(don_hang_id)
    if err:
        return jsonify(schema.error(err, 404)[0]), 404
    return jsonify(schema.success(schema.don_hang_schema(
        result['don_hang'],
        chi_tiets=result['chi_tiets'],
        thanh_toans=result['thanh_toans'],
        bao_hanhs=result['bao_hanhs'],
    )))


@admin_bp.put('/don-hang/<int:don_hang_id>/trang-thai')
@nhan_vien_required
def admin_cap_nhat_trang_thai(don_hang_id):
    d = _json()
    dh, err = service.admin_cap_nhat_trang_thai_don_hang(
        don_hang_id, d.get('trang_thai', '')
    )
    if err:
        return jsonify(schema.error(err)[0]), 400
    return jsonify(schema.success(schema.don_hang_short_schema(dh), "Cập nhật trạng thái thành công."))


# --- Sản phẩm (Admin) ---
@admin_bp.post('/san-pham')
@admin_required()
def admin_them_san_pham():
    d = _json()
    sp = datalayer.create_san_pham(d)
    return jsonify(schema.success(schema.san_pham_schema(sp), "Thêm sản phẩm thành công.")), 201


@admin_bp.put('/san-pham/<int:san_pham_id>')
@admin_required()
def admin_sua_san_pham(san_pham_id):
    d = _json()
    sp = datalayer.update_san_pham(san_pham_id, d)
    if not sp:
        return jsonify(schema.error("Sản phẩm không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.san_pham_schema(sp), "Cập nhật sản phẩm thành công."))


# --- Biến thể ---
@admin_bp.post('/bien-the')
@admin_required()
def admin_them_bien_the():
    d = _json()
    bt = datalayer.create_bien_the(d)
    return jsonify(schema.success(schema.bien_the_schema(bt), "Thêm biến thể thành công.")), 201


@admin_bp.put('/bien-the/<int:bien_the_id>')
@admin_required()
def admin_sua_bien_the(bien_the_id):
    d = _json()
    bt = datalayer.update_bien_the(bien_the_id, d)
    if not bt:
        return jsonify(schema.error("Biến thể không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.bien_the_schema(bt), "Cập nhật biến thể thành công."))


# --- Thương hiệu ---
@admin_bp.post('/thuong-hieu')
@admin_required()
def admin_them_thuong_hieu():
    d = _json()
    th = datalayer.create_thuong_hieu(d)
    return jsonify(schema.success(schema.thuong_hieu_schema(th), "Thêm thương hiệu thành công.")), 201


@admin_bp.put('/thuong-hieu/<int:thuong_hieu_id>')
@admin_required()
def admin_sua_thuong_hieu(thuong_hieu_id):
    d = _json()
    th = datalayer.update_thuong_hieu(thuong_hieu_id, d)
    if not th:
        return jsonify(schema.error("Thương hiệu không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.thuong_hieu_schema(th), "Cập nhật thành công."))


@admin_bp.delete('/thuong-hieu/<int:thuong_hieu_id>')
@admin_required()
def admin_xoa_thuong_hieu(thuong_hieu_id):
    ok = datalayer.delete_thuong_hieu(thuong_hieu_id)
    if not ok:
        return jsonify(schema.error("Thương hiệu không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(message="Đã ẩn thương hiệu."))


# --- Mã giảm giá ---
@admin_bp.post('/ma-giam-gia')
@admin_required()
def admin_them_ma_giam_gia():
    d = _json()
    mgg = datalayer.create_ma_giam_gia(d)
    return jsonify(schema.success(schema.ma_giam_gia_schema(mgg), "Tạo mã giảm giá thành công.")), 201


@admin_bp.put('/ma-giam-gia/<int:ma_giam_gia_id>')
@admin_required()
def admin_sua_ma_giam_gia(ma_giam_gia_id):
    d = _json()
    mgg = datalayer.update_ma_giam_gia(ma_giam_gia_id, d)
    if not mgg:
        return jsonify(schema.error("Mã giảm giá không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.ma_giam_gia_schema(mgg), "Cập nhật thành công."))


# --- Nhân viên ---
@admin_bp.get('/nhan-vien')
@admin_required(vai_tros=('SuperAdmin',))
def admin_xem_nhan_vien():
    nvs = datalayer.get_all_nhan_vien()
    return jsonify(schema.success(schema.nhan_vien_list_schema(nvs)))


@admin_bp.post('/nhan-vien')
@admin_required(vai_tros=('SuperAdmin',))
def admin_them_nhan_vien():
    d = _json()
    from flask_bcrypt import Bcrypt
    _bcrypt = Bcrypt()
    d['MatKhau'] = _bcrypt.generate_password_hash(d.get('MatKhau', '')).decode('utf-8')
    nv = datalayer.create_nhan_vien(d)
    return jsonify(schema.success(schema.nhan_vien_schema(nv), "Thêm nhân viên thành công.")), 201


@admin_bp.put('/nhan-vien/<int:nhan_vien_id>')
@admin_required(vai_tros=('SuperAdmin',))
def admin_sua_nhan_vien(nhan_vien_id):
    d = _json()
    d.pop('MatKhau', None)   # không cho đổi mật khẩu qua route này
    nv = datalayer.update_nhan_vien(nhan_vien_id, d)
    if not nv:
        return jsonify(schema.error("Nhân viên không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.nhan_vien_schema(nv), "Cập nhật thành công."))


@admin_bp.delete('/nhan-vien/<int:nhan_vien_id>')
@admin_required(vai_tros=('SuperAdmin',))
def admin_xoa_nhan_vien(nhan_vien_id):
    ok = datalayer.deactivate_nhan_vien(nhan_vien_id)
    if not ok:
        return jsonify(schema.error("Nhân viên không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(message="Đã vô hiệu hóa tài khoản nhân viên."))


# --- Khách hàng (Admin xem) ---
@admin_bp.get('/khach-hang')
@nhan_vien_required
def admin_xem_khach_hang():
    khs = datalayer.get_all_khach_hang()
    return jsonify(schema.success([schema.khach_hang_schema(k) for k in khs]))


# --- Đánh giá (Admin duyệt) ---
@admin_bp.put('/danh-gia/<int:danh_gia_id>/xac-nhan')
@nhan_vien_required
def admin_xac_nhan_danh_gia(danh_gia_id):
    dg = datalayer.xac_nhan_danh_gia(danh_gia_id)
    if not dg:
        return jsonify(schema.error("Đánh giá không tồn tại.", 404)[0]), 404
    return jsonify(schema.success(schema.danh_gia_schema(dg), "Đã xác nhận đánh giá."))