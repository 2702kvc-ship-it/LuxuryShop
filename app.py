from flask import Flask, redirect, url_for
import click

# Load environment variables from .env (if present) early so config.py picks them up
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

if __package__:
    from .config import Config
    from .extensions import db, login_manager, mail
else:
    from config import Config
    from extensions import db, login_manager, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))

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
        try:
            from .models import KhachHang
        except ImportError:
            from models import KhachHang

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

    return app

# Cho Flask-Login biết cách load user từ DB
@login_manager.user_loader
def load_user(user_id):
    if __package__:
        from .models import KhachHang, NhanVien
    else:
        from models import KhachHang, NhanVien

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