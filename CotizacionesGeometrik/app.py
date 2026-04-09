import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import streamlit as st
import fitz 
from transformers import pipeline
from utils.genpdf import *
from utils.gestorDB import *
from utils.solarCalculator import *
import pytesseract
from PIL import Image
import openai
import json
import re
from openai import OpenAI
import tempfile
import os

        





# Inicializar la base de datos
@st.cache_resource
def init_db():
    return DatabaseManager()

def openAi(content, path_image):
    
    client = OpenAI(api_key='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')

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "user", "content": f"{content}"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"{path_image}"
                    }
                ]
            }
        ]
    )

    return response.output_text


db = init_db()

# Título principal
st.title("☀️ Sistema de Cotización Solar")
st.markdown("---")

# Sidebar para navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.selectbox(
    "Seleccione una opción:",
    ["Nueva Cotización", "Historial de Cotizaciones"]
)

if opcion == "Nueva Cotización":
    st.header("Nueva Cotización de Sistema Solar")
    
    # Crear pestañas para organizar mejor la información
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Datos del Cliente", "⚡ Consumo Energético", "🛠️ Material" ,"💰 Cotización", "prueba"])
    
    with tab1:
        st.subheader("Información del Cliente")
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo*", placeholder="Ej: Juan Pérez")
            cedula = st.text_input("Cédula*", placeholder="Ej: 12345678")
            telefono = st.text_input("Teléfono", placeholder="Ej: 3001234567")
        
        with col2:
            email = st.text_input("Email", placeholder="Ej: juan@email.com")
            direccion = st.text_input("Dirección", placeholder="Ej: Calle 123 #45-67")
            ciudad = st.selectbox("Ciudad*", list(CIUDADES_IRRADIACION.keys()))
    
    with tab2:
        st.subheader("Análisis de Consumo Energético")
        
        col1, col2 , col3= st.columns([2, 1,1])
        
        with col1:
            tipo_facturacion = st.radio(
                "Tipo de facturación:",
                ["Mensual", "Bimensual"],
                horizontal=True
            )

            st.write("**Ingrese los consumos de las últimas facturas (en kWh):**")
            num_facturas = st.slider("Número de facturas a ingresar:", 1, 12, 1)

            consumos = []
            cols = st.columns(3)
            for i in range(num_facturas):
                with cols[i % 3]:
                    consumo = st.number_input(
                        f"Factura {i+1}:",
                        min_value=0,
                        value=200,
                        step=10,
                        key=f"consumo_{i}"
                    )
                    consumos.append(consumo)
        
        with col2:
            st.info(f"**Ciudad seleccionada:** {ciudad}")
            st.info(f"**Irradiación solar:** {CIUDADES_IRRADIACION[ciudad]} kWh/m²/año")
            
            if consumos and all(c > 0 for c in consumos):
                consumo_promedio = SolarCalculator.calcular_consumo_promedio(consumos, tipo_facturacion)
                st.success(f"**Consumo promedio mensual:** {consumo_promedio:.2f} kWh")
            

            # Título simple
            
        st.title("PVWATTS información")
        

        # Input para buscar ciudad y centrar el mapa
        lat_centro = st.number_input("Latitud:", value=4.60971)
        
        lon_centro = st.number_input("Longitud:", value=-74.08175)
        

        # Intentar obtener coordenadas de la ciudad buscada


        # Mostrar coordenadas cuando se hace clic
       
        params = {
                    'api_key': 'mVIsZR9LB1SmgmI23BUtBFLc4fumDgWwsT2uKLhb',
                    'system_capacity': 1,
                    'module_type': 0,
                    'losses': 20,
                    'array_type': 1,
                    'tilt': 10,
                    'azimuth': 180,
                    'timeframe': 'hourly'
                }
        params['lat'] = lat_centro
        params['lon'] = lon_centro
        try:
                
            

                response = requests.get('https://developer.nrel.gov/api/pvwatts/v8.json', params)
                resp = response.json()
                ac_annual = resp['outputs']['ac_annual']

                st.write(f"**Coordenadas:** {resp['station_info']['lat']}, {resp['station_info']['lon']}")
                st.write(f'**Outputs:** {ac_annual}')
        except requests.exceptions.HTTPError as e:
                st.error(f"Error al consultar la API PVWatts: {e}")
        except Exception as e:
                st.error(f"Ocurrió un error en la Conexión: {e}")
    with tab3:
        st.subheader("Material")
        st.image('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80', caption='Paneles solares - Foto por Unsplash')

        # Cambio de acometida
        cambio_acometida = st.checkbox("¿Requiere cambio de acometida?")

        st.markdown("### Tramos de Cableado y Tubería")
        tramos = [
            ("Trenzado - Medidor", "trenzado_medidor"),
            ("Medidor - Tablero", "medidor_tablero"),
            ("Tablero - Inversor", "tablero_inv"),
            ("Inversor - Paneles", "inv_paneles")
        ]

        tramo_data = {}
        for label, key in tramos:
            st.markdown(f"**{label}**")
            col1, col2 = st.columns(2)
            with col1:
                distancia = st.number_input(
                    f"Distancia {label} (m):",
                    min_value=0.0,
                    value=5.0,
                    step=0.5,
                    key=f"dist_{key}"
                )
            with col2:
                diametro = st.selectbox(
                    f"Diámetro tubería {label}:",
                    options=["1/2\"", "3/4\"", "1\"", "1 1/4\"", "1 1/2\"", "2\""],
                    index=1,
                    key=f"diam_{key}"
                )
            tramo_data[key] = {"distancia": distancia, "diametro": diametro}
            st.markdown("---")

        # Puedes usar tramo_data y cambio_acometida en la pestaña de cotización para cálculos o mostrar resumen.
    with tab4:
        if nombre and cedula and ciudad and consumos and all(c > 0 for c in consumos):
            st.subheader("Parámetros de Cotización")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Porcentajes:**")
                iva = st.slider("IVA (%)", 0, 30, 19)
                utilidad = st.slider("Utilidad (%)", 0, 50, 20)
                imprevistos = st.slider("Imprevistos (%)", 0, 20, 10)
            
            with col2:
                st.write("**Mano de Obra:**")
                num_trabajadores = st.number_input("Número de trabajadores", min_value=1, value=2)
                dias_trabajo = st.number_input("Días de trabajo", min_value=1, value=3)
                precio_trabajador = st.number_input("Precio por trabajador/día (COP)", min_value=0, value=80000, step=10000)
            
            # Realizar cálculos
            consumo_promedio = SolarCalculator.calcular_consumo_promedio(consumos, tipo_facturacion)
            # Usar ac_annual si está definido, si no usar la irradiación de la ciudad
            irradiacion = ac_annual if 'ac_annual' in locals() else CIUDADES_IRRADIACION[ciudad]
            
            potencia_requerida = SolarCalculator.calcular_potencia_requerida(consumo_promedio, irradiacion)
            
            costo_base = SolarCalculator.calcular_costo_base(potencia_requerida)
            costo_mano_obra = SolarCalculator.calcular_costo_mano_obra(num_trabajadores, dias_trabajo, precio_trabajador)
            
            # Cálculos detallados
            subtotal = costo_base + costo_mano_obra
            valor_utilidad = subtotal * (utilidad/100)
            subtotal_con_utilidad = subtotal + valor_utilidad
            valor_imprevistos = subtotal_con_utilidad * (imprevistos/100)
            subtotal_con_imprevistos = subtotal_con_utilidad + valor_imprevistos
            valor_iva = subtotal_con_imprevistos * (iva/100)
            costo_total = subtotal_con_imprevistos + valor_iva
            

            paneles = SolarCalculator.calcular_paneles_necesarios(potencia_requerida)
            paneles_615 = paneles[615]

            # Mostrar resultados
            st.markdown("---")
            st.subheader("Resumen de la Cotización")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Potencia Requerida", f"{potencia_requerida:.2f} kWp")
                st.metric("Consumo Anual", f"{consumo_promedio * 12:.0f} kWh")
                st.metric("Paneles Necesarios", str(paneles_615['paneles']))
                st.metric("Porcentaje de Cubrimiento", f"{paneles_615["porcentaje_cubierto"]:.2f}%")
            
            with col2:
                st.metric("Costo Base", f"${costo_base:,.0f}")
                st.metric("Mano de Obra", f"${costo_mano_obra:,.0f}")
            
            with col3:
                st.metric("Costo Total", f"${costo_total:,.0f}", delta=f"+${valor_iva:,.0f} IVA")
            
            # Tabla detallada
            st.subheader("Desglose Detallado")
            desglose_data = {
                "Concepto": [
                    "Costo base del sistema",
                    "Mano de obra",
                    f"Utilidad ({utilidad}%)",
                    f"Imprevistos ({imprevistos}%)",
                    f"IVA ({iva}%)",
                    "TOTAL"
                ],
                "Valor (COP)": [
                    f"${costo_base:,.0f}",
                    f"${costo_mano_obra:,.0f}",
                    f"${valor_utilidad:,.0f}",
                    f"${valor_imprevistos:,.0f}",
                    f"${valor_iva:,.0f}",
                    f"${costo_total:,.0f}"
                ]
            }
            st.table(pd.DataFrame(desglose_data))
            
            # Botones de acción
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Guardar Cotización", type="primary", use_container_width=True):
                    # Guardar cliente
                    datos_cliente = {
                        'nombre': nombre,
                        'cedula': cedula,
                        'telefono': telefono,
                        'email': email,
                        'direccion': direccion,
                        'ciudad': ciudad
                    }
                    cliente_id = db.insertar_cliente(datos_cliente)
                    
                    # Guardar cotización
                    datos_cotizacion = {
                        'consumo_promedio': consumo_promedio,
                        'tipo_facturacion': tipo_facturacion,
                        'consumos': consumos,
                        'ciudad': ciudad,
                        'irradiacion': irradiacion,
                        'potencia_requerida': potencia_requerida,
                        'iva_porcentaje': iva,
                        'utilidad_porcentaje': utilidad,
                        'imprevistos_porcentaje': imprevistos,
                        'num_trabajadores': num_trabajadores,
                        'dias_trabajo': dias_trabajo,
                        'precio_trabajador': precio_trabajador,
                        'costo_total': costo_total
                    }
                    cotizacion_id = db.insertar_cotizacion(cliente_id, datos_cotizacion)
                    
                    st.success(f"✅ Cotización guardada exitosamente (ID: {cotizacion_id})")
            
            with col2:
                # Generar PDF
                calculos = {
                    'consumo_promedio': consumo_promedio,
                    'consumo_anual': consumo_promedio * 12,
                    'potencia_requerida': potencia_requerida,
                    'generacion_anual': potencia_requerida * irradiacion,
                    'costo_base': costo_base,
                    'costo_mano_obra': costo_mano_obra,
                    'utilidad': valor_utilidad,
                    'imprevistos': valor_imprevistos,
                    'iva': valor_iva,
                    'costo_total': costo_total
                }
                
                datos_cliente_pdf = {
                    'nombre': nombre,
                    'cedula': cedula,
                    'telefono': telefono,
                    'email': email,
                    'direccion': direccion,
                    'ciudad': ciudad
                }
                
                datos_cotizacion_pdf = {
                    'consumos': consumos,
                    'tipo_facturacion': tipo_facturacion,
                    'irradiacion': irradiacion,
                    'iva_porcentaje': iva,
                    'utilidad_porcentaje': utilidad,
                    'imprevistos_porcentaje': imprevistos
                }
                
                pdf_buffer = PDFGenerator.generar_pdf(datos_cliente_pdf, datos_cotizacion_pdf, calculos)
                
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"cotizacion_solar_{cedula}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
        else:
            st.warning("⚠️ Complete todos los campos obligatorios en las pestañas anteriores para generar la cotización.")
    with tab5:
        st.subheader("Prueba")
        uploaded_file = st.file_uploader("Selecciona un PDF o una imagen", type=["pdf", "png", "jpg", "jpeg"])

        if uploaded_file is not None:
            # Guardar archivo temporalmente

            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

            # Si es PDF, extraer la primera página como imagen
            if uploaded_file.type == "application/pdf":
                doc = fitz.open(temp_path)
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img_path = temp_path + ".png"
                pix.save(img_path)
                st.image(img_path, caption="Primera página del PDF")    
                path_to_send = img_path
            else:
                st.image(temp_path, caption="Imagen seleccionada")
                path_to_send = temp_path

            response = openAi('Saca los valores de la gráfica de consumos de la siguiente imagen', path_to_send)
            st.write("Respuesta OpenAI:")
            st.write(response)
        else:
            st.info("Por favor, selecciona un archivo PDF o una imagen.")


elif opcion == "Historial de Cotizaciones":
    st.header("Historial de Cotizaciones")
    
    cotizaciones_df = db.obtener_cotizaciones()
    
    if not cotizaciones_df.empty:
        st.dataframe(
            cotizaciones_df,
            use_container_width=True,
            column_config={
                "id": "ID",
                "nombre": "Cliente",
                "ciudad": "Ciudad",
                "potencia_requerida": st.column_config.NumberColumn(
                    "Potencia (kW)",
                    format="%.2f kW"
                ),
                "costo_total": st.column_config.NumberColumn(
                    "Costo Total",
                    format="$%.0f COP"
                ),
                "fecha_cotizacion": st.column_config.DatetimeColumn(
                    "Fecha",
                    format="DD/MM/YYYY HH:mm"
                )
            }
        )
        
        st.subheader("Estadísticas")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cotizaciones", len(cotizaciones_df))
        
        with col2:
            promedio_potencia = cotizaciones_df['potencia_requerida'].mean()
            st.metric("Potencia Promedio", f"{promedio_potencia:.2f} kW")
        
        with col3:
            promedio_costo = cotizaciones_df['costo_total'].mean()
            st.metric("Costo Promedio", f"${promedio_costo:,.0f}")
        
        with col4:
            ciudad_mas_comun = cotizaciones_df['ciudad'].mode().iloc[0] if not cotizaciones_df.empty else "N/A"
            st.metric("Ciudad Más Común", ciudad_mas_comun)
    else:
        st.info("No hay cotizaciones registradas aún.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "💡 Sistema de Cotización Solar - Desarrollado por Mateo Salazar Zapata"
    "</div>",
    unsafe_allow_html=True
)


