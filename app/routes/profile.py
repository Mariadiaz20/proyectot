from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, User  # Mantengo tu import original

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        gmail = request.form.get('gmail')
        password = request.form.get('password')

        # Actualizar los datos del usuario
        current_user.name = name
        current_user.email = email
        current_user.gmail = gmail

        # Solo cambia la contraseña si el usuario la ingresó
        if password:
            current_user.password = generate_password_hash(password)

        # Guardar los cambios en la base de datos
        db.session.commit()

        flash('✅ Perfil actualizado correctamente', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile.html')
