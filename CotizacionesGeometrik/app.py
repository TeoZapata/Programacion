
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import json

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

class DatabaseManager:
    def __init__(self, db_name="solar_quotes.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                ciudad TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de cotizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                consumo_promedio REAL,
                tipo_facturacion TEXT,
                consumos TEXT,
                ciudad TEXT,
                irradiacion REAL,
                potencia_requerida REAL,
                iva_porcentaje REAL,
                utilidad_porcentaje REAL,
                imprevistos_porcentaje REAL,
                num_trabajadores INTEGER,
                dias_trabajo INTEGER,
                precio_trabajador REAL,
                costo_total REAL,
                fecha_cotizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insertar_cliente(self, datos_cliente):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nombre, cedula, telefono, email, direccion, ciudad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datos_cliente['nombre'],
            datos_cliente['cedula'],
            datos_cliente['telefono'],
            datos_cliente['email'],
            datos_cliente['direccion'],
            datos_cliente['ciudad']
        ))
        
        cliente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cliente_id
    
    def insertar_cotizacion(self, cliente_id, datos_cotizacion):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cotizaciones (
                cliente_id, consumo_promedio, tipo_facturacion, consumos,
                ciudad, irradiacion, potencia_requerida, iva_porcentaje,
                utilidad_porcentaje, imprevistos_porcentaje, num_trabajadores,
                dias_trabajo, precio_trabajador, costo_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cliente_id,
            datos_cotizacion['consumo_promedio'],
            datos_cotizacion['tipo_facturacion'],
            json.dumps(datos_cotizacion['consumos']),
            datos_cotizacion['ciudad'],
            datos_cotizacion['irradiacion'],
            datos_cotizacion['potencia_requerida'],
            datos_cotizacion['iva_porcentaje'],
            datos_cotizacion['utilidad_porcentaje'],
            datos_cotizacion['imprevistos_porcentaje'],
            datos_cotizacion['num_trabajadores'],
            datos_cotizacion['dias_trabajo'],
            datos_cotizacion['precio_trabajador'],
            datos_cotizacion['costo_total']
        ))
        
        cotizacion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cotizacion_id
    
    def obtener_cotizaciones(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT c.id, cl.nombre, cl.ciudad, c.potencia_requerida, 
                   c.costo_total, c.fecha_cotizacion
            FROM cotizaciones c
            JOIN clientes cl ON c.cliente_id = cl.id
            ORDER BY c.fecha_cotizacion DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

class SolarCalculator:
    @staticmethod
    def calcular_consumo_promedio(consumos, tipo_facturacion):
        if tipo_facturacion == "Mensual":
            return sum(consumos)
        else:  # Bimensual
            return sum(consumos)/2
    
    @staticmethod
    def calcular_potencia_requerida(consumo_promedio_mensual, irradiacion):
        consumo_anual = consumo_promedio_mensual * 12
        potencia_kw = consumo_anual / irradiacion
        return potencia_kw
    
    @staticmethod
    def calcular_costo_base(potencia_kw):
        # Costo base estimado por kW instalado (en COP)
        costo_por_kw = 4500000  # 4.5 millones por kW
        return potencia_kw * costo_por_kw
    
    @staticmethod
    def calcular_costo_mano_obra(num_trabajadores, dias_trabajo, precio_trabajador):
        return num_trabajadores * dias_trabajo * precio_trabajador
    
    @staticmethod
    def calcular_costo_total(costo_base, costo_mano_obra, iva, utilidad, imprevistos):
        subtotal = costo_base + costo_mano_obra
        subtotal_con_utilidad = subtotal * (1 + utilidad/100)
        subtotal_con_imprevistos = subtotal_con_utilidad * (1 + imprevistos/100)
        total_con_iva = subtotal_con_imprevistos * (1 + iva/100)
        return total_con_iva

    @staticmethod
    def calcular_paneles_necesarios(potencia_requerida_kwp):
        """
        Calcula la cantidad de paneles necesarios para varias potencias de panel (W)
        para cubrir la potencia requerida (kWp) al 100%.
        Devuelve un diccionario con los resultados.
        """
        potencias = [620, 615, 590, 565, 560]
        resultados = {}
        for potencia in potencias:
            num_paneles = int(-(-potencia_requerida_kwp * 1000 // potencia))  # Redondeo hacia arriba
            energia_cubierta = num_paneles * potencia / 1000  # kW cubiertos con paneles completos
            porcentaje_cubierto = (energia_cubierta / potencia_requerida_kwp) * 100 if potencia_requerida_kwp else 0
            resultados[potencia] = {
                "paneles": num_paneles,
                "porcentaje_cubierto": porcentaje_cubierto
            }

        # Calcular diferencia porcentual respecto a panel de 615W
        base_paneles = resultados[615]["paneles"]
        base_energia = base_paneles * 615 / 1000
        for potencia in potencias:
            energia = resultados[potencia]["paneles"] * potencia / 1000
            if base_energia > 0:
                diferencia = ((energia - base_energia) / base_energia) * 100
            else:
                diferencia = 0
            resultados[potencia]["diferencia_vs_615"] = diferencia

        return resultados

        


class PDFGenerator:
    @staticmethod
    def generar_pdf(datos_cliente, datos_cotizacion, calculos):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkblue,
            alignment=1
        )
        story.append(Paragraph("COTIZACIÓN SISTEMA SOLAR FOTOVOLTAICO", title_style))
        story.append(Spacer(1, 20))
        
        # Información del cliente
        story.append(Paragraph("INFORMACIÓN DEL CLIENTE", styles['Heading2']))
        cliente_data = [
            ['Nombre:', datos_cliente['nombre']],
            ['Cédula:', datos_cliente['cedula']],
            ['Teléfono:', datos_cliente['telefono']],
            ['Email:', datos_cliente['email']],
            ['Dirección:', datos_cliente['direccion']],
            ['Ciudad:', datos_cliente['ciudad']]
        ]
        
        cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cliente_table)
        story.append(Spacer(1, 20))
        
        # Análisis de consumo
        story.append(Paragraph("ANÁLISIS DE CONSUMO", styles['Heading2']))
        consumo_data = [
            ['Consumos registrados:', ', '.join(map(str, datos_cotizacion['consumos'])) + ' kWh'],
            ['Tipo de facturación:', datos_cotizacion['tipo_facturacion']],
            ['Consumo promedio mensual:', f"{calculos['consumo_promedio']:.2f} kWh"],
            ['Consumo anual estimado:', f"{calculos['consumo_anual']:.2f} kWh"],
            ['Irradiación solar:', f"{datos_cotizacion['irradiacion']} kWh/m²/año"]
        ]
        
        consumo_table = Table(consumo_data, colWidths=[3*inch, 3*inch])
        consumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(consumo_table)
        story.append(Spacer(1, 20))
        
        # Dimensionamiento del sistema
        story.append(Paragraph("DIMENSIONAMIENTO DEL SISTEMA", styles['Heading2']))
        sistema_data = [
            ['Potencia requerida:', f"{calculos['potencia_requerida']:.2f} kW"],
            ['Generación anual estimada:', f"{calculos['generacion_anual']:.2f} kWh"]
        ]
        
        sistema_table = Table(sistema_data, colWidths=[3*inch, 3*inch])
        sistema_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(sistema_table)
        story.append(Spacer(1, 20))
        
        # Cotización
        story.append(Paragraph("COTIZACIÓN", styles['Heading2']))
        cotizacion_data = [
            ['Costo base del sistema:', f"${calculos['costo_base']:,.0f} COP"],
            ['Costo mano de obra:', f"${calculos['costo_mano_obra']:,.0f} COP"],
            ['Utilidad (%s%%):'% datos_cotizacion['utilidad_porcentaje'], f"${calculos['utilidad']:,.0f} COP"],
            ['Imprevistos (%s%%):'% datos_cotizacion['imprevistos_porcentaje'], f"${calculos['imprevistos']:,.0f} COP"],
            ['IVA (%s%%):'% datos_cotizacion['iva_porcentaje'], f"${calculos['iva']:,.0f} COP"],
            ['TOTAL:', f"${calculos['costo_total']:,.0f} COP"]
        ]
        
        cotizacion_table = Table(cotizacion_data, colWidths=[3*inch, 3*inch])
        cotizacion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -2), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, -2), colors.black),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cotizacion_table)
        
        # Fecha
        story.append(Spacer(1, 30))
        fecha_actual = datetime.now().strftime("%d de %B de %Y")
        story.append(Paragraph(f"Fecha: {fecha_actual}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

# Inicializar la base de datos
@st.cache_resource
def init_db():
    return DatabaseManager()

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