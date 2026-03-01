import sqlite3

def crear_base():
    # Establece la conexión con el archivo (se creará automáticamente)
    conexion = sqlite3.connect('floreria.db')
    cursor = conexion.cursor()
    
    # Crear la tabla 'arreglos' con los campos necesarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS arreglos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    
    # Insertar unos datos iniciales para que el catálogo no esté vacío
    arreglos_iniciales = [
        ('Caja Corazón', 10, 45.0, '9 Rosas rojas eternas en caja de lujo.'),
        ('Cúpula Encantada', 5, 35.0, 'Rosa azul preservada inspirada en cuentos.'),
        ('Arreglo Premium Gold', 3, 60.0, 'Rosas blancas con detalles en pan de oro.')
    ]
    
    cursor.executemany('''
        INSERT INTO arreglos (nombre, cantidad, precio, descripcion) 
        VALUES (?, ?, ?, ?)
    ''', arreglos_iniciales)
    
    conexion.commit()
    conexion.close()
    print("✅ Base de datos 'floreria.db' creada y cargada con éxito.")

if __name__ == "__main__":
    crear_base()