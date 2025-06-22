
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json
from utils.genpdf import *
from utils.solarCalculadora import *
from utils.gestorDB import *
import os
import pandas as pd
import requests
import json
import warnings


# Configuración de la página
st.set_page_config(
    page_title="Sistema de Cotización Solar",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Datos de ciudades colombianas con irradiación promedio
CIUDADES_IRRADIACION = {
    "Bogotá": 1200,
    "Medellín": 1300,
    "Cali": 1400,
    "Barranquilla": 1500,
    "Cartagena": 1550,
    "Bucaramanga": 1350,
    "Pereira": 1250,
    "Ibagué": 1300,
    "Santa Marta": 1600,
    "Villavicencio": 1250,
    "Manizales": 1200,
    "Neiva": 1400,
    "Soledad": 1500,
    "Armenia": 1280,
    "Soacha": 1200,
    "Valledupar": 1500,
    "Montería": 1450,
    "Itagüí": 1300,
    "Pasto": 1100,
    "Palmira": 1400
}


# Inicializar la base de datos
@st.cache_resource
def init_db():
    return DatabaseManager()


def load(system_capacity=4, module_type=0, losses=14, array_type=0, tilt=25, azimuth=180, address=None, lat=51.9607, lon=7.6261, radius=100, dataset='intl', suppress_warnings=False):
        """
        Imports data from PVWatts using the requests package.
        Only fields that are of importance for this forecasting purpose
        can be specified.
        """
        params = {
            'api_key': 'mVIsZR9LB1SmgmI23BUtBFLc4fumDgWwsT2uKLhb',
            'system_capacity': system_capacity,
            'module_type': module_type,
            'losses': losses,
            'array_type': array_type,
            'tilt': tilt,
            'azimuth': azimuth,
            'radius': radius,
            'timeframe': 'hourly',
            'dataset': dataset
        }
        if address:
            params['address'] = address
        else:
            params['lat'] = lat
            params['lon'] = lon

        response = requests.get('https://developer.nrel.gov/api/pvwatts/v8.json', params)
        print(response.request.url)
        json = response.json()
        if not suppress_warnings:
            if json['errors']: warnings.warn(f'API ERROR: {json["errors"]}')
            if json['warnings']: warnings.warn(f'API WARNING: {json["warnings"]}')
        response.raise_for_status()
        return f"loaded {json['station_info']['city']}"

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
    tab1, tab2, tab3 = st.tabs(["📋 Datos del Cliente", "⚡ Consumo Energético", "💰 Cotización"])
    
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
        
        col1, col2 = st.columns([2, 1])
        
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
            import streamlit as st
            import folium
            from streamlit_folium import st_folium

            # Título simple
            st.title("Mapa Simple - Coordenadas")

            # Crear mapa centrado en Bogotá
            mapa = folium.Map(
                location=[4.6097, -74.0817],  # Bogotá por defecto
                zoom_start=10
            )

            # Mostrar el mapa y capturar datos
            datos_mapa = st_folium(mapa, width=700, height=400)

            # Mostrar coordenadas cuando se hace clic
            if datos_mapa['last_clicked']:
                lat = datos_mapa['last_clicked']['lat']
                lon = datos_mapa['last_clicked']['lng']
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
                params['lat'] = lat
                params['lon'] = lon
                try:
                    
                

                    response = requests.get('https://developer.nrel.gov/api/pvwatts/v8.json', params)
                    print(response.request.url)
                    resp = response.json()
                    ac_annual = resp['outputs']['ac_annual']

                    st.write(f"**Latitud:** {lat}")
                    st.write(f"**Longitud:** {lon}")
                    st.write(f"**Coordenadas:** {lat}, {lon}")
                    st.write(f'**Outputs:** {ac_annual}')
                except requests.exceptions.HTTPError as e:
                    st.error(f"Error al consultar la API PVWatts: {e}")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")
            else:
                st.write("Haz clic en el mapa para obtener las coordenadas")
    
    with tab3:
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
            irradiacion = CIUDADES_IRRADIACION[ciudad]
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
