from urllib.parse import urljoin, urlparse

from flask import Flask, redirect, request, url_for
import click

# Load environment variables from .env (if present) early so config.py picks them up
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


from config import Config
from extensions import db, login_manager, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    def is_safe_redirect_url(target):
        if not target:
            return False
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

    @app.context_processor
    def inject_preferences():
        lang = request.cookies.get('luxury_lang', 'vi')
        theme = request.cookies.get('luxury_theme', 'light')
        if lang not in ('vi', 'en'):
            lang = 'vi'
        if theme not in ('light', 'dark'):
            theme = 'light'
        return {
            'luxury_lang': lang,
            'luxury_theme': theme,
        }

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

    @app.route('/preferences', methods=['POST'])
    def set_preferences():
        lang = request.form.get('lang', 'vi')
        theme = request.form.get('theme', 'light')
        next_page = request.form.get('next') or request.referrer

        if lang not in ('vi', 'en'):
            lang = 'vi'
        if theme not in ('light', 'dark'):
            theme = 'light'
        if not is_safe_redirect_url(next_page):
            next_page = url_for('khach.trang_chu')

        response = redirect(next_page)
        cookie_options = {
            'max_age': 365 * 24 * 60 * 60,
            'secure': request.is_secure,
            'samesite': 'Lax',
        }
        response.set_cookie('luxury_lang', lang, **cookie_options)
        response.set_cookie('luxury_theme', theme, **cookie_options)
        return response

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    if __package__:
        from .blueprints.products.routes import products_bp
        from .blueprints.admin.routes import admin_bp
        from .blueprints.auth.routes import auth_bp
        from .blueprints.guest.routes import khach_bp
    else:
        from blueprints.products.routes import products_bp
        from blueprints.admin.routes import admin_bp
        from blueprints.auth.routes import auth_bp
        from blueprints.guest.routes import khach_bp

    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(admin_bp, url_prefix='/staff')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(khach_bp, url_prefix='')

    @app.cli.command('confirm-user')
    @click.argument('email')
    def confirm_user(email):
        """Mark a pending customer account as confirmed."""

        from Model.Models import KhachHang

        kh = KhachHang.query.filter_by(Email=email.strip().lower()).first()
        if not kh:
            click.echo(f'Khong tim thay tai khoan voi email: {email}')
            return

        kh.HangThanhVien = 'Standard'
        db.session.commit()
        click.echo(f'Da kich hoat tai khoan: {kh.Email}')

    @app.cli.command('migrate-nhanvien-matkhau')
    def migrate_nhanvien_matkhau():
        """Alter NhanVien.MatKhau column to length 255 for common DB backends.

        This runs a raw ALTER TABLE statement; review and back up your DB before running.
        """
        try:
            dialect = db.engine.dialect.name
        except Exception as e:
            click.echo(f'Khong the lay dialect engine: {e}')
            return

        click.echo(f'Detected dialect: {dialect}')
        conn = db.engine.connect()
        try:
            if dialect.startswith('mssql'):
                sql = 'ALTER TABLE NhanVien ALTER COLUMN MatKhau NVARCHAR(255) NOT NULL'
            elif dialect.startswith('mysql'):
                sql = 'ALTER TABLE NhanVien MODIFY MatKhau VARCHAR(255) NOT NULL'
            elif dialect.startswith('postgres'):
                sql = "ALTER TABLE \"NhanVien\" ALTER COLUMN \"MatKhau\" TYPE VARCHAR(255)"
            elif dialect == 'sqlite':
                click.echo('SQLite detected: automatic ALTER COLUMN is not supported. Please run manual migration or use a proper migration tool.')
                return
            else:
                click.echo('Unsupported dialect for automated migration. Please alter the column manually.')
                return

            click.echo(f'Executing: {sql}')
            with conn.begin():
                conn.execute(sql)
            click.echo('Migration executed. Verify the column type in your database.')
        except Exception as e:
            click.echo(f'Error executing migration: {e}')
        finally:
            conn.close()

    @app.cli.command('migrate-unicode-columns')
    def migrate_unicode_columns():
        """Convert text columns to NVARCHAR for Vietnamese/Unicode data on SQL Server."""
        try:
            dialect = db.engine.dialect.name
        except Exception as e:
            click.echo(f'Khong the lay dialect engine: {e}')
            return

        if not dialect.startswith('mssql'):
            click.echo(f'Lenh nay chi ap dung cho SQL Server. Detected dialect: {dialect}')
            return

        unicode_columns = [
            ('ThuongHieu', 'TenThuongHieu', 'NVARCHAR(100)', 'NOT NULL'),
            ('ThuongHieu', 'QuocGiaXuatXu', 'NVARCHAR(100)', 'NOT NULL'),
            ('ThuongHieu', 'MoTa', 'NVARCHAR(500)', 'NULL'),
            ('ThuongHieu', 'Logo', 'NVARCHAR(255)', 'NULL'),
            ('DanhMuc', 'TenDanhMuc', 'NVARCHAR(100)', 'NOT NULL'),
            ('DanhMuc', 'MoTa', 'NVARCHAR(300)', 'NULL'),
            ('SanPham', 'TenSanPham', 'NVARCHAR(200)', 'NOT NULL'),
            ('SanPham', 'MaSanPham', 'NVARCHAR(50)', 'NOT NULL'),
            ('SanPham', 'ChatLieu', 'NVARCHAR(200)', 'NULL'),
            ('SanPham', 'XuatXu', 'NVARCHAR(100)', 'NOT NULL'),
            ('SanPham', 'MoTa', 'NVARCHAR(MAX)', 'NULL'),
            ('SanPham', 'TrangThai', 'NVARCHAR(20)', 'NULL'),
            ('GiayChungNhan', 'MaChungNhan', 'NVARCHAR(100)', 'NOT NULL'),
            ('GiayChungNhan', 'ToChucCap', 'NVARCHAR(200)', 'NOT NULL'),
            ('GiayChungNhan', 'QRCode', 'NVARCHAR(500)', 'NULL'),
            ('BienTheSanPham', 'SerialNumber', 'NVARCHAR(100)', 'NOT NULL'),
            ('BienTheSanPham', 'MauSac', 'NVARCHAR(50)', 'NOT NULL'),
            ('BienTheSanPham', 'KichThuoc', 'NVARCHAR(20)', 'NULL'),
            ('BienTheSanPham', 'MaVach', 'NVARCHAR(50)', 'NOT NULL'),
            ('BienTheSanPham', 'HinhAnh', 'NVARCHAR(255)', 'NULL'),
            ('HinhAnhSanPham', 'DuongDan', 'NVARCHAR(500)', 'NOT NULL'),
            ('KhachHang', 'HoTen', 'NVARCHAR(100)', 'NOT NULL'),
            ('KhachHang', 'Email', 'NVARCHAR(150)', 'NOT NULL'),
            ('KhachHang', 'MatKhau', 'NVARCHAR(255)', 'NOT NULL'),
            ('KhachHang', 'SoDienThoai', 'NVARCHAR(15)', 'NULL'),
            ('KhachHang', 'HangThanhVien', 'NVARCHAR(20)', 'NULL'),
            ('ChuongTrinhVIP', 'HangVIP', 'NVARCHAR(20)', 'NOT NULL'),
            ('MaGiamGia', 'MaCode', 'NVARCHAR(50)', 'NOT NULL'),
            ('MaGiamGia', 'LoaiGiam', 'NVARCHAR(30)', 'NOT NULL'),
            ('DonHang', 'MaDonHang', 'NVARCHAR(20)', 'NOT NULL'),
            ('DonHang', 'TrangThai', 'NVARCHAR(30)', 'NULL'),
            ('DonHang', 'DiaChiGiao', 'NVARCHAR(300)', 'NOT NULL'),
            ('DonHang', 'GhiChu', 'NVARCHAR(500)', 'NULL'),
            ('BaoHanh', 'DieuKienBaoHanh', 'NVARCHAR(500)', 'NULL'),
            ('BaoHanh', 'TrangThaiBaoHanh', 'NVARCHAR(20)', 'NULL'),
            ('ThanhToan', 'PhuongThuc', 'NVARCHAR(30)', 'NOT NULL'),
            ('ThanhToan', 'MaGiaoDich', 'NVARCHAR(100)', 'NULL'),
            ('ThanhToan', 'TrangThai', 'NVARCHAR(20)', 'NULL'),
            ('DanhGia', 'NhanXet', 'NVARCHAR(MAX)', 'NULL'),
            ('NhanVien', 'HoTen', 'NVARCHAR(100)', 'NOT NULL'),
            ('NhanVien', 'Email', 'NVARCHAR(100)', 'NOT NULL'),
            ('NhanVien', 'MatKhau', 'NVARCHAR(255)', 'NOT NULL'),
            ('NhanVien', 'SoDienThoai', 'NVARCHAR(15)', 'NULL'),
            ('NhanVien', 'VaiTro', 'NVARCHAR(30)', 'NULL'),
        ]

        click.echo('Dang chuyen cac cot chu sang NVARCHAR...')
        failures = []
        with db.engine.begin() as conn:
            for table, column, sql_type, nullability in unicode_columns:
                sql = f'ALTER TABLE [{table}] ALTER COLUMN [{column}] {sql_type} {nullability}'
                try:
                    conn.exec_driver_sql(sql)
                    click.echo(f'OK: {table}.{column} -> {sql_type}')
                except Exception as e:
                    failures.append((table, column, str(e)))
                    click.echo(f'FAIL: {table}.{column}: {e}')

        if failures:
            click.echo('')
            click.echo('Mot so cot chua alter duoc, thuong do unique/index/constraint dang phu thuoc.')
            click.echo('Hay backup DB roi xu ly cac cot FAIL bang migration rieng neu can.')
        else:
            click.echo('Da chuyen xong cac cot sang NVARCHAR.')

    return app

# Cho Flask-Login biết cách load user từ DB
@login_manager.user_loader
def load_user(user_id):
    print("LOAD_USER CALLED")
    print("user_id =", user_id)
    from Model.Models import KhachHang, NhanVien

    # Support both 'nv-' and 'nv_' prefixes used for staff IDs.
    if isinstance(user_id, str) and (user_id.startswith('nv-') or user_id.startswith('nv_')):
        try:
            # strip first three chars (nv- or nv_)
            return db.session.get(NhanVien, int(user_id[3:]))
        except (ValueError, TypeError):
            return None

    try:
        return db.session.get(KhachHang, int(user_id))
    except (ValueError, TypeError):
        return None

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
