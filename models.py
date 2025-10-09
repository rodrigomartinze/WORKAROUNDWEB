# from flask import Flask, render_template, request, redirect
# import mysql.connector

# # ----------------------------------------------------
# # CONFIGURACIÓN INICIAL
# # ----------------------------------------------------
# app = Flask(__name__)

# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "formulario_db",
# }


# # Función para obtener una conexión a la base de datos
# def obtener_conexion():
#     return mysql.connector.connect(**DB_CONFIG)


# # ----------------------------------------------------
# # RUTA PRINCIPAL
# # ----------------------------------------------------
# @app.route("/")
# def index():
#     conexion = obtener_conexion()
#     cursor = conexion.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM personas")
#     personas = cursor.fetchall()
#     cursor.close()
#     conexion.close()
#     return render_template("index.html", personas=personas)


# # ----------------------------------------------------
# # GUARDAR NUEVO REGISTRO
# # ----------------------------------------------------
# @app.route("/signup", methods=["POST"])
# def guardar():
#     nombre = request.form["nombre"]
#     email = request.form["email"]
#     telefono = request.form["telefono"]

#     conexion = obtener_conexion()
#     cursor = conexion.cursor()
#     cursor.execute(
#         "INSERT INTO personas (nombre, email, telefono) VALUES (%s, %s, %s)",
#         (nombre, email, telefono),
#     )
#     conexion.commit()
#     cursor.close()
#     conexion.close()
#     return redirect("/")


# # ----------------------------------------------------
# # BUSCAR REGISTRO POR ID
# # ----------------------------------------------------
# @app.route("/buscar", methods=["POST"])
# def buscar():
#     id = request.form["id"]

#     conexion = obtener_conexion()
#     cursor = conexion.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM personas WHERE id = %s", (id,))
#     persona = cursor.fetchone()
#     cursor.execute("SELECT * FROM personas")
#     personas = cursor.fetchall()
#     cursor.close()
#     conexion.close()

#     return render_template("index.html", persona=persona, personas=personas)


# # ----------------------------------------------------
# # MODIFICAR REGISTRO EXISTENTE
# # ----------------------------------------------------
# @app.route("/modificar", methods=["POST"])
# def modificar():
#     id = request.form["id"]
#     nombre = request.form["nombre"]
#     email = request.form["email"]
#     telefono = request.form["telefono"]

#     conexion = obtener_conexion()
#     cursor = conexion.cursor()
#     cursor.execute(
#         "UPDATE personas SET nombre=%s, email=%s, telefono=%s WHERE id=%s",
#         (nombre, email, telefono, id),
#     )
#     conexion.commit()
#     cursor.close()
#     conexion.close()
#     return redirect("/")


# # ----------------------------------------------------
# # ELIMINAR REGISTRO
# # ----------------------------------------------------
# @app.route("/eliminar", methods=["POST"])
# def eliminar():
#     id = request.form["id"]

#     conexion = obtener_conexion()
#     cursor = conexion.cursor()
#     cursor.execute("DELETE FROM personas WHERE id=%s", (id,))
#     conexion.commit()
#     cursor.close()
#     conexion.close()
#     return redirect("/")


# # ----------------------------------------------------
# # INICIAR SERVIDOR
# # ----------------------------------------------------
# if __name__ == "__main__":
#     app.run(debug=True)
