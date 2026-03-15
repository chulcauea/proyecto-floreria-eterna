import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",        # Tu usuario de MySQL
            password="",        # Tu contraseña (deja vacío si no tienes)
            database="floreria_db" # Nombre de tu base de datos
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
        return None