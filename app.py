
import logging as log
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from functools import wraps

# 🔧 LOGGING PROFESIONAL
log.basicConfig(
    level=log.INFO,
    format="%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s] %(message)s",
    datefmt="%I:%M:%S %p",
    handlers=[
        log.FileHandler("militech.log"),
        log.StreamHandler()
    ]
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "militech-secret-2026"

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# 🪖 USUARIOS MILITECH (sin hash)
USUARIOS = {
    "soldado": {"password": "123", "rango": 1, "nombre": "Soldado Raso"},
    "sargento": {"password": "123", "rango": 2, "nombre": "Sargento Primero"}
}

class User(UserMixin):
    def __init__(self, id, rango=0, nombre="Soldado"):
        self.id = id
        self.rango = rango
        self.nombre = nombre

@login_manager.user_loader
def load_user(user_id):
    log.info(f"load_user llamado para: {user_id}")
    if user_id in USUARIOS:
        data = USUARIOS[user_id]
        return User(user_id, data["rango"], data["nombre"])
    log.warning(f"Usuario NO encontrado: {user_id}")
    return None

# 🛡️ DECORADOR RANGOS
def role_required(min_rango):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            log.info(f"Chequeo rango {min_rango}+ para {current_user.id} (rango {current_user.rango})")
            if current_user.rango < min_rango:
                log.warning(f"ACCESO DENEGADO a {current_user.id}")
                return "401 - Acceso denegado", 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 📋 WTForms FORMULARIO
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message="Campo requerido"),
        Length(min=3, max=20, message="3-20 caracteres")
    ])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('🔑 AUTENTIFICAR')

# RUTAS
@app.route("/")
def home():
    log.info("→ Página principal")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    log.info("→ Login page")
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        log.info(f"Login intento: {username}")
        
        if username in USUARIOS and USUARIOS[username]["password"] == password:
            user = load_user(username)
            login_user(user)
            log.info(f"✅ LOGIN OK: {user.nombre} (Rango {user.rango})")
            flash(f"¡Bienvenido {user.nombre}!", "success")
            return redirect(url_for("dashboard"))
        else:
            log.warning(f"❌ Login fallido: {username}")
            flash("Usuario o contraseña incorrectos", "error")
    
    return render_template("login.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    log.info(f"→ Dashboard: {current_user.nombre}")
    return render_template("dashboard.html", user=current_user)

@app.route("/soldado")
@role_required(1)
def zona_soldado():
    log.info(f"→ Zona Soldado: {current_user.nombre}")
    return render_template("soldado.html", user=current_user)

@app.route("/sargento")
@role_required(2)
def zona_sargento():
    log.info(f"→ Zona Sargento: {current_user.nombre}")
    return render_template("sargento.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    log.info(f"→ Logout: {current_user.nombre}")
    logout_user()
    flash("Sesión cerrada")
    return redirect(url_for("home"))

if __name__ == "__main__":
    log.info("🚀 === MILITECH CORPORATION INICIADO ===")
    log.info("Usuarios: soldado/123, sargento/123")
    app.run(debug=True, port=5000, host="0.0.0.0", ssl_context="adhoc") # ssl_context crea el candado pero sale como poco segura por que lo hemos autofirmado


