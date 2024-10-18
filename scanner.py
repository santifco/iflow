import streamlit as st
import streamlit.components.v1 as components

# Título de la aplicación
st.title("Lector de códigos de barras con html5-qrcode")

# Instrucciones
st.write("Coloca el código de barras delante de la cámara para escanearlo.")

# Crear un bloque HTML/JavaScript para leer el código de barras usando html5-qrcode
html_code = """
<html>
  <head>
    <!-- Incluir la librería html5-qrcode -->
    <script src="https://unpkg.com/html5-qrcode/minified/html5-qrcode.min.js"></script>
  </head>
  <body>
    <div id="qr-reader" style="width: 500px"></div>
    <div id="qr-reader-results"></div>
    
    <script>
      function onScanSuccess(decodedText, decodedResult) {
        // Mostrar el resultado en el elemento con id "qr-reader-results"
        document.getElementById('qr-reader-results').innerText = `Código detectado: ${decodedText}`;
        
        // Enviar el código de barras detectado a Streamlit
        window.parent.postMessage({barcode: decodedText}, "*");
      }

      function onScanFailure(error) {
        // No se detectó código de barras en el frame actual
        console.warn(`Código no detectado. Error: ${error}`);
      }

      // Inicializar html5-qrcode y pasar las funciones de éxito y fracaso
      const html5QrCode = new Html5Qrcode("qr-reader");
      html5QrCode.start(
        { facingMode: "environment" }, // Usa la cámara trasera si está disponible
        {
          fps: 10,    // Velocidad de fotogramas por segundo
          qrbox: { width: 250, height: 250 }  // Dimensiones del área de escaneo
        },
        onScanSuccess,
        onScanFailure
      );
    </script>
  </body>
</html>
"""

# Renderizar el HTML que contiene el escáner de código de barras
components.html(html_code, height=600)

# Capturar el código de barras enviado desde el bloque HTML/JavaScript
barcode_input = st.experimental_get_query_params().get('barcode', [''])[0]

# Si se ha detectado un código de barras, mostrarlo en la app
if barcode_input:
    st.write(f"Código de barras detectado: {barcode_input}")

