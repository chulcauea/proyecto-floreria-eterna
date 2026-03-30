from Conexion.conexion import obtener_conexion

class ProductoService:
    
    @staticmethod
    def listar_todos():
        con = obtener_conexion()
        if con:
            cursor = con.cursor(dictionary=True)
            # Usamos la tabla 'arreglos' para todo el proyecto
            cursor.execute("SELECT * FROM arreglos") 
            productos = cursor.fetchall()
            con.close()
            return productos
        return []

    @staticmethod
    def crear_producto(nombre, precio, cantidad, descripcion):
        con = obtener_conexion()
        if con:
            try:
                cursor = con.cursor()
                sql = "INSERT INTO arreglos (nombre, precio, cantidad, descripcion) VALUES (%s, %s, %s, %s)"
                values = (nombre, precio, cantidad, descripcion)
                cursor.execute(sql, values)
                con.commit()
                con.close()
                return True
            except Exception as e:
                print(f"Error al insertar: {e}")
                return False
        return False

    @staticmethod
    def eliminar(id_producto):
        con = obtener_conexion()
        if con:
            cursor = con.cursor()
            # Eliminamos directamente de la tabla 'arreglos'
            cursor.execute("DELETE FROM arreglos WHERE id = %s", (id_producto,))
            con.commit()
            con.close()

    @staticmethod
    def buscar_productos(query):
        con = obtener_conexion()
        if con:
            cursor = con.cursor(dictionary=True)
            # Buscador para el catálogo
            sql = "SELECT * FROM arreglos WHERE nombre LIKE %s OR descripcion LIKE %s"
            values = (f"%{query}%", f"%{query}%")
            cursor.execute(sql, values)
            resultados = cursor.fetchall()
            con.close()
            return resultados
        return []

    @staticmethod
    def obtener_por_id(id_producto):
        con = obtener_conexion()
        if con:
            cursor = con.cursor(dictionary=True)
            # Buscamos por ID para cargar los datos en el formulario de edición
            cursor.execute("SELECT * FROM arreglos WHERE id = %s", (id_producto,))
            producto = cursor.fetchone()
            con.close()
            return producto
        return None

    @staticmethod
    def actualizar(id_prod, nombre, precio, cantidad, descripcion):
        con = obtener_conexion()
        if con:
            try:
                cursor = con.cursor()
                # Actualiza los datos del arreglo editado en MySQL
                sql = """
                    UPDATE arreglos 
                    SET nombre = %s, precio = %s, cantidad = %s, descripcion = %s 
                    WHERE id = %s
                """
                cursor.execute(sql, (nombre, precio, cantidad, descripcion, id_prod))
                con.commit()
                con.close()
                return True
            except Exception as e:
                print(f"Error al actualizar: {e}")
                return False
        return False