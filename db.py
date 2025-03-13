import mysql.connector



def conectar_bd(host="localhost", user="root", password="nancy2015", database="super1"):
    """
    Establece una conexión a una base de datos MySQL.

    Args:
        host (str): El host de la base de datos MySQL.
        user (str): El nombre de usuario de la base de datos MySQL.
        password (str): La contraseña de la base de datos MySQL.
        database (str): El nombre de la base de datos MySQL.

    Returns:
        mysql.connector.connection.MySQLConnection: Un objeto de conexión si la conexión es exitosa, o None si falla.
    """
    try:
        conexion = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos MySQL: {err}")
        return None

