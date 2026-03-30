from Conexion.conexion import obtener_conexion

class ClienteService:
    @staticmethod
    def listar_clientes():
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes")
        res = cursor.fetchall()
        con.close()
        return res

    @staticmethod
    def guardar_cliente(nombre, telefono, direccion):
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("INSERT INTO clientes (nombre_cliente, telefono, direccion) VALUES (%s, %s, %s)", 
                       (nombre, telefono, direccion))
        con.commit()
        con.close()