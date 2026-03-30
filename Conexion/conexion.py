import mysql.connector

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='', # Por defecto en XAMPP está vacío
            database='floreria_db',
            port='3306' # <-- Verifica que diga 3306
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None