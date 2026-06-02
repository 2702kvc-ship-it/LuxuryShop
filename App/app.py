"""
app.py
Khởi tạo Flask app, đăng ký extensions và toàn bộ blueprints.
"""

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from config import Config
from extensions import db, login_manager, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Extensions ──
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.dang_nhap'

    # ── Blueprints ──
    from Routers.routes import (
        auth_bp, khachhang_bp, sanpham_bp,
        giohang_bp, donhang_bp, baohang_bp,
        danhgia_bp, admin_bp,
    )

    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(khachhang_bp, url_prefix='/khachhang')
    app.register_blueprint(sanpham_bp,   url_prefix='/sanpham')
    app.register_blueprint(giohang_bp,   url_prefix='/giohang')
    app.register_blueprint(donhang_bp,   url_prefix='/donhang')
    app.register_blueprint(baohang_bp,   url_prefix='/baohang')
    app.register_blueprint(danhgia_bp,   url_prefix='/danhgia')
    app.register_blueprint(admin_bp,     url_prefix='/admin')

    return app


# ── Flask-Login user loader ──
@login_manager.user_loader
def load_user(user_id):
    from models import KhachHang, NhanVien
    if user_id.startswith('nv-'):
        return db.session.get(NhanVien, int(user_id[3:]))
    return db.session.get(KhachHang, int(user_id))


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
