
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from ..models import db, Product, Address, Order, OrderItem

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/checkout", methods=["GET","POST"])
@login_required
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("Tu carrito está vacío", "warning")
        return redirect(url_for("cart.view_cart"))
    if request.method == "POST":
        addr = Address(user_id=current_user.id,
                       line1=request.form.get("line1"),
                       line2=request.form.get("line2"),
                       city=request.form.get("city"),
                       state=request.form.get("state"),
                       zip_code=request.form.get("zip_code"),
                       country=request.form.get("country","Colombia"))
        db.session.add(addr)
        db.session.flush()
        order = Order(user_id=current_user.id, address_id=addr.id, status="paid")
        db.session.add(order)
        db.session.flush()
        total = 0
        for pid, qty in cart.items():
            product = Product.query.get(int(pid))
            if not product: 
                continue
            qty = int(qty)
            if product.stock < qty:
                flash(f"No hay stock suficiente para {product.name}", "danger")
                return redirect(url_for("cart.view_cart"))
            product.stock -= qty
            line_total = float(product.price) * qty
            total += line_total
            item = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, unit_price=product.price)
            db.session.add(item)
        order.total = total
        db.session.commit()
        session["cart"] = {}
        flash("Pedido realizado con éxito", "success")
        return redirect(url_for("orders.my_orders"))
    return render_template("checkout.html")

@orders_bp.route("/mine")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template("my_orders.html", orders=orders)
