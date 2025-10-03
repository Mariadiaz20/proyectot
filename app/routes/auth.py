from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import db, User
from .. import bcrypt, mail
from flask_mail import Message
from flask import url_for

auth_bp = Blueprint("auth", __name__)

# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Bienvenido, {user.name}!", "success")

            # 👇 Redirigir según el rol
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))  
            else:
                return redirect(url_for("public.index"))

        flash("Correo o contraseña incorrectos", "danger")
    return render_template("login.html")

# ---------------- REGISTRO ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")  # 👈 aquí tomamos el rol desde el formulario

        if not name or not email or not password:
            flash("Completa todos los campos", "warning")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Este correo ya está registrado", "warning")
            return render_template("register.html")

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(name=name, email=email, password_hash=pw_hash, role=role)  # 👈 guardamos el rol
        db.session.add(user)
        db.session.commit()

        flash("Registro exitoso. Inicia sesión.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("public.index"))

# ---------------- PERFIL ----------------
@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", current_user.name)
        current_user.email = request.form.get("email", current_user.email)
        db.session.commit()
        flash("Perfil actualizado", "success")
    return render_template("profile.html")

# ---------------- RESET PASSWORD (pedir correo) ----------------
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            msg = Message(
                "Restablecimiento de contraseña",
                sender="soporte@tienda.com",
                recipients=[email]
            )
            # Enlace al formulario para nueva contraseña
            msg.body = f"Para restablecer tu contraseña visita: http://localhost:5000/reset_password_form?email={email}"
            mail.send(msg)
            flash("Se ha enviado un correo con instrucciones para restablecer la contraseña.", "info")
        else:
            flash("No existe una cuenta con ese correo.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("reset_password_request.html")

# ---------------- RESET PASSWORD (formulario nueva contraseña) ----------------
@auth_bp.route("/reset_password_form", methods=["GET", "POST"])
def reset_password_form():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            db.session.commit()
            flash("Tu contraseña ha sido actualizada. Inicia sesión.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Correo no encontrado.", "danger")
    # Pasamos el email si viene desde el enlace del correo
    email = request.args.get("email", "")
    return render_template("reset_password.html", email=email)
# ---------------- EMAIL ----------------
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        subject="Recuperar contraseña",
        sender="soporte@tuapp.com",
        recipients=[user.email]
    )
    msg.body = (
        f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n"
        f"{url_for('auth.reset_token', token=token, _external=True)}\n\n"
        "Si no solicitaste este cambio, ignora este correo."
    )
    msg.charset = 'utf-8'
    mail.send(msg)