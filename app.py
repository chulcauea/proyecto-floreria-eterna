import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- REQUISITO POO: Clase para gestionar el Inventario ---
class InventarioDB:
    def __init__(self, db_name='floreria.db'):
        self.db_name = db_name

    def conectar(self):
        conexion = sqlite3.connect(self.db_name)
        conexion.row_factory = sqlite3.Row
        return conexion

    def obtener_todos(self):
        con = self.conectar()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM arreglos')
        productos = cursor.fetchall()
        con.close()
        return productos

# Instanciamos nuestra clase de POO
gestion_flores = InventarioDB()

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/nosotros')
def acerca_de():
    return render_template('about.html')

# --- RUTAS CRUD (INTEGRADAS) ---

@app.route('/catalogo')
def catalogo():
    productos = gestion_flores.obtener_todos()
    return render_template('catalogo.html', productos=productos)

@app.route('/agregar_arreglo')
def agregar_arreglo():
    return render_template('agregar.html')

@app.route('/guardar_arreglo', methods=['POST'])
def guardar_arreglo():
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    
    con = gestion_flores.conectar()
    cursor = con.cursor()
    cursor.execute('''
        INSERT INTO arreglos (nombre, cantidad, precio, descripcion) 
        VALUES (?, ?, ?, ?)
    ''', (nombre, cantidad, precio, descripcion))
    con.commit()
    con.close()
    return redirect(url_for('catalogo'))

# NUEVA RUTA: Para cargar los datos en el formulario de editar
@app.route('/editar/<int:id>')
def editar(id):
    con = gestion_flores.conectar()
    cursor = con.cursor()
    cursor.execute('SELECT * FROM arreglos WHERE id = ?', (id,))
    producto = cursor.fetchone()
    con.close()
    return render_template('editar.html', producto=producto)

# NUEVA RUTA: Para guardar los cambios editados
@app.route('/actualizar_arreglo', methods=['POST'])
def actualizar_arreglo():
    id = request.form['id']
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    precio = request.form['precio']
    descripcion = request.form['descripcion']
    
    con = gestion_flores.conectar()
    cursor = con.cursor()
    cursor.execute('''
        UPDATE arreglos 
        SET nombre=?, cantidad=?, precio=?, descripcion=? 
        WHERE id=?
    ''', (nombre, cantidad, precio, descripcion, id))
    con.commit()
    con.close()
    return redirect(url_for('catalogo'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    con = gestion_flores.conectar()
    cursor = con.cursor()
    cursor.execute('DELETE FROM arreglos WHERE id = ?', (id,))
    con.commit()
    con.close()
    return redirect(url_for('catalogo'))

@app.route('/buscar')
def buscar():
    query = request.args.get('query')
    con = gestion_flores.conectar()
    cursor = con.cursor()
    cursor.execute('SELECT * FROM arreglos WHERE nombre LIKE ?', ('%' + query + '%',))
    productos = cursor.fetchall()
    con.close()
    return render_template('catalogo.html', productos=productos)

@app.route('/arreglo/<cliente>')
def detalle_arreglo(cliente):
    return render_template('index.html', usuario=cliente)

# --- INICIO DE LA APP ---
if __name__ == '__main__':
    app.run(debug=True)