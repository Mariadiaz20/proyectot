
from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from ..models import Product

cart_bp = Blueprint("cart", __name__)

def get_cart():
    return session.setdefault("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

@cart_bp.route("/")
def view_cart():
    cart = get_cart()
    items = []
    subtotal = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            line_total = float(product.price) * qty
            subtotal += line_total
            items.append({"product": product, "qty": qty, "line_total": line_total})
    return render_template("cart.html", items=items, subtotal=subtotal)

@cart_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = get_cart()
    qty = int(request.form.get("qty", 1))
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    save_cart(cart)
    flash("Producto agregado al carrito", "success")
    return redirect(url_for("public.product_detail", product_id=product_id))

@cart_bp.route("/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash("Producto eliminado del carrito", "info")
    return redirect(url_for("cart.view_cart"))

@cart_bp.route("/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = get_cart()
    qty = max(0, int(request.form.get("qty", 1)))
    if qty == 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    save_cart(cart)
    return redirect(url_for("cart.view_cart"))
