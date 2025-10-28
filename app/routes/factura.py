# ...existing code...
from io import BytesIO
from flask import send_file, abort
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Añade estas importaciones
from flask import Blueprint  # Importa Blueprint de Flask
from flask_login import login_required, current_user
from .orders import orders_bp                # importa el blueprint definido en orders.py
from ..models import Order, OrderItem 

orders_invoice_bp = Blueprint("orders_invoice", __name__)

@orders_invoice_bp.route("/invoice/<int:order_id>")
@login_required
def invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and getattr(current_user, "role", "") != "admin":
        abort(403)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 50, "Factura - Tienda Zapatillas")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, f"Factura ID: {order.id}")
    c.drawString(300, height - 70, f"Fecha: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(40, height - 95, f"Cliente: {order.user.name if order.user else ''}")
    c.drawString(40, height - 110, f"Email: {order.user.email if order.user else ''}")

    y = height - 140
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Producto")
    c.drawString(330, y, "Cantidad")
    c.drawString(400, y, "Precio")
    c.drawString(470, y, "Total")
    c.setFont("Helvetica", 10)
    y -= 15

    items = OrderItem.query.filter_by(order_id=order.id).all()
    subtotal = 0
    for it in items:
        prod_name = getattr(it, "product").name if getattr(it, "product", None) else "Producto"
        qty = getattr(it, "quantity", getattr(it, "qty", 1))
        price = getattr(it, "unit_price", getattr(it, "price", 0))
        total_line = qty * price
        subtotal += total_line

        c.drawString(40, y, prod_name[:40])
        c.drawString(330, y, str(qty))
        c.drawString(400, y, f"${price}")
        c.drawString(470, y, f"${total_line}")
        y -= 15
        if y < 80:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "Subtotal:")
    c.drawString(470, y, f"${subtotal}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"factura_{order.id}.pdf",
        mimetype="application/pdf"
    )
# ...existing code...