
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, Product, Category, Order, User
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)

def admin_required(func_view):
    from functools import wraps
    @wraps(func_view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Acceso no autorizado", "danger")
            return redirect(url_for("auth.login"))
        return func_view(*args, **kwargs)
    return wrapper

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    products_count = Product.query.count()
    orders_count = Order.query.count()
    users_count = User.query.count()
    sales_total = db.session.query(func.coalesce(func.sum(Order.total), 0)).scalar()
    last7 = datetime.utcnow() - timedelta(days=6)
    daily = (
        db.session.query(func.date(Order.created_at), func.coalesce(func.sum(Order.total), 0))
        .filter(Order.created_at >= last7)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    return render_template("admin/dashboard.html",
                           products_count=products_count,
                           orders_count=orders_count,
                           users_count=users_count,
                           sales_total=sales_total,
                           daily=daily)

@admin_bp.route("/products")
@login_required
@admin_required
def products_list():
    products = Product.query.order_by(Product.id.desc()).all()
    categories = Category.query.all()
    return render_template("admin/products.html", products=products, categories=categories)

@admin_bp.route("/products/create", methods=["POST"])
@login_required
@admin_required
def products_create():
    p = Product(name=request.form["name"],
                description=request.form.get("description",""),
                price=request.form.get("price", 0),
                stock=int(request.form.get("stock", 0)),
                image_url=request.form.get("image_url"),
                category_id=int(request.form.get("category_id")) if request.form.get("category_id") else None)
    db.session.add(p)
    db.session.commit()
    flash("Producto creado", "success")
    return redirect(url_for("admin.products_list"))

@admin_bp.route("/products/<int:pid>/update", methods=["POST"])
@login_required
@admin_required
def products_update(pid):
    p = Product.query.get_or_404(pid)
    p.name = request.form["name"]
    p.description = request.form.get("description","")
    p.price = request.form.get("price", 0)
    p.stock = int(request.form.get("stock", 0))
    p.image_url = request.form.get("image_url")
    p.category_id = int(request.form.get("category_id")) if request.form.get("category_id") else None
    db.session.commit()
    flash("Producto actualizado", "success")
    return redirect(url_for("admin.products_list"))

@admin_bp.route("/products/<int:pid>/delete", methods=["POST"])
@login_required
@admin_required
def products_delete(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash("Producto eliminado", "info")
    return redirect(url_for("admin.products_list"))

@admin_bp.route("/categories", methods=["GET","POST"])
@login_required
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        if name:
            db.session.add(Category(name=name))
            db.session.commit()
            flash("Categoría creada", "success")
    cats = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=cats)

@admin_bp.route("/orders")
@login_required
@admin_required
def orders_list():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("admin/orders.html", orders=orders)

@admin_bp.route("/orders/<int:oid>/status", methods=["POST"])
@login_required
@admin_required
def orders_status(oid):
    order = Order.query.get_or_404(oid)
    order.status = request.form.get("status", order.status)
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("admin.orders_list"))

@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/report")
@login_required
@admin_required
def report():
    rows = (
        db.session.query(func.date(Order.created_at).label("fecha"),
                         func.coalesce(func.sum(Order.total), 0).label("ventas"))
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    return render_template("admin/report.html", rows=rows)
