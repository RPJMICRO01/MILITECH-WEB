from flask import Flask, render_template, url_for, redirect, request
from flask_login import LoginManager, UserMixin, logout_user # administra los logins


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret" # configuramos la clave para la creacion de la cookie 

login_manager = LoginManager(app)


#valores a comprobar para ver si se autentica o no el usuario
user_02 = "user"
password_02 = "password"

class user(UserMixin):

    def __init__(self, id, name, password, is_admin=False):
        self.id = id
        self.name = name
        self.password = password
        self.is_admin = is_admin
    
    #users = [user]

    def get_user(password):
        for user in users:
            if user.password == password:
                return user
        return None

# aqui estamos configurando los datos que se van a pedir, esto es de wtforms, PasswordField, SubmitField
#class LoginForm(FlaskForm):
 #   user = user("user", validators=[DataRequired()])
  #  password = PasswordField("Password", validators=[DataRequired()])
   # submit = SubmitField("Login")

# recuperamos el id
@login_manager.user_loader
def load_user(id):
    return (user, int(id))











#---------------------- RUTAS ---------------

# nuestro primer archivo
@app.route("/")
def home():
    return render_template("index.html")

#para iniciar sesion
@app.route("/login", methods=["GET","POST"]) # configuramos los metodos
def login():
    #if request.method == "POST":
    user = request.form.get("user") # recuperamos los datos de post
    password = request.form.get("password")
   # if current_user.is_authenticated: # se ejecuta esto si ya estamos autenticados
    if user == user_02 and password == password_02: # verificamos que los datos recibidos del formulario llegan bien
        return redirect(url_for("home"))
    else:
        pass

    return render_template("login.html")# la final

#para salir
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index.html"))
