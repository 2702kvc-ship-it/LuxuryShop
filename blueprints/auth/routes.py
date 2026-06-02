from urllib.parse import urljoin, urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from datetime import datetime

try:
    from ...extensions import db, mail
    from ...models import KhachHang, NhanVien
except ImportError:
    from extensions import db, mail
    from models import KhachHang, NhanVien

auth_bp = Blueprint('auth', __name__)


def _is_safe_redirect_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


# ─── Helper: tạo token từ email ──────────────────────────────────────────────
def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def tao_token(email):
    return _serializer().dumps(email, salt='email-confirm')

def xac_nhan_token(token, expiration=3600):
    """Giải mã token. Trả về email nếu hợp lệ, None nếu hết hạn/sai."""
    try:
        email = _serializer().loads(token, salt='email-confirm', max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None

def gui_email(tieu_de, nguoi_nhan, noi_dung_html):
    msg = Message(tieu_de, recipients=[nguoi_nhan], html=noi_dung_html)
    mail.send(msg)


# ─── ĐĂNG KÝ ─────────────────────────────────────────────────────────────────
@auth_bp.route('/dang-ky', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        ho_ten     = request.form.get('ho_ten', '').strip()
        email      = request.form.get('email', '').strip().lower()
        mat_khau   = request.form.get('mat_khau', '')
        xac_nhan   = request.form.get('xac_nhan_mat_khau', '')
        sdt        = request.form.get('so_dien_thoai', '').strip()

        # --- Validation ---
        loi = []
        if not ho_ten:
            loi.append('Vui lòng nhập họ tên.')
        if not email or '@' not in email:
            loi.append('Email không hợp lệ.')
        if len(mat_khau) < 6:
            loi.append('Mật khẩu phải có ít nhất 6 ký tự.')
        if mat_khau != xac_nhan:
            loi.append('Mật khẩu xác nhận không khớp.')
        if KhachHang.query.filter_by(Email=email).first():
            loi.append('Email này đã được đăng ký.')
        if sdt and KhachHang.query.filter_by(SoDienThoai=sdt).first():
            loi.append('Số điện thoại này đã được sử dụng.')

        if loi:
            for l in loi:
                flash(l, 'danger')
            return render_template('register.html',
                                   ho_ten=ho_ten, email=email, sdt=sdt)

        # --- Tạo tài khoản chưa xác nhận ---
        kh = KhachHang(
            HoTen       = ho_ten,
            Email       = email,
            MatKhau     = generate_password_hash(mat_khau),
            SoDienThoai = sdt or None,
            NgayDangKy  = datetime.now(),
            # Dùng HangThanhVien='Pending' để đánh dấu chưa xác nhận email
            HangThanhVien = 'Pending'
        )
        db.session.add(kh)
        db.session.commit()

        # --- Gửi email xác nhận ---
        token = tao_token(email)
        link  = url_for('auth.confirm_email', token=token, _external=True)
        html  = render_template('email/confirm_email.html',
                                ho_ten=ho_ten, link=link)
        try:
            gui_email('Xác nhận tài khoản LuxuryShop', email, html)
            flash('Đăng ký thành công! Vui lòng kiểm tra email để xác nhận tài khoản.', 'success')
        except Exception:
            flash('Đăng ký thành công nhưng không gửi được email. Liên hệ hỗ trợ.', 'warning')

        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ─── XÁC NHẬN EMAIL ──────────────────────────────────────────────────────────
@auth_bp.route('/xac-nhan-email/<token>')
def confirm_email(token):
    email = xac_nhan_token(token, expiration=3600)  # token hết hạn sau 1 giờ

    if not email:
        flash('Link xác nhận không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.login'))

    kh = KhachHang.query.filter_by(Email=email).first()
    if not kh:
        flash('Không tìm thấy tài khoản.', 'danger')
        return redirect(url_for('auth.login'))

    if kh.HangThanhVien != 'Pending':
        flash('Tài khoản đã được xác nhận trước đó.', 'info')
        return redirect(url_for('auth.login'))

    # Kích hoạt tài khoản
    kh.HangThanhVien = 'Standard'
    db.session.commit()
    flash('Xác nhận email thành công! Bạn có thể đăng nhập.', 'success')
    return redirect(url_for('auth.login'))


# ─── GỬI LẠI EMAIL XÁC NHẬN ─────────────────────────────────────────────────
@auth_bp.route('/gui-lai-xac-nhan', methods=['GET', 'POST'])
def resend_confirm():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        kh    = KhachHang.query.filter_by(Email=email).first()

        if not kh:
            flash('Không tìm thấy tài khoản với email này.', 'danger')
        elif kh.HangThanhVien != 'Pending':
            flash('Tài khoản này đã được xác nhận rồi.', 'info')
        else:
            token = tao_token(email)
            link  = url_for('auth.confirm_email', token=token, _external=True)
            html  = render_template('email/confirm_email.html',
                                    ho_ten=kh.HoTen, link=link)
            gui_email('Xác nhận tài khoản LuxuryShop', email, html)
            flash('Đã gửi lại email xác nhận!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('resend_confirm.html')


# ─── ĐĂNG NHẬP ───────────────────────────────────────────────────────────────
@auth_bp.route('/dang-nhap', methods=['GET', 'POST'])
def login():
    # Keep legacy route but send users to the customer login page.
    return redirect(url_for('auth.login_khach'))


@auth_bp.route('/dang-nhap-khach', methods=['GET', 'POST'])
def login_khach():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        mat_khau = request.form.get('mat_khau', '')
        nho_toi = request.form.get('nho_toi') == 'on'

        kh = KhachHang.query.filter_by(Email=email).first()
        if not kh or not check_password_hash(kh.MatKhau, mat_khau):
            flash('Email hoặc mật khẩu không đúng.', 'danger')
            return render_template('login_khach.html', email=email)

        if kh.HangThanhVien == 'Pending':
            flash('Tài khoản chưa xác nhận email. Vui lòng kiểm tra hộp thư.', 'warning')
            return render_template('login_khach.html', email=email)

        login_user(kh, remember=nho_toi)
        flash(f'Chào mừng trở lại, {kh.HoTen}!', 'success')

        next_page = request.args.get('next')
        if not _is_safe_redirect_url(next_page):
            next_page = None
        return redirect(next_page or url_for('admin.dashboard'))

    return render_template('login_khach.html')


@auth_bp.route('/dang-nhap-nhanvien', methods=['GET', 'POST'])
def login_nhanvien():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        mat_khau = request.form.get('mat_khau', '')
        nho_toi = request.form.get('nho_toi') == 'on'

        nv = NhanVien.query.filter_by(Email=email).first()
        if not nv or not check_password_hash(nv.MatKhau, mat_khau):
            flash('Email hoặc mật khẩu không đúng.', 'danger')
            return render_template('login_nhanvien.html', email=email)

        if not nv.TrangThai:
            flash('Tài khoản nhân viên đang bị khóa.', 'danger')
            return render_template('login_nhanvien.html', email=email)

        login_user(nv, remember=nho_toi)
        flash(f'Chào mừng nhân viên, {nv.HoTen}!', 'success')

        next_page = request.args.get('next')
        if not _is_safe_redirect_url(next_page):
            next_page = None
        return redirect(next_page or url_for('admin.dashboard'))

    return render_template('login_nhanvien.html')


# ─── ĐĂNG XUẤT ───────────────────────────────────────────────────────────────
@auth_bp.route('/dang-xuat')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


# ─── QUÊN MẬT KHẨU — Bước 1: nhập email ─────────────────────────────────────
@auth_bp.route('/quen-mat-khau', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        kh    = KhachHang.query.filter_by(Email=email).first()

        # Luôn hiện thông báo thành công dù email có tồn tại hay không
        # (tránh lộ thông tin tài khoản)
        if kh and kh.HangThanhVien != 'Pending':
            token = tao_token(email)
            link  = url_for('auth.reset_password', token=token, _external=True)
            html  = render_template('email/reset_password.html',
                                    ho_ten=kh.HoTen, link=link)
            gui_email('Đặt lại mật khẩu LuxuryShop', email, html)

        flash('Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


# ─── QUÊN MẬT KHẨU — Bước 2: đặt mật khẩu mới ──────────────────────────────
@auth_bp.route('/dat-lai-mat-khau/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = xac_nhan_token(token, expiration=1800)  # hết hạn sau 30 phút

    if not email:
        flash('Link đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    kh = KhachHang.query.filter_by(Email=email).first()
    if not kh:
        flash('Không tìm thấy tài khoản.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        mat_khau_moi = request.form.get('mat_khau_moi', '')
        xac_nhan     = request.form.get('xac_nhan_mat_khau', '')

        if len(mat_khau_moi) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
            return render_template('reset_password.html', token=token)

        if mat_khau_moi != xac_nhan:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
            return render_template('reset_password.html', token=token)

        kh.MatKhau = generate_password_hash(mat_khau_moi)
        db.session.commit()
        flash('Đặt lại mật khẩu thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)


# ─── PROFILE (xem thông tin cá nhân) ─────────────────────────────────────────
@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', kh=current_user)


# ─── ĐỔI MẬT KHẨU (khi đã đăng nhập) ───────────────────────────────────────
@auth_bp.route('/doi-mat-khau', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        cu    = request.form.get('mat_khau_cu', '')
        moi   = request.form.get('mat_khau_moi', '')
        xn    = request.form.get('xac_nhan', '')

        if not check_password_hash(current_user.MatKhau, cu):
            flash('Mật khẩu hiện tại không đúng.', 'danger')
        elif len(moi) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự.', 'danger')
        elif moi != xn:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
        else:
            current_user.MatKhau = generate_password_hash(moi)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('change_password.html')