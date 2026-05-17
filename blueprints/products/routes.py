from flask import Blueprint, render_template
from flask_login import current_user, login_required

products_bp = Blueprint('products', __name__)


@products_bp.route('/')
@login_required
def index():
	return render_template('products/index.html', kh=current_user)
