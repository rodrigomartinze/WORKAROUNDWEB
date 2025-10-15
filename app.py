from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import os
from werkzeug.utils import secure_filename
import time

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


# Context processor para hacer variables disponibles en todas las plantillas
@app.context_processor
def inject_user_profile():
    perfil = None
    if session.get("logged_in"):
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM perfiles_usuarios WHERE UsuarioId = %s",
                (session["user_id"],),
            )
            perfil = cursor.fetchone()
            cursor.close()
            conexion.close()
        except:
            perfil = None

    return dict(perfil=perfil)


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
                # 🔹 Primero verificamos la contraseña
                if usuario["Password"] == password:
                    # Guardar información en sesión
                    session["user_id"] = usuario["Id"]
                    session["user_name"] = usuario["NombreCompleto"]
                    session["user_email"] = usuario["Email"]
                    session["rol"] = usuario["rol"]
                    session["logged_in"] = True

                    # 🔹 Ahora decidimos según el rol
                    if usuario["rol"] == "admin":
                        return redirect("/admin/dashboard")
                    else:
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


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("logged_in") or session.get("rol") != "admin":
        flash("Acceso denegado", "error")
        return redirect("/login")

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM perfiles_usuarios")
    perfiles = cursor.fetchall()

    cursor.execute("SELECT * FROM empresas")
    empresas = cursor.fetchall()

    cursor.execute("SELECT * FROM vacantes")
    vacantes = cursor.fetchall()

    cursor.execute("SELECT * FROM aplicaciones")
    postulaciones = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "dashboard.html",
        usuarios=usuarios,
        perfiles=perfiles,
        empresas=empresas,
        vacantes=vacantes,
        postulaciones=postulaciones,
    )


@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("index.html")


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


@app.route("/company", methods=["GET", "POST"])
def company():
    if not session.get("logged_in"):
        flash("Debes iniciar sesión para acceder a esta página", "error")
        return redirect("/login")

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener datos del usuario actual
        cursor.execute(
            "SELECT * FROM usuarios WHERE Email = %s", (session["user_email"],)
        )
        usuario = cursor.fetchone()

        if not usuario:
            flash("Usuario no encontrado", "error")
            session.clear()
            return redirect("/login")

        # Verificar tipo de usuario
        if usuario["TipoUsuario"] != "Empleador":
            flash("Acceso denegado. Esta página es solo para empleadores", "error")
            return redirect("/")

        # Buscar empresa asociada
        cursor.execute("SELECT * FROM empresas WHERE UsuarioId = %s", (usuario["Id"],))
        empresa = cursor.fetchone()

        # Si envía formulario (crear empresa)
        if request.method == "POST" and not empresa:
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()
            industria = request.form.get("industria", "").strip()
            direccion = request.form.get("direccion", "").strip()
            ciudad = request.form.get("ciudad", "").strip()
            pais = request.form.get("pais", "").strip()
            sitio = request.form.get("sitio", "").strip()

            # Validar campos obligatorios
            if not nombre:
                flash("El nombre de la empresa es obligatorio", "error")
                cursor.close()
                conexion.close()
                return redirect("/company")

            cursor.execute(
                """
                INSERT INTO empresas 
                (UsuarioId, NombreEmpresa, Descripcion, Industria, Direccion, Ciudad, Pais, Sitio, FechaCreacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    usuario["Id"],
                    nombre,
                    descripcion,
                    industria,
                    direccion,
                    ciudad,
                    pais,
                    sitio,
                ),
            )
            conexion.commit()

            flash("Empresa creada exitosamente", "success")
            cursor.close()
            conexion.close()
            return redirect("/company")

        cursor.close()
        conexion.close()

        # Renderizar HTML con empresa (si existe) o formulario (si no)
        return render_template("company.html", usuario=usuario, empresa=empresa)

    except Exception as e:
        flash(f"Error al obtener datos: {str(e)}", "error")
        return redirect("/login")


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


def limpiar_texto(texto):
    """Elimina espacios extras al inicio, final y múltiples espacios intermedios"""
    if texto and isinstance(texto, str):
        return " ".join(texto.split())
    return texto


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()

        # Limpiar todos los campos de texto
        nombre = limpiar_texto(data.get("name"))
        profesion = limpiar_texto(data.get("profession"))
        email = limpiar_texto(data.get("email"))
        telefono = limpiar_texto(data.get("phone"))
        localidad = limpiar_texto(data.get("location"))
        direccion = limpiar_texto(data.get("address"))
        empresa = limpiar_texto(data.get("company"))
        habilidades = limpiar_texto(data.get("skills"))
        bio = limpiar_texto(data.get("bio"))
        certificaciones = limpiar_texto(data.get("certifications"))

        conexion = obtener_conexion()
        cursor = conexion.cursor()

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
                nombre,
                profesion,
                data.get("age"),
                data.get("gender"),
                email,
                telefono,
                localidad,
                direccion,
                data.get("experience"),
                empresa,
                habilidades,
                bio,
                certificaciones,
                data.get("projects", 0),
                data.get("clients", 0),
                data.get("rating", 0.0),
                session["user_id"],
            ),
        )

        # Actualizar tabla usuarios también
        cursor.execute(
            """
            UPDATE usuarios SET
                Email = %s,
                NombreCompleto = %s,
                Telefono = %s
            WHERE Id = %s
            """,
            (email, nombre, telefono, session["user_id"]),
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        # Actualizar sesión
        session["user_name"] = nombre
        session["user_email"] = email

        return {"success": True, "message": "Perfil actualizado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# Configuración para subida de archivos
UPLOAD_FOLDER = "static/uploads/profile_photos"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Asegúrate de crear la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB máximo


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_profile_photo", methods=["POST"])
def upload_profile_photo():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    if "photo" not in request.files:
        return {"success": False, "message": "No se envió ninguna foto"}, 400

    file = request.files["photo"]

    if file.filename == "":
        return {"success": False, "message": "No se seleccionó ningún archivo"}, 400

    if not allowed_file(file.filename):
        return {"success": False, "message": "Formato de archivo no permitido"}, 400

    try:
        # Generar nombre único para el archivo
        filename = secure_filename(file.filename)
        unique_filename = f"{session['user_id']}_{int(time.time())}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

        # Guardar archivo
        file.save(filepath)

        # URL para acceder a la foto
        photo_url = f"/static/uploads/profile_photos/{unique_filename}"

        # Actualizar base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE perfiles_usuarios SET FotoPerfil = %s WHERE UsuarioId = %s",
            (photo_url, session["user_id"]),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {
            "success": True,
            "photo_url": photo_url,
            "message": "Foto actualizada exitosamente",
        }

    except Exception as e:
        return {"success": False, "message": f"Error al subir la foto: {str(e)}"}, 500


@app.route("/get_profile_photo")
def get_profile_photo():
    if not session.get("logged_in"):
        return {"success": False}

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT FotoPerfil FROM perfiles_usuarios WHERE UsuarioId = %s",
            (session["user_id"],),
        )
        perfil = cursor.fetchone()
        cursor.close()
        conexion.close()

        if perfil and perfil.get("FotoPerfil"):
            return {"success": True, "photo_url": perfil["FotoPerfil"]}
        else:
            return {"success": False}

    except Exception as e:
        return {"success": False, "message": str(e)}


@app.route("/upload_company_photo", methods=["POST"])
def upload_company_photo():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    if "photo" not in request.files:
        return {"success": False, "message": "No se envió ninguna foto"}, 400

    file = request.files["photo"]

    if file.filename == "":
        return {"success": False, "message": "No se seleccionó ningún archivo"}, 400

    if not allowed_file(file.filename):
        return {"success": False, "message": "Formato de archivo no permitido"}, 400

    try:
        # Verificar que el usuario tenga una empresa
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM empresas WHERE UsuarioId = %s", (session["user_id"],)
        )
        empresa = cursor.fetchone()

        if not empresa:
            cursor.close()
            conexion.close()
            return {
                "success": False,
                "message": "No tienes una empresa registrada",
            }, 404

        # Generar nombre único para el archivo
        filename = secure_filename(file.filename)
        unique_filename = f"company_{empresa['Id']}_{int(time.time())}_{filename}"

        # Crear carpeta si no existe
        company_folder = os.path.join(app.config["UPLOAD_FOLDER"], "../company_photos")
        os.makedirs(company_folder, exist_ok=True)

        filepath = os.path.join(company_folder, unique_filename)

        # Guardar archivo
        file.save(filepath)

        # URL para acceder a la foto
        photo_url = f"/static/uploads/company_photos/{unique_filename}"

        # Actualizar base de datos
        cursor.execute(
            "UPDATE empresas SET LogoEmpresa = %s WHERE Id = %s",
            (photo_url, empresa["Id"]),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {
            "success": True,
            "photo_url": photo_url,
            "message": "Logo actualizado exitosamente",
        }

    except Exception as e:
        return {"success": False, "message": f"Error al subir el logo: {str(e)}"}, 500


@app.route("/get_company_photo")
def get_company_photo():
    if not session.get("logged_in"):
        return {"success": False}

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT LogoEmpresa FROM empresas WHERE UsuarioId = %s",
            (session["user_id"],),
        )
        empresa = cursor.fetchone()
        cursor.close()
        conexion.close()

        if empresa and empresa.get("LogoEmpresa"):
            return {"success": True, "photo_url": empresa["LogoEmpresa"]}
        else:
            return {"success": False}

    except Exception as e:
        return {"success": False, "message": str(e)}


@app.route("/update_company", methods=["POST"])
def update_company():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()

        # Limpiar todos los campos de texto
        nombre = limpiar_texto(data.get("nombre"))
        descripcion = limpiar_texto(data.get("descripcion"))
        industria = limpiar_texto(data.get("industria"))
        direccion = limpiar_texto(data.get("direccion"))
        ciudad = limpiar_texto(data.get("ciudad"))
        pais = limpiar_texto(data.get("pais"))
        sitio = limpiar_texto(data.get("sitio"))

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE empresas SET
                NombreEmpresa = %s,
                Descripcion = %s,
                Industria = %s,
                Direccion = %s,
                Ciudad = %s,
                Pais = %s,
                SitioWeb = %s
            WHERE UsuarioId = %s
        """,
            (
                nombre,
                descripcion,
                industria,
                direccion,
                ciudad,
                pais,
                sitio,
                session["user_id"],
            ),
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Empresa actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# Crear la carpeta de fotos de empresa si no existe
os.makedirs("static/uploads/company_photos", exist_ok=True)


@app.route("/crear_vacante", methods=["POST"])
def crear_vacante():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()

        # Verificar que el usuario tenga una empresa
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM empresas WHERE UsuarioId = %s", (session["user_id"],)
        )
        empresa = cursor.fetchone()

        if not empresa:
            cursor.close()
            conexion.close()
            return {
                "success": False,
                "message": "No tienes una empresa registrada",
            }, 404

        # Limpiar datos
        titulo = limpiar_texto(data.get("titulo"))
        descripcion = limpiar_texto(data.get("descripcion"))
        requisitos = limpiar_texto(data.get("requisitos"))
        responsabilidades = limpiar_texto(data.get("responsabilidades"))
        salario_min = data.get("salarioMin")
        salario_max = data.get("salarioMax")
        ubicacion = limpiar_texto(data.get("ubicacion"))
        tipo_trabajo = data.get("tipoTrabajo")
        tipo_contrato = data.get("tipoContrato")
        experiencia = data.get("experiencia")

        # Insertar vacante
        cursor.execute(
            """
            INSERT INTO vacantes 
            (EmpresaId, Titulo, Descripcion, Requisitos, Responsabilidades, 
             SalarioMin, SalarioMax, Ubicacion, TipoTrabajo, TipoContrato, 
             Experiencia, FechaPublicacion, Activa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
            """,
            (
                empresa["Id"],
                titulo,
                descripcion,
                requisitos,
                responsabilidades,
                salario_min,
                salario_max,
                ubicacion,
                tipo_trabajo,
                tipo_contrato,
                experiencia,
            ),
        )
        conexion.commit()
        vacante_id = cursor.lastrowid
        cursor.close()
        conexion.close()

        return {
            "success": True,
            "message": "Vacante creada exitosamente",
            "vacante_id": vacante_id,
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/get_vacantes_empresa")
def get_vacantes_empresa():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener empresa del usuario
        cursor.execute(
            "SELECT Id FROM empresas WHERE UsuarioId = %s", (session["user_id"],)
        )
        empresa = cursor.fetchone()

        if not empresa:
            return {"success": False, "message": "No tienes una empresa registrada"}

        # Obtener vacantes de la empresa
        cursor.execute(
            """
            SELECT * FROM vacantes 
            WHERE EmpresaId = %s 
            ORDER BY FechaPublicacion DESC
            """,
            (empresa["Id"],),
        )
        vacantes = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Convertir fechas a string
        for vacante in vacantes:
            if vacante.get("FechaPublicacion"):
                vacante["FechaPublicacion"] = vacante["FechaPublicacion"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if vacante.get("FechaCierre"):
                vacante["FechaCierre"] = vacante["FechaCierre"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        return {"success": True, "vacantes": vacantes}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/update_vacante", methods=["POST"])
def update_vacante():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()
        vacante_id = data.get("id")

        # Verificar que la vacante pertenezca a la empresa del usuario
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT v.* FROM vacantes v
            INNER JOIN empresas e ON v.EmpresaId = e.Id
            WHERE v.Id = %s AND e.UsuarioId = %s
            """,
            (vacante_id, session["user_id"]),
        )
        vacante = cursor.fetchone()

        if not vacante:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Vacante no encontrada"}, 404

        # Actualizar vacante
        cursor.execute(
            """
            UPDATE vacantes SET
                Titulo = %s,
                Descripcion = %s,
                Requisitos = %s,
                Responsabilidades = %s,
                SalarioMin = %s,
                SalarioMax = %s,
                Ubicacion = %s,
                TipoTrabajo = %s,
                TipoContrato = %s,
                Experiencia = %s,
                Activa = %s
            WHERE Id = %s
            """,
            (
                limpiar_texto(data.get("titulo")),
                limpiar_texto(data.get("descripcion")),
                limpiar_texto(data.get("requisitos")),
                limpiar_texto(data.get("responsabilidades")),
                data.get("salarioMin"),
                data.get("salarioMax"),
                limpiar_texto(data.get("ubicacion")),
                data.get("tipoTrabajo"),
                data.get("tipoContrato"),
                data.get("experiencia"),
                data.get("activa", 1),
                vacante_id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Vacante actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/delete_vacante/<int:id>", methods=["DELETE"])
def delete_vacante(id):
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que la vacante pertenezca a la empresa del usuario
        cursor.execute(
            """
            SELECT v.* FROM vacantes v
            INNER JOIN empresas e ON v.EmpresaId = e.Id
            WHERE v.Id = %s AND e.UsuarioId = %s
            """,
            (id, session["user_id"]),
        )
        vacante = cursor.fetchone()

        if not vacante:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Vacante no encontrada"}, 404

        cursor.execute("DELETE FROM vacantes WHERE Id = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Vacante eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/get_all_vacantes")
def get_all_vacantes():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener vacantes activas con información de la empresa
        cursor.execute(
            """
            SELECT v.*, e.NombreEmpresa, e.LogoEmpresa, e.Ciudad as CiudadEmpresa
            FROM vacantes v
            INNER JOIN empresas e ON v.EmpresaId = e.Id
            WHERE v.Activa = 1
            ORDER BY v.FechaPublicacion DESC
            LIMIT 50
            """
        )
        vacantes = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Convertir fechas a string
        for vacante in vacantes:
            if vacante.get("FechaPublicacion"):
                vacante["FechaPublicacion"] = vacante["FechaPublicacion"].strftime(
                    "%Y-%m-%d"
                )

        return {"success": True, "vacantes": vacantes}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# ==================== ENDPOINTS CRUD PARA DASHBOARD ADMIN ====================


# -------------------- USUARIOS --------------------
@app.route("/api/usuario", methods=["POST"])
def create_usuario():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (NombreCompleto, Email, Password, TipoUsuario,
                                  Telefono, FotoPerfil, Documento, Activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.get("NombreCompleto"),
                data.get("Email"),
                data.get("Password"),
                data.get("TipoUsuario", "freelancer"),
                data.get("Telefono"),
                data.get("FotoPerfil"),
                data.get("Documento"),
                data.get("Activo", 1),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Usuario creado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/usuario/<int:id>", methods=["PUT"])
def update_usuario(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE usuarios SET
                NombreCompleto = %s,
                Email = %s,
                Password = %s,
                TipoUsuario = %s,
                Telefono = %s,
                FotoPerfil = %s,
                Documento = %s,
                Activo = %s
            WHERE Id = %s
            """,
            (
                data.get("NombreCompleto"),
                data.get("Email"),
                data.get("Password"),
                data.get("TipoUsuario"),
                data.get("Telefono"),
                data.get("FotoPerfil"),
                data.get("Documento"),
                data.get("Activo"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Usuario actualizado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/usuario/<int:id>", methods=["DELETE"])
def delete_usuario(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Eliminar primero los registros relacionados
        cursor.execute("DELETE FROM perfiles_usuarios WHERE UsuarioId = %s", (id,))
        cursor.execute("DELETE FROM empresas WHERE UsuarioId = %s", (id,))
        cursor.execute("DELETE FROM usuarios WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Usuario eliminado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# -------------------- PERFILES --------------------
@app.route("/api/perfil", methods=["POST"])
def create_perfil():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO perfiles_usuarios
            (UsuarioId, NombreCompleto, Profesion, Edad, Genero, Email, Telefono,
             Localidad, Direccion, AniosExperiencia, EmpresaActual, Habilidades,
             DescripcionProfesional)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.get("UsuarioId"),
                data.get("NombreCompleto"),
                data.get("Profesion"),
                data.get("Edad"),
                data.get("Genero"),
                data.get("Email"),
                data.get("Telefono"),
                data.get("Localidad"),
                data.get("Direccion"),
                data.get("AniosExperiencia"),
                data.get("EmpresaActual"),
                data.get("Habilidades"),
                data.get("DescripcionProfesional"),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Perfil creado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/perfil/<int:id>", methods=["PUT"])
def update_perfil_admin(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE perfiles_usuarios SET
                UsuarioId = %s,
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
                DescripcionProfesional = %s
            WHERE Id = %s
            """,
            (
                data.get("UsuarioId"),
                data.get("NombreCompleto"),
                data.get("Profesion"),
                data.get("Edad"),
                data.get("Genero"),
                data.get("Email"),
                data.get("Telefono"),
                data.get("Localidad"),
                data.get("Direccion"),
                data.get("AniosExperiencia"),
                data.get("EmpresaActual"),
                data.get("Habilidades"),
                data.get("DescripcionProfesional"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Perfil actualizado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/perfil/<int:id>", methods=["DELETE"])
def delete_perfil(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM perfiles_usuarios WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Perfil eliminado exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# -------------------- EMPRESAS --------------------
@app.route("/api/empresa", methods=["POST"])
def create_empresa():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO empresas
            (NombreEmpresa, Email, Telefono, Direccion, Descripcion)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data.get("Nombre"),
                data.get("Email"),
                data.get("Telefono"),
                data.get("Direccion"),
                data.get("Descripcion"),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Empresa creada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/empresa/<int:id>", methods=["PUT"])
def update_empresa_admin(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE empresas SET
                NombreEmpresa = %s,
                Email = %s,
                Telefono = %s,
                Direccion = %s,
                Descripcion = %s
            WHERE Id = %s
            """,
            (
                data.get("Nombre"),
                data.get("Email"),
                data.get("Telefono"),
                data.get("Direccion"),
                data.get("Descripcion"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Empresa actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/empresa/<int:id>", methods=["DELETE"])
def delete_empresa(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Eliminar vacantes relacionadas primero
        cursor.execute("DELETE FROM vacantes WHERE EmpresaId = %s", (id,))
        cursor.execute("DELETE FROM empresas WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Empresa eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# -------------------- VACANTES (ADMIN) --------------------
@app.route("/api/vacante", methods=["POST"])
def create_vacante_admin():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Para el dashboard admin, necesitamos obtener o crear empresa primero
        # Por simplicidad, permitiremos crear vacantes sin empresa asociada
        cursor.execute(
            """
            INSERT INTO vacantes
            (Titulo, Empresa, Ubicacion, Descripcion, Salario, TipoContrato, FechaPublicacion, Activa)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), 1)
            """,
            (
                data.get("Titulo"),
                data.get("Empresa"),
                data.get("Ubicacion"),
                data.get("Descripcion"),
                data.get("Salario"),
                data.get("TipoContrato"),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Vacante creada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/vacante/<int:id>", methods=["PUT"])
def update_vacante_admin(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE vacantes SET
                Titulo = %s,
                Empresa = %s,
                Ubicacion = %s,
                Descripcion = %s,
                Salario = %s,
                TipoContrato = %s
            WHERE Id = %s
            """,
            (
                data.get("Titulo"),
                data.get("Empresa"),
                data.get("Ubicacion"),
                data.get("Descripcion"),
                data.get("Salario"),
                data.get("TipoContrato"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Vacante actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/vacante/<int:id>", methods=["DELETE"])
def delete_vacante_admin(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Eliminar aplicaciones relacionadas primero
        cursor.execute("DELETE FROM aplicaciones WHERE VacanteId = %s", (id,))
        cursor.execute("DELETE FROM vacantes WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Vacante eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# -------------------- POSTULACIONES --------------------
@app.route("/api/postulacion", methods=["POST"])
def create_postulacion():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO aplicaciones
            (Usuario, Vacante, Estado, Fecha)
            VALUES (%s, %s, %s, NOW())
            """,
            (
                data.get("Usuario"),
                data.get("Vacante"),
                data.get("Estado", "pendiente"),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Postulación creada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/postulacion/<int:id>", methods=["PUT"])
def update_postulacion(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE aplicaciones SET
                Usuario = %s,
                Vacante = %s,
                Estado = %s
            WHERE Id = %s
            """,
            (
                data.get("Usuario"),
                data.get("Vacante"),
                data.get("Estado"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Postulación actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/postulacion/<int:id>", methods=["DELETE"])
def delete_postulacion(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM aplicaciones WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Postulación eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
