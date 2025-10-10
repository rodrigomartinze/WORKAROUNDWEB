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
                if usuario["Password"] == password:
                    # Guardar información del usuario en la sesión
                    session["user_id"] = usuario["Id"]
                    session["user_name"] = usuario["NombreCompleto"]
                    session["user_email"] = usuario["Email"]
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

            # Verifica si el email ya existe en usuarios
            cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
            if cursor.fetchone():
                flash("El email ya está registrado", "error")
                cursor.close()
                conexion.close()
                return redirect("/login")

            # Inserta el nuevo usuario en la tabla usuarios
            cursor.execute(
                "INSERT INTO usuarios (NombreCompleto, Email, Password) VALUES (%s, %s, %s)",
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

    return render_template("login.html")


@app.route("/logout")
def logout():
    # Limpiar la sesión
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
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

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE Email = %s", (session["user_email"],)
        )
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if not usuario:
            flash("Usuario no encontrado", "error")
            session.clear()
            return redirect("/login")

        # Verificar que el usuario sea un Empleador
        if usuario["TipoUsuario"] != "Empleador":
            flash("Acceso denegado. Esta página es solo para empleadores", "error")
            return redirect("/")

    except Exception as e:
        flash(f"Error al obtener datos: {str(e)}", "error")
        return redirect("/login")

    return render_template("company.html", usuario=usuario)


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


@app.route("/myprofile")
@app.route("/myprofile")
def myprofile():
    if not session.get("logged_in"):
        flash("Debes iniciar sesión para acceder a esta página", "error")
        return redirect("/login")

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener datos del usuario
        cursor.execute("SELECT * FROM usuarios WHERE Id = %s", (session["user_id"],))
        usuario = cursor.fetchone()

        # Obtener o crear perfil
        cursor.execute(
            "SELECT * FROM perfiles_usuarios WHERE UsuarioId = %s",
            (session["user_id"],),
        )
        perfil = cursor.fetchone()

        if not perfil:
            # Crear perfil inicial si no existe
            query_insert = """
                INSERT INTO perfiles_usuarios (UsuarioId, NombreCompleto, Email, Telefono) 
                VALUES (%s, %s, %s, %s)
            """
            telefono = usuario.get("Telefono", "") if usuario.get("Telefono") else ""
            cursor.execute(
                query_insert,
                (
                    session["user_id"],
                    usuario["NombreCompleto"],
                    usuario["Email"],
                    telefono,
                ),
            )
            conexion.commit()

            # Obtener el perfil recién creado
            cursor.execute(
                "SELECT * FROM perfiles_usuarios WHERE UsuarioId = %s",
                (session["user_id"],),
            )
            perfil = cursor.fetchone()

        cursor.close()
        conexion.close()

        return render_template("myprofile.html", perfil=perfil)

    except Exception as e:
        flash(f"Error al cargar perfil: {str(e)}", "error")
        return redirect("/")


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Actualizar perfil
        cursor.execute(
            """
            UPDATE perfiles_usuarios SET
                NombreCompleto = %s,
                Profesion = %s,
                Edad = %s,
                Genero = %s,
                Email = %s,
                Telefono = %s,
                Localidad = %s,
                Direccion = %s,
                AniosExperiencia = %s,
                EmpresaActual = %s,
                Habilidades = %s,
                DescripcionProfesional = %s,
                Certificaciones = %s,
                ProyectosCompletados = %s,
                ClientesSatisfechos = %s,
                CalificacionPromedio = %s
            WHERE UsuarioId = %s
        """,
            (
                data.get("name"),
                data.get("profession"),
                data.get("age"),
                data.get("gender"),
                data.get("email"),
                data.get("phone"),
                data.get("location"),
                data.get("address"),
                data.get("experience"),
                data.get("company"),
                data.get("skills"),
                data.get("bio"),
                data.get("certifications"),
                data.get("projects", 0),
                data.get("clients", 0),
                data.get("rating", 0.0),
                session["user_id"],
            ),
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        # Actualizar sesión
        session["user_name"] = data.get("name")
        session["user_email"] = data.get("email")

        return {"success": True, "message": "Perfil actualizado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
