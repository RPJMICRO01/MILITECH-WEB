from database import db  # ← SOLO database.py, NO app.py

class Usuario(db.Model):
    __tablename__ = "usuarios"
    usuario = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    rango = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

