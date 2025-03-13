import cx_Oracle
from flask import Flask, render_template, redirect, url_for, request,session,flash
import mercadopago




from flask_login import LoginManager, current_user, login_user, logout_user,login_required
from Usuario import Usuario
from datetime import datetime
from db import conectar_bd  # Importa la conexión a la BD
import os



app = Flask(__name__)

app.secret_key = "clave_secreta"  # Necesario para sesiones en Flask


MERCADO_PAGO_ACCESS_TOKEN = "TEST-8325666085224932-030611-78b2b39df94a47f450c21dec398e2738-728204204"
sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)






conexion = conectar_bd()
if conexion is None:
    print("¡Conexión falla!")
else:
    print("conectado")


# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Página a la que redirige si el usuario no está autenticado

# Función para cargar usuarios desde la base de datos

from privado import privado_bp
app.register_blueprint(privado_bp)
@login_manager.user_loader
def load_user(rutU):
    try:
        conn = conectar_bd()
        if conn:
            cur = conn.cursor()
            cur.execute('SELECT NOMBRE, RUT_CLIENTE, TELEFONO, ROL FROM CLIENTE WHERE RUT_CLIENTE = %s', (rutU,))

            res = cur.fetchone()
            cur.close()
            conn.close()
            print(f"Resultado de la consulta load_user: {res}")
            
            if res:
                return Usuario(res[0], res[1], res[2], res[3])  # Incluyendo el rol
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error de base de datos: {error.code} - {error.message}")
    return None

#Para solucionar el problema, 
# debes asegurarte de que la conexión a la base de datos y la configuración de Flask-Login
#  se realicen antes de que se registren los blueprints.

from Autenticacion import autenticacion_bp
app.register_blueprint(autenticacion_bp)



from publico import publico_bp
app.register_blueprint(publico_bp)
# Ruta de inicio



@app.route('/')
def home():
    try:
        conn = conectar_bd()  # Asegúrate de tener una función que conecte a la BD
        
        if conn:
            cur = conn.cursor()
            query = """
                SELECT 
                    V.COD_VUELO, 
                    V.VALOR, 
                    I.FECHA_VUELO, 
                    O.CIUDAD AS CIUDAD_ORIGEN, 
                    D.CIUDAD_D AS CIUDAD_DESTINO
                FROM VUELO V
                JOIN ITINERARIO I ON V.COD_ITINERARIO = I.COD_ITINERARIO
                JOIN ORIGEN O ON I.COD_ORIGEN = O.COD_ORIGEN
                JOIN DESTINO D ON I.COD_DESTINO = D.COD_DESTINO
            """
            cur.execute(query)
            vuelos = cur.fetchall()  # Obtener todos los resultados
            print(vuelos)
            cur.close()
            conn.close()

            # Convertimos los datos a un diccionario para facilitar su uso en la plantilla
            vuelos_lista = [
                {"id": v[0], "valor": v[1], "fecha": v[2], "origen": v[3], "destino": v[4],"imagen": f"static/imagen/{v[0]}.jpg"} for v in vuelos
            ]

            return render_template("index.html", viajes=vuelos_lista)
        else:
            return "Error de conexión con la base de datos", 500
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/ver_carrito')
@login_required
def ver_carrito():
    # Verificar si el carrito está vacío
    if 'cart' not in session or not session['cart']:
        return render_template("carrito.html", vuelos=[],total=0)

    try:
        cur = conexion.cursor()

        # Convertir la lista de IDs en una tupla
        vuelos_ids = tuple(session['cart'])

        # Si solo hay un elemento, asegurar que sea una tupla válida
        if len(vuelos_ids) == 1:
            vuelos_ids = (vuelos_ids[0],)

        # Consulta SQL corregida con placeholders
        query = """
            SELECT 
                V.COD_VUELO, 
                V.VALOR, 
                I.FECHA_VUELO, 
                O.CIUDAD AS CIUDAD_ORIGEN, 
                D.CIUDAD_D AS CIUDAD_DESTINO
            FROM VUELO V
            JOIN ITINERARIO I ON V.COD_ITINERARIO = I.COD_ITINERARIO
            JOIN ORIGEN O ON I.COD_ORIGEN = O.COD_ORIGEN
            JOIN DESTINO D ON I.COD_DESTINO = D.COD_DESTINO
            WHERE V.COD_VUELO IN (%s)
        """ % (', '.join(['%s'] * len(vuelos_ids)))  # Reemplazar con la cantidad correcta de placeholders

        cur.execute(query, vuelos_ids)
        vuelos = cur.fetchall()
        cur.close()

        # Convertir los resultados en una lista de diccionarios
        vuelos_lista = [
            {"id": v[0], "valor": v[1], "fecha": v[2], "origen": v[3], "destino": v[4]} 
            for v in vuelos
        ]
        total = sum(v[1] for v in vuelos)

        return render_template("carrito.html", vuelos=vuelos_lista, total=total)

    except Exception as e:
        return f"Error: {e}", 500


@app.route('/eliminar_del_carrito/<int:vuelo_id>')
@login_required
def eliminar_del_carrito(vuelo_id):
    if 'cart' in session and vuelo_id in session['cart']:
        session['cart'].remove(vuelo_id)
        session['cart_count'] = len(session['cart'])
        session.modified = True  # Asegura que Flask actualice la sesión

        flash("Vuelo eliminado del carrito", "danger")

    return redirect(url_for('ver_carrito'))
 


@app.route('/procesar_pago', methods=['POST'])
@login_required
def procesar_pago():
    email="sergioleon10@outlook.es"
    total = request.form.get('total', type=float)

    if total <= 0:
        return "No tienes productos en tu carrito.", 400

    # Configurar la preferencia de pago
    preference_data = {
        "items": [
            {
                "title": "Compra en Vuelos",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": total
            }
        ],
        "payer": {
            "email": email # Asegúrate que 'current_user' tiene 'email'
        },
        "back_urls": {
            "success": url_for('pago_exitoso', _external=True),
            "failure": url_for('pago_fallido', _external=True),
            "pending": url_for('pago_pendiente', _external=True)
        },
        "auto_return": "approved"
    }

    # Crear la preferencia en Mercado Pago
    preference_response = sdk.preference().create(preference_data)
    
    # Imprimir la respuesta completa de Mercado Pago para depuración
    print(preference_response)

    # Asegúrate de que la respuesta tenga 'init_point'
    if 'init_point' not in preference_response['response']:
        return f"Error: La respuesta de Mercado Pago no contiene 'init_point'. Respuesta: {preference_response}", 500

    preference = preference_response["response"]

    # Redirige a `pago.html` con el link de pago
    return render_template("pago.html", total=total, mp_url=preference["init_point"])



@app.route('/pago_exitoso')
@login_required
def pago_exitoso():
    session.pop('cart', None)  # Vaciar el carrito después del pago exitoso
    return render_template("pago_exitoso.html")

@app.route('/pago_fallido')
@login_required
def pago_fallido():
    return render_template("pago_fallido.html")

@app.route('/pago_pendiente')
@login_required
def pago_pendiente():
    return render_template("pago_pendiente.html")


@app.route('/contacto')
def contacto():
    errores = ["El archivo solicitado es incorrecto"]
    return render_template("contacto.html", errores=errores)





@app.route("/login", methods=["GET", "POST"])
def login():
    errores = []
    if request.method == "POST":
        rut = request.form["rut"].strip()
        telefono = request.form["telefono"]
        rut_sin_formato = request.form.get('rut_sin_formato')

        try:
            rut_int = int(rut_sin_formato)
            conn = conectar_bd()
            if conn:
                cur = conn.cursor()
                cur.execute('SELECT NOMBRE, RUT_CLIENTE, TELEFONO FROM CLIENTE WHERE RUT_CLIENTE = %s', (rut_sin_formato,))
                res = cur.fetchone()
                cur.close()
                conn.close()

                if res is not None:
                    if str(res[2]).strip() == telefono.strip():
                        # Crear el objeto Usuario
                        user = Usuario(res[0], res[1], res[2])
                        
                        # Iniciar sesión
                        login_user(user)

                        # Obtener la URL de redirección (next) o redirigir a la home
                        next_page = request.args.get('next', url_for('privado.admin'))
                        return redirect(next_page)
                    else:
                        errores.append("No se pudo conectar con la base de datos.")
                        
                        
                else:
                    errores.append("Usuario no existente o inválido")
                    
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            print(f"Error de base de datos: {error.code} - {error.message}")

    return render_template("login.html",errores=errores)

@app.route('/perfil')
def perfil():
    errores = ["El archivo solicitado es incorrecto"]
    return render_template("usuario/perfil.html", errores=errores)


@app.route('/carrito')
@login_required
def carrito():
    if 'cart' not in session or not session['cart']:
        return render_template("carrito.html", vuelos=[])

    try:
        conn = conectar_bd()
        cur = conn.cursor()

        # Obtener los vuelos guardados en el carrito
        vuelos_ids = tuple(session['cart'])  # Convierte la lista en tupla para SQL
        query = """
            SELECT 
                V.COD_VUELO, 
                V.VALOR, 
                I.FECHA_VUELO, 
                O.CIUDAD AS CIUDAD_ORIGEN, 
                D.CIUDAD_D AS CIUDAD_DESTINO
            FROM VUELO V
            JOIN ITINERARIO I ON V.COD_ITINERARIO = I.COD_ITINERARIO
            JOIN ORIGEN O ON I.COD_ORIGEN = O.COD_ORIGEN
            JOIN DESTINO D ON I.COD_DESTINO = D.COD_DESTINO
            WHERE V.COD_VUELO IN %s
        """ % str(vuelos_ids)  # Inserta los IDs en la consulta

        cur.execute(query)
        vuelos = cur.fetchall()
        cur.close()
        conn.close()

        vuelos_lista = [
            {"id": v[0], "valor": v[1], "fecha": v[2], "origen": v[3], "destino": v[4]} for v in vuelos
        ]

        return render_template("carrito.html", vuelos=vuelos_lista)

    except Exception as e:
        return f"Error: {e}", 500


@app.route('/actualizar_carrito')
def actualizar_carrito():
    cart_count = session.get('cart_count', 0)
    return {"cart_count": cart_count}


@app.route('/agregar_al_carrito/<int:vuelo_id>')
@login_required  # Asegura que solo usuarios autenticados puedan agregar vuelos al carrito
def agregar_al_carrito(vuelo_id):
    if 'cart' not in session:
        session['cart'] = []
        session['cart_count'] = 0

    session['cart'].append(vuelo_id)
    session['cart_count'] = len(session['cart'])
    session.modified = True  # Asegura que Flask actualice la sesión

    flash("Vuelo agregado al carrito", "success")
    return redirect(url_for('home'))


@app.route('/detalle/<int:viaje_id>')
def detalle(viaje_id):
    try:
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    V.COD_VUELO, 
                    V.VALOR, 
                    I.FECHA_VUELO, 
                    O.CIUDAD AS CIUDAD_ORIGEN, 
                    D.CIUDAD_D AS CIUDAD_DESTINO
                FROM VUELO V
                JOIN ITINERARIO I ON V.COD_ITINERARIO = I.COD_ITINERARIO
                JOIN ORIGEN O ON I.COD_ORIGEN = O.COD_ORIGEN
                JOIN DESTINO D ON I.COD_DESTINO = D.COD_DESTINO
                WHERE V.COD_VUELO = %s
            """,(viaje_id,))
            viaje = cursor.fetchone()  # Solo un resultado
            
            
            cursor.close()
            conn.close()

            if viaje:
                viaje_dict = {
                    "id": viaje[0], 
                    "valor": viaje[1], 
                    "fecha": viaje[2], 
                    "origen": viaje[3], 
                    "destino": viaje[4],
                    "imagen": f"static/imagen/{viaje[0]}.jpg"
                }
                return render_template("detalle.html", viaje=viaje_dict)
            else:
                return "Viaje no encontrado", 404
    except Exception as e:
        return f"Error: {e}", 500

# Ruta de cierre de sesión
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))




if __name__ == "__main__":
    

     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 1000)))
     #app.run(debug=True, port=5001)


