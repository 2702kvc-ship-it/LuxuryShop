"""
khach_hang/routes.py  — SSR thuần
Blueprint 'khach' — toàn bộ thao tác phía khách hàng:
  /san-pham           — xem sản phẩm, tìm kiếm, đánh giá
  /gio-hang           — giỏ hàng
  /don-hang           — đặt hàng, lịch sử, hủy
  /bao-hanh           — xem bảo hành
  /tai-khoan          — hồ sơ, VIP, cập nhật thông tin

Logic gọi qua Service/Logic.py — route không chứa nghiệp vụ.
Template nằm trong templates/products/ (storefront) và templates/ (auth dùng chung).
"""

from functools import wraps

from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, abort,
)
from flask_login import current_user, login_required

import Service.Logic as logic
import Model.Datalayer as datalayer
from Model.Models import KhachHang

khach_bp = Blueprint("khach", __name__)


# ══════════════════════════════════════════════
# DECORATOR — chỉ KhachHang mới vào được
# ══════════════════════════════════════════════

def khach_hang_required(f):
    @wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not isinstance(current_user._get_current_object(), KhachHang):
            flash("Chức năng này chỉ dành cho khách hàng.", "danger")
            return redirect(url_for("khach.trang_chu"))
        return f(*args, **kwargs)
    return wrapped


# ══════════════════════════════════════════════
# TRANG CHỦ / SẢN PHẨM
# ══════════════════════════════════════════════

@khach_bp.route("/")
@khach_bp.route("/san-pham")
def trang_chu():
    """Trang danh sách sản phẩm với filter thương hiệu / danh mục / tìm kiếm."""
    keyword        = request.args.get("q", "").strip()
    thuong_hieu_id = request.args.get("thuong_hieu_id", type=int)
    danh_muc_id    = request.args.get("danh_muc_id",    type=int)

    if keyword:
        san_phams = datalayer.search_san_pham(keyword)
    elif thuong_hieu_id:
        san_phams = datalayer.get_san_pham_by_thuong_hieu(thuong_hieu_id)
    elif danh_muc_id:
        san_phams = datalayer.get_san_pham_by_danh_muc(danh_muc_id)
    else:
        san_phams = datalayer.get_all_san_pham()

    return render_template(
        "products/index_kh.html",
        san_phams      = san_phams,
        thuong_hieus   = datalayer.get_all_thuong_hieu(),
        danh_mucs      = datalayer.get_all_danh_muc(),
        keyword        = keyword,
        thuong_hieu_id = thuong_hieu_id,
        danh_muc_id    = danh_muc_id,
    )


@khach_bp.route("/san-pham/<int:san_pham_id>")
def chi_tiet_san_pham(san_pham_id):
    """Trang chi tiết sản phẩm — hiện biến thể, giấy chứng nhận, đánh giá."""
    sp = datalayer.get_san_pham_by_id(san_pham_id)
    if not sp:
        abort(404)

    bien_thes  = datalayer.get_bien_the_by_san_pham(san_pham_id)
    chung_nhans= datalayer.get_giay_chung_nhan_by_san_pham(san_pham_id)
    danh_gias  = datalayer.get_danh_gia_by_san_pham(san_pham_id)
    selected_bien_the_id = request.cookies.get(
        f"luxury_product_{san_pham_id}_variant", type=int
    )
    selected_so_luong = request.cookies.get(
        f"luxury_product_{san_pham_id}_qty", 1, type=int
    )
    valid_bien_the_ids = {bt.BienTheID for bt in bien_thes if bt.SoLuongTon > 0}
    if selected_bien_the_id not in valid_bien_the_ids:
        selected_bien_the_id = None
    if not selected_so_luong or selected_so_luong < 1:
        selected_so_luong = 1

    # Kiểm tra khách đã mua sp này chưa (để hiện form đánh giá)
    da_mua      = False
    da_danh_gia = False
    if current_user.is_authenticated and isinstance(current_user._get_current_object(), KhachHang):
        don_hangs = datalayer.get_don_hang_by_khach_hang(current_user.KhachHangID)
        for dh in don_hangs:
            if dh.TrangThai == "DaGiao":
                for ct in datalayer.get_chi_tiet_by_don_hang(dh.DonHangID):
                    if ct.bien_the.SanPhamID == san_pham_id:
                        da_mua = True
                        break
            if da_mua:
                break
        da_danh_gia = bool(
            datalayer.get_danh_gia_by_khach_va_san_pham(current_user.KhachHangID, san_pham_id)
        )

    return render_template(
        "products/detail.html",
        sp          = sp,
        bien_thes   = bien_thes,
        chung_nhans = chung_nhans,
        danh_gias   = danh_gias,
        da_mua      = da_mua,
        da_danh_gia = da_danh_gia,
        selected_bien_the_id = selected_bien_the_id,
        selected_so_luong = selected_so_luong,
    )


# ══════════════════════════════════════════════
# ĐÁNH GIÁ SẢN PHẨM
# ══════════════════════════════════════════════

@khach_bp.route("/san-pham/<int:san_pham_id>/danh-gia", methods=["POST"])
@khach_hang_required
def gui_danh_gia(san_pham_id):
    diem_so  = request.form.get("diem_so", type=int)
    nhan_xet = request.form.get("nhan_xet", "").strip() or None

    if diem_so is None:
        flash("Vui lòng chọn điểm đánh giá.", "danger")
        return redirect(url_for("khach.chi_tiet_san_pham", san_pham_id=san_pham_id))

    dg, loi = logic.gui_danh_gia(
        khach_hang_id = current_user.KhachHangID,
        san_pham_id   = san_pham_id,
        diem_so       = diem_so,
        nhan_xet      = nhan_xet,
    )
    if loi:
        flash(loi, "danger")
    else:
        flash("Gửi đánh giá thành công! Cảm ơn bạn.", "success")

    return redirect(url_for("khach.chi_tiet_san_pham", san_pham_id=san_pham_id))


# ══════════════════════════════════════════════
# GIỎ HÀNG
# ══════════════════════════════════════════════

@khach_bp.route("/gio-hang")
@khach_hang_required
def xem_gio_hang():
    gio_hang_data, _ = logic.xem_gio_hang(current_user.KhachHangID)
    return render_template(
        "products/cart.html",
        items     = gio_hang_data["items"],
        tong_tien = gio_hang_data["tong_tien"],
    )


@khach_bp.route("/gio-hang/them", methods=["POST"])
@khach_hang_required
def them_gio_hang():
    bien_the_id = request.form.get("bien_the_id", type=int)
    so_luong    = request.form.get("so_luong", 1, type=int)
    san_pham_id = request.form.get("san_pham_id", type=int)
    redirect_target = request.referrer or url_for("khach.xem_gio_hang")

    if not so_luong or so_luong < 1:
        so_luong = 1

    bien_the = datalayer.get_bien_the_by_id(bien_the_id) if bien_the_id else None
    if bien_the:
        san_pham_id = bien_the.SanPhamID

    if not bien_the_id:
        flash("Không xác định được sản phẩm.", "danger")
        response = redirect(redirect_target)
        if san_pham_id:
            response.set_cookie(
                f"luxury_product_{san_pham_id}_qty",
                str(so_luong),
                max_age=7 * 24 * 60 * 60,
                httponly=True,
                secure=request.is_secure,
                samesite="Lax",
            )
        return response

    item, loi = logic.them_vao_gio_hang(
        current_user.KhachHangID, bien_the_id, so_luong
    )
    if loi:
        flash(loi, "danger")
    else:
        flash("Đã thêm vào giỏ hàng.", "success")

    # Quay lại trang sản phẩm hoặc trang trước
    response = redirect(redirect_target)
    if san_pham_id:
        cookie_options = {
            "max_age": 7 * 24 * 60 * 60,
            "httponly": True,
            "secure": request.is_secure,
            "samesite": "Lax",
        }
        response.set_cookie(
            f"luxury_product_{san_pham_id}_variant",
            str(bien_the_id),
            **cookie_options,
        )
        response.set_cookie(
            f"luxury_product_{san_pham_id}_qty",
            str(so_luong),
            **cookie_options,
        )
    return response


@khach_bp.route("/gio-hang/cap-nhat", methods=["POST"])
@khach_hang_required
def cap_nhat_gio_hang():
    bien_the_id = request.form.get("bien_the_id", type=int)
    so_luong    = request.form.get("so_luong", type=int)

    if bien_the_id is None or so_luong is None:
        flash("Dữ liệu không hợp lệ.", "danger")
        return redirect(url_for("khach.xem_gio_hang"))

    _, loi = logic.cap_nhat_gio_hang(
        current_user.KhachHangID, bien_the_id, so_luong
    )
    if loi:
        flash(loi, "danger")
    else:
        flash("Đã cập nhật giỏ hàng.", "success")

    return redirect(url_for("khach.xem_gio_hang"))


@khach_bp.route("/gio-hang/xoa", methods=["POST"])
@khach_hang_required
def xoa_gio_hang():
    bien_the_id = request.form.get("bien_the_id", type=int)
    if bien_the_id:
        logic.xoa_khoi_gio_hang(current_user.KhachHangID, bien_the_id)
        flash("Đã xóa sản phẩm khỏi giỏ hàng.", "info")
    return redirect(url_for("khach.xem_gio_hang"))


# ══════════════════════════════════════════════
# CHECKOUT & ĐẶT HÀNG
# ══════════════════════════════════════════════

@khach_bp.route("/dat-hang", methods=["GET", "POST"])
@khach_hang_required
def dat_hang():
    """
    GET  → trang checkout — hiện giỏ hàng + form địa chỉ + ô nhập mã giảm giá.
    POST → xử lý đặt hàng.
    """
    if request.method == "GET":
        gio_hang_data, _ = logic.xem_gio_hang(current_user.KhachHangID)
        if not gio_hang_data["items"]:
            flash("Giỏ hàng đang trống.", "warning")
            return redirect(url_for("khach.trang_chu"))

        # Preview mã giảm giá nếu đã nhập từ query string
        ma_code   = request.args.get("ma_code", "").strip()
        giam_gia  = 0
        loi_ma    = None
        mgg_info  = None

        if ma_code:
            from decimal import Decimal
            giam, mgg_obj, loi_ma = logic.ap_ma_giam_gia(
                ma_code, Decimal(str(gio_hang_data["tong_tien"]))
            )
            if not loi_ma:
                giam_gia = float(giam)
                mgg_info = mgg_obj

        return render_template(
            "products/checkout.html",
            items     = gio_hang_data["items"],
            tong_tien = gio_hang_data["tong_tien"],
            giam_gia  = giam_gia,
            thanh_toan= gio_hang_data["tong_tien"] - giam_gia,
            ma_code   = ma_code,
            loi_ma    = loi_ma,
            mgg_info  = mgg_info,
            kh        = current_user,
        )

    # POST — đặt hàng
    dia_chi    = request.form.get("dia_chi_giao", "").strip()
    phuong_thuc= request.form.get("phuong_thuc_thanh_toan", "ChuyenKhoan")
    ma_code    = request.form.get("ma_code", "").strip() or None
    ghi_chu    = request.form.get("ghi_chu", "").strip() or None

    if not dia_chi:
        flash("Vui lòng nhập địa chỉ giao hàng.", "danger")
        return redirect(url_for("khach.dat_hang"))

    dh, loi = logic.dat_hang(
        khach_hang_id       = current_user.KhachHangID,
        dia_chi_giao        = dia_chi,
        phuong_thuc_thanh_toan = phuong_thuc,
        ma_giam_gia_code    = ma_code,
        ghi_chu             = ghi_chu,
    )
    if loi:
        flash(loi, "danger")
        return redirect(url_for("khach.dat_hang"))

    flash(f"Đặt hàng thành công! Mã đơn hàng: {dh.MaDonHang}", "success")
    return redirect(url_for("khach.chi_tiet_don_hang", don_hang_id=dh.DonHangID))


@khach_bp.route("/dat-hang/kiem-tra-ma", methods=["POST"])
@khach_hang_required
def kiem_tra_ma_giam_gia():
    """
    POST form: ma_code, tong_tien
    Redirect lại trang checkout với ma_code trên query string
    để render preview giảm giá ngay.
    """
    ma_code   = request.form.get("ma_code", "").strip()
    return redirect(url_for("khach.dat_hang", ma_code=ma_code))


# ══════════════════════════════════════════════
# LỊCH SỬ & CHI TIẾT ĐƠN HÀNG
# ══════════════════════════════════════════════

@khach_bp.route("/don-hang")
@khach_hang_required
def lich_su_don_hang():
    don_hangs, _ = logic.xem_don_hang_khach(current_user.KhachHangID)
    return render_template(
        "products/orders.html",
        don_hangs = don_hangs,
        kh        = current_user,
    )


@khach_bp.route("/don-hang/<int:don_hang_id>")
@khach_hang_required
def chi_tiet_don_hang(don_hang_id):
    result, loi = logic.xem_chi_tiet_don_hang(
        don_hang_id, khach_hang_id=current_user.KhachHangID
    )
    if loi:
        flash(loi, "danger")
        return redirect(url_for("khach.lich_su_don_hang"))

    return render_template(
        "products/order_detail.html",
        dh          = result["don_hang"],
        chi_tiets   = result["chi_tiets"],
        thanh_toans = result["thanh_toans"],
        bao_hanhs   = result["bao_hanhs"],
        kh          = current_user,
    )


@khach_bp.route("/don-hang/<int:don_hang_id>/huy", methods=["POST"])
@khach_hang_required
def huy_don_hang(don_hang_id):
    dh, loi = logic.huy_don_hang(
        don_hang_id, khach_hang_id=current_user.KhachHangID
    )
    if loi:
        flash(loi, "danger")
    else:
        flash("Đã hủy đơn hàng thành công.", "info")
    return redirect(url_for("khach.chi_tiet_don_hang", don_hang_id=don_hang_id))


# ══════════════════════════════════════════════
# BẢO HÀNH
# ══════════════════════════════════════════════

@khach_bp.route("/bao-hanh")
@khach_hang_required
def xem_bao_hanh():
    bao_hanhs, _ = logic.xem_bao_hanh_khach(current_user.KhachHangID)
    return render_template(
        "products/warranty.html",
        bao_hanhs = bao_hanhs,
        kh        = current_user,
    )


@khach_bp.route("/bao-hanh/don-hang/<int:don_hang_id>")
@khach_hang_required
def bao_hanh_theo_don(don_hang_id):
    bao_hanhs, loi = logic.kiem_tra_bao_hanh(
        don_hang_id, khach_hang_id=current_user.KhachHangID
    )
    if loi:
        flash(loi, "danger")
        return redirect(url_for("khach.xem_bao_hanh"))

    return render_template(
        "products/warranty_detail.html",
        bao_hanhs   = bao_hanhs,
        don_hang_id = don_hang_id,
        kh          = current_user,
    )


# ══════════════════════════════════════════════
# TÀI KHOẢN — hồ sơ, VIP, cập nhật
# ══════════════════════════════════════════════

@khach_bp.route("/tai-khoan")
@khach_hang_required
def tai_khoan():
    """Trang tổng quan tài khoản — hồ sơ + VIP + lịch sử ngắn."""
    vip, _ = logic.xem_thong_tin_vip(current_user.KhachHangID)
    don_hangs_gan_day = (
        datalayer.get_don_hang_by_khach_hang(current_user.KhachHangID)[:5]
    )
    return render_template(
        "products/profile_kh.html",
        kh              = current_user,
        vip             = vip,
        don_hangs_gan_day = don_hangs_gan_day,
    )


@khach_bp.route("/tai-khoan/cap-nhat", methods=["GET", "POST"])
@khach_hang_required
def cap_nhat_tai_khoan():
    """Cập nhật họ tên, số điện thoại, ngày sinh."""
    if request.method == "POST":
        kh, loi = logic.cap_nhat_thong_tin_ca_nhan(
            current_user.KhachHangID,
            {
                "HoTen"      : request.form.get("ho_ten", "").strip(),
                "SoDienThoai": request.form.get("so_dien_thoai", "").strip() or None,
                "NgaySinh"   : request.form.get("ngay_sinh") or None,
            },
        )
        if loi:
            datalayer.db.session.rollback()  # Hủy thay đổi nếu có lỗi (nhất là lỗi trùng số điện thoại)
            flash(loi, "danger")
            # Render lại trang hiện tại, KHÔNG redirect
            return render_template("products/profile_kh.html", kh=current_user)
        else:
            flash("Cập nhật thông tin thành công.", "success")
        return redirect(url_for("khach.tai_khoan"))

    return render_template("products/profile_kh.html", kh=current_user)


@khach_bp.route("/tai-khoan/vip")
@khach_hang_required
def xem_vip():
    vip, loi = logic.xem_thong_tin_vip(current_user.KhachHangID)
    if loi:
        flash(loi, "info")
    return render_template(
        "products/vip.html",
        kh  = current_user,
        vip = vip,
    )
