import os
import uuid
from datetime import date, timedelta
from decimal import Decimal
from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from extensions import db
try:
    from ...models import KhachHang, NhanVien, SanPham, DonHang, MaGiamGia, ThuongHieu, DanhMuc, HinhAnhSanPham, BienTheSanPham
except ImportError:
    from models import KhachHang, NhanVien, SanPham, DonHang, MaGiamGia, ThuongHieu, DanhMuc, HinhAnhSanPham, BienTheSanPham
from Model.Datalayer import get_hinh_anh_by_san_pham
admin_bp = Blueprint('admin', __name__)


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not isinstance(current_user, NhanVien):
            flash('Bạn không có quyền truy cập khu vực quản trị.', 'danger')
            return redirect(url_for('products.index'))
        return view_func(*args, **kwargs)

    return wrapped


def _load_product_choices():
    brands = ThuongHieu.query.order_by(ThuongHieu.TenThuongHieu.asc()).all()
    categories = DanhMuc.query.order_by(DanhMuc.TenDanhMuc.asc()).all()
    return brands, categories


def _safe_decimal(raw_value, default=Decimal('0')):
    try:
        return Decimal(str(raw_value))
    except Exception:
        return default


def _parse_date(raw_value, default_value=None):
    if raw_value:
        try:
            return date.fromisoformat(raw_value)
        except ValueError:
            return default_value
    return default_value


def _save_product_images(product_id, uploaded_files, main_image_index=None):
    saved_paths = []
    static_root = current_app.static_folder or current_app.root_path
    base_folder = os.path.join(static_root, 'uploads', 'products', str(product_id))
    os.makedirs(base_folder, exist_ok=True)
    has_existing_images = HinhAnhSanPham.query.filter_by(SanPhamID=product_id).first() is not None
    try:
        main_image_index = int(main_image_index) if main_image_index is not None else None
    except (TypeError, ValueError):
        main_image_index = None

    if has_existing_images and main_image_index is not None:
        HinhAnhSanPham.query.filter_by(SanPhamID=product_id).update({'LaAnhChinh': False})

    for index, file_storage in enumerate(uploaded_files):
        if not file_storage or not file_storage.filename:
            continue

        filename = secure_filename(file_storage.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(base_folder, unique_name)
        file_storage.save(file_path)

        relative_path = os.path.relpath(file_path, static_root).replace('\\', '/')
        saved_paths.append(relative_path)

        image_record = HinhAnhSanPham(
            SanPhamID=product_id,
            DuongDan=relative_path,
            LaAnhChinh=(index == main_image_index if main_image_index is not None else (not has_existing_images and index == 0)),
            ThuTu=index + 1,
        )
        db.session.add(image_record)

    return saved_paths


def _save_variant_image(variant_id, uploaded_file):
    if not uploaded_file or not uploaded_file.filename:
        return None

    static_root = current_app.static_folder or current_app.root_path
    base_folder = os.path.join(static_root, 'uploads', 'variants', str(variant_id))
    os.makedirs(base_folder, exist_ok=True)
    filename = secure_filename(uploaded_file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(base_folder, unique_name)
    uploaded_file.save(file_path)
    return os.path.relpath(file_path, static_root).replace('\\', '/')


def _delete_variant_image_file(image_path):
    if not image_path:
        return
    static_root = current_app.static_folder or current_app.root_path
    file_path = os.path.join(static_root, image_path.replace('/', os.sep))
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass


@admin_bp.route('/')
@staff_required
def dashboard():
    stats = {
        'customers': KhachHang.query.count(),
        'staff': NhanVien.query.count(),
        'products': SanPham.query.count(),
        'orders': DonHang.query.count(),
        'discounts': MaGiamGia.query.count(),
    }
    return render_template('admin/dashboard.html', staff=current_user, stats=stats)


@admin_bp.route('/nguoi-dung')
@staff_required
def users():
    staff_list = NhanVien.query.order_by(NhanVien.NgayTao.desc()).all()
    customer_list = KhachHang.query.order_by(KhachHang.NgayDangKy.desc()).all()
    return render_template(
        'admin/users.html',
        staff=current_user,
        staff_list=staff_list,
        customer_list=customer_list,
    )


@admin_bp.route('/san-pham')
@staff_required
def products():
    product_list = SanPham.query.order_by(SanPham.SanPhamID.desc()).limit(20).all()
    return render_template('admin/products.html', staff=current_user, product_list=product_list)


@admin_bp.route('/ma-giam-gia')
@staff_required
def discounts():
    discount_list = MaGiamGia.query.order_by(MaGiamGia.MaGiamGiaID.desc()).all()
    return render_template('admin/discounts.html', staff=current_user, discount_list=discount_list)


@admin_bp.route('/don-hang')
@staff_required
def orders():
    order_list = DonHang.query.order_by(DonHang.DonHangID.desc()).limit(20).all()
    return render_template('admin/orders.html', staff=current_user, order_list=order_list)


@admin_bp.route('/thuong-hieu')
@staff_required
def brands():
    brand_list = ThuongHieu.query.order_by(ThuongHieu.ThuongHieuID.desc()).all()
    return render_template('admin/brand_list.html', staff=current_user, brand_list=brand_list)


@admin_bp.route('/danh-muc')
@staff_required
def categories():
    category_list = DanhMuc.query.order_by(DanhMuc.DanhMucID.desc()).all()
    return render_template('admin/category_list.html', staff=current_user, category_list=category_list)


# --- PRODUCT CRUD -------------------------------------------------


@admin_bp.route('/san-pham/them', methods=['GET', 'POST'])
@staff_required
def add_product():
    brands, categories = _load_product_choices()
    if request.method == 'POST':
        ten = request.form.get('ten', '').strip()
        ma = request.form.get('ma', '').strip()
        thuong_hieu_id = request.form.get('thuong_hieu_id', '').strip()
        danh_muc_id = request.form.get('danh_muc_id', '').strip()
        gia = _safe_decimal(request.form.get('gia', '0'))
        gia_goc = _safe_decimal(request.form.get('gia_goc', gia), default=gia)
        chat_lieu = request.form.get('chat_lieu', '').strip()
        xuat_xu = request.form.get('xuat_xu', '').strip() or 'Việt Nam'
        mo_ta = request.form.get('mo_ta', '').strip()
        trang_thai = request.form.get('trang_thai', 'DangBan').strip() or 'DangBan'

        if not ten or not ma or not thuong_hieu_id or not danh_muc_id:
            flash('Tên, mã, thương hiệu và danh mục là bắt buộc.', 'danger')
            return render_template('admin/product_form.html', staff=current_user, brands=brands, categories=categories)

        from extensions import db
        sp = SanPham(
            TenSanPham=ten,
            MaSanPham=ma,
            ThuongHieuID=int(thuong_hieu_id),
            DanhMucID=int(danh_muc_id),
            GiaBan=gia,
            GiaGoc=gia_goc,
            ChatLieu=chat_lieu or None,
            XuatXu=xuat_xu,
            MoTa=mo_ta or None,
            TrangThai=trang_thai,
        )
        db.session.add(sp)
        db.session.commit()

        _save_product_images(sp.SanPhamID, request.files.getlist('images'), request.form.get('main_image_index'))
        db.session.commit()

        flash('Đã tạo sản phẩm.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', staff=current_user, brands=brands, categories=categories)


@admin_bp.route('/san-pham/<int:pid>/sua', methods=['GET', 'POST'])
@staff_required
def edit_product(pid):
    sp = SanPham.query.get_or_404(pid)
    brands, categories = _load_product_choices()
    if request.method == 'POST':
        sp.TenSanPham = request.form.get('ten', sp.TenSanPham)
        sp.MaSanPham = request.form.get('ma', sp.MaSanPham)
        sp.ThuongHieuID = int(request.form.get('thuong_hieu_id', sp.ThuongHieuID))
        sp.DanhMucID = int(request.form.get('danh_muc_id', sp.DanhMucID))
        try:
            sp.GiaBan = _safe_decimal(request.form.get('gia', sp.GiaBan), default=sp.GiaBan)
            sp.GiaGoc = _safe_decimal(request.form.get('gia_goc', sp.GiaGoc), default=sp.GiaGoc)
        except Exception:
            pass
        sp.ChatLieu = request.form.get('chat_lieu', sp.ChatLieu)
        sp.XuatXu = request.form.get('xuat_xu', sp.XuatXu)
        sp.MoTa = request.form.get('mo_ta', sp.MoTa)
        sp.TrangThai = request.form.get('trang_thai', sp.TrangThai)
        from extensions import db
        db.session.commit()

        _save_product_images(sp.SanPhamID, request.files.getlist('images'), request.form.get('main_image_index'))
        db.session.commit()

        flash('Cập nhật sản phẩm thành công.', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', staff=current_user, product=sp, brands=brands, categories=categories)


@admin_bp.route('/san-pham/<int:pid>/xoa', methods=['POST'])
@staff_required
def delete_product(pid):
    sp = SanPham.query.get_or_404(pid)
    from extensions import db
    variants = BienTheSanPham.query.filter_by(SanPhamID=sp.SanPhamID).all()
    for variant in variants:
        _delete_variant_image_file(variant.HinhAnh)
        db.session.delete(variant)
    images = HinhAnhSanPham.query.filter_by(SanPhamID=sp.SanPhamID).all()
    for image in images:
        file_path = os.path.join(current_app.static_folder, image.DuongDan.replace('/', os.sep))
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
    HinhAnhSanPham.query.filter_by(SanPhamID=sp.SanPhamID).delete()
    db.session.delete(sp)
    db.session.commit()
    flash('Đã xóa sản phẩm.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/san-pham/<int:pid>/bien-the')
@staff_required
def product_variants(pid):
    sp = SanPham.query.get_or_404(pid)
    variants = BienTheSanPham.query.filter_by(SanPhamID=pid).order_by(BienTheSanPham.BienTheID.desc()).all()
    return render_template('admin/variant_list.html', staff=current_user, product=sp, variants=variants)


@admin_bp.route('/san-pham/<int:pid>/bien-the/them', methods=['GET', 'POST'])
@staff_required
def add_variant(pid):
    sp = SanPham.query.get_or_404(pid)
    if request.method == 'POST':
        serial = request.form.get('serial', '').strip()
        mau = request.form.get('mau', '').strip()
        kich = request.form.get('kich_thuoc', '').strip()
        ma_vach = request.form.get('ma_vach', '').strip()
        so_luong = request.form.get('so_luong_ton', '0').strip()
        gia_rieng = request.form.get('gia_ban_rieng', '').strip()

        if not serial or not mau or not ma_vach:
            flash('Serial, màu sắc và mã vạch là bắt buộc.', 'danger')
            return render_template('admin/variant_form.html', staff=current_user, product=sp)

        from extensions import db
        variant = BienTheSanPham(
            SanPhamID=sp.SanPhamID,
            SerialNumber=serial,
            MauSac=mau,
            KichThuoc=kich or None,
            MaVach=ma_vach,
            SoLuongTon=int(so_luong) if so_luong else 0,
            GiaBanRieng=_safe_decimal(gia_rieng) if gia_rieng else None,
        )
        db.session.add(variant)
        db.session.commit()

        uploaded_image = request.files.get('image')
        if uploaded_image and uploaded_image.filename:
            variant.HinhAnh = _save_variant_image(variant.BienTheID, uploaded_image)
            db.session.commit()

        flash('Đã tạo biến thể.', 'success')
        return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))

    return render_template('admin/variant_form.html', staff=current_user, product=sp)


@admin_bp.route('/san-pham/<int:pid>/bien-the/<int:vid>/sua', methods=['GET', 'POST'])
@staff_required
def edit_variant(pid, vid):
    sp = SanPham.query.get_or_404(pid)
    variant = BienTheSanPham.query.get_or_404(vid)
    if variant.SanPhamID != sp.SanPhamID:
        flash('Biến thể không thuộc sản phẩm này.', 'danger')
        return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))

    if request.method == 'POST':
        variant.SerialNumber = request.form.get('serial', variant.SerialNumber).strip()
        variant.MauSac = request.form.get('mau', variant.MauSac).strip()
        variant.KichThuoc = request.form.get('kich_thuoc', variant.KichThuoc)
        variant.MaVach = request.form.get('ma_vach', variant.MaVach).strip()
        so_luong = request.form.get('so_luong_ton', variant.SoLuongTon)
        variant.SoLuongTon = int(so_luong) if str(so_luong).strip() else 0
        gia_rieng = request.form.get('gia_ban_rieng', '').strip()
        variant.GiaBanRieng = _safe_decimal(gia_rieng) if gia_rieng else None
        from extensions import db
        db.session.commit()

        uploaded_image = request.files.get('image')
        if uploaded_image and uploaded_image.filename:
            _delete_variant_image_file(variant.HinhAnh)
            variant.HinhAnh = _save_variant_image(variant.BienTheID, uploaded_image)
            db.session.commit()

        flash('Cập nhật biến thể thành công.', 'success')
        return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))

    return render_template('admin/variant_form.html', staff=current_user, product=sp, variant=variant)


@admin_bp.route('/san-pham/<int:pid>/bien-the/<int:vid>/xoa', methods=['POST'])
@staff_required
def delete_variant(pid, vid):
    sp = SanPham.query.get_or_404(pid)
    variant = BienTheSanPham.query.get_or_404(vid)
    if variant.SanPhamID != sp.SanPhamID:
        flash('Biến thể không thuộc sản phẩm này.', 'danger')
        return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))

    from extensions import db
    _delete_variant_image_file(variant.HinhAnh)
    db.session.delete(variant)
    db.session.commit()
    flash('Đã xóa biến thể.', 'info')
    return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))


@admin_bp.route('/thuong-hieu/them', methods=['GET', 'POST'])
@staff_required
def add_brand():
    if request.method == 'POST':
        ten = request.form.get('ten', '').strip()
        quoc_gia = request.form.get('quoc_gia', '').strip()
        nam = request.form.get('nam', '').strip()
        mo_ta = request.form.get('mo_ta', '').strip()
        logo = request.form.get('logo', '').strip()
        trang_thai = request.form.get('trang_thai') == 'on'

        if not ten or not quoc_gia:
            flash('Tên thương hiệu và quốc gia xuất xứ là bắt buộc.', 'danger')
            return render_template('admin/brand_form.html', staff=current_user)

        from extensions import db
        brand = ThuongHieu(
            TenThuongHieu=ten,
            QuocGiaXuatXu=quoc_gia,
            NamThanhLap=int(nam) if nam else None,
            MoTa=mo_ta or None,
            Logo=logo or None,
            TrangThai=trang_thai,
        )
        db.session.add(brand)
        db.session.commit()
        flash('Đã tạo thương hiệu.', 'success')
        return redirect(url_for('admin.brands'))

    return render_template('admin/brand_form.html', staff=current_user)


@admin_bp.route('/thuong-hieu/<int:bid>/sua', methods=['GET', 'POST'])
@staff_required
def edit_brand(bid):
    brand = ThuongHieu.query.get_or_404(bid)
    if request.method == 'POST':
        brand.TenThuongHieu = request.form.get('ten', brand.TenThuongHieu).strip()
        brand.QuocGiaXuatXu = request.form.get('quoc_gia', brand.QuocGiaXuatXu).strip()
        nam = request.form.get('nam', '').strip()
        brand.NamThanhLap = int(nam) if nam else None
        brand.MoTa = request.form.get('mo_ta', brand.MoTa)
        brand.Logo = request.form.get('logo', brand.Logo)
        brand.TrangThai = request.form.get('trang_thai') == 'on'
        from extensions import db
        db.session.commit()
        flash('Cập nhật thương hiệu thành công.', 'success')
        return redirect(url_for('admin.brands'))

    return render_template('admin/brand_form.html', staff=current_user, brand=brand)


@admin_bp.route('/thuong-hieu/<int:bid>/xoa', methods=['POST'])
@staff_required
def delete_brand(bid):
    brand = ThuongHieu.query.get_or_404(bid)
    from extensions import db
    if SanPham.query.filter_by(ThuongHieuID=brand.ThuongHieuID).first():
        flash('Không thể xóa thương hiệu vì vẫn còn sản phẩm liên kết.', 'danger')
        return redirect(url_for('admin.brands'))
    if MaGiamGia.query.filter_by(ThuongHieuID=brand.ThuongHieuID).first():
        flash('Không thể xóa thương hiệu vì vẫn còn mã giảm giá liên kết.', 'danger')
        return redirect(url_for('admin.brands'))
    db.session.delete(brand)
    db.session.commit()
    flash('Đã xóa thương hiệu.', 'info')
    return redirect(url_for('admin.brands'))


@admin_bp.route('/danh-muc/them', methods=['GET', 'POST'])
@staff_required
def add_category():
    categories = DanhMuc.query.order_by(DanhMuc.TenDanhMuc.asc()).all()
    if request.method == 'POST':
        ten = request.form.get('ten', '').strip()
        cha_id = request.form.get('cha_id', '').strip()
        mo_ta = request.form.get('mo_ta', '').strip()
        trang_thai = request.form.get('trang_thai') == 'on'

        if not ten:
            flash('Tên danh mục là bắt buộc.', 'danger')
            return render_template('admin/category_form.html', staff=current_user, categories=categories)

        from extensions import db
        category = DanhMuc(
            TenDanhMuc=ten,
            DanhMucChaID=int(cha_id) if cha_id else None,
            MoTa=mo_ta or None,
            TrangThai=trang_thai,
        )
        db.session.add(category)
        db.session.commit()
        flash('Đã tạo danh mục.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', staff=current_user, categories=categories)


@admin_bp.route('/danh-muc/<int:cid>/sua', methods=['GET', 'POST'])
@staff_required
def edit_category(cid):
    category = DanhMuc.query.get_or_404(cid)
    categories = DanhMuc.query.filter(DanhMuc.DanhMucID != cid).order_by(DanhMuc.TenDanhMuc.asc()).all()
    if request.method == 'POST':
        category.TenDanhMuc = request.form.get('ten', category.TenDanhMuc).strip()
        cha_id = request.form.get('cha_id', '').strip()
        category.DanhMucChaID = int(cha_id) if cha_id else None
        category.MoTa = request.form.get('mo_ta', category.MoTa)
        category.TrangThai = request.form.get('trang_thai') == 'on'
        from extensions import db
        db.session.commit()
        flash('Cập nhật danh mục thành công.', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', staff=current_user, category=category, categories=categories)


@admin_bp.route('/danh-muc/<int:cid>/xoa', methods=['POST'])
@staff_required
def delete_category(cid):
    category = DanhMuc.query.get_or_404(cid)
    from extensions import db
    if SanPham.query.filter_by(DanhMucID=category.DanhMucID).first():
        flash('Không thể xóa danh mục vì vẫn còn sản phẩm liên kết.', 'danger')
        return redirect(url_for('admin.categories'))
    if DanhMuc.query.filter_by(DanhMucChaID=category.DanhMucID).first():
        flash('Không thể xóa danh mục vì vẫn còn danh mục con.', 'danger')
        return redirect(url_for('admin.categories'))
    db.session.delete(category)
    db.session.commit()
    flash('Đã xóa danh mục.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/san-pham/<int:pid>/bien-the/<int:vid>/anh', methods=['POST'])
@staff_required
def upload_variant_image(pid, vid):
    sp = SanPham.query.get_or_404(pid)
    variant = BienTheSanPham.query.get_or_404(vid)
    if variant.SanPhamID != sp.SanPhamID:
        flash('Biến thể không thuộc sản phẩm này.', 'danger')
        return redirect(url_for('admin.product_variants', pid=sp.SanPhamID))

    uploaded_file = request.files.get('image')
    if not uploaded_file or not uploaded_file.filename:
        flash('Vui lòng chọn ảnh.', 'danger')
        return redirect(url_for('admin.edit_variant', pid=sp.SanPhamID, vid=variant.BienTheID))

    _delete_variant_image_file(variant.HinhAnh)
    variant.HinhAnh = _save_variant_image(variant.BienTheID, uploaded_file)
    from extensions import db
    db.session.commit()
    flash('Đã cập nhật ảnh biến thể.', 'success')
    return redirect(url_for('admin.edit_variant', pid=sp.SanPhamID, vid=variant.BienTheID))


# --- DISCOUNT CRUD ------------------------------------------------


@admin_bp.route('/ma-giam-gia/them', methods=['GET', 'POST'])
@staff_required
def add_discount():
    brands = ThuongHieu.query.order_by(ThuongHieu.TenThuongHieu.asc()).all()
    if request.method == 'POST':
        code = request.form.get('ma', '').strip()
        loai = request.form.get('loai', 'PhanTram')
        gia = _safe_decimal(request.form.get('gia', '0'))
        giam_toi_da = request.form.get('giam_toi_da', '').strip()
        don_hang_toi_thieu = request.form.get('don_hang_toi_thieu', '').strip()
        ngay_bat_dau = _parse_date(request.form.get('ngay_bat_dau', ''), default_value=date.today())
        ngay_ket_thuc = _parse_date(request.form.get('ngay_ket_thuc', ''), default_value=date.today() + timedelta(days=30))
        so_luot_toi_da = request.form.get('so_luot_toi_da', '').strip()
        trang_thai = request.form.get('trang_thai') == 'on'
        thuong_hieu_id = request.form.get('thuong_hieu_id', '').strip() or None

        if not code:
            flash('Mã là bắt buộc.', 'danger')
            return render_template('admin/discount_form.html', staff=current_user, brands=brands)

        mg = MaGiamGia(
            MaCode=code,
            LoaiGiam=loai,
            GiaTri=gia,
            GiamToiDa=_safe_decimal(giam_toi_da, default=None) if giam_toi_da else None,
            DonHangToiThieu=_safe_decimal(don_hang_toi_thieu),
            NgayBatDau=ngay_bat_dau,
            NgayKetThuc=ngay_ket_thuc,
            SoLuotToiDa=int(so_luot_toi_da) if so_luot_toi_da else None,
            TrangThai=trang_thai,
            ThuongHieuID=int(thuong_hieu_id) if thuong_hieu_id else None,
        )
        from extensions import db
        db.session.add(mg)
        db.session.commit()
        flash('Đã tạo mã giảm giá.', 'success')
        return redirect(url_for('admin.discounts'))

    return render_template('admin/discount_form.html', staff=current_user, brands=brands)


@admin_bp.route('/ma-giam-gia/<int:mid>/sua', methods=['GET', 'POST'])
@staff_required
def edit_discount(mid):
    mg = MaGiamGia.query.get_or_404(mid)
    brands = ThuongHieu.query.order_by(ThuongHieu.TenThuongHieu.asc()).all()
    if request.method == 'POST':
        mg.MaCode = request.form.get('ma', mg.MaCode)
        mg.LoaiGiam = request.form.get('loai', mg.LoaiGiam)
        mg.GiaTri = _safe_decimal(request.form.get('gia', mg.GiaTri), default=mg.GiaTri)
        giam_toi_da = request.form.get('giam_toi_da', '').strip()
        mg.GiamToiDa = _safe_decimal(giam_toi_da, default=None) if giam_toi_da else None
        mg.DonHangToiThieu = _safe_decimal(request.form.get('don_hang_toi_thieu', mg.DonHangToiThieu), default=mg.DonHangToiThieu)
        mg.NgayBatDau = _parse_date(request.form.get('ngay_bat_dau', ''), default_value=mg.NgayBatDau)
        mg.NgayKetThuc = _parse_date(request.form.get('ngay_ket_thuc', ''), default_value=mg.NgayKetThuc)
        so_luot_toi_da = request.form.get('so_luot_toi_da', '').strip()
        mg.SoLuotToiDa = int(so_luot_toi_da) if so_luot_toi_da else None
        mg.TrangThai = request.form.get('trang_thai') == 'on'
        thuong_hieu_id = request.form.get('thuong_hieu_id', '').strip()
        mg.ThuongHieuID = int(thuong_hieu_id) if thuong_hieu_id else None
        from extensions import db
        db.session.commit()
        flash('Cập nhật mã giảm giá thành công.', 'success')
        return redirect(url_for('admin.discounts'))

    return render_template('admin/discount_form.html', staff=current_user, discount=mg, brands=brands)


@admin_bp.route('/ma-giam-gia/<int:mid>/xoa', methods=['POST'])
@staff_required
def delete_discount(mid):
    mg = MaGiamGia.query.get_or_404(mid)
    from extensions import db
    db.session.delete(mg)
    db.session.commit()
    flash('Đã xóa mã giảm giá.', 'info')
    return redirect(url_for('admin.discounts'))


# --- STAFF MANAGEMENT (simple) ------------------------------------


@admin_bp.route('/nguoi-dung/them-nhanvien', methods=['GET', 'POST'])
@staff_required
def add_staff():
    if request.method == 'POST':
        ho = request.form.get('ho_ten', '').strip()
        email = request.form.get('email', '').strip().lower()
        mat = request.form.get('mat_khau', '')
        vai = request.form.get('vai_tro', 'NhanVienBanHang')
        if not ho or not email or not mat:
            flash('Họ tên, email và mật khẩu là bắt buộc.', 'danger')
            return render_template('admin/staff_form.html', staff=current_user)

        from werkzeug.security import generate_password_hash
        nv = NhanVien(HoTen=ho, Email=email, MatKhau=generate_password_hash(mat), VaiTro=vai)
        from extensions import db
        db.session.add(nv)
        db.session.commit()
        flash('Đã tạo nhân viên.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/staff_form.html', staff=current_user)


@admin_bp.route('/nguoi-dung/<int:nid>/khoa', methods=['POST'])
@staff_required
def toggle_staff(nid):
    nv = NhanVien.query.get_or_404(nid)
    nv.TrangThai = not nv.TrangThai
    from extensions import db
    db.session.commit()
    flash('Đã cập nhật trạng thái nhân viên.', 'success')
    return redirect(url_for('admin.users'))
