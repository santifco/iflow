import streamlit as st
import streamlit.components.v1 as components

# Título de la aplicación
st.title("Escáner de código de barras")

# Verificar si ya hay un código de barras leído almacenado en session_state
if 'barcode' not in st.session_state:
    st.session_state.barcode = ""

# Mostrar el código de barras leído en la pantalla si existe
st.write(f"Código de barras detectado: {st.session_state.barcode}")

# Instrucciones
st.write("Usa la cámara del celular para escanear un código de barras.")

# Crear un bloque HTML/JavaScript para leer el código de barras
barcode_scanner_html = f"""
<html>
  <body>
    <div id="barcode-scanner" style="width: 100%; height: 400px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
    <script type="text/javascript">
      Quagga.init({{
        inputStream: {{
          name: "Live",
          type: "LiveStream",
          target: document.querySelector('#barcode-scanner'),
        }},
        decoder: {{
          readers: ["code_128_reader", "ean_reader", "upc_reader"] // Tipos de códigos de barras que se pueden leer
        }}
      }}, function(err) {{
        if (err) {{
          console.log(err);
          return;
        }}
        console.log("Quagga initialized");
        Quagga.start();
      }});

      Quagga.onDetected(function(data) {{
        var code = data.codeResult.code;
        console.log("Código de barras detectado: " + code);
        
        // Enviar el código de barras leído a Streamlit usando la función Streamlit.setComponentValue
        window.parent.postMessage({{"barcode": code}}, "*");
        
        Quagga.stop(); // Detener la lectura después de capturar el código de barras
      }});
    </script>
  </body>
</html>
"""

# Crear el componente de QuaggaJS dentro de Streamlit
components.html(barcode_scanner_html, height=500)

# Capturar el código de barras enviado desde el bloque HTML/JavaScript
barcode_input = st.experimental_get_query_params().get('barcode', [''])[0]

# Si se ha detectado un código de barras, actualizar session_state y mostrarlo en la app
if barcode_input:
    st.session_state.barcode = barcode_input
    st.write(f"Código de barras detectado: {barcode_input}")
