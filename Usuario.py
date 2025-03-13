from flask_login import UserMixin


class Usuario(UserMixin):
    def __init__(self, nombre, rut, telefono, role="user"):  
        self.id = rut  # Flask-Login usa `id` para identificar al usuario
        self.rut = rut
        self.nombre = nombre
        self.telefono = telefono  # La contraseña será el número de teléfono
        self.role = role  # Nuevo campo para definir el rol
