from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from .models import db

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()  # <--- la instancia de mail

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/tienda_zapatillas'

    # Configuración de correo (ejemplo con Gmail)
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "tunombre@gmail.com"
    app.config["MAIL_PASSWORD"] = "miclave123"  # usa password de aplicación

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Rutas extra (profile)
    from .routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    # Importar modelos
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints principales
    from .routes.auth import auth_bp
    from .routes.public import public_bp
    from .routes.cart import cart_bp
    from .routes.orders import orders_bp
    from .routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        seed_data()

    return app


# -------------------
# Función seed_data
# -------------------
def seed_data():
    from .models import User, Category, Product, db

    # Crear admin si no existe
    if not User.query.filter_by(email="admin@tienda.com").first():
        from . import bcrypt
        admin = User(
            name="Admin",
            email="admin@tienda.com",
            password_hash=bcrypt.generate_password_hash("admin123").decode("utf-8"),
            role="admin"
        )
        db.session.add(admin)

    # Crear categorías si no existen
    if Category.query.count() == 0:
        cats = [
            "Zapatillas para césped artificial",
            "Zapatillas para césped natural.",
            "Zapatillas de fútbol multitacos.",
            "Zapatillas de futbol de toque",
            "Zapatillas de futbol de potencia",
            "Zapatillas de futbol clasicas"
        ]
        categories = [Category(name=c) for c in cats]
        db.session.add_all(categories)
        db.session.flush()
    else:
        categories = Category.query.order_by(Category.id).all()

    # Normalizador de nombres
    def normalize_name(name):
        return name.strip().lower()

    existing_names = {normalize_name(p.name) for p in Product.query.all()}

    sample_products = [
        Product(
            name="New Balance Furon 4.0 Pro FG",
            description="Presenta una horma rediseñada para un ajuste superior y comodidad, con una puntera más baja. Incorpora la tecnología FantomFit para un ajuste ligero y seguro.",
            price=489000,
            stock=20,
            category_id=categories[0].id,
            image_url="https://www.futbolemotion.com/imagesarticulos/236637/750/bota-adidas-f50-elite-fg-turbo-aurora-black-platin-met-0.webp"
        ),
        Product(
            name="Adidas F50 League SG.",
            description="Cuentan con una parte superior de material sintético que busca un ajuste cómodo y una buena sensación con el balón",
            price=340000,
            stock=35,
            category_id=categories[1].id,
            image_url="https://media.foot-store.es/catalog/product/cache/image/1800x/9df78eab33525d08d6e5fb8d27136e95/a/d/adidas_if8819_9_footwear_photography_mirrored_pair_view_white-nw052424.jpg"
        ),
        Product(
            name="Nike Phantom GX 2 Academy",
            description="La parte superior suave y el diseño general buscan proporcionar un ajuste cómodo durante todo el partido",
            price=450000,
            stock=15,
            category_id=categories[2].id,
            image_url="https://images.prodirectsport.com/ProductImages/Main/1019031_Main_1832897.jpg"
        ),
        Product(
            name="Adidas Predator Club Turf",
            description="Cuentan con un ajuste clásico, sistema de amarre de cordones y forro interno textil para mayor comodidad.",
            price=220000,
            stock=10,
            category_id=categories[3].id,
            image_url="https://www.futbolemotion.com/imagesarticulos/248158/540/bota-adidas-predator-league-turf-nino-core-black-grey-four-lucid-red-0.jpg"
        ),
        Product(
            name="Zapatilla nike zoom vapor 16 academy FG/MG",
            description="NikeSkin con chevrones incrustados para un mejor control del balón.",
            price=102990,
            stock=8,
            category_id=categories[4].id,
            image_url="https://www.futbolemotion.com/imagesarticulos/259751/750/bota-nike-zm-vapor-16-pro-fg-verde-0.webp"
        ),
        Product(
            name="Nike Air Zoom Mercurial Superfly IX Elite FG",
            description="Un material suave y flexible unido por un revestimiento fino, que envuelve el pie para un contacto más natural con el balón., para mejorar el contacto y la precisión al golpear el balón.",
            price=250000,
            stock=8,
            category_id=categories[4].id,
            image_url="https://i.pinimg.com/736x/4f/b8/8d/4fb88dbdc92acafd5f584196e8c2aee0.jpg"
        ),
        Product(
            name="2025 Football Shoes Men Soccer Shoes Long Spikes Soccer",
            description="Diseñada para entrenamiento profesional y atletas que buscan máximo rendimiento.",
            price=250000,
            stock=8,
            category_id=categories[4].id,
            image_url="https://http2.mlstatic.com/D_NQ_NP_2X_715249-MCO89897322532_082025-F.webp"
        ),
        Product(
            name="Nike Zoom Mercurial Superfly 9 Elite FG",
            description="Incorpora una unidad Zoom Air articulada en la suela, que se extiende a lo largo de tres cuartas partes del zapato, proporcionando amortiguación y propulsión en cada pisada",
            price=250000,
            stock=8,
            category_id=categories[4].id,
            image_url="https://images.prodirectsport.com/ProductImages/Main/1001459_Main_Thumb_1644581.jpg"
        ),
        Product(
            name="Nike Phantom Luna II LV8 Elite FG Vortex Pack - Green Glow/Black",
            description="La parte superior está hecha con Vaporposite+, una combinación de malla de rejilla con agarre y un material premium para un control óptimo del balón a altas velocidades",
            price=329000,
            stock=8,
            category_id=categories[4].id,
            image_url="https://www.ypsoccer.net/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/n/i/nike-phantom-luna-ii-elite-fg-vortex-pack-green-glow-black-1.jpg"
        )
    ]

    # Solo agrega productos que no existan por nombre normalizado
    to_add = [p for p in sample_products if normalize_name(p.name) not in existing_names]
    if to_add:
        db.session.add_all(to_add)
        db.session.commit()
