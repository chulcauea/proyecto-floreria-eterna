from flask import Flask

app = Flask(__name__)

# Ruta principal: Presentación del negocio
@app.route('/')
def inicio():
    return """
    <h1>Bienvenido a  Floristería y arreglos personalizados </h1>
    <p>Creamos momentos inolvidables con nuestras exclusivas rosas eternas.</p>
    <hr>
    <h3>Nuestros Servicios:</h3>
    <ul>
        <li>Arreglos personalizados</li>
        <li>Cajas de rosas preservadas</li>
        <li>Detalles para eventos especiales</li>
    </ul>
    """

# Ruta dinámica: Detalles del arreglo personalizado
@app.route('/arreglo/<cliente>')
def detalle_arreglo(cliente):
    # Simulamos que el sistema reconoce al cliente para su pedido de rosas eternas
    return f"""
    <h2>Pedido de: {cliente.capitalize()}</h2>
    <p>Estado: <b>En proceso de diseño.</b></p>
    <p>Detalle: Arreglo personalizado con Rosas Eternas Premium.</p>
    <p>Gracias por confiar en Eterna Flor para tu regalo especial.</p>
    """

if __name__ == '__main__':
    app.run(debug=True)