import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from Conexion.conexion import obtener_conexion
from fpdf import FPDF 

# --- IMPORTACIÓN DE SERVICIOS ---
from services.producto_service import ProductoService
from services.cliente_service import ClienteService

app = Flask(__name__)
app.secret_key = 'clave_secreta_eterna_flor_2026'

# --- CONFIGURACIÓN DE FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = None 

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

# --- GENERACIÓN DE REPORTES PDF ---
@app.route('/reporte_pdf')
@login_required
def reporte_pdf():
    productos = ProductoService.listar_todos()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "REPORTE DE INVENTARIO - ETERNA FLOR", ln=True, align='C')
    pdf.ln(10)
    
    # Encabezados
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(15, 10, "ID", 1)
    pdf.cell(85, 10, "Nombre del Arreglo", 1)
    pdf.cell(40, 10, "Cantidad", 1)
    pdf.cell(40, 10, "Precio", 1)
    pdf.ln()

    # Datos
    pdf.set_font("Arial", size=12)
    for p in productos:
        pdf.cell(15, 10, str(p['id']), 1)
        pdf.cell(85, 10, p['nombre'], 1)
        pdf.cell(40, 10, str(p['cantidad']), 1)
        pdf.cell(40, 10, f"${p['precio']}", 1)
        pdf.ln()

    path_pdf = os.path.join(os.path.abspath(os.path.dirname(__file__)), "reporte_inventario.pdf")
    pdf.output(path_pdf)
    return send_file(path_pdf, as_attachment=True)

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = obtener_conexion()
        if con:
            cursor = con.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE mail = %s AND password = %s", (email, password))
            user_data = cursor.fetchone()
            con.close()
            if user_data:
                user_obj = Usuario(user_data['id_usuario'], user_data['nombre'], user_data['mail'])
                login_user(user_obj)
                return redirect(url_for('catalogo'))
        flash('Correo o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- CRUD PRODUCTOS (CATALOGO CON BUSCADOR) ---

@app.route('/catalogo')
@login_required
def catalogo():
    query = request.args.get('query')
    if query:
        productos = ProductoService.buscar_productos(query)
    else:
        productos = ProductoService.listar_todos()
        
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    con.close()
    return render_template('catalogo.html', productos=productos, usuarios=usuarios)

@app.route('/buscar', methods=['GET'])
@login_required
def buscar():
    query = request.args.get('query', '')
    return redirect(url_for('catalogo', query=query))

@app.route('/guardar_arreglo', methods=['POST'])
@login_required
def guardar_arreglo():
    try:
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        descripcion = request.form['descripcion']
        ProductoService.crear_producto(nombre, precio, cantidad, descripcion)
        flash('🌸 Arreglo guardado con éxito.')
    except Exception as e:
        flash(f'❌ Error al guardar: {e}')
    return redirect(url_for('catalogo'))

# --- RUTAS DE EDICIÓN (CORREGIDAS) ---

@app.route('/editar/<int:id>')
@login_required
def editar(id):
    # Usamos el servicio corregido que consulta a la tabla 'arreglos'
    producto = ProductoService.obtener_por_id(id)
    
    if producto:
        return render_template('editar.html', producto=producto)
    else:
        flash("❌ El arreglo no existe.")
        return redirect(url_for('catalogo'))

@app.route('/actualizar_arreglo', methods=['POST'])
@login_required
def actualizar_arreglo():
    try:
        id_prod = request.form['id']
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        descripcion = request.form['descripcion']
        
        # Usamos el servicio corregido que hace el UPDATE en la tabla 'arreglos'
        exito = ProductoService.actualizar(id_prod, nombre, precio, cantidad, descripcion)
        
        if exito:
            flash('🌸 Arreglo actualizado correctamente.')
        else:
            flash('❌ No se pudo actualizar el arreglo.')
            
    except Exception as e:
        flash(f'❌ Error al actualizar: {e}')
    
    return redirect(url_for('catalogo'))

@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    ProductoService.eliminar(id)
    flash('Producto eliminado correctamente.')
    return redirect(url_for('catalogo'))

# --- GESTIÓN DE CLIENTES ---

@app.route('/clientes')
@login_required
def gestion_clientes():
    lista_clientes = ClienteService.listar_clientes()
    return render_template('clientes.html', clientes=lista_clientes)

@app.route('/guardar_cliente', methods=['POST'])
@login_required
def guardar_cliente():
    ClienteService.guardar_cliente(
        request.form['nombre'], 
        request.form['telefono'], 
        request.form['direccion']
    )
    flash('👤 Cliente registrado con éxito.')
    return redirect(url_for('gestion_clientes'))

# --- GESTIÓN DE USUARIOS (PERSONAL) ---

@app.route('/guardar_usuario', methods=['POST'])
@login_required
def guardar_usuario():
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)", 
                       (request.form['nombre'], request.form['mail'], request.form['password']))
        con.commit()
        con.close()
        flash('✅ Usuario del sistema registrado.')
    return redirect(url_for('catalogo'))

@app.route('/eliminar_usuario/<int:id>')
@login_required
def eliminar_usuario(id):
    con = obtener_conexion()
    if con:
        cursor = con.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id,))
        con.commit()
        con.close()
        flash('🗑️ Acceso de usuario revocado.')
    return redirect(url_for('catalogo'))

if __name__ == '__main__':
    app.run(debug=True)