
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
# GIỎ HÀNG
# ══════════════════════════════════════════════

def them_vao_gio_hang(khach_hang_id, bien_the_id, so_luong):
    """Thêm sản phẩm vào giỏ, kiểm tra tồn kho trước."""
    if so_luong <= 0:
        return None, "Số lượng phải lớn hơn 0."

    bien_the = get_bien_the_by_id(bien_the_id)
    if not bien_the:
        return None, "Sản phẩm không tồn tại."

    # Kiểm tra tổng số lượng sau khi thêm
    item_cu = get_gio_hang_item(khach_hang_id, bien_the_id)
    so_luong_hien_tai = item_cu.SoLuong if item_cu else 0
    if so_luong_hien_tai + so_luong > bien_the.SoLuongTon:
        return None, f"Chỉ còn {bien_the.SoLuongTon} sản phẩm trong kho."

    item = add_to_gio_hang(khach_hang_id, bien_the_id, so_luong)
    return item, None


def cap_nhat_gio_hang(khach_hang_id, bien_the_id, so_luong_moi):
    """Cập nhật số lượng item trong giỏ (0 = xóa)."""
    if so_luong_moi < 0:
        return None, "Số lượng không hợp lệ."

    if so_luong_moi > 0:
        bien_the = get_bien_the_by_id(bien_the_id)
        if not bien_the:
            return None, "Sản phẩm không tồn tại."
        if so_luong_moi > bien_the.SoLuongTon:
            return None, f"Chỉ còn {bien_the.SoLuongTon} sản phẩm trong kho."

    item = update_so_luong_gio_hang(khach_hang_id, bien_the_id, so_luong_moi)
    return item, None


def xoa_khoi_gio_hang(khach_hang_id, bien_the_id):
    ok = remove_from_gio_hang(khach_hang_id, bien_the_id)
    if not ok:
        return False, "Sản phẩm không có trong giỏ."
    return True, None


def xem_gio_hang(khach_hang_id):
    """Trả về danh sách item giỏ hàng kèm thông tin biến thể."""
    items = get_gio_hang_by_khach_hang(khach_hang_id)
    result = []
    tong_tien = Decimal('0')
    for item in items:
        bt = item.bien_the
        gia = bt.GiaBanRieng or bt.san_pham.GiaBan
        thanh_tien = gia * item.SoLuong
        tong_tien += thanh_tien
        result.append({
            'gio_hang_id': item.GioHangID,
            'bien_the_id': bt.BienTheID,
            'ten_san_pham': bt.san_pham.TenSanPham,
            'mau_sac': bt.MauSac,
            'kich_thuoc': bt.KichThuoc,
            'serial': bt.SerialNumber,
            'gia': float(gia),
            'so_luong': item.SoLuong,
            'thanh_tien': float(thanh_tien),
            'hinh_anh': bt.HinhAnh,
        })
    return {'items': result, 'tong_tien': float(tong_tien)}, None


# ══════════════════════════════════════════════
# MÃ GIẢM GIÁ
# ══════════════════════════════════════════════

def ap_ma_giam_gia(ma_code: str, tong_tien: Decimal, thuong_hieu_id=None):
    """
    Kiểm tra và tính số tiền giảm.
    Trả về (so_tien_giam, ma_giam_gia_obj, None) hoặc (0, None, error_msg).
    """
    mgg = get_ma_giam_gia_by_code(ma_code)
    if not mgg:
        return Decimal('0'), None, "Mã giảm giá không hợp lệ hoặc đã hết hạn."

    today = date.today()
    if today < mgg.NgayBatDau or today > mgg.NgayKetThuc:
        return Decimal('0'), None, "Mã giảm giá chưa có hiệu lực hoặc đã hết hạn."

    if mgg.SoLuotToiDa and mgg.SoLuotDaDung >= mgg.SoLuotToiDa:
        return Decimal('0'), None, "Mã giảm giá đã hết lượt sử dụng."

    if tong_tien < mgg.DonHangToiThieu:
        return Decimal('0'), None, f"Đơn hàng tối thiểu {mgg.DonHangToiThieu:,.0f}đ để dùng mã này."

    # Kiểm tra thương hiệu
    if mgg.ThuongHieuID and thuong_hieu_id and mgg.ThuongHieuID != thuong_hieu_id:
        return Decimal('0'), None, "Mã giảm giá không áp dụng cho thương hiệu này."

    # Tính giảm
    if mgg.LoaiGiam == 'PhanTram':
        giam = tong_tien * mgg.GiaTri / Decimal('100')
        if mgg.GiamToiDa:
            giam = min(giam, mgg.GiamToiDa)
    else:
        giam = min(mgg.GiaTri, tong_tien)

    return giam, mgg, None


# ══════════════════════════════════════════════
# ĐẶT HÀNG
# ══════════════════════════════════════════════

def _sinh_ma_don_hang():
    return 'LX-' + uuid.uuid4().hex[:7].upper()


def dat_hang(khach_hang_id, dia_chi_giao, phuong_thuc_thanh_toan,
             ma_giam_gia_code=None, ghi_chu=None):
    """
    Luồng đặt hàng đầy đủ:
    1. Lấy giỏ hàng
    2. Kiểm tra tồn kho
    3. Áp mã giảm giá (nếu có)
    4. Tạo DonHang + ChiTietDonHang
    5. Trừ tồn kho
    6. Tạo ThanhToan
    7. Tạo BaoHanh cho từng biến thể
    8. Xóa giỏ hàng
    9. Cập nhật điểm & hạng thành viên
    """
    # 1. Lấy giỏ hàng
    gio_hang_data, _ = xem_gio_hang(khach_hang_id)
    items = gio_hang_data['items']
    if not items:
        return None, "Giỏ hàng trống."

    tong_tien = Decimal(str(gio_hang_data['tong_tien']))

    # 2. Kiểm tra tồn kho lần cuối
    gio_hang_items = get_gio_hang_by_khach_hang(khach_hang_id)
    for gh in gio_hang_items:
        bt = gh.bien_the
        if gh.SoLuong > bt.SoLuongTon:
            return None, f"Sản phẩm '{bt.san_pham.TenSanPham}' không đủ hàng."

    # 3. Mã giảm giá
    giam_gia = Decimal('0')
    mgg_obj = None
    if ma_giam_gia_code:
        giam_gia, mgg_obj, err = ap_ma_giam_gia(ma_giam_gia_code, tong_tien)
        if err:
            return None, err

    thanh_toan_final = tong_tien - giam_gia

    # 4. Tạo DonHang
    don_hang = create_don_hang({
        'MaDonHang': _sinh_ma_don_hang(),
        'KhachHangID': khach_hang_id,
        'TrangThai': 'ChoXacNhan',
        'TongTienHang': tong_tien,
        'GiamGia': giam_gia,
        'ThanhToan': thanh_toan_final,
        'DiaChiGiao': dia_chi_giao,
        'GhiChu': ghi_chu,
    })

    # Tạo ChiTietDonHang
    chi_tiets_data = []
    for gh in gio_hang_items:
        bt = gh.bien_the
        gia = bt.GiaBanRieng or bt.san_pham.GiaBan
        chi_tiets_data.append({
            'DonHangID': don_hang.DonHangID,
            'BienTheID': bt.BienTheID,
            'SoLuong': gh.SoLuong,
            'DonGia': float(gia),
            'GiamGiaDong': 0,
            'ThanhTienDong': float(gia * gh.SoLuong),
        })
    bulk_create_chi_tiet(chi_tiets_data)

    # 5. Trừ tồn kho
    for gh in gio_hang_items:
        update_ton_kho(gh.BienTheID, -gh.SoLuong)

    # 6. Tạo ThanhToan
    create_thanh_toan({
        'DonHangID': don_hang.DonHangID,
        'PhuongThuc': phuong_thuc_thanh_toan,
        'SoTien': float(thanh_toan_final),
        'TrangThai': 'ChoPhanHoi',
    })

    # 7. Tạo BaoHanh — mỗi biến thể bảo hành 24 tháng
    today = date.today()
    for gh in gio_hang_items:
        create_bao_hanh({
            'BienTheID': gh.BienTheID,
            'KhachHangID': khach_hang_id,
            'DonHangID': don_hang.DonHangID,
            'NgayBatDau': today,
            'NgayKetThuc': date(today.year + 2, today.month, today.day),
            'DieuKienBaoHanh': 'Bảo hành chính hãng 24 tháng, không áp dụng hư hỏng do người dùng.',
            'TrangThaiBaoHanh': 'ConHan',
        })

    # 8. Tăng lượt dùng mã giảm giá
    if mgg_obj:
        tang_luot_su_dung(mgg_obj.MaGiamGiaID)

    # 9. Xóa giỏ hàng
    clear_gio_hang(khach_hang_id)

    # 10. Cập nhật điểm & hạng thành viên
    _cap_nhat_diem_va_hang(khach_hang_id, thanh_toan_final)

    return don_hang, None


def _cap_nhat_diem_va_hang(khach_hang_id, so_tien: Decimal):
    """Cộng điểm và nâng hạng thành viên sau khi đặt hàng thành công."""
    kh = get_khach_hang_by_id(khach_hang_id)
    if not kh:
        return

    # 1 điểm / 100,000đ
    diem_moi = int(so_tien / Decimal('100000'))
    tong_chi_tieu_moi = kh.TongChiTieu + so_tien
    diem_tich_luy_moi = kh.DiemTichLuy + diem_moi

    # Xác định hạng
    hang_moi = _xac_dinh_hang(tong_chi_tieu_moi)

    update_khach_hang(khach_hang_id, {
        'DiemTichLuy': diem_tich_luy_moi,
        'TongChiTieu': tong_chi_tieu_moi,
        'HangThanhVien': hang_moi,
    })

    # Cập nhật VIP nếu đủ điều kiện
    if hang_moi in ('Silver', 'Gold', 'Platinum'):
        create_or_update_vip(khach_hang_id, {
            'HangVIP': hang_moi,
            'DiemHienTai': diem_tich_luy_moi,
            'NgayLenHang': date.today(),
            'UuDaiPhanTram': _uu_dai_theo_hang(hang_moi),
        })


def _xac_dinh_hang(tong_chi_tieu: Decimal) -> str:
    if tong_chi_tieu >= Decimal('500000000'):
        return 'Platinum'
    elif tong_chi_tieu >= Decimal('200000000'):
        return 'Gold'
    elif tong_chi_tieu >= Decimal('50000000'):
        return 'Silver'
    return 'Standard'


def _uu_dai_theo_hang(hang: str) -> Decimal:
    return {'Silver': Decimal('5'), 'Gold': Decimal('10'), 'Platinum': Decimal('15')}.get(hang, Decimal('0'))


# ══════════════════════════════════════════════
# QUẢN LÝ ĐƠN HÀNG
# ══════════════════════════════════════════════

def xem_don_hang_khach(khach_hang_id):
    return get_don_hang_by_khach_hang(khach_hang_id), None


def xem_chi_tiet_don_hang(don_hang_id, khach_hang_id=None):
    dh = get_don_hang_by_id(don_hang_id)
    if not dh:
        return None, "Đơn hàng không tồn tại."
    # Khách chỉ xem đơn của mình
    if khach_hang_id and dh.KhachHangID != khach_hang_id:
        return None, "Bạn không có quyền xem đơn hàng này."
    chi_tiets = get_chi_tiet_by_don_hang(don_hang_id)
    thanh_toans = get_thanh_toan_by_don_hang(don_hang_id)
    bao_hanhs = get_bao_hanh_by_don_hang(don_hang_id)
    return {
        'don_hang': dh,
        'chi_tiets': chi_tiets,
        'thanh_toans': thanh_toans,
        'bao_hanhs': bao_hanhs,
    }, None


def huy_don_hang(don_hang_id, khach_hang_id=None):
    """Khách hủy đơn — chỉ được hủy khi đang ở trạng thái ChoXacNhan."""
    dh = get_don_hang_by_id(don_hang_id)
    if not dh:
        return None, "Đơn hàng không tồn tại."
    if khach_hang_id and dh.KhachHangID != khach_hang_id:
        return None, "Bạn không có quyền hủy đơn hàng này."
    if dh.TrangThai != 'ChoXacNhan':
        return None, "Chỉ có thể hủy đơn hàng đang chờ xác nhận."

    # Hoàn tồn kho
    chi_tiets = get_chi_tiet_by_don_hang(don_hang_id)
    for ct in chi_tiets:
        update_ton_kho(ct.BienTheID, ct.SoLuong)

    update_trang_thai_don_hang(don_hang_id, 'DaHuy')
    return dh, None


# ══════════════════════════════════════════════
# ADMIN — QUẢN LÝ ĐƠN HÀNG
# ══════════════════════════════════════════════

TRANG_THAI_HOP_LE = {
    'ChoXacNhan': ['DaXacNhan', 'DaHuy'],
    'DaXacNhan':  ['DangGiao'],
    'DangGiao':   ['DaGiao'],
}

def admin_cap_nhat_trang_thai_don_hang(don_hang_id, trang_thai_moi):
    dh = get_don_hang_by_id(don_hang_id)
    if not dh:
        return None, "Đơn hàng không tồn tại."
    hop_le = TRANG_THAI_HOP_LE.get(dh.TrangThai, [])
    if trang_thai_moi not in hop_le:
        return None, f"Không thể chuyển từ '{dh.TrangThai}' sang '{trang_thai_moi}'."
    update_trang_thai_don_hang(don_hang_id, trang_thai_moi)

    # Khi đơn giao thành công → cập nhật thanh toán
    if trang_thai_moi == 'DaGiao':
        for tt in get_thanh_toan_by_don_hang(don_hang_id):
            if tt.TrangThai == 'ChoPhanHoi':
                update_trang_thai_thanh_toan(tt.ThanhToanID, 'ThanhCong')

    return dh, None


def admin_xem_tat_ca_don_hang(trang_thai=None):
    return get_all_don_hang(trang_thai), None


# ══════════════════════════════════════════════
# ĐÁNH GIÁ SẢN PHẨM
# ══════════════════════════════════════════════

def gui_danh_gia(khach_hang_id, san_pham_id, diem_so, nhan_xet=None):
    if not (1 <= diem_so <= 5):
        return None, "Điểm đánh giá phải từ 1 đến 5."

    # Kiểm tra đã mua chưa — tìm trong chi tiết đơn hàng đã giao
    don_hangs = get_don_hang_by_khach_hang(khach_hang_id)
    da_mua = False
    for dh in don_hangs:
        if dh.TrangThai == 'DaGiao':
            for ct in get_chi_tiet_by_don_hang(dh.DonHangID):
                if ct.bien_the.SanPhamID == san_pham_id:
                    da_mua = True
                    break
        if da_mua:
            break

    if not da_mua:
        return None, "Bạn chỉ có thể đánh giá sản phẩm đã mua và được giao thành công."

    if get_danh_gia_by_khach_va_san_pham(khach_hang_id, san_pham_id):
        return None, "Bạn đã đánh giá sản phẩm này rồi."

    dg = create_danh_gia({
        'SanPhamID': san_pham_id,
        'KhachHangID': khach_hang_id,
        'DiemSo': diem_so,
        'NhanXet': nhan_xet,
        'DaXacNhan': 1,
    })
    return dg, None


# ══════════════════════════════════════════════
# BẢO HÀNH
# ══════════════════════════════════════════════

def xem_bao_hanh_khach(khach_hang_id):
    return get_bao_hanh_by_don_hang_and_khach(khach_hang_id), None


def kiem_tra_bao_hanh(don_hang_id, khach_hang_id):
    dh = get_don_hang_by_id(don_hang_id)
    if not dh or dh.KhachHangID != khach_hang_id:
        return None, "Không tìm thấy đơn hàng."
    bao_hanhs = get_bao_hanh_by_don_hang(don_hang_id)
    return bao_hanhs, None


# ══════════════════════════════════════════════
# THÔNG TIN KHÁCH HÀNG
# ══════════════════════════════════════════════

def cap_nhat_thong_tin_ca_nhan(khach_hang_id, data: dict):
    """Chỉ cho phép cập nhật các trường an toàn."""
    TRUONG_CHO_PHEP = {'HoTen', 'SoDienThoai', 'NgaySinh'}
    data_sach = {k: v for k, v in data.items() if k in TRUONG_CHO_PHEP}
    if not data_sach:
        return None, "Không có trường hợp lệ để cập nhật."
    kh = update_khach_hang(khach_hang_id, data_sach)
    return kh, None


def xem_thong_tin_vip(khach_hang_id):
    vip = get_vip_by_khach_hang(khach_hang_id)
    if not vip:
        return None, "Khách hàng chưa đạt hạng VIP."
    return vip, None


# Helper tránh import vòng
def get_bao_hanh_by_don_hang_and_khach(khach_hang_id):
    from datalayer import get_bao_hanh_by_khach_hang
    return get_bao_hanh_by_khach_hang(khach_hang_id)