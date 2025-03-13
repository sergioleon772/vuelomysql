import cx_Oracle
from flask import render_template, url_for, redirect, request
from flask_login import current_user, login_user, logout_user
from Usuario import Usuario
from . import autenticacion_bp  # Importar el blueprint localmente
from db import conectar_bd


@autenticacion_bp.route('/iniciar_sesion', methods=["POST", "GET"])   
def iniciar_sesion():
    global conexion  # Agregar esta línea para declarar que vas a usar la variable global

    errores = []
    
    if current_user.is_authenticated:
        print("El usuario ya está dentro del sistema")
        return redirect(url_for("inicio"))
    else:
        print("El usuario no está dentro del sistema")
        if request.method == "POST":
            rutU = request.form["rutU"]
            tel = request.form["tel"]
            
            # Verifica si conexion2 está activa
            if conexion is None:
                # Si conexion2 no está activa, intenta establecerla
                conexion = conectar_bd() 

                if conexion is None:
                    # Si la conexión no se puede establecer, retorna un error
                    print("Error al conectar con la base de datos")
                    errores.append("No se pudo conectar con la base de datos.")
                    return render_template("autenticacion/iniciar_sesion.html", errores=errores)
            
            try:
                # Intenta obtener el cursor y ejecutar la consulta
                cur = conexion.cursor()
                cur.execute('SELECT NOMBRE, RUT_CLIENTE FROM CLIENTE WHERE RUT_CLIENTE=:RUT AND TELEFONO=:TEL', [rutU, tel])
                res = cur.fetchone()
                print(res)
            except Exception as e:
                # Manejo de errores si algo falla al ejecutar la consulta
                print(f"Error al ejecutar la consulta: {e}")
                return redirect(url_for('privado.errores'))
            
            if res is None:
                errores.append("Usuario no existente o inválido")
            else:
                # Si la consulta tiene resultados, realiza el login
                login_user(Usuario(res[0], res[1]))
                print("Usuario Ingresó")
                return redirect(url_for('index2'))

    return render_template("autenticacion/iniciar_sesion.html", errores=errores)


@autenticacion_bp.route('/iniciar_sesionAd', methods=["POST", "GET"])   # conexion2
def iniciar_sesionAd():
    errores = []
    
    if current_user.is_authenticated:
        print("El usuario ya está dentro del sistema")
        return redirect(url_for("inicio"))
    else:
        print("El usuario no está dentro del sistema")
        if request.method == "POST":
            rutU = request.form["rutU"]
            tel = request.form["tel"]
            cur = conexion.cursor()
            try:
                cur.execute('SELECT NOMBRE, RUT_CLIENTE, TELEFONO FROM CLIENTE WHERE RUT_CLIENTE=:RUT AND TELEFONO=:TEL', [rutU, tel])
                res = cur.fetchone()
                print(res)
            except:
                return redirect(url_for('privado.errores'))
            if res == None:
                errores.append("Usuario no existente o inválido")
            else:
                if res[1] == 201437067:
                    login_user(Usuario(res[0], res[1], res[2]))
                    print("Usuario Ingresó")
                    return redirect(url_for('publico.vista_clientes'))
                else:
                    return redirect(url_for('privado.erroresAd'))

    return render_template("admin1.html", errores=errores)

@autenticacion_bp.route("/cerrar_sesion")
def cerrar_sesion():
    if current_user.is_authenticated:
        logout_user()
        print("Usuario Salio")
    return redirect(url_for("inicio"))

@autenticacion_bp.route("/cerrar_sesionAd")
def cerrar_sesionAd():
    if current_user.is_authenticated:
        logout_user()
        print("Usuario Salio")
    return redirect(url_for("privado.admin"))
