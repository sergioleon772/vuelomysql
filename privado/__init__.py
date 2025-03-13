from flask import Blueprint

# Crear Blueprint
privado_bp = Blueprint('privado', __name__)

from . import rutas  # Importa después de definir el Blueprint
