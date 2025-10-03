
from flask import Blueprint, render_template, request
from ..models import db, Product, Category

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def index():
    products = Product.query.order_by(Product.id.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template("index.html", products=products, categories=categories)

@public_bp.route("/catalog")
def catalog():
    category_id = request.args.get("category")
    q = request.args.get("q","").strip()
    query = Product.query
    if category_id:
        query = query.filter(Product.category_id == int(category_id))
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(db.func.lower(Product.name).like(like))
    products = query.order_by(Product.id.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template("catalog.html", products=products, categories=categories, selected_category=category_id, q=q)

@public_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

@public_bp.route("/contact")
def contact():
    return render_template("contact.html")

@public_bp.route("/ayuda")
def ayuda():
    return render_template("ayuda.html")

@public_bp.route("/informacion de la pagina")
def informacion():
    return render_template("informacion.html")

