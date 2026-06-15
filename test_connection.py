from app import create_app
from extensions import db
from Model.Models import SanPham, KhachHang, DonHang

app = create_app()

with app.app_context():
    try:
        print("Models load OK:", SanPham, KhachHang, DonHang)
    except Exception as e:
        print(f"❌ Lỗi kết nối: {e}")