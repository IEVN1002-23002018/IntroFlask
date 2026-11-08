from flask import Blueprint, jsonify, request

from database import mysql


maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    return dict(zip(columnas, fila))


# GET: Listar maestros
@maestros_bp.route("/", methods=['GET'])
def listar_maestros():

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT * FROM maestros
        """)

        datos = cursor.fetchall()

        maestros = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'maestros': maestros,
            'mensaje': 'Lista de maestros',
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar los maestros',
            'error': str(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# GET: Consultar un maestro
@maestros_bp.route("/<string:idmaestro>", methods=['GET'])
def leer_maestro(idmaestro):

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT * FROM maestros
            WHERE idmaestro = %s
        """, (idmaestro,))

        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                'mensaje': 'maestro no encontrado',
                'exito': False
            }), 404

        maestro = fila_a_diccionario(cursor, fila)

        return jsonify({
            'maestro': maestro,
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar el maestro {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# POST: Registrar un maestro
@maestros_bp.route('/', methods=['POST'])
def registrar_maestro():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    campos = [
        'idmaestro', 'nombre', 'apaterno',
        'amaterno', 'correo'
    ]

    if (
        'idmaestro' not in datos
        or datos['idmaestro'] is None
        or not str(datos['idmaestro']).strip()
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
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (str(datos['idmaestro']).strip(),)
        )

        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'La matrícula ya existe',
                'exito': False
            }), 409

        # Insertar el registro
        cursor.execute("""
            INSERT INTO maestros
                (idmaestro, nombre, apaterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            str(datos['idmaestro']).strip(),
            datos['nombre'].strip(),
            datos['apaterno'].strip(),
            datos['amaterno'].strip(),
            datos['correo'].strip()
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            'mensaje': 'Error al registrar el maestro: {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: Modificar un maestro
@maestros_bp.route("/<string:idmaestro>", methods=['PUT'])
def modificar_maestro(idmaestro):

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
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        maestro = cursor.fetchone()

        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con esa matrícula"
            }), 404

        sql = """
            UPDATE maestros
            SET nombre = %s,
                apaterno = %s,
                amaterno = %s,
                correo = %s
            WHERE idmaestro = %s
        """

        cursor.execute(sql, (
            nombre.strip(),
            apaterno.strip(),
            amaterno.strip(),
            correo.strip(),
            idmaestro
        ))

        mysql.connection.commit()

        return jsonify({
            "mensaje": "maestro modificado correctamente",
            "idmaestro": idmaestro,
            "exito": True
        }), 200

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            "mensaje": "Error al modificar el maestro",
            "error": str(ex)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: Eliminar un maestro
@maestros_bp.route("/<string:idmaestro>", methods=['DELETE'])
def eliminar_maestro(idmaestro):

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        maestro = cursor.fetchone()

        if not maestro:
            return jsonify({
                "mensaje": "No existe un maestro con esa matrícula"
            }), 404

        cursor.execute(
            "DELETE FROM maestros WHERE idmaestro = %s",
            (idmaestro,)
        )

        mysql.connection.commit()

        return jsonify({
            "mensaje": "maestro eliminado correctamente",
            "idmaestro": idmaestro,
            "exito": True
        }), 200

    except Exception as ex:
        mysql.connection.rollback()

        return jsonify({
            "mensaje": "Error al eliminar el maestro",
            "error": str(ex)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()