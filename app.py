from flask import Flask, render_template, request, jsonify, make_response
import mysql.connector
import pusher

# Conexión a la base de datos para reservas
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_tst0_reservas",
    password="dJ0CIAFF="
)

app = Flask(__name__)

# Página principal que carga el CRUD de reservas
@app.route("/")
def index():
    return render_template("app.html")

# Crear o actualizar una reserva
@app.route("/reservas/guardar", methods=["POST"])
def reservasGuardar():
    if not con.is_connected():
        con.reconnect()

    id_reserva = request.form.get("id_reserva")
    nombre_apellido = request.form["nombre_apellido"]
    telefono = request.form["telefono"]
    fecha = request.form["fecha"]

    cursor = con.cursor()
    if id_reserva:  # Actualizar
        sql = """
        UPDATE tst0_reservas SET Nombre_Apellido = %s, Telefono = %s, Fecha = %s WHERE Id_Reserva = %s
        """
        val = (nombre_apellido, telefono, fecha, id_reserva)
    else:  # Crear nueva reserva
        sql = """
        INSERT INTO tst0_reservas (Nombre_Apellido, Telefono, Fecha) VALUES (%s, %s, %s)
        """
        val = (nombre_apellido, telefono, fecha)

    cursor.execute(sql, val)
    con.commit()
    cursor.close()

    notificar_actualizacion_reservas()

    return make_response(jsonify({"message": "Reserva guardada exitosamente"}))

# Obtener todas las reservas
@app.route("/reservas", methods=["GET"])
def obtener_reservas():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tst0_reservas")
    reservas = cursor.fetchall()
    cursor.close()

    return make_response(jsonify(reservas))

# Función para editar y eliminar similar a usuarios

# Notificar a través de Pusher sobre actualizaciones en la tabla de reservas
def notificar_actualizacion_reservas():
    pusher_client = pusher.Pusher(
        app_id="1874485",
        key="970a7d4d6af4b86adcc6",
        secret="2e26ccd3273ad909a49d",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("canalReservas", "actualizacion", {})

if __name__ == "__main__":
    app.run(debug=True)
