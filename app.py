from flask import Flask, render_template, request, redirect, flash, session, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
import time
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tu_clave_secreta_cambiar_en_produccion")

# Configuración para que Flask recargue archivos estáticos
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# ========== CONFIGURACIÓN PARA PYTHONANYWHERE ==========
# DB_CONFIG = {
#     "host": "workaround.mysql.pythonanywhere-services.com",
#     "user": "workaround",
#     "password": "data_B4s3_WA_123",
#     "database": "workaround$workarounddb",
# }
# =======================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "workarounddb",
}


# Función para obtener una conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)


# Funciones de validación de seguridad
def validar_password(password):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad:
    - Mínimo 10 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un símbolo especial
    """
    if len(password) < 10:
        return False, "La contraseña debe tener al menos 10 caracteres"

    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"

    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"

    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        return (
            False,
            "La contraseña debe contener al menos un símbolo especial (!@#$%^&*, etc.)",
        )

    return True, "Contraseña válida"


def validar_nombre(nombre):
    """
    Valida que el nombre contenga solo letras y espacios
    """
    if not nombre or not nombre.strip():
        return False, "El nombre es obligatorio"

    # Permitir letras (incluyendo acentuadas), espacios y apóstrofes
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s']+$", nombre):
        return False, "El nombre solo debe contener letras"

    return True, "Nombre válido"


def validar_telefono(telefono):
    """
    Valida que el teléfono contenga solo números
    """
    if not telefono:
        return True, "Teléfono válido"  # El teléfono es opcional en registro

    # Permitir solo dígitos, espacios, guiones y paréntesis (formato común de teléfonos)
    # Pero validar que contenga al menos un número
    telefono_limpio = re.sub(r"[\s\-\(\)]", "", telefono)

    if not telefono_limpio.isdigit():
        return False, "El teléfono solo debe contener números"

    if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
        return False, "El teléfono debe tener entre 7 y 15 dígitos"

    return True, "Teléfono válido"


def validar_edad(edad):
    """
    Valida que la edad sea un número válido y mayor o igual a 18 años
    """
    try:
        edad_num = int(edad)
        if edad_num < 18:
            return False, "Debes ser mayor de 18 años para registrarte"
        if edad_num > 120:
            return False, "Por favor ingresa una edad válida"
        return True, "Edad válida"
    except (ValueError, TypeError):
        return False, "La edad debe ser un número válido"


def validar_email(email):
    """
    Valida que el email tenga un formato válido con @ y dominio
    """
    if not email or not email.strip():
        return False, "El email es obligatorio"

    email = email.strip()

    # Patrón básico de email: nombre@dominio.extension
    # Permite letras, números, puntos, guiones y guiones bajos antes del @
    # Requiere dominio con al menos un punto y extensión
    patron_email = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(patron_email, email):
        return (
            False,
            "El email debe tener un formato válido (ejemplo: usuario@dominio.com)",
        )

    # Validar que no tenga espacios
    if " " in email:
        return False, "El email no debe contener espacios"

    # Validar que el dominio tenga al menos 2 caracteres después del último punto
    partes = email.split("@")
    if len(partes) != 2:
        return False, "El email debe contener solo un símbolo @"

    dominio = partes[1]
    if "." not in dominio:
        return False, "El email debe tener un dominio válido (ejemplo: gmail.com)"

    return True, "Email válido"


def limpiar_texto(texto):
    """Elimina espacios extras al inicio, final y múltiples espacios intermedios"""
    if texto and isinstance(texto, str):
        return " ".join(texto.split())
    return texto


# Configuración para subida de archivos
# ========== RUTAS PARA PYTHONANYWHERE ==========
# PythonAnywhere usa rutas absolutas desde /home/tu_usuario/
UPLOAD_FOLDER = "/home/workaround/mysite/static/uploads/profile_photos"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Asegúrate de crear la carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("/home/workaround/mysite/static/uploads/company_photos", exist_ok=True)
# ==============================================

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB máximo


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== RUTAS PRINCIPALES ====================


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
        # Soportar tanto JSON como form data
        if request.is_json:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        else:
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
                    redirect_url = "/admin/dashboard" if usuario["rol"] == "admin" else "/"

                    # Si es AJAX, devolver JSON
                    if request.is_json:
                        return jsonify({"success": True, "redirect": redirect_url})
                    else:
                        return redirect(redirect_url)
                else:
                    if request.is_json:
                        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"})
                    else:
                        flash("Usuario o contraseña incorrectos", "error")
                        return redirect("/login")
            else:
                if request.is_json:
                    return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"})
                else:
                    flash("Usuario o contraseña incorrectos", "error")
                    return redirect("/login")

        except Exception as e:
            if request.is_json:
                return jsonify({"success": False, "message": f"Error en la base de datos: {str(e)}"})
            else:
                flash(f"Error en la base de datos: {str(e)}", "error")
                return redirect("/login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Soportar tanto JSON como form data
        if request.is_json:
            data = request.get_json()
            nombre = data.get("nombre", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            telefono = data.get("telefono", "").strip()
            edad = data.get("edad", "")
            tipo = data.get("tipo", "Candidato").strip()
        else:
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            telefono = request.form.get("telefono", "").strip()
            edad = request.form.get("edad", "")
            tipo = request.form.get("tipo", "Candidato").strip()

        # Validar nombre
        nombre_valido, mensaje_nombre = validar_nombre(nombre)
        if not nombre_valido:
            if request.is_json:
                return jsonify({"success": False, "message": mensaje_nombre})
            else:
                flash(mensaje_nombre, "error")
                return redirect("/login")

        # Validar edad
        edad_valido, mensaje_edad = validar_edad(edad)
        if not edad_valido:
            if request.is_json:
                return jsonify({"success": False, "message": mensaje_edad})
            else:
                flash(mensaje_edad, "error")
                return redirect("/login")

        # Validar contraseña
        password_valido, mensaje_password = validar_password(password)
        if not password_valido:
            if request.is_json:
                return jsonify({"success": False, "message": mensaje_password})
            else:
                flash(mensaje_password, "error")
                return redirect("/login")

        # Validar teléfono si se proporciona
        if telefono:
            telefono_valido, mensaje_telefono = validar_telefono(telefono)
            if not telefono_valido:
                if request.is_json:
                    return jsonify({"success": False, "message": mensaje_telefono})
                else:
                    flash(mensaje_telefono, "error")
                    return redirect("/login")

        # Validar email
        email_valido, mensaje_email = validar_email(email)
        if not email_valido:
            if request.is_json:
                return jsonify({"success": False, "message": mensaje_email})
            else:
                flash(mensaje_email, "error")
                return redirect("/login")

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            # Verifica si el email ya existe en usuarios
            cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                conexion.close()
                if request.is_json:
                    return jsonify({"success": False, "message": "El email ya está registrado"})
                else:
                    flash("El email ya está registrado", "error")
                    return redirect("/login")

            # Verifica si el teléfono ya existe en usuarios (solo si se proporcionó)
            if telefono:
                cursor.execute("SELECT * FROM usuarios WHERE Telefono = %s AND Telefono != ''", (telefono,))
                if cursor.fetchone():
                    cursor.close()
                    conexion.close()
                    if request.is_json:
                        return jsonify({"success": False, "message": "El teléfono ya está registrado"})
                    else:
                        flash("El teléfono ya está registrado", "error")
                        return redirect("/login")

            # Inserta el nuevo usuario en la tabla usuarios
            if telefono:
                cursor.execute(
                    "INSERT INTO usuarios (NombreCompleto, Email, Password, Telefono, TipoUsuario) VALUES (%s, %s, %s, %s, %s)",
                    (nombre, email, password, telefono, tipo),
                )
            else:
                cursor.execute(
                    "INSERT INTO usuarios (NombreCompleto, Email, Password, TipoUsuario) VALUES (%s, %s, %s, %s)",
                    (nombre, email, password, tipo),
                )

            # Obtener el ID del usuario recién creado
            usuario_id = cursor.lastrowid

            # Crear perfil inicial con la edad
            cursor.execute(
                """
                INSERT INTO perfiles_usuarios (UsuarioId, NombreCompleto, Email, Telefono, Edad)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (usuario_id, nombre, email, telefono if telefono else "", int(edad)),
            )

            conexion.commit()
            cursor.close()
            conexion.close()

            if request.is_json:
                return jsonify({"success": True, "message": "Registro exitoso! Ahora puedes iniciar sesión"})
            else:
                flash("Registro exitoso! Ahora puedes iniciar sesión", "success")
                return redirect("/login")
        except Exception as e:
            if request.is_json:
                return jsonify({"success": False, "message": f"Error al registrar: {str(e)}"})
            else:
                flash(f"Error al registrar: {str(e)}", "error")
                return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    # Limpiar la sesión
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect("/")


@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("index.html")


@app.route("/myjob")
def myjob():
    if not session.get("logged_in"):
        flash("Debes iniciar sesión para acceder a esta página", "error")
        return redirect("/login")
    return render_template("myjob.html")


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/soon")
def soon():
    return render_template("soon.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ==================== PERFIL DE USUARIO ====================


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

        # Validar campos obligatorios
        edad = data.get("age")
        if not edad:
            return {"success": False, "message": "La edad es obligatoria"}, 400

        # Validar edad
        edad_valido, mensaje_edad = validar_edad(edad)
        if not edad_valido:
            return {"success": False, "message": mensaje_edad}, 400

        # Validar años de experiencia (obligatorio)
        anios_experiencia = data.get("experience")
        if not anios_experiencia:
            return {"success": False, "message": "Los años de experiencia son obligatorios"}, 400

        # Validar que años de experiencia sea un número válido
        anios_exp_str = str(anios_experiencia).strip()
        if not anios_exp_str.replace('-', '').isdigit():
            return {"success": False, "message": "Los años de experiencia deben ser un número válido"}, 400

        # Validar localidad (obligatoria)
        if not localidad or not localidad.strip():
            return {"success": False, "message": "La localidad es obligatoria"}, 400

        # Validar dirección (obligatoria)
        if not direccion or not direccion.strip():
            return {"success": False, "message": "La dirección es obligatoria"}, 400

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


# ==================== EMPRESA ====================


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
                Sitio = %s
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
        company_folder = "/home/workaround/mysite/static/uploads/company_photos"
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


# ==================== VACANTES ====================


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


@app.route("/get_estadisticas_empresa")
def get_estadisticas_empresa():
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

        empresa_id = empresa["Id"]

        # Contar vacantes activas
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM vacantes
            WHERE EmpresaId = %s AND Activa = 1
            """,
            (empresa_id,),
        )
        vacantes_activas = cursor.fetchone()["total"]

        # Contar total de candidatos (aplicaciones únicas)
        cursor.execute(
            """
            SELECT COUNT(DISTINCT a.UsuarioId) as total
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.VacanteId = v.Id
            WHERE v.EmpresaId = %s
            """,
            (empresa_id,),
        )
        total_candidatos = cursor.fetchone()["total"]

        # Contar contrataciones (aplicaciones aceptadas)
        cursor.execute(
            """
            SELECT COUNT(*) as total
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.VacanteId = v.Id
            WHERE v.EmpresaId = %s AND a.Estado = 'Aceptada'
            """,
            (empresa_id,),
        )
        contrataciones = cursor.fetchone()["total"]

        cursor.close()
        conexion.close()

        return {
            "success": True,
            "estadisticas": {
                "vacantes_activas": vacantes_activas,
                "candidatos": total_candidatos,
                "contrataciones": contrataciones,
            },
        }

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


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

        # Si el usuario está logueado, verificar a cuáles vacantes ya aplicó
        vacantes_aplicadas = []
        if session.get("logged_in"):
            cursor.execute(
                "SELECT VacanteId FROM aplicaciones WHERE UsuarioId = %s",
                (session["user_id"],),
            )
            vacantes_aplicadas = [row["VacanteId"] for row in cursor.fetchall()]

        cursor.close()
        conexion.close()

        # Convertir fechas a string y agregar info de aplicación
        for vacante in vacantes:
            if vacante.get("FechaPublicacion"):
                vacante["FechaPublicacion"] = vacante["FechaPublicacion"].strftime(
                    "%Y-%m-%d"
                )
            vacante["yaAplico"] = vacante["Id"] in vacantes_aplicadas

        return {"success": True, "vacantes": vacantes}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# ==================== APLICACIONES/POSTULACIONES ====================


@app.route("/aplicar_vacante", methods=["POST"])
def aplicar_vacante():
    if not session.get("logged_in"):
        return {"success": False, "message": "Debes iniciar sesión para aplicar"}, 401

    try:
        data = request.get_json()
        vacante_id = data.get("vacanteId")

        if not vacante_id:
            return {"success": False, "message": "ID de vacante no proporcionado"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que la vacante existe
        cursor.execute("SELECT * FROM vacantes WHERE Id = %s", (vacante_id,))
        vacante = cursor.fetchone()

        if not vacante:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Vacante no encontrada"}, 404

        # Verificar si ya aplicó a esta vacante
        cursor.execute(
            "SELECT * FROM aplicaciones WHERE UsuarioId = %s AND VacanteId = %s",
            (session["user_id"], vacante_id),
        )
        aplicacion_existente = cursor.fetchone()

        if aplicacion_existente:
            cursor.close()
            conexion.close()
            return {
                "success": False,
                "message": "Ya has aplicado a esta vacante anteriormente",
            }, 400

        # Crear nueva aplicación
        cursor.execute(
            """
            INSERT INTO aplicaciones (UsuarioId, VacanteId, Estado, FechaSolicitud)
            VALUES (%s, %s, 'Pendiente', NOW())
            """,
            (session["user_id"], vacante_id),
        )
        conexion.commit()
        aplicacion_id = cursor.lastrowid

        cursor.close()
        conexion.close()

        return {
            "success": True,
            "message": "¡Aplicación enviada exitosamente!",
            "aplicacion_id": aplicacion_id,
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/get_mis_aplicaciones")
def get_mis_aplicaciones():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener aplicaciones del usuario con información de vacante y empresa
        cursor.execute(
            """
            SELECT
                a.Id as AplicacionId,
                a.FechaSolicitud as FechaAplicacion,
                a.Estado,
                v.Titulo as VacanteTitulo,
                v.Ubicacion,
                v.TipoTrabajo,
                v.SalarioMin,
                v.SalarioMax,
                v.Descripcion,
                e.NombreEmpresa,
                e.LogoEmpresa,
                e.Ciudad as CiudadEmpresa
            FROM aplicaciones a
            INNER JOIN vacantes v ON a.VacanteId = v.Id
            INNER JOIN empresas e ON v.EmpresaId = e.Id
            WHERE a.UsuarioId = %s
            ORDER BY a.FechaSolicitud DESC
            """,
            (session["user_id"],),
        )
        aplicaciones = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Convertir fechas a string y mapear estados
        for aplicacion in aplicaciones:
            if aplicacion.get("FechaAplicacion"):
                aplicacion["FechaAplicacion"] = aplicacion["FechaAplicacion"].strftime(
                    "%Y-%m-%d"
                )

            # Mapear estados de BD a estados del frontend
            estado_map = {
                "Pendiente": "en_espera",
                "En Revision": "en_espera",
                "Entrevista": "en_espera",
                "Aceptada": "aceptado",
                "Rechazada": "rechazado",
            }
            aplicacion["Estado"] = estado_map.get(aplicacion["Estado"], "en_espera")

        return {"success": True, "aplicaciones": aplicaciones}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# ==================== CANDIDATOS (PARA EMPLEADORES) ====================


@app.route("/get_candidatos_vacante/<int:vacante_id>")
def get_candidatos_vacante(vacante_id):
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
            (vacante_id, session["user_id"]),
        )
        vacante = cursor.fetchone()

        if not vacante:
            return {
                "success": False,
                "message": "Vacante no encontrada o no autorizado",
            }, 404

        # Obtener candidatos (aplicaciones) con información del usuario
        cursor.execute(
            """
            SELECT
                a.Id as AplicacionId,
                a.FechaSolicitud as FechaAplicacion,
                a.Estado,
                u.Id as UsuarioId,
                u.NombreCompleto,
                u.Email,
                p.Profesion,
                p.FotoPerfil,
                p.AniosExperiencia,
                p.Habilidades
            FROM aplicaciones a
            INNER JOIN usuarios u ON a.UsuarioId = u.Id
            LEFT JOIN perfiles_usuarios p ON u.Id = p.UsuarioId
            WHERE a.VacanteId = %s
            ORDER BY a.FechaSolicitud DESC
            """,
            (vacante_id,),
        )
        candidatos = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Convertir fechas a string y mapear estados
        for candidato in candidatos:
            if candidato.get("FechaAplicacion"):
                candidato["FechaAplicacion"] = candidato["FechaAplicacion"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Mapear estados
            estado_map = {
                "Pendiente": "en_espera",
                "En Revision": "en_espera",
                "Entrevista": "en_espera",
                "Aceptada": "aceptado",
                "Rechazada": "rechazado",
            }
            candidato["Estado"] = estado_map.get(candidato["Estado"], "en_espera")

        return {"success": True, "candidatos": candidatos, "vacante": vacante}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/get_candidato_detalle/<int:usuario_id>")
def get_candidato_detalle(usuario_id):
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener información del usuario
        cursor.execute(
            "SELECT * FROM usuarios WHERE Id = %s",
            (usuario_id,),
        )
        usuario = cursor.fetchone()

        if not usuario:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Usuario no encontrado"}, 404

        # Obtener perfil completo del candidato (puede no existir)
        cursor.execute(
            """
            SELECT p.*, u.Email, u.NombreCompleto as NombreUsuario
            FROM perfiles_usuarios p
            INNER JOIN usuarios u ON p.UsuarioId = u.Id
            WHERE p.UsuarioId = %s
            """,
            (usuario_id,),
        )
        perfil = cursor.fetchone()

        # Si no existe perfil, crear uno con datos del usuario
        if not perfil:
            perfil = {
                "UsuarioId": usuario["Id"],
                "NombreCompleto": usuario["NombreCompleto"],
                "Email": usuario["Email"],
                "Profesion": "No especificada",
                "Edad": 0,
                "Genero": "No especificado",
                "Telefono": usuario.get("Telefono", "No especificado"),
                "Localidad": "No especificada",
                "Direccion": "No especificada",
                "AniosExperiencia": "0",
                "EmpresaActual": "No especificada",
                "Habilidades": "Sin habilidades especificadas",
                "DescripcionProfesional": "Sin descripción",
                "ProyectosCompletados": 0,
                "ClientesSatisfechos": 0,
                "CalificacionPromedio": 0.00,
                "FotoPerfil": None,
            }

        # Obtener certificaciones del usuario
        cursor.execute(
            """
            SELECT cc.Nombre, cc.Categoria, uc.FechaObtencion, uc.FechaVencimiento, uc.InstitucionEmisora
            FROM usuario_certificaciones uc
            INNER JOIN catalogo_certificaciones cc ON uc.CertificacionId = cc.Id
            WHERE uc.UsuarioId = %s
            ORDER BY uc.FechaObtencion DESC
            """,
            (usuario_id,),
        )
        certificaciones = cursor.fetchall()

        # Obtener experiencias del usuario
        cursor.execute(
            """
            SELECT ce.TipoExperiencia, ce.Categoria, ue.AniosExperiencia
            FROM usuario_experiencias ue
            INNER JOIN catalogo_experiencias ce ON ue.ExperienciaId = ce.Id
            WHERE ue.UsuarioId = %s
            ORDER BY ue.AniosExperiencia DESC
            """,
            (usuario_id,),
        )
        experiencias = cursor.fetchall()

        cursor.close()
        conexion.close()

        return {"success": True, "perfil": perfil, "certificaciones": certificaciones, "experiencias": experiencias}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/actualizar_estado_aplicacion", methods=["POST"])
def actualizar_estado_aplicacion():
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()
        aplicacion_id = data.get("aplicacionId")
        nuevo_estado = data.get("estado")  # 'aceptado', 'rechazado', 'en_espera'

        if not aplicacion_id or not nuevo_estado:
            return {"success": False, "message": "Datos incompletos"}, 400

        # Mapear estados del frontend a estados de BD
        estado_map_inverso = {
            "en_espera": "Pendiente",
            "aceptado": "Aceptada",
            "rechazado": "Rechazada",
        }
        estado_bd = estado_map_inverso.get(nuevo_estado, "Pendiente")

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que la aplicación pertenezca a una vacante de la empresa del usuario
        cursor.execute(
            """
            SELECT a.* FROM aplicaciones a
            INNER JOIN vacantes v ON a.VacanteId = v.Id
            INNER JOIN empresas e ON v.EmpresaId = e.Id
            WHERE a.Id = %s AND e.UsuarioId = %s
            """,
            (aplicacion_id, session["user_id"]),
        )
        aplicacion = cursor.fetchone()

        if not aplicacion:
            cursor.close()
            conexion.close()
            return {
                "success": False,
                "message": "Aplicación no encontrada o no autorizado",
            }, 404

        # Actualizar estado
        cursor.execute(
            "UPDATE aplicaciones SET Estado = %s WHERE Id = %s",
            (estado_bd, aplicacion_id),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {
            "success": True,
            "message": f"Candidato {nuevo_estado} exitosamente",
        }

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# ==================== DASHBOARD ADMIN ====================


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

    cursor.execute("SELECT * FROM catalogo_certificaciones ORDER BY Categoria, Nombre")
    certificaciones = cursor.fetchall()

    cursor.execute("SELECT * FROM catalogo_experiencias ORDER BY Categoria, TipoExperiencia")
    experiencias = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "dashboard.html",
        usuarios=usuarios,
        perfiles=perfiles,
        empresas=empresas,
        vacantes=vacantes,
        postulaciones=postulaciones,
        certificaciones=certificaciones,
        experiencias=experiencias,
    )


# ==================== ENDPOINTS CRUD PARA DASHBOARD ADMIN ====================


# -------------------- USUARIOS --------------------
@app.route("/api/usuario", methods=["POST"])
def create_usuario():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()

        # Obtener y limpiar datos
        nombre = limpiar_texto(data.get("NombreCompleto", ""))
        email = limpiar_texto(data.get("Email", ""))
        password = data.get("Password", "")
        telefono = limpiar_texto(data.get("Telefono", ""))

        # Validar nombre
        nombre_valido, mensaje_nombre = validar_nombre(nombre)
        if not nombre_valido:
            return {"success": False, "message": mensaje_nombre}, 400

        # Validar email
        email_valido, mensaje_email = validar_email(email)
        if not email_valido:
            return {"success": False, "message": mensaje_email}, 400

        # Validar contraseña
        password_valido, mensaje_password = validar_password(password)
        if not password_valido:
            return {"success": False, "message": mensaje_password}, 400

        # Validar teléfono si se proporciona
        if telefono:
            telefono_valido, mensaje_telefono = validar_telefono(telefono)
            if not telefono_valido:
                return {"success": False, "message": mensaje_telefono}, 400

        # Validar TipoUsuario
        tipo_usuario = data.get("TipoUsuario", "Candidato")
        if tipo_usuario not in ["Candidato", "Empleador"]:
            return {"success": False, "message": "Tipo de usuario debe ser 'Candidato' o 'Empleador'"}, 400

        # Validar Activo
        activo = data.get("Activo", 1)
        try:
            activo = int(activo)
            if activo not in [0, 1]:
                return {"success": False, "message": "El campo Activo debe ser 0 o 1"}, 400
        except (ValueError, TypeError):
            return {"success": False, "message": "El campo Activo debe ser un número (0 o 1)"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el email no exista
        cursor.execute("SELECT Id FROM usuarios WHERE Email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return {"success": False, "message": "El email ya está registrado"}, 400

        cursor.execute(
            """
            INSERT INTO usuarios (NombreCompleto, Email, Password, TipoUsuario,
                                  Telefono, FotoPerfil, Documento, Activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                nombre,
                email,
                password,
                tipo_usuario,
                telefono,
                data.get("FotoPerfil"),
                data.get("Documento"),
                activo,
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

        # Obtener y limpiar datos
        nombre = limpiar_texto(data.get("NombreCompleto", ""))
        email = limpiar_texto(data.get("Email", ""))
        password = data.get("Password", "")
        telefono = limpiar_texto(data.get("Telefono", ""))

        # Validar nombre
        nombre_valido, mensaje_nombre = validar_nombre(nombre)
        if not nombre_valido:
            return {"success": False, "message": mensaje_nombre}, 400

        # Validar email
        email_valido, mensaje_email = validar_email(email)
        if not email_valido:
            return {"success": False, "message": mensaje_email}, 400

        # Validar contraseña (solo si no está vacía, permitir no cambiarla)
        if password and password.strip():
            password_valido, mensaje_password = validar_password(password)
            if not password_valido:
                return {"success": False, "message": mensaje_password}, 400

        # Validar teléfono si se proporciona
        if telefono:
            telefono_valido, mensaje_telefono = validar_telefono(telefono)
            if not telefono_valido:
                return {"success": False, "message": mensaje_telefono}, 400

        # Validar TipoUsuario
        tipo_usuario = data.get("TipoUsuario", "Candidato")
        if tipo_usuario not in ["Candidato", "Empleador"]:
            return {"success": False, "message": "Tipo de usuario debe ser 'Candidato' o 'Empleador'"}, 400

        # Validar Activo
        activo = data.get("Activo", 1)
        try:
            activo = int(activo)
            if activo not in [0, 1]:
                return {"success": False, "message": "El campo Activo debe ser 0 o 1"}, 400
        except (ValueError, TypeError):
            return {"success": False, "message": "El campo Activo debe ser un número (0 o 1)"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el email no esté en uso por otro usuario
        cursor.execute(
            "SELECT Id FROM usuarios WHERE Email = %s AND Id != %s",
            (email, id)
        )
        if cursor.fetchone():
            cursor.close()
            conexion.close()
            return {"success": False, "message": "El email ya está en uso por otro usuario"}, 400

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
                nombre,
                email,
                password,
                tipo_usuario,
                telefono,
                data.get("FotoPerfil"),
                data.get("Documento"),
                activo,
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

        # Obtener y limpiar datos
        nombre = limpiar_texto(data.get("NombreCompleto", ""))
        email = limpiar_texto(data.get("Email", ""))
        telefono = limpiar_texto(data.get("Telefono", ""))
        edad = data.get("Edad")

        # Validar nombre
        nombre_valido, mensaje_nombre = validar_nombre(nombre)
        if not nombre_valido:
            return {"success": False, "message": mensaje_nombre}, 400

        # Validar email
        email_valido, mensaje_email = validar_email(email)
        if not email_valido:
            return {"success": False, "message": mensaje_email}, 400

        # Validar edad si se proporciona
        if edad:
            edad_valido, mensaje_edad = validar_edad(edad)
            if not edad_valido:
                return {"success": False, "message": mensaje_edad}, 400

        # Validar teléfono si se proporciona
        if telefono:
            telefono_valido, mensaje_telefono = validar_telefono(telefono)
            if not telefono_valido:
                return {"success": False, "message": mensaje_telefono}, 400

        # Validar AniosExperiencia (solo números)
        anios_exp = data.get("AniosExperiencia")
        if anios_exp:
            anios_exp_str = str(anios_exp).strip()
            if anios_exp_str and not anios_exp_str.replace('-', '').isdigit():
                return {"success": False, "message": "Años de experiencia debe ser un número válido"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el usuario exista y obtener sus datos
        cursor.execute(
            "SELECT Id, Email, Telefono, NombreCompleto FROM usuarios WHERE Id = %s",
            (data.get("UsuarioId"),)
        )
        usuario = cursor.fetchone()
        if not usuario:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "El usuario especificado no existe"}, 400

        # Usar email y teléfono del usuario si no se proporcionaron
        email_perfil = email if email else usuario.get("Email", "")
        telefono_perfil = telefono if telefono else (usuario.get("Telefono", "") or "")
        nombre_perfil = nombre if nombre else usuario.get("NombreCompleto", "")

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
                nombre_perfil,
                limpiar_texto(data.get("Profesion")),
                edad,
                data.get("Genero"),
                email_perfil,
                telefono_perfil,
                limpiar_texto(data.get("Localidad")),
                limpiar_texto(data.get("Direccion")),
                anios_exp,
                limpiar_texto(data.get("EmpresaActual")),
                limpiar_texto(data.get("Habilidades")),
                limpiar_texto(data.get("DescripcionProfesional")),
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

        # Obtener y limpiar datos
        nombre = limpiar_texto(data.get("NombreCompleto", ""))
        email = limpiar_texto(data.get("Email", ""))
        telefono = limpiar_texto(data.get("Telefono", ""))
        edad = data.get("Edad")

        # Validar nombre
        nombre_valido, mensaje_nombre = validar_nombre(nombre)
        if not nombre_valido:
            return {"success": False, "message": mensaje_nombre}, 400

        # Validar email
        email_valido, mensaje_email = validar_email(email)
        if not email_valido:
            return {"success": False, "message": mensaje_email}, 400

        # Validar edad si se proporciona
        if edad:
            edad_valido, mensaje_edad = validar_edad(edad)
            if not edad_valido:
                return {"success": False, "message": mensaje_edad}, 400

        # Validar teléfono si se proporciona
        if telefono:
            telefono_valido, mensaje_telefono = validar_telefono(telefono)
            if not telefono_valido:
                return {"success": False, "message": mensaje_telefono}, 400

        # Validar AniosExperiencia (solo números)
        anios_exp = data.get("AniosExperiencia")
        if anios_exp:
            anios_exp_str = str(anios_exp).strip()
            if anios_exp_str and not anios_exp_str.replace('-', '').isdigit():
                return {"success": False, "message": "Años de experiencia debe ser un número válido"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el usuario exista
        cursor.execute(
            "SELECT Id FROM usuarios WHERE Id = %s",
            (data.get("UsuarioId"),)
        )
        if not cursor.fetchone():
            cursor.close()
            conexion.close()
            return {"success": False, "message": "El usuario especificado no existe"}, 400

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
                nombre,
                limpiar_texto(data.get("Profesion")),
                edad,
                data.get("Genero"),
                email,
                telefono,
                limpiar_texto(data.get("Localidad")),
                limpiar_texto(data.get("Direccion")),
                anios_exp,
                limpiar_texto(data.get("EmpresaActual")),
                limpiar_texto(data.get("Habilidades")),
                limpiar_texto(data.get("DescripcionProfesional")),
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
            (UsuarioId, NombreEmpresa, Descripcion, Industria, Sitio, Direccion, Ciudad, Pais)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.get("UsuarioId"),
                data.get("NombreEmpresa"),
                data.get("Descripcion"),
                data.get("Industria"),
                data.get("Sitio"),
                data.get("Direccion"),
                data.get("Ciudad"),
                data.get("Pais"),
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
                Descripcion = %s,
                Industria = %s,
                Sitio = %s,
                Direccion = %s,
                Ciudad = %s,
                Pais = %s
            WHERE Id = %s
            """,
            (
                data.get("NombreEmpresa"),
                data.get("Descripcion"),
                data.get("Industria"),
                data.get("Sitio"),
                data.get("Direccion"),
                data.get("Ciudad"),
                data.get("Pais"),
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

        # Validar campos obligatorios
        ubicacion = limpiar_texto(data.get("Ubicacion", ""))
        descripcion = limpiar_texto(data.get("Descripcion", ""))
        requisitos = limpiar_texto(data.get("Requisitos", ""))
        responsabilidades = limpiar_texto(data.get("Responsabilidades", ""))

        if not ubicacion:
            return {"success": False, "message": "La ubicación es obligatoria"}, 400
        if not descripcion:
            return {"success": False, "message": "La descripción es obligatoria"}, 400
        if not requisitos:
            return {"success": False, "message": "Los requisitos son obligatorios"}, 400
        if not responsabilidades:
            return {"success": False, "message": "Las responsabilidades son obligatorias"}, 400

        # Validar salarios (solo números)
        salario_min = data.get("SalarioMin")
        salario_max = data.get("SalarioMax")

        if salario_min:
            try:
                salario_min = float(salario_min)
                if salario_min < 0:
                    return {"success": False, "message": "El salario mínimo debe ser un número positivo"}, 400
            except (ValueError, TypeError):
                return {"success": False, "message": "El salario mínimo debe ser un número válido"}, 400

        if salario_max:
            try:
                salario_max = float(salario_max)
                if salario_max < 0:
                    return {"success": False, "message": "El salario máximo debe ser un número positivo"}, 400
            except (ValueError, TypeError):
                return {"success": False, "message": "El salario máximo debe ser un número válido"}, 400

        # Validar Activa (0 o 1)
        activa = data.get("Activa", 1)
        try:
            activa = int(activa)
            if activa not in [0, 1]:
                return {"success": False, "message": "El campo Activa debe ser 0 o 1"}, 400
        except (ValueError, TypeError):
            return {"success": False, "message": "El campo Activa debe ser un número (0 o 1)"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO vacantes
            (EmpresaId, Titulo, Descripcion, Requisitos, Responsabilidades,
             SalarioMin, SalarioMax, Ubicacion, TipoTrabajo, TipoContrato, Experiencia, Activa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.get("EmpresaId"),
                limpiar_texto(data.get("Titulo")),
                descripcion,
                requisitos,
                responsabilidades,
                salario_min,
                salario_max,
                ubicacion,
                data.get("TipoTrabajo"),
                data.get("TipoContrato"),
                data.get("Experiencia"),
                activa,
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

        # Validar campos obligatorios
        ubicacion = limpiar_texto(data.get("Ubicacion", ""))
        descripcion = limpiar_texto(data.get("Descripcion", ""))
        requisitos = limpiar_texto(data.get("Requisitos", ""))
        responsabilidades = limpiar_texto(data.get("Responsabilidades", ""))

        if not ubicacion:
            return {"success": False, "message": "La ubicación es obligatoria"}, 400
        if not descripcion:
            return {"success": False, "message": "La descripción es obligatoria"}, 400
        if not requisitos:
            return {"success": False, "message": "Los requisitos son obligatorios"}, 400
        if not responsabilidades:
            return {"success": False, "message": "Las responsabilidades son obligatorias"}, 400

        # Validar salarios (solo números)
        salario_min = data.get("SalarioMin")
        salario_max = data.get("SalarioMax")

        if salario_min:
            try:
                salario_min = float(salario_min)
                if salario_min < 0:
                    return {"success": False, "message": "El salario mínimo debe ser un número positivo"}, 400
            except (ValueError, TypeError):
                return {"success": False, "message": "El salario mínimo debe ser un número válido"}, 400

        if salario_max:
            try:
                salario_max = float(salario_max)
                if salario_max < 0:
                    return {"success": False, "message": "El salario máximo debe ser un número positivo"}, 400
            except (ValueError, TypeError):
                return {"success": False, "message": "El salario máximo debe ser un número válido"}, 400

        # Validar Activa (0 o 1) si viene en la solicitud
        activa = data.get("Activa")
        if activa is not None:
            try:
                activa = int(activa)
                if activa not in [0, 1]:
                    return {"success": False, "message": "El campo Activa debe ser 0 o 1"}, 400
            except (ValueError, TypeError):
                return {"success": False, "message": "El campo Activa debe ser un número (0 o 1)"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Construir query dinámicamente según si se incluye Activa
        if activa is not None:
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
                    Experiencia = %s,
                    Activa = %s
                WHERE Id = %s
                """,
                (
                    limpiar_texto(data.get("Titulo")),
                    descripcion,
                    requisitos,
                    responsabilidades,
                    salario_min,
                    salario_max,
                    ubicacion,
                    data.get("TipoTrabajo"),
                    data.get("Experiencia"),
                    activa,
                    id,
                ),
            )
        else:
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
                    Experiencia = %s
                WHERE Id = %s
                """,
                (
                    limpiar_texto(data.get("Titulo")),
                    descripcion,
                    requisitos,
                    responsabilidades,
                    salario_min,
                    salario_max,
                    ubicacion,
                    data.get("TipoTrabajo"),
                    data.get("Experiencia"),
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
            (VacanteId, UsuarioId, Estado)
            VALUES (%s, %s, %s)
            """,
            (
                data.get("VacanteId"),
                data.get("UsuarioId"),
                data.get("Estado", "Pendiente"),
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
                VacanteId = %s,
                UsuarioId = %s,
                Estado = %s
            WHERE Id = %s
            """,
            (
                data.get("VacanteId"),
                data.get("UsuarioId"),
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


# -------------------- CATÁLOGO DE CERTIFICACIONES --------------------
@app.route("/api/certificacion", methods=["POST"])
def create_certificacion():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO catalogo_certificaciones
            (Nombre, Categoria, Descripcion, Activa)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.get("Nombre"),
                data.get("Categoria"),
                data.get("Descripcion"),
                data.get("Activa", 1),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Certificación creada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/certificacion/<int:id>", methods=["PUT"])
def update_certificacion(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE catalogo_certificaciones SET
                Nombre = %s,
                Categoria = %s,
                Descripcion = %s,
                Activa = %s
            WHERE Id = %s
            """,
            (
                data.get("Nombre"),
                data.get("Categoria"),
                data.get("Descripcion"),
                data.get("Activa"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Certificación actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/certificacion/<int:id>", methods=["DELETE"])
def delete_certificacion(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM catalogo_certificaciones WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Certificación eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# -------------------- CATÁLOGO DE EXPERIENCIAS --------------------
@app.route("/api/experiencia", methods=["POST"])
def create_experiencia():
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO catalogo_experiencias
            (TipoExperiencia, Categoria, Descripcion, Activa)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data.get("TipoExperiencia"),
                data.get("Categoria"),
                data.get("Descripcion"),
                data.get("Activa", 1),
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Experiencia creada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/experiencia/<int:id>", methods=["PUT"])
def update_experiencia(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        data = request.get_json()
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE catalogo_experiencias SET
                TipoExperiencia = %s,
                Categoria = %s,
                Descripcion = %s,
                Activa = %s
            WHERE Id = %s
            """,
            (
                data.get("TipoExperiencia"),
                data.get("Categoria"),
                data.get("Descripcion"),
                data.get("Activa"),
                id,
            ),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Experiencia actualizada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


@app.route("/api/experiencia/<int:id>", methods=["DELETE"])
def delete_experiencia(id):
    if not session.get("logged_in") or session.get("rol") != "admin":
        return {"success": False, "message": "Acceso denegado"}, 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM catalogo_experiencias WHERE Id = %s", (id,))

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Experiencia eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}, 500


# Desactiva caché en desarrollo
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


# ==================== ENDPOINTS PARA CATÁLOGO DE CERTIFICACIONES ====================


@app.route("/get_catalogo_certificaciones")
def get_catalogo_certificaciones():
    """Obtiene el catálogo completo de certificaciones"""
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM catalogo_certificaciones WHERE Activa = 1 ORDER BY Categoria, Nombre"
        )
        certificaciones = cursor.fetchall()

        cursor.close()
        conexion.close()

        return {"success": True, "certificaciones": certificaciones}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/get_certificaciones_usuario")
def get_certificaciones_usuario():
    """Obtiene las certificaciones del usuario logueado desde la tabla usuario_certificaciones"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Obtener certificaciones del usuario desde la tabla usuario_certificaciones
        cursor.execute(
            """
            SELECT uc.Id, cc.Nombre, cc.Categoria, uc.FechaObtencion, uc.FechaVencimiento, uc.InstitucionEmisora
            FROM usuario_certificaciones uc
            INNER JOIN catalogo_certificaciones cc ON uc.CertificacionId = cc.Id
            WHERE uc.UsuarioId = %s
            ORDER BY uc.FechaObtencion DESC
            """,
            (session["user_id"],),
        )
        certificaciones = cursor.fetchall()

        cursor.close()
        conexion.close()

        return {"success": True, "certificaciones": certificaciones}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/agregar_certificacion_usuario", methods=["POST"])
def agregar_certificacion_usuario():
    """Agrega una certificación del catálogo a la tabla usuario_certificaciones"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()
        certificacion_id = data.get("certificacionId")

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que la certificación exista en el catálogo
        cursor.execute(
            "SELECT Id FROM catalogo_certificaciones WHERE Id = %s AND Activa = 1",
            (certificacion_id,),
        )
        certificacion = cursor.fetchone()

        if not certificacion:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Certificación no encontrada en el catálogo"}, 404

        # Insertar en usuario_certificaciones (el UNIQUE KEY evita duplicados)
        try:
            cursor.execute(
                """
                INSERT INTO usuario_certificaciones (UsuarioId, CertificacionId)
                VALUES (%s, %s)
                """,
                (session["user_id"], certificacion_id),
            )
            conexion.commit()
        except Exception as e:
            cursor.close()
            conexion.close()
            if "Duplicate entry" in str(e):
                return {"success": False, "message": "Esta certificación ya fue agregada"}, 400
            raise e

        cursor.close()
        conexion.close()

        return {"success": True, "message": "Certificación agregada exitosamente"}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/eliminar_certificacion_usuario/<int:id>", methods=["DELETE"])
def eliminar_certificacion_usuario(id):
    """Elimina una certificación de la tabla usuario_certificaciones (id es el Id de usuario_certificaciones)"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Eliminar la certificación del usuario (verificando que sea del usuario logueado)
        cursor.execute(
            "DELETE FROM usuario_certificaciones WHERE Id = %s AND UsuarioId = %s",
            (id, session["user_id"]),
        )

        if cursor.rowcount == 0:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Certificación no encontrada o no tienes permiso para eliminarla"}, 404

        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Certificación eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# ==================== ENDPOINTS PARA EXPERIENCIAS ====================


@app.route("/get_catalogo_experiencias")
def get_catalogo_experiencias():
    """Obtiene el catálogo completo de experiencias"""
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM catalogo_experiencias WHERE Activa = 1 ORDER BY Categoria, TipoExperiencia"
        )
        experiencias = cursor.fetchall()

        cursor.close()
        conexion.close()

        return {"success": True, "experiencias": experiencias}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/get_experiencias_usuario")
def get_experiencias_usuario():
    """Obtiene las experiencias del usuario logueado"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT ue.*, ce.TipoExperiencia, ce.Categoria
            FROM usuario_experiencias ue
            INNER JOIN catalogo_experiencias ce ON ue.ExperienciaId = ce.Id
            WHERE ue.UsuarioId = %s
            ORDER BY ue.FechaAgregado DESC
            """,
            (session["user_id"],),
        )
        experiencias = cursor.fetchall()

        cursor.close()
        conexion.close()

        return {"success": True, "experiencias": experiencias}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/agregar_experiencia_usuario", methods=["POST"])
def agregar_experiencia_usuario():
    """Agrega una experiencia con años al usuario"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        data = request.get_json()
        experiencia_id = data.get("experienciaId")
        anios_experiencia = data.get("aniosExperiencia")

        if not anios_experiencia or int(anios_experiencia) < 0:
            return {"success": False, "message": "Años de experiencia inválidos"}, 400

        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar si ya existe
        cursor.execute(
            "SELECT * FROM usuario_experiencias WHERE UsuarioId = %s AND ExperienciaId = %s",
            (session["user_id"], experiencia_id),
        )
        existe = cursor.fetchone()

        if existe:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Experiencia ya agregada"}, 400

        # Agregar experiencia
        cursor.execute(
            "INSERT INTO usuario_experiencias (UsuarioId, ExperienciaId, AniosExperiencia) VALUES (%s, %s, %s)",
            (session["user_id"], experiencia_id, anios_experiencia),
        )
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Experiencia agregada exitosamente"}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


@app.route("/eliminar_experiencia_usuario/<int:id>", methods=["DELETE"])
def eliminar_experiencia_usuario(id):
    """Elimina una experiencia del usuario"""
    if not session.get("logged_in"):
        return {"success": False, "message": "No autorizado"}, 401

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que la experiencia pertenece al usuario
        cursor.execute(
            "SELECT * FROM usuario_experiencias WHERE Id = %s AND UsuarioId = %s",
            (id, session["user_id"]),
        )
        experiencia = cursor.fetchone()

        if not experiencia:
            cursor.close()
            conexion.close()
            return {"success": False, "message": "Experiencia no encontrada"}, 404

        cursor.execute("DELETE FROM usuario_experiencias WHERE Id = %s", (id,))
        conexion.commit()
        cursor.close()
        conexion.close()

        return {"success": True, "message": "Experiencia eliminada exitosamente"}

    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# ==================== CONFIGURACIÓN FINAL PYTHONANYWHERE ====================
if __name__ == "__main__":
    # Para desarrollo local
    app.run(debug=True, port=5000)

# Para PythonAnywhere, el objeto 'app' será usado directamente por el servidor WSGI
