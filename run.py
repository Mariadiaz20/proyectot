
from app import create_app, db, seed_data

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Crea tablas y datos de ejemplo (incluye admin)."""
    db.create_all()
    seed_data()
    print("Base de datos inicializada.")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)