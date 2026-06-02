from flask import Flask, redirect, url_for
import click

# Load environment variables from .env (if present) early so config.py picks them up
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

if __package__:
    from ..config import Config
    from ..extensions import db, login_manager, mail
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
        from ..blueprints.products.routes import products_bp
        from ..blueprints.auth.routes import auth_bp
    else:
        from blueprints.products.routes import products_bp
        from blueprints.auth.routes import auth_bp

    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.cli.command('confirm-user')
    @click.argument('email')
    def confirm_user(email):
        """Mark a pending customer account as confirmed."""
        try:
            from ..models import KhachHang
        except ImportError:
            from models import KhachHang

        kh = KhachHang.query.filter_by(Email=email.strip().lower()).first()
        if not kh:
            click.echo(f'Khong tim thay tai khoan voi email: {email}')
            return

        kh.HangThanhVien = 'Standard'
        db.session.commit()
        click.echo(f'Da kich hoat tai khoan: {kh.Email}')

    return app

# Cho Flask-Login biết cách load user từ DB
@login_manager.user_loader
def load_user(user_id):
    if __package__:
        from ..models import KhachHang
    else:
        from models import KhachHang
    return db.session.get(KhachHang, int(user_id))

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)