import streamlit as st




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
        costo_por_kw = 3200000  # 4.5 millones por kW
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
