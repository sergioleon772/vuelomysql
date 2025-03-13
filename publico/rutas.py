from flask import render_template, url_for, redirect, request,session,flash
from flask_login import current_user,login_user,logout_user

from . import publico_bp

from ejecutar import conexion



@publico_bp.route('/vista_origen')
def vista_origen():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_DATO')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/viaje/ver_origenes.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')

@publico_bp.route('/vista_destino')
def vista_destino():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_DATO2')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/viaje/ver_destinos.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')

@publico_bp.route('/vista_clientes')
def vista_clientes():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_CLIENTES')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/cliente/ver_clientes.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')
        
@publico_bp.route('/vista_vuelo')
def vista_vuelo():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_VUELOS')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/vuelo/ver_vuelo.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')

@publico_bp.route('/vista_agencia')
def vista_agencia():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_AGENCIAS')
            rows=cur.fetchall()
            cur.close()
            print("consulta agencia:",rows)
            return render_template('Admin/agencia/ver_agencia.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except Exception as e:
        print(f"Error en vista_agencia: {e}")
    return render_template('Admin/error_admin.html')

@publico_bp.route('/vista_itinerario')
def vista_itinerario():
    try:
        if(current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_ITINERARIOS')
            rows=cur.fetchall()
            cur.close()
            
            return render_template('Admin/itinerario/ver_itinerario.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')

@publico_bp.route('/vista_encuesta')
def vista_encuesta():
    try:
        if (current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_ENCUESTAS')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/cliente/vista_enc.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')



@publico_bp.route('/vista_pasajes')
def vista_pasajes():
    try:
        if (current_user.is_authenticated and current_user.role=="admin"):
            cur=conexion.cursor()
            cur.execute('SELECT * FROM VISTA_PASAJES')
            rows=cur.fetchall()
            cur.close()
            print(rows)
            return render_template('Admin/compra/vista_pasajes.html',filas=rows)
        else:
            return render_template('Admin/error_admin.html')
    except:
        return render_template('Admin/error_admin.html')

@publico_bp.route('/compra_pasaje') #conexion2
def compra_pasaje():
    cur=conexion.cursor()
    cur.execute('SELECT * FROM VUELOS_DE')
    rows=cur.fetchall()
    cur.close()
    print(rows)
    return render_template('Compra/pasaje.html',filas=rows)

@publico_bp.route('/ver_info_cliente') #conexion2
def ver_info_cliente():
    cur=conexion.cursor()
    print(current_user.rut)
    cur.execute('SELECT * FROM VISTA_CLIENTES WHERE RUT_CLIENTE=%s',(current_user.rut,))
    rows=cur.fetchall()
    cur.close()
    print(rows)
    return render_template('usuario/info_cliente.html',filas=rows)


@publico_bp.route('/vista_vuelos_index')    #conexion3
def vista_vuelos_index():
    cur=conexion.cursor()
    cur2=conexion.cursor()
    cur3=conexion.cursor()
    cur4=conexion.cursor()
    cur5=conexion.cursor()
    cur6=conexion.cursor()
    cur.execute('SELECT * FROM VUELOS')
    cur2.execute('SELECT * FROM SUPER.VUELO_T WHERE COD_VUELO=1005')
    cur3.execute('SELECT * FROM SUPER.VUELO_T WHERE COD_VUELO=1014')
    cur4.execute('SELECT * FROM SUPER.VUELO_T WHERE COD_VUELO=1015')
    cur5.execute('SELECT * FROM SUPER.VUELO_T WHERE COD_VUELO=1016')
    cur6.execute('SELECT * FROM SUPER.VUELO_T WHERE COD_VUELO=1017')
    rows=cur.fetchall()
    temuco=cur2.fetchall()
    talca=cur3.fetchall()
    arica=cur4.fetchall()
    rancagua=cur5.fetchall()
    isla=cur6.fetchall()
    cur.close()
    print(rows)
    return render_template('Vuelo/vista_vuelo_index.html',filas=rows,temuco=temuco,talca=talca,arica=arica,rancagua=rancagua,isla=isla)



