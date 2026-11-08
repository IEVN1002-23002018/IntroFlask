from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from database import mysql
from blueprints.alumnos.routes import alumnos_bp
from blueprints.maestros.routes import maestros_bp

from config import config

app = Flask(__name__)

# Configuración
app.config.from_object(config['development'])

# Conexión a MySQL
con = mysql
con.init_app(app)

# CORS
CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:4200"
    }
})

# Registrar blueprints
app.register_blueprint(alumnos_bp)
app.register_blueprint(maestros_bp)


def pagina_no_encontrada(error):
    return "<h1>Pagina no encontrada</h1>", 404


app.register_error_handler(404, pagina_no_encontrada)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)