import logging as log
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from functools import wraps

# 1. SOLO IMPORTAR DATABASE (NO modelos aún)
from database import db

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mi_base.db' # se 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🚀 CLAVE: Configurar DB ANTES de importar modelos
db.init_app(app)

# 2. AHORA SÍ importar modelo y DAO
from models.usuario import Usuario
from daos.usuario_dao import UsuarioDAO  # ← NUEVO: DAO completo

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, rango=0, nombre="Soldado"):
        self.id = id
        self.rango = rango
        self.nombre = nombre

@login_manager.user_loader
def load_user(user_id):
    log.info(f"load_user llamado para: {user_id}")
    user_db = Usuario.query.get(user_id)
    if user_db:
        return User(user_db.usuario, user_db.rango, user_db.nombre)
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
                flash("Acceso denegado - Rango insuficiente", "error")
                return redirect(url_for('dashboard'))
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

# 🧱 Inicializar DB (CORREGIDO)
@app.route("/init_db")
def init_db_route():
    log.info("→ Inicializando base de datos SQLite")
    db.create_all()
    
    creado = False
    if not Usuario.query.get("soldado"):
        db.session.add(Usuario(usuario="soldado", password="123", rango=1, nombre="Soldado Raso"))
        log.info("✅ Soldado creado")
        creado = True
    
    if not Usuario.query.get("sargento"):
        db.session.add(Usuario(usuario="sargento", password="123", rango=2, nombre="Sargento Primero"))
        log.info("✅ Sargento creado")
        creado = True
    
    if creado:
        db.session.commit()
        log.info("✅ Usuarios iniciales creados")
    else:
        log.info("ℹ️ Usuarios ya existen")
    
    return "Base de datos inicializada. ¡Listo!"

# 🔥 PANEL ADMIN SARGENTO (NUEVO)
@app.route("/admin")
@role_required(2)
def admin():
    usuarios = UsuarioDAO.seleccionar_todos()
    return render_template("admin.html", usuarios=usuarios, total_usuarios=len(usuarios), user=current_user)

@app.route("/admin/crear", methods=["POST"])
@role_required(2)
def admin_crear():
    data = {
        'usuario': request.form['usuario'].lower(),
        'password': request.form['password'],
        'rango': 1,  # Siempre soldado
        'nombre': request.form['nombre']
    }
    resultado = UsuarioDAO.insertar(data)
    flash(f"✅ '{data['nombre']}' reclutado!" if resultado else "❌ Usuario ya existe", "success" if resultado else "error")
    return redirect(url_for("admin"))

@app.route("/admin/actualizar/<usuario>", methods=["POST"])
@role_required(2)
def admin_actualizar(usuario):
    data = {'usuario': usuario, 'password': request.form['password']}
    resultado = UsuarioDAO.actualizar(data)
    flash(f"✅ Contraseña actualizada" if resultado else "❌ Error", "success" if resultado else "error")
    return redirect(url_for("admin"))

@app.route("/admin/eliminar/<usuario>", methods=["POST"])
@role_required(2)
def admin_eliminar(usuario):
    if UsuarioDAO.eliminar(usuario):
        flash(f"✅ '{usuario}' eliminado", "success")
    else:
        flash("❌ No se puede eliminar (rango alto o no existe)", "error")
    return redirect(url_for("admin"))

# RUTAS ORIGINALES (INTACTAS)
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
        
        user_db = Usuario.query.get(username)
        if user_db and user_db.password == password:
            user = User(user_db.usuario, user_db.rango, user_db.nombre)
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
    with app.app_context():
        db.create_all()
        # Crear usuarios si no existen (robusto)
        if not Usuario.query.get("soldado"):
            db.session.add(Usuario(usuario="soldado", password="123", rango=1, nombre="Soldado Raso"))
        if not Usuario.query.get("sargento"):
            db.session.add(Usuario(usuario="sargento", password="123", rango=2, nombre="Sargento Primero"))
        db.session.commit()
    
    log.info("🚀 === MILITECH CORPORATION INICIADO ===")
    log.info("👉 Usuarios: soldado/123, sargento/123")
    log.info("👉 Sargento puede ir a /admin")
    app.run(debug=True, port=5000, host="0.0.0.0", ssl_context="adhoc")

