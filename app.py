import os
import json
import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS Y PERSISTENCIA (Semana 12) ---
# Definimos la ruta absoluta para evitar el error "unable to open database file"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'inventario', 'data')
DB_PATH = os.path.join(DATA_DIR, 'floreria.db')

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS (ORM) ---
class Arreglo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)

# Crear carpetas y base de datos automáticamente al iniciar
with app.app_context():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    db.create_all()

# --- FUNCIONES DE PERSISTENCIA EN ARCHIVOS (Semana 12) ---
def guardar_en_archivos_locales(nombre, cantidad, precio, descripcion):
    # 1. Guardar en TXT
    with open(os.path.join(DATA_DIR, 'datos.txt'), 'a', encoding='utf-8') as f:
        f.write(f"Nombre: {nombre} | Stock: {cantidad} | Precio: ${precio}\n")

    # 2. Guardar en JSON (Librería json)
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

    # 3. Guardar en CSV (Librería csv)
    with open(os.path.join(DATA_DIR, 'datos.csv'), 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([nombre, cantidad, precio, descripcion])

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    # Consulta usando el ORM
    productos = Arreglo.query.all()
    return render_template('catalogo.html', productos=productos)

@app.route('/datos') # RUTA DE VISUALIZACIÓN DE ARCHIVOS
def mostrar_datos():
    archivo_json = os.path.join(DATA_DIR, 'datos.json')
    registros = []
    if os.path.exists(archivo_json) and os.path.getsize(archivo_json) > 0:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            registros = json.load(f)
    return render_template('datos.html', arreglos=registros)

# --- RUTAS CRUD ACTUALIZADAS ---

@app.route('/guardar_arreglo', methods=['POST'])
def guardar_arreglo():
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    precio = float(request.form['precio'])
    descripcion = request.form['descripcion']
    
    # Persistencia en Base de Datos
    nuevo_arreglo = Arreglo(nombre=nombre, cantidad=cantidad, precio=precio, descripcion=descripcion)
    db.session.add(nuevo_arreglo)
    db.session.commit()
    
    # Persistencia en Archivos Locales
    guardar_en_archivos_locales(nombre, cantidad, precio, descripcion)
    
    return redirect(url_for('catalogo'))

@app.route('/editar/<int:id>')
def editar(id):
    producto = Arreglo.query.get_or_404(id)
    return render_template('editar.html', producto=producto)

@app.route('/actualizar_arreglo', methods=['POST'])
def actualizar_arreglo():
    id_arreglo = request.form['id']
    arreglo = Arreglo.query.get(id_arreglo)
    
    arreglo.nombre = request.form['nombre']
    arreglo.cantidad = int(request.form['cantidad'])
    arreglo.precio = float(request.form['precio'])
    arreglo.descripcion = request.form['descripcion']
    
    db.session.commit()
    return redirect(url_for('catalogo'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    arreglo = Arreglo.query.get_or_404(id)
    db.session.delete(arreglo)
    db.session.commit()
    return redirect(url_for('catalogo'))

@app.route('/buscar')
def buscar():
    query = request.args.get('query')
    # Búsqueda filtrada con SQLAlchemy
    productos = Arreglo.query.filter(Arreglo.nombre.like(f'%{query}%')).all()
    return render_template('catalogo.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)