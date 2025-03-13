import mysql.connector



def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host="switchback.proxy.rlwy.net",
            user="root",
            password="OvWAktvtspaRXVskSNaNLyftQfIENDKa",
            database="railway"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos MySQL: {err}")
        return None

