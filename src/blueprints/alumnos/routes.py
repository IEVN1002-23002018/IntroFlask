from flask import Blueprint, jsonify, request

from database import mysql


alumnos_bp = Blueprint(
    'alumnos',
    __name__,
    url_prefix='/api/alumnos'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


# GET: Listar alumnos
@alumnos_bp.route("/", methods=['GET'])
def listar_alumnos():

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT * FROM alumnos
        """)

        datos = cursor.fetchall()

        alumnos = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'alumnos': alumnos,
            'mensaje': 'Lista de alumnos',
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar los alumnos',
            'error': str(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# GET: Consultar un alumno
@alumnos_bp.route("/<string:matricula>", methods=['GET'])
def leer_alumno(matricula):

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT * FROM alumnos
            WHERE matricula = %s
        """, (matricula,))

        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                'mensaje': 'Alumno no encontrado',
                'exito': False
            }), 404

        alumno = fila_a_diccionario(cursor, fila)

        return jsonify({
            'alumno': alumno,
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar el alumno {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# POST: Registrar un alumno
@alumnos_bp.route('/', methods=['POST'])
def registrar_alumno():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    campos = [
        'matricula', 'nombre', 'apaterno',
        'amaterno', 'correo'
    ]

    if (
        'matricula' not in datos
        or datos['matricula'] is None
        or not str(datos['matricula']).strip()
        or any(
            campo not in datos
            or not isinstance(datos[campo], str)
            or not datos[campo].strip()
            for campo in campos[1:]
        )
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios o son inválidos',
            'exito': False
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        # Comprobar si la matrícula ya existe
        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (str(datos['matricula']).strip(),)
        )

        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'La matrícula ya existe',
                'exito': False
            }), 409

        # Insertar el registro
        cursor.execute("""
            INSERT INTO alumnos
                (matricula, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            str(datos['matricula']).strip(),
            datos['nombre'].strip(),
            datos['apaterno'].strip(),
            datos['amaterno'].strip(),
            datos['correo'].strip()
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Alumno registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            'mensaje': 'Error al registrar el alumno: {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: Modificar un alumno
@alumnos_bp.route("/<string:matricula>", methods=['PUT'])
def modificar_alumno(matricula):

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "mensaje": "No se recibieron datos para modificar"
        }), 400

    nombre = datos.get('nombre')
    apaterno = datos.get('apaterno')
    amaterno = datos.get('amaterno')
    correo = datos.get('correo')

    if (
        not isinstance(nombre, str) or not nombre.strip()
        or not isinstance(apaterno, str) or not apaterno.strip()
        or not isinstance(amaterno, str) or not amaterno.strip()
        or not isinstance(correo, str) or not correo.strip()
    ):
        return jsonify({
            "mensaje": "Todos los campos son obligatorios"
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        alumno = cursor.fetchone()

        if not alumno:
            return jsonify({
                "mensaje": "No existe un alumno con esa matrícula"
            }), 404

        sql = """
            UPDATE alumnos
            SET nombre = %s,
                apaterno = %s,
                amaterno = %s,
                correo = %s
            WHERE matricula = %s
        """

        cursor.execute(sql, (
            nombre.strip(),
            apaterno.strip(),
            amaterno.strip(),
            correo.strip(),
            matricula
        ))

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Alumno modificado correctamente",
            "matricula": matricula,
            "exito": True
        }), 200

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            "mensaje": "Error al modificar el alumno",
            "error": str(ex)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: Eliminar un alumno
@alumnos_bp.route("/<string:matricula>", methods=['DELETE'])
def eliminar_alumno(matricula):

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT matricula FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        alumno = cursor.fetchone()

        if not alumno:
            return jsonify({
                "mensaje": "No existe un alumno con esa matrícula"
            }), 404

        cursor.execute(
            "DELETE FROM alumnos WHERE matricula = %s",
            (matricula,)
        )

        mysql.connection.commit()

        return jsonify({
            "mensaje": "Alumno eliminado correctamente",
            "matricula": matricula,
            "exito": True
        }), 200

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            "mensaje": "Error al eliminar el alumno",
            "error": str(ex)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()