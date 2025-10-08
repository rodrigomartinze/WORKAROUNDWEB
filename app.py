from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = (
    "tu_clave_secreta_aqui_cambiar_en_produccion"  # Cambia esto en producción
)

# Configuración para que Flask recargue archivos estáticos
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "workarounddb",
}


# Función para obtener una conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
            usuario = cursor.fetchone()
            cursor.close()
            conexion.close()

            if usuario:
                # Aquí deberías verificar la contraseña (idealmente hasheada)
                # Por ahora verificamos contra el campo telefono (temporal)
                if (
                    usuario["Password"] == password
                ):  # Cambia esto cuando agregues campo password
                    # Guardar información del usuario en la sesión
                    session["user_id"] = usuario["Id"]
                    session["user_name"] = usuario["NombreCompleto"]
                    session["user_emal"] = usuario["Email"]
                    session["logged_in"] = True

                    return redirect("/")
                else:
                    flash("Usuario o contraseña incorrectos", "error")
                    return redirect("/login")
            else:
                flash("Usuario o contraseña incorrectos", "error")
                return redirect("/login")
        except Exception as e:
            flash(f"Error en la base de datos: {str(e)}", "error")
            return redirect("/login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verifica si el email ya existe
            cursor.execute("SELECT * FROM personas WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("El email ya está registrado", "error")
                cursor.close()
                conexion.close()
                return redirect("/login")

            # Inserta el nuevo usuario (temporalmente en campo telefono)
            # Cambia esto cuando agregues el campo password a tu tabla
            cursor.execute(
                "INSERT INTO personas (nombre, email, telefono) VALUES (%s, %s, %s)",
                (nombre, email, password),
            )
            conexion.commit()
            cursor.close()
            conexion.close()

            flash("Registro exitoso! Ahora puedes iniciar sesión", "success")
            return redirect("/login")
        except Exception as e:
            flash(f"Error al registrar: {str(e)}", "error")
            return redirect("/login")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    # Limpiar la sesión
    session.clear()

    return redirect("/")


@app.route("/myjob")
def myjob():
    if not session.get("logged_in"):
        flash("Debes iniciar sesión para acceder a esta página", "error")
        return redirect("/login")
    return render_template("myjob.html")


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/company")
def company():
    if not session.get("logged_in"):
        flash("Debes iniciar sesión para acceder a esta página", "error")
        return redirect("/login")
    return render_template("company.html")


@app.route("/soon")
def soon():
    return render_template("soon.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# Desactiva caché en desarrollo
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
