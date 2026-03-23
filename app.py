import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for, flash
# NUEVAS IMPORTACIONES PARA SEMANA 14
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# Importamos la conexión desde tu carpeta Conexion
from Conexion.conexion import obtener_conexion

app = Flask(__name__)
app.secret_key = 'clave_secreta_eterna_flor_2026' # Necesaria para sesiones y mensajes flash

# --- CONFIGURACIÓN DE FLASK-LOGIN (Semana 14) ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Nombre de la función que maneja el inicio de sesión

# Modelo de Usuario para Flask-Login
class Usuario(UserMixin):
    def __init__(self, id, nombre, email):
        self.id = id
        self.nombre = nombre
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    con = obtener_conexion()
    if con:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
        user_data = cursor.fetchone()
        con.close()
        if user_data:
            return Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'])
    return None

# --- CONFIGURACIÓN DE RUTAS PARA ARCHIVOS (Semana 12) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'inventario', 'data')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# --- FUNCIONES DE PERSISTENCIA EN ARCHIVOS (Semana 12) ---
def guardar_en_archivos_locales(nombre, cantidad, precio, descripcion):
    # 1. TXT
    with open(os.path.join(DATA_DIR, 'datos.txt'), 'a', encoding='utf-8') as f:
        f.write(f"Nombre: {nombre} | Stock: {cantidad} | Precio: ${precio}\n")

    # 2. JSON
    archivo_json = os.path.join(DATA_DIR, 'datos.json')
    datos_json = []
    if os.path.exists(archivo_json) and os.path.getsize(archivo_json) > 0:
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
        except json.JSONDecodeError:
            datos_json = []
    datos_json.append({"nombre": nombre, "cantidad": cantidad, "precio": precio})
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump(datos_json, f, indent=4)

    # 3. CSV
    with open(os.path.join(DATA_DIR, 'datos.csv'), 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([nombre, cantidad, precio, descripcion])

# --- RUTAS DE AUTENTICACIÓN (Semana 14) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        con = obtener_conexion()
        if con:
            cursor = con.cursor(dictionary=True)
            # Buscamos usuario con ese correo y esa clave
            cursor.execute("SELECT * FROM usuarios WHERE mail = %s AND password = %s", (email, password))
            user_data = cursor.fetchone()
            con.close()

            if user_data:
                user_obj = Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'])
                login_user(user_obj)
                return redirect(url_for('catalogo'))
            else:
                flash('Correo o contraseña incorrectos. Intente de nuevo.')
                
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('login'))

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
@login_required # PROTEGIDA: Solo usuarios logueados pueden ver el inventario
def catalogo():
    con = obtener_conexion()
    productos = []
    usuarios = []
    if con:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM arreglos")
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        con.close()
    return render_template('catalogo.html', productos=productos, usuarios=usuarios)

@app.route('/datos')
@login_required # PROTEGIDA
def mostrar_datos():
    archivo_json = os.path.join(DATA_DIR, 'datos.json')
    registros = []
    if os.path.exists(archivo_json) and os.path.getsize(archivo_json) > 0:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            registros = json.load(f)
    return render_template('datos.html', arreglos=registros)

# --- RUTAS CRUD ARREGLOS (MySQL) ---

@app.route('/guardar_arreglo', methods=['POST'])
@login_required # PROTEGIDA
def guardar_arreglo():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    descripcion = request.form['descripcion']
    
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        sql = "INSERT INTO arreglos (nombre, cantidad, precio, descripcion) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nombre, cantidad, precio, descripcion))
        con.commit()
        con.close()
    
    guardar_en_archivos_locales(nombre, cantidad, precio, descripcion)
    return redirect(url_for('catalogo'))

@app.route('/editar/<int:id>')
@login_required # PROTEGIDA
def editar(id):
    con = obtener_conexion()
    producto = None
    if con:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM arreglos WHERE id = %s", (id,))
        producto = cursor.fetchone()
        con.close()
    return render_template('editar.html', producto=producto)

@app.route('/actualizar_arreglo', methods=['POST'])
@login_required # PROTEGIDA
def actualizar_arreglo():
    id_arreglo = request.form['id']
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    descripcion = request.form['descripcion']
    
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        sql = "UPDATE arreglos SET nombre=%s, cantidad=%s, precio=%s, descripcion=%s WHERE id=%s"
        cursor.execute(sql, (nombre, cantidad, precio, descripcion, id_arreglo))
        con.commit()
        con.close()
    return redirect(url_for('catalogo'))

@app.route('/eliminar/<int:id>')
@login_required # PROTEGIDA
def eliminar(id):
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM arreglos WHERE id = %s", (id,))
        con.commit()
        con.close()
    return redirect(url_for('catalogo'))

@app.route('/buscar')
@login_required # PROTEGIDA
def buscar():
    query = request.args.get('query')
    con = obtener_conexion()
    productos = []
    usuarios = []
    if con:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM arreglos WHERE nombre LIKE %s", (f'%{query}%',))
        productos = cursor.fetchall()
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        con.close()
    return render_template('catalogo.html', productos=productos, usuarios=usuarios)

# --- CRUD USUARIOS (Semana 13) ---

@app.route('/guardar_usuario', methods=['POST'])
@login_required # PROTEGIDA (Solo alguien logueado puede crear más usuarios)
def guardar_usuario():
    nombre = request.form['nombre']
    mail = request.form['mail']
    password = request.form['password']
    
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        sql = "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, mail, password))
        con.commit()
        con.close()
    return redirect(url_for('catalogo'))

@app.route('/eliminar_usuario/<int:id>')
@login_required # PROTEGIDA
def eliminar_usuario(id):
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        con.commit()
        con.close()
    return redirect(url_for('catalogo'))

if __name__ == '__main__':
    app.run(debug=True)