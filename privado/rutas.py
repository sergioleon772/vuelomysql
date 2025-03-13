from flask import render_template, request, redirect, url_for, flash,jsonify
from flask_login import LoginManager, current_user, login_user, logout_user,login_required

from datetime import datetime
from . import privado_bp  # Importa desde __init__.py
from Usuario import Usuario
import qrcode

from ejecutar import conexion  # Importa la conexión correctamente
import os
from werkzeug.utils import secure_filename

# Configuración para aceptar solo ciertos tipos de archivo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#-----INGRESO DE DATOS DE ADMIN------
@privado_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    mensaje = ""
    errores = []
    if request.method == 'POST':
        try:
            rut = request.form["rut_sin_formato"]
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            correo = request.form["correo"]
            fecha_nac = request.form["fecha_nac"]
            region = request.form["region"]
            comuna = request.form["comuna"]
            calle = request.form["calle"]
            numero = int(request.form["numero"])  # Convertir a entero
            telefono = request.form["telefono"]

            cursor = conexion.cursor()
            if conexion is None:
                errores.append("No hay conexión a la base de datos.")
                return render_template('Admin/cliente/formulario_cliente.html', mensaje=mensaje, errores=errores)

            fecha_nac_formateada = datetime.strptime(fecha_nac, "%Y-%m-%d").strftime("%d/%m/%Y")
            print("Fecha formateada:", fecha_nac_formateada)  # Depuración
            print("Tipo de numero:", type(numero)) #Depuración
            rol = ''
            parametros = [rut, nombre, apellido, correo, fecha_nac_formateada, region, comuna, calle, numero, telefono, '']
            print("Parámetros:", parametros)  # Depuración

            cursor.callproc("INSERTAR_CLIENTE", parametros)
            cursor.execute("SELECT @MENSAJE")
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)
            conexion.commit()

        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error: {e}")
            print(f"Error: {e}") #Depuración
            conexion.rollback()

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    return render_template('Admin/cliente/formulario_cliente.html', mensaje=mensaje, errores=errores)

#--INGRESO DE DATOS DE USUSARIO



from datetime import datetime

@privado_bp.route('/registrar2', methods=['GET', 'POST'])
def registrar2():
    mensaje = ""
    errores = []
    redireccionar = False  # Inicialización de redireccionar

    if request.method == 'POST':
        try:
            if not conexion:
                errores.append("Error al conectar con la base de datos.")
                return render_template('register.html', mensaje=mensaje, errores=errores)

            with conexion.cursor() as cursor:
                # Obtener datos del formulario
                rut = request.form["rut_sin_formato"]
                nombre = request.form["nombre"]
                apellido = request.form["apellido"]
                correo = request.form["correo"]
                fecha_nac = request.form["fecha_nac"]
                region = request.form["region"]
                comuna = request.form["comuna"]
                calle = request.form["calle"]
                numero = request.form["numero"]
                telefono = request.form["telefono"]

                # Convertir fecha
                fecha_nac_formateada = datetime.strptime(fecha_nac, "%Y-%m-%d").strftime("%d/%m/%Y")

                parametros = [rut, nombre, apellido, correo, fecha_nac_formateada, region, comuna, calle, numero, telefono, '']
                print(parametros)

                # Llamar al procedimiento almacenado
                cursor.callproc("INSERTAR_CLIENTE", parametros)

                # Recuperar el mensaje de salida
                cursor.execute("SELECT @MENSAJE")
                mensaje = cursor.fetchone()[0]
                print(mensaje)

                # Verificar el mensaje
                if mensaje == 'CLIENTE INGRESADO CORRECTAMENTE':
                    redireccionar = True
                
                conexion.commit()

        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error: {e}")
            return redirect(url_for('privado.errores'))
        cursor.close()

       
    return render_template('register.html',  mensaje=mensaje, redireccionar=redireccionar,errores=errores)




from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Acceso denegado. Se requiere rol de administrador.", "danger")
            # Redirige al login pasando la URL actual como 'next'
            return redirect(url_for("home"))
            
        return f(*args, **kwargs)
    return decorated_function

@privado_bp.route('/admin')
@login_required
@admin_required
def admin():
    return render_template("admin.html")

from functools import wraps


@privado_bp.route('/actualizar_cliente', methods=['GET', 'POST'])
def actualizar_cliente():
    mensaje = ""
    errores = []
    usuario = {}
    cursor = conexion.cursor()

    if request.method == 'GET':
        print("A través del método GET")
        rut_cliente =request.args.get('cod_iti_act') #cambio de nombre de variable
        print("RUT del usuario:", rut_cliente) #cambio de nombre de variable
        cursor.execute("""
            SELECT 
                RUT_CLIENTE, NOMBRE, APELLIDO, CORREO, FECHA_NACIMIENTO,
                REGION, 
                COMUNA, 
                CALLE, 
                NUMERO, 
                TELEFONO
            FROM CLIENTE 
            WHERE RUT_CLIENTE = %s
        """, (rut_cliente,)) #cambio de nombre de variable

        datos_usuario = cursor.fetchone()

        if datos_usuario:
            usuario = {
                "rut": datos_usuario[0],
                "nombre": datos_usuario[1],
                "apellido": datos_usuario[2],
                "correo": datos_usuario[3],
                "fecha_nacimiento": datos_usuario[4],
                "region": datos_usuario[5],
                "comuna": datos_usuario[6],
                "calle": datos_usuario[7],
                "numero": datos_usuario[8],
                "telefono": datos_usuario[9],
            }
        else:
            errores.append("No se encontraron datos para este usuario.")

        cursor.close()
        return render_template('Admin/cliente/actualizar_cliente.html', usuario=usuario, mensaje=mensaje, errores=errores)


    
    elif request.method == 'POST':
        try:
            rut = request.form["rut"]
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            region = request.form["region"]
            comuna = request.form["comuna"]
            calle = request.form["calle"]
            numero = request.form["numero"]
            telefono = request.form["telefono"]

        
       
            parametros = [rut, nombre, apellido, region, comuna, calle, numero, telefono, ''] #cambio de nombre de variable

            cursor.callproc("ACTUALIZAR_INFO_CLIENTE", parametros)
            cursor.execute("SELECT @MENSAJE")  # Capturar mensaje del procedimiento almacenado
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)
            conexion.commit()

        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error. Asegúrese de haber introducido bien los datos. {e}")
            conexion.rollback()
        cursor.close()
    else:
        return '<h1>Método no encontrado</h1>'

    return render_template('Admin/cliente/actualizar_cliente.html', usuario=usuario, mensaje=mensaje, errores=errores, )

@privado_bp.route('/eliminar_cliente', methods=['GET', 'POST'])
def eliminar_cliente():
    mensaje = ""
    errores = []
    if request.method == 'POST':
        cod_iti_act = request.form.get("cod_iti_act")
        print("RUT a eliminar:", cod_iti_act)  # Depuración

        try:
            cursor = conexion.cursor()
            cursor.execute("SET @MENSAJE = '';")
            cursor.execute('CALL ELIMINAR_CLIENTE(%s, @MENSAJE)', (cod_iti_act,))
            cursor.execute("SELECT @MENSAJE;")
            mensaje = cursor.fetchone()[0]
            print("Mensaje cliente:", mensaje)  # Depuración
            conexion.commit()
            #return redirect(url_for('publico.vista_clientes'))
        except Exception as e:
            errores.append(f'Error al eliminar: {e}')
            print(f'Error: {e}')  # Depuración
            conexion.rollback()
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    return render_template('Admin/cliente/mensaje_cliente.html', mensaje=mensaje, errores=errores)
    return redirect(url_for('publico.vista_clientes'))
    #return render_template('Admin/cliente/eliminar_cliente.html',mensaje=mensaje,errores=errores)

#VUELOS METODOS INSERTAR,ACTUALIZAR Y ELIMINAR
import os
from werkzeug.utils import secure_filename

# Configuración para aceptar solo ciertos tipos de archivo
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# Verificar y crear la carpeta si no existe
upload_folder = os.path.join('static', 'imagen')
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)


from PIL import Image
@privado_bp.route('/ingresar_vuelo', methods=['GET', 'POST'])
def ingresar_vuelo():
    mensaje = ""
    try:
        conn = conexion  # Asegurar que la conexión esté definida
        cursor = conn.cursor()

        # Obtener agencias e itinerarios
        cursor.execute("SELECT ID_AGENCIA, NOMBRE_AGENCIA FROM AGENCIA")
        agencias = cursor.fetchall()

        query_itinerarios = """
            SELECT I.COD_ITINERARIO, O.CIUDAD AS ORIGEN, D.CIUDAD_D AS DESTINO
            FROM ITINERARIO I
            JOIN ORIGEN O ON I.COD_ORIGEN = O.COD_ORIGEN
            JOIN DESTINO D ON I.COD_DESTINO = D.COD_DESTINO
        """
        cursor.execute(query_itinerarios)
        itinerarios = cursor.fetchall()

        cursor.close()

        agencias_lista = [{"id": a[0], "nombre": a[1]} for a in agencias]
        itinerarios_lista = [{"id": i[0], "ruta": f"{i[1]} -> {i[2]}"} for i in itinerarios]

        if request.method == 'POST':
            cod_agen_v = request.form["cod_agen_v"]
            cod_itin_v = request.form["cod_itin_v"]
            canti_a_v = request.form["canti_a_v"]
            valor_vue = request.form["valor_vue"]

            # Manejo de la imagen cargada
          
            imagen = request.files.get("imagen_vuelo")
            print("archivo",request.files)

            if imagen:
                print(f"Archivo recibido: {imagen.filename}")
            else:
                print("No se recibió ninguna imagen.")

            
            # Insertar el vuelo y obtener el COD_VUELO
            try:
                cursor = conn.cursor()
                 # Definir una variable de usuario en MySQL para capturar el mensaje
                cursor.execute("SET @mensaje = '';")
                cursor.execute(
                    "CALL INSERTAR_VUELO(%s, %s, %s, %s, %s, @mensaje);", 
                    (cod_agen_v, cod_itin_v, canti_a_v, valor_vue, canti_a_v)
                )
                conn.commit()

                # Recuperar el mensaje del procedimiento almacenado
                cursor.execute("SELECT @mensaje;")
                mensaje = cursor.fetchone()[0]
                print("mensaje de vuelo",mensaje)
                # Obtener el COD_VUELO generado (supongamos que es el último ID insertado)
                cursor.execute("SELECT MAX(COD_VUELO) FROM VUELO")
                cod_vuelo = cursor.fetchone()[0]  # Recuperamos el último COD_VUELO generado
                print(f"Último COD_VUELO insertado: {cod_vuelo}")
                # Guardar la imagen solo si es válida
                if imagen and allowed_file(imagen.filename):
                    # Generar un nombre de archivo usando el COD_VUELO
                    filename = f"{cod_vuelo}.jpg"  # Asumiendo que el formato es .jpg
                    filepath = os.path.join('static', 'imagen', filename)
                    
                    img = Image.open(imagen)
                    TAMANO_IMAGEN = (400, 400)
                    imagen= img.resize(TAMANO_IMAGEN, Image.ANTIALIAS)
                    # Guardar la imagen en el directorio estático
                    imagen.save(filepath)
                    print(f"Imagen guardada en: {filepath}")
                    # Si quieres guardar la ruta de la imagen en la base de datos, puedes hacerlo aquí
                    # Actualizar la tabla con el nombre del archivo de la imagen o la ruta

                #mensaje = "Vuelo ingresado correctamente."
                return render_template(
                    'Admin/vuelo/mensajevuelo.html',mensaje=mensaje)
            except Exception as e:
                mensaje = f"Error en la base de datos: {str(e)}"
            finally:
                cursor.close()

        
    except Exception as e:
        return f"<h1>Error: {e}</h1>"
    
    return render_template(
            'Admin/vuelo/ingresar_vuelo.html',
            mensaje=mensaje,
            agencias=agencias_lista,
            itinerarios=itinerarios_lista
        )



from flask import render_template, request, redirect, url_for, flash

@privado_bp.route('/actualizar_vuelo', methods=['GET', 'POST'])
def actualizar_vuelo():
    mensaje = ""
    errores = []
    vuelo = {}

    if request.method == 'GET':
        codigo_vuelo = request.args.get('cod_vuelo')
        cursor = conexion.cursor()
        cursor.execute("SELECT COD_VUELO, ID_AGENCIA, COD_ITINERARIO, VALOR FROM VUELO WHERE COD_VUELO = %s", (codigo_vuelo,))
        datos_vuelos = cursor.fetchone()
        if datos_vuelos:
            vuelo = {
                'cod_vuelo': datos_vuelos[0],
                'id_agencia': datos_vuelos[1],
                'cod_itinerario': datos_vuelos[2],
                'valor': float(datos_vuelos[3])  # Asegurar que el valor sea float
            }
        else:
            errores.append("Vuelo no encontrado.")
        cursor.close()

    elif request.method == 'POST':
        cod_vuelo_m = request.form["cod_vuelo_m"]
        cod_agenc_m = request.form["cod_agenc_m"]
        cod_iti_mod = request.form["cod_iti_mod"]
        valor_vue = request.form["valor_vue"]

        cursor = conexion.cursor()

        try:
            # Definir una variable para almacenar el mensaje de salida
            mensaje_salida = ""

            # Llamar al procedimiento almacenado con una lista de parámetros, incluyendo una variable mutable para OUT
            resultado = cursor.callproc('ACTUALIZAR_VUELO', [cod_vuelo_m, cod_agenc_m, cod_iti_mod, valor_vue, mensaje_salida])

            # El último valor de la lista de salida es el mensaje retornado por el procedimiento almacenado
            mensaje = resultado[-1]  # Accede al último valor (mensaje OUT)
            print(mensaje)
            conexion.commit()

            if mensaje == 'VUELO ACTUALIZADO':
                flash('Vuelo actualizado con éxito', 'success')  # Mensaje flash.
                #return redirect(url_for('privado.vista_vuelo'))  # Redirección.
                return render_template('Admin/vuelo/actualizar_vuelo.html', mensaje=mensaje, vuelo=vuelo, errores=errores)
            else:
                flash(mensaje, 'danger')  # Mensaje flash en caso de error.

        except Exception as e:
            errores.append(f'Error al actualizar: {e}')
            conexion.rollback()

        finally:
            cursor.close()

    return render_template('Admin/vuelo/actualizar_vuelo.html', mensaje=mensaje, vuelo=vuelo, errores=errores)





@privado_bp.route('/eliminar_vuelo',methods=['GET','POST'])
def eliminar_vuelo():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        cod_vuelo=request.form.get("cod_vuelo")
        print("codigo a eliminar",cod_vuelo)
       
        

        
        try:
            cursor = conexion.cursor()

            cursor.execute("SET @MENSAJE = '';")
            cursor.execute("CALL ELIMINAR_VUELO(%s, @MENSAJE);", (cod_vuelo,))
            cursor.execute("SELECT @MENSAJE;")
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)
            #VUELO ELIMINADO
            conexion.commit()
        except:
            errores.append('Error al eliminar')
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/vuelo/mensajevuelo.html',mensaje=mensaje,errores=errores)

#METODOS INSERTAR , ACTUALIZAR Y ELIMINAR ITINERARIO
@privado_bp.route('/ingresar_itinerario', methods=['GET', 'POST'])
def ingresar_itinerario():
    mensaje = ""
    errores = []

    if request.method == 'POST':
        fecha_salida = request.form.get("fecha_salida")
        horaS = request.form.get("horaS")
        fecha_llegada = request.form.get("fecha_llegada")
        horaL = request.form.get("horaL")
        cod_origen_iL = request.form.get("cod_origen_iL")
        cod_d_iL = request.form.get("cod_d_iL")

        # Validar campos vacíos
        if not fecha_salida or not horaS or not fecha_llegada or not horaL or not cod_origen_iL or not cod_d_iL:
            errores.append("Todos los campos son obligatorios.")
        else:
            try:
                cursor = conexion.cursor()
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute(
                    "CALL INSERTAR_ITINERARIO(%s, %s, %s, %s, %s, %s, @MENSAJE);",
                    (fecha_salida, horaS, fecha_llegada, horaL, cod_origen_iL, cod_d_iL)
                )
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                if "incorrectamente" not in mensaje:
                    errores.append(mensaje)
                    mensaje = ""
                conexion.commit()

            except Exception as e:
                errores.append(f"¡Ups! Ha ocurrido un error: {str(e)}")
                conexion.rollback()

            finally:
                cursor.close()

    return render_template('Admin/itinerario/ingresar_itinerario.html', mensaje=mensaje, errores=errores)

@privado_bp.route('/actualizar_itinerario', methods=['GET', 'POST'])
def actualizar_itinerario():
    mensaje = ""
    errores = []
    itinerario = None

    if request.method == 'GET':
        cod_iti_act = request.args.get('cod_iti_act')
        if cod_iti_act:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT FECHA_VUELO, HORA_SALIDA, HORA_LLEGADA, COD_ORIGEN, COD_DESTINO FROM ITINERARIO WHERE COD_ITINERARIO = %s", (cod_iti_act,))
                result = cursor.fetchone()
                if result:
                    itinerario = {
                        'fecha_salida': result[0].strftime('%Y-%m-%d'),
                        'hora_salida': result[1].strftime('%H:%M'),
                        'fecha_llegada': result[2].strftime('%Y-%m-%d'),
                        'hora_llegada': result[2].strftime('%H:%M'),
                        'cod_origen': result[3],
                        'cod_destino': result[4]
                    }
                else:
                    errores.append("Itinerario no encontrado.")
                cursor.close()
            except Exception as e:
                errores.append(f"Error al obtener el itinerario: {str(e)}")

    elif request.method == 'POST':
        cod_iti_act = request.form.get("cod_iti_act")
        fecha_salida = request.form.get("fecha_salida")
        horaS = request.form.get("horaS")
        fecha_llegada = request.form.get("fecha_llegada")
        horaL = request.form.get("horaL")
        cod_origen_iL = request.form.get("cod_origen_iL")
        cod_d_iL = request.form.get("cod_d_iL")

        if not cod_iti_act or not fecha_salida or not horaS or not fecha_llegada or not horaL or not cod_origen_iL or not cod_d_iL:
            errores.append("Todos los campos son obligatorios.")
        else:
            try:
                cursor = conexion.cursor()
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute(
                    "CALL ACTUALIZAR_ITINERARIO(%s, %s, %s, %s, %s, %s, %s, @MENSAJE);",
                    (cod_iti_act, fecha_salida, horaS, fecha_llegada, horaL, cod_origen_iL, cod_d_iL)
                )
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                if "correctamente" not in mensaje:
                    errores.append(mensaje)
                    mensaje = ""
                conexion.commit()
                cursor.close()
            except Exception as e:
                errores.append(f"Error al actualizar el itinerario: {str(e)}")
                conexion.rollback()

    return render_template('Admin/itinerario/actualizar_itinerario.html', mensaje=mensaje, errores=errores, itinerario=itinerario)



@privado_bp.route('/eliminar_itinerario', methods=['GET', 'POST'])
def eliminar_itinerario():
    if request.method == 'GET':
        cod_iti_act = request.args.get('cod_iti_act')
        print("A través del método GET. Cod_iti_act:", cod_iti_act)
        return "GET request received. No action taken."  # Retorna una respuesta válida

    elif request.method == 'POST':
        cod_iti_act = request.form.get("cod_iti_act")
        print("Eliminar itinerario POST. Cod_iti_act:", cod_iti_act)
        if cod_iti_act:
            try:
                cursor = conexion.cursor()
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute("CALL ELIMINAR_ITINERARIO(%s, @MENSAJE);", (cod_iti_act,))
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                conexion.commit()
                cursor.close()
                return redirect(url_for('publico.vista_itinerario'))
            except Exception as e:
                print(f"Error al eliminar el itinerario: {e}")
                conexion.rollback()
                return redirect(url_for('publico.vista_itinerario'))
        else:
            return redirect(url_for('publico.vista_itinerario'))
    else:
        return '<h1>Método no encontrado</h1>'
#-- ORIGEN METODOS INSERTAR,ACTUALIZ
@privado_bp.route('/ingresar_origen',methods=['GET','POST'])
def ingresar_origen():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        try:
            aero_o=request.form["aero_o"]
            ciudad_o=request.form["ciudad_o"]
            pais_o=request.form["pais_o"]

            with conexion.cursor() as cursor:
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute("CALL INSERTAR_ORIGEN(%s, %s, %s, @MENSAJE);", (aero_o, ciudad_o, pais_o))
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                print("Origen ingresado:", mensaje)
                conexion.commit()


        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")
            #return redirect(url_for('privado.errores'))
        
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/ingresar_origen.html',mensaje=mensaje,errores=errores)

@privado_bp.route('/actualizar_origen',methods=['GET','POST'])
def actualizar_origen():
    mensaje=""
    errores=[]
    origen={}
    if request.method == 'GET':
        print("A traves del metodo get")
        cod_origen=request.args.get('cod_origen')
        print("codigo origen a  actualizar",cod_origen)
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COD_ORIGEN, AEROPUERTO, CIUDAD, PAIS FROM ORIGEN WHERE COD_ORIGEN = %s", (cod_origen,))
            datos_origen = cursor.fetchone()
            if datos_origen:
                origen = {
                    'cod_origen': datos_origen[0],
                    'aeropuerto': datos_origen[1],
                    'ciudad': datos_origen[2],
                    'pais': datos_origen[3]
                }
            else:
                errores.append("Origen no encontrado.")
            cursor.close()
        
        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error: {e}")
            #return redirect(url_for('privado.errores'))
            
    elif request.method == 'POST':
        try:
            cod_ori_modi=request.form["cod_ori_modi"]
            nombreAero=request.form["nombreAero"]
            ciudad_n=request.form["ciudad_n"]
            pais_nuevo=request.form["pais_nuevo"]
            print("datos a cambiar",cod_ori_modi,nombreAero,ciudad_n,pais_nuevo)
        

        
    

            with conexion.cursor() as cursor:
    # Definir la variable de sesión @MENSAJE
                cursor.execute("SET @MENSAJE = '';")

                # Llamar al procedimiento almacenado correctamente
                cursor.execute("CALL ACTUALIZAR_ORIGEN(%s, %s, %s, %s, @MENSAJE);", 
                            (cod_ori_modi, nombreAero, ciudad_n, pais_nuevo))

                # Obtener el valor de la variable de sesión @MENSAJE
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                print("Recupero:", mensaje)
                # Confirmar la transacción
                conexion.commit()

        except Exception as e:
            errores.append(f'Error: {str(e)}')

        cursor.close()

    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/actualizar_origen.html',mensaje=mensaje,errores=errores,origen=origen)


@privado_bp.route('/eliminar_origen',methods=['GET','POST'])
def eliminar_origen():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        cod_origen=request.form.get("cod_origen")
        print(cod_origen)
        
        try:
            cursor = conexion.cursor()
            cursor.execute("SET @MENSAJE = '';")
            cursor.execute("CALL ELIMINAR_ORIGEN(%s, @MENSAJE);", (cod_origen,))
            cursor.execute("SELECT @MENSAJE;")
            mensaje = cursor.fetchone()[0]
            print("Mensaje Eliminar:", mensaje)
            conexion.commit()
        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")
            #return redirect(url_for('privado.errores'))
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/eliminar_origen.html',mensaje=mensaje,errores=errores)

#destinos
@privado_bp.route('/ingresar_destino',methods=['GET','POST'])
def ingresar_destino():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        try:
            aero_d=request.form["aero_d"]
            ciudad_d=request.form["ciudad_d"]
            pais_d=request.form["pais_d"]

            with conexion.cursor() as cursor:
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute("CALL INSERTAR_DESTINO(%s, %s, %s, @MENSAJE);", (aero_d, ciudad_d, pais_d))
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                print("Destino ingresado:", mensaje)
                conexion.commit()
        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")
            #return redirect(url_for('privado.errores'))
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/ingresar_destino.html',mensaje=mensaje,errores=errores)


@privado_bp.route('/actualizar_destino',methods=['GET','POST'])
def actualizar_destino():
    mensaje=""
    errores=[]
    destino={}
    if request.method == 'GET':
        cod_destino=request.args.get('cod_destino')
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COD_DESTINO, AEROPUERTO_D, CIUDAD_D, PAIS_D FROM DESTINO WHERE COD_DESTINO = %s", (cod_destino,))
            datos_destino = cursor.fetchone()
            if datos_destino:
                destino = {
                    'cod_destino': datos_destino[0],
                    'aeropuerto': datos_destino[1],
                    'ciudad': datos_destino[2],
                    'pais': datos_destino[3]
                }
            else:
                errores.append("Destino no encontrado.")
            cursor.close()
        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error: {e}")
            #return redirect(url_for('privado.errores'))
    elif request.method == 'POST':
        try:
            cod_des_modi=request.form["cod_des_modi"]
            nombreAero=request.form["nombreAero"]
            ciudad_n=request.form["ciudad_n"]
            pais_nuevo=request.form["pais_nuevo"]

            with conexion.cursor() as cursor:
                cursor.execute("SET @MENSAJE = '';")
                cursor.execute("CALL ACTUALIZAR_DESTINO(%s, %s, %s, %s, @MENSAJE);", 
                            (cod_des_modi, nombreAero, ciudad_n, pais_nuevo))
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]
                print("destino:", mensaje)
                conexion.commit()

        except Exception as e:
            errores.append(f'Error, ingrese correctamente{str(e)}')
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/actualizar_destino.html',mensaje=mensaje,errores=errores,destino=destino)

@privado_bp.route('/eliminar_destino',methods=['GET','POST'])
def eliminar_destino():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        cod_destino=request.form.get("cod_destino")
       
        try:
            cursor=conexion.cursor()
            cursor.execute("SET @MENSAJE = '';")
            cursor.execute("CALL ELIMINAR_DESTINO(%s, @MENSAJE);", (cod_destino,))
            cursor.execute("SELECT @MENSAJE;")
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)
            conexion.commit()

        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")

        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/viaje/eliminar_destino.html',mensaje=mensaje,errores=errores)




# Asumiendo que 'conexion' es tu objeto de conexión psycopg2 configurado correctamente
# Ejemplo (reemplaza con tus datos):
# conexion = psycopg2.connect(host="tu_host", database="tu_base_de_datos", user="tu_usuario", password="tu_contraseña")

@privado_bp.route('/actualizar_cuenta', methods=['GET', 'POST'])
def actualizar_cuenta():
    mensaje = ""
    errores = []
    usuario = {}

    cursor = conexion.cursor()

    if request.method == 'GET':
        print("A través del método GET")
        rut_cliente = current_user.rut #cambio de nombre de variable
        cursor.execute("""
            SELECT 
                RUT_CLIENTE, NOMBRE, APELLIDO, CORREO, FECHA_NACIMIENTO,
                REGION, 
                COMUNA, 
                CALLE, 
                NUMERO, 
                TELEFONO
            FROM CLIENTE 
            WHERE RUT_CLIENTE = %s
        """, (rut_cliente,)) #cambio de nombre de variable

        datos_usuario = cursor.fetchone()

        if datos_usuario:
            usuario = {
                "rut": datos_usuario[0],
                "nombre": datos_usuario[1],
                "apellido": datos_usuario[2],
                "correo": datos_usuario[3],
                "fecha_nacimiento": datos_usuario[4],
                "region": datos_usuario[5],
                "comuna": datos_usuario[6],
                "calle": datos_usuario[7],
                "numero": datos_usuario[8],
                "telefono": datos_usuario[9],
            }
        else:
            errores.append("No se encontraron datos para este usuario.")

        cursor.close()
        return render_template('usuario/actualizar_cuenta.html', usuario=usuario, mensaje=mensaje, errores=errores)

    elif request.method == 'POST':
        try:
            rut_cliente = current_user.rut #cambio de nombre de variable
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            region = request.form["region"]
            comuna = request.form["comuna"]
            calle = request.form["calle"]
            numero = int(request.form["numero"])
            telefono = int(request.form["telefono"])

            print("RUT del usuario:", rut_cliente) #cambio de nombre de variable
            mensaje_salida = ""
            parametros = [rut_cliente, nombre, apellido, region, comuna, calle, numero, telefono, ''] #cambio de nombre de variable

            cursor.callproc("ACTUALIZAR_INFO_CLIENTE", parametros)

            parametros = [rut_cliente, nombre, apellido, region, comuna, calle, numero, telefono, ""]


            cursor.execute("SELECT @MENSAJE")  # Capturar mensaje del procedimiento almacenado
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)

            conexion.commit()

        except Exception as e:
            errores.append(f"¡Ups! Ha ocurrido un error: {str(e)}")
            conexion.rollback()

        cursor.close()
        
        
        
        return render_template('usuario/actualizar_cuenta.html', usuario=usuario, mensaje=mensaje, errores=errores)

    return '<h1>Método no encontrado</h1>'

@privado_bp.route('/ingresar_agencia', methods=['GET', 'POST'])
def ingresar_agencia():
    mensaje = ""
    errores = []

    if request.method == 'POST':
        try:
            # Recuperar datos del formulario
            rutA = request.form.get("rutA")
            nombreA = request.form.get("nombreA")
            regionA = request.form.get("regionA")
            comunaA = request.form.get("comunaA")
            calleA = request.form.get("calleA")
            numeroA = request.form.get("numeroA")
            telefonoA = request.form.get("telefonoA")

            # Convertir los datos a los tipos correctos
            rutA = int(rutA)  # Convertir a INT
            numeroA = int(numeroA)  # Convertir a INT
            telefonoA = int(telefonoA)  # Convertir a BIGINT

            with conexion.cursor() as cursor:
                # Llamar al procedimiento almacenado en MySQL
                cursor.execute("CALL INSERTAR_AGENCIA(%s, %s, %s, %s, %s, %s, %s, @MENSAJE);",
                               (rutA, nombreA, regionA, comunaA, calleA, numeroA, telefonoA))

                # Obtener el mensaje de salida
                cursor.execute("SELECT @MENSAJE;")
                mensaje = cursor.fetchone()[0]

                # Confirmar la transacción
                conexion.commit()

        except ValueError as e:
            errores.append(f"Error: Los datos numéricos no son válidos. {str(e)}")
            conexion.rollback()
        except Exception as e:
            errores.append(f"Error: {str(e)}")
            conexion.rollback()

    return render_template('Admin/agencia/ingresar_agencia.html', mensaje=mensaje, errores=errores)



@privado_bp.route('/obtener_agencia/<id>', methods=['GET'])
def obtener_agencia(id):
    cursor = conexion.cursor()
    print("id seleccionado: ",id)
    try:
        cursor.execute("""SELECT a.ID_AGENCIA, a.NOMBRE_AGENCIA, a.DIRECCION_A.REGION, a.DIRECCION_A.COMUNA, a.DIRECCION_A.CALLE,
a.DIRECCION_A.NUMERO, a.TELEFONO FROM AGENCIA a WHERE ID_AGENCIA = :id""", [id])
        agencia = cursor.fetchone()
        cursor.close()

        if agencia:
            return jsonify({
                "cod_agencia": agencia[0],
                "nombre": agencia[1],
                "region": agencia[2],
                "comuna": agencia[3],
                "calle": agencia[4],
                "numero": agencia[5],
                "telefono": agencia[6]
            })
        else:
            return jsonify({"error": "No se encontró la agencia con ese ID."})
    except Exception as e:
        return jsonify({"error": str(e)})



@privado_bp.route('/actualizar_agencia', methods=['GET', 'POST'])
def actualizar_agencia():
    mensaje = ""
    errores = []
    agencia = {}

    if request.method == 'GET':
        print("A través del método GET")
        cod_ag_act = request.args.get('cod_ag_act')

        print("Código a actualizar:", cod_ag_act)
        cursor = conexion.cursor()

        try:
            cursor.execute('SELECT NOMBRE_AGENCIA, REGION, COMUNA, CALLE, NUMERO, TELEFONO FROM AGENCIA WHERE ID_AGENCIA = %s', (cod_ag_act,))
            datos_agencia = cursor.fetchone()
            if datos_agencia:
                agencia = {
                    'nombre': datos_agencia[0],
                    'region': datos_agencia[1],
                    'comuna': datos_agencia[2],
                    'calle': datos_agencia[3],
                    'numero': datos_agencia[4],
                    'telefono': datos_agencia[5]
                }
            else:
                errores.append("No se pudo recuperar la agencia")
            
            cursor.close()
        except Exception as e:
            errores.append(f"Error al recuperar la agencia: {str(e)}")

    elif request.method == 'POST':
        cod_agenciaAg = request.form["cod_agenciaAg"]
        nombreAg = request.form["nombreAg"]
        regionAg = request.form["regionAg"]
        comunaAg = request.form["comunaAg"]
        calleAg = request.form["calleAg"]
        numeroAg = request.form["numeroAg"]
        telefonoAg = request.form["telefonoAg"]

        print("Datos de la agencia:", cod_agenciaAg, nombreAg, regionAg, comunaAg, calleAg, numeroAg, telefonoAg)

        cursor = conexion.cursor()

        try:
            # Ejecutar el procedimiento almacenado
            cursor.callproc('ACTUALIZAR_AGENCIA', (cod_agenciaAg, nombreAg, regionAg, comunaAg, calleAg, numeroAg, telefonoAg))

            # Obtener el mensaje de salida del procedimiento
            for result in cursor.stored_results():
                mensaje = result.fetchone()[0]

            print("Mensaje actualizar agencia:", mensaje)
            cursor.close()
        except Exception as e:
            errores.append(f"Error al actualizar la agencia: {str(e)}")

    else:
        return '<h1>Método no permitido</h1>'

    return render_template('Admin/agencia/actualizar_agencia.html', mensaje=mensaje, errores=errores, agencia=agencia)

@privado_bp.route('/eliminar_agencia',methods=['GET','POST'])
def eliminar_agencia():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        cod_ag_act=request.form.get("cod_ag_act")
        print("codigo a eliminar",cod_ag_act)

        try:
            cursor = conexion.cursor()
            cursor.execute("SET @MENSAJE = '';")
            cursor.execute("CALL ELIMINAR_AGENCIA(%s, @MENSAJE);", (cod_ag_act,))
            cursor.execute("SELECT @MENSAJE;")
            mensaje = cursor.fetchone()[0]
            print("Mensaje:", mensaje)
            conexion.commit()
        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Admin/agencia/eliminar_agencia.html',mensaje=mensaje, errores=errores)


@privado_bp.route('/eliminar_cuenta',methods=['GET','POST'])    #conexion2
def eliminar_cuenta():  
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':

        cursor = conexion.cursor()

        mensaje= cursor.var(str)
        try:
            cursor.execute('CALL PROYECTOFINAL.ELIMINAR_CLIENTE(:RUT_ELI,:MENSAJE)',[current_user.rut,mensaje])
            conexion.commit()
        except:
            errores.append('Error al eliminar')
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('usuario/eliminar_cuenta.html',mensaje=mensaje,errores=errores)



@privado_bp.route('/compra_pasaje', methods=['GET', 'POST'])  #conexion2
def compra_pasaje():
    if current_user.is_authenticated:
        mensaje = ""
        errores = []
        filas = []  # Inicializamos la variable

        cursor=conexion.cursor()
        if request.method == 'GET':
            print("A traves del metodo get")

            cursor.execute('SELECT * FROM VUELOS_DE')
            filas = cursor.fetchall()
        elif request.method == 'POST':
          
                rutP = current_user.rut
                cod_vuelo = request.form["cod_vuelo"]
                nAsi = request.form["nAsi"]
                fVuelo = request.form["fVuelo"]
                tarj = request.form["tarj"]
                cvv = request.form["cvv"]
                print("Datos de compra:", rutP, cod_vuelo, nAsi, fVuelo, tarj, cvv)
                
                mensaje = cursor.var(str)

                cursor.execute('SELECT * FROM VUELOS_DE')
                filas = cursor.fetchall()
                try:

                # Obtener el precio del vuelo antes de la llamada al procedimiento
                    cursor.execute('SELECT VALOR FROM VUELO WHERE COD_VUELO = :COD_VUELO', [cod_vuelo])
                    resultado = cursor.fetchone()
                
                    if resultado:
                        total_pago = resultado[0]  # Extraer el precio del vuelo
                    else:
                        total_pago = 0  # Si no se encuentra, poner 0 o manejar un error

                # Llamar al procedimiento almacenado con el total del pago obtenido
                    cursor.execute(
                        'CALL COMPRA_PASAJE(:RUT_PER, :COD_VUELO_COM, :N_ASIENTO, :FECHA_VUELO, :TIPO_PAGO_EN, :TOTALPAGO, :TARJETA_E, :CVV_E, :MENSAJE)',
                        [rutP, cod_vuelo, nAsi, fVuelo, 1, total_pago, tarj, cvv, mensaje]
                    )

                # Insertar en el carrito de compras con el mismo total del pago
                    cursor.execute(
                        'CALL INSERTAR_CARRITO(:RUT_CLIENTE, :COD_VUELO_C, :TOTALPAGO)',
                        [current_user.rut, cod_vuelo, total_pago]
                    )
    
                    cursor.execute(
                        'SELECT * FROM VISTA_PASAJES WHERE RUT_CLIENTE=:RUT AND COD_VUELO=:VUELO AND N_ASIENTO=:ASI AND TIPO_PAGO=:PAGO',
                        [rutP, cod_vuelo, nAsi, 1]
                    )
                    res = cursor.fetchone()
                    conexion.commit()

                    # Generar código QR
                    qr = qrcode.QRCode(version=1, box_size=15, border=5)
                    qr.add_data(res)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    img.save('static/imagen/codQR.png')

                    
                except:
                    errores.append('Error al comprar')
                cursor.close()
        else:
            return '<h1>Metodo no encontrado</h1>'

        return render_template('Compra/pasaje.html',mensaje=mensaje,errores=errores,filas=filas)
    else:
        return render_template("salida_errores.html")

@privado_bp.route('/ingresar_encuesta',methods=['GET','POST'])  #conexion2
def ingresar_encuesta():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        rut_cl=current_user.rut
        cod_p=request.form["cod_p"]
        ate=request.form["ate"]
        cal=request.form["cal"]
        rap=request.form["rap"]

        cursor = conexion.cursor()
        cursor2 = conexion.cursor()
        mensaje= cursor.var(str)
        try:
            cursor2.execute('SELECT COD_PASAJE FROM PASAJE WHERE RUT_CLIENTE=:RUT',[rut_cl])
            res=cursor2.fetchone()
            res=str(res[0])
            cursor.execute('CALL A_ENCUESTA(:RUT_CLI,:RUT_CLI_PAS,:COD_PASJE,:COD_PASJE_ENC,:ATENCION_EN,:CALIDAD_EN,:RAPIDEZ_EN,:MENSAJE)',[rut_cl,rut_cl,cod_p,res,ate,cal,rap,mensaje])
        except:
            errores.append("¡Ups! Ha ocurrido un error. Asegurece de haber introducido bien los datos")
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('usuario/ingresar_encuesta.html',mensaje=mensaje,errores=errores)


@privado_bp.route('/pagar',methods=['GET','POST']) 
def pagar():
    mensaje=""
    errores=[]
    if request.method == 'GET':
        print("A traves del metodo get")
    elif request.method == 'POST':
        tarj=request.form["tarj"]
        cvv=request.form["cvv"]

        cursor = conexion.cursor()

        mensaje= cursor.var(str)
        try:
            cursor.execute('CALL PAGO(:RUT_C_EN,:TARJETA_E,:CVV_E,:MENSAJE)',[current_user.rut,tarj,cvv,mensaje])
            conexion.commit()
        except:
            errores.append('Error al pagar')
        cursor.close()
    else:
        return '<h1>Metodo no encontrado</h1>'
    return render_template('Compra/pagar.html',mensaje=mensaje,errores=errores)

@privado_bp.route('/ticket',methods=['GET','POST']) #ver tema del ticket
def ticket():
    if(current_user.is_authenticated):
        return render_template('Compra/ticket.html')
    else:
        return render_template("salida_errores.html")

@privado_bp.route('/errores')
def errores():
    return render_template("salida_errores.html")

@privado_bp.route('/erroresAd')
def erroresAd():
    return render_template("Admin/error_admin.html")
