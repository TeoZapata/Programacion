"""
RETIE Manager - Módulo de Dimensionamiento Solar
Calcula parámetros para sistemas fotovoltaicos basado en normativa colombiana.
"""

import math
from dataclasses import dataclass
from typing import Optional


# Radiación solar promedio en Colombia por departamento (kWh/m²/día - HSP)
RADIACION_COLOMBIA = {
    "Antioquia": 4.5, "Atlántico": 5.8, "Bolívar": 5.5, "Boyacá": 4.2,
    "Caldas": 4.3, "Caquetá": 4.8, "Casanare": 5.2, "Cauca": 4.6,
    "Cesar": 5.6, "Chocó": 4.1, "Córdoba": 5.4, "Cundinamarca": 4.5,
    "Guajira": 6.2, "Huila": 5.1, "Magdalena": 5.7, "Meta": 5.0,
    "Nariño": 4.4, "Norte de Santander": 5.0, "Putumayo": 4.7,
    "Quindío": 4.4, "Risaralda": 4.3, "Santander": 4.8, "Sucre": 5.5,
    "Tolima": 5.0, "Valle del Cauca": 4.7, "Vichada": 5.3,
    "Bogotá D.C.": 4.5, "Bucaramanga": 4.8, "Medellín": 4.5,
    "Cali": 4.7, "Barranquilla": 5.8, "Cartagena": 5.5,
}

# Factor de desempeño típico del sistema (pérdidas por cableado, temperatura, suciedad, etc.)
FACTOR_DESEMPENO_DEFAULT = 0.80

# Eficiencia de inversores modernos
EFICIENCIA_INVERSOR_DEFAULT = 0.97


@dataclass
class ResultadoDimensionamiento:
    """Resultado del cálculo de dimensionamiento fotovoltaico."""
    # Entradas
    consumo_kwh_mes: float
    hsp: float
    eficiencia_sistema: float
    potencia_panel_wp: float

    # Resultados
    energia_diaria_kwh: float
    potencia_sistema_kwp: float
    cantidad_paneles: int
    potencia_real_kwp: float
    generacion_mensual_kwh: float
    cobertura_porcentaje: float
    area_aproximada_m2: float

    # Recomendaciones eléctricas
    corriente_cortocircuito_total: float = 0.0
    tension_circuito_abierto: float = 0.0

    def resumen(self) -> str:
        return f"""
=== DIMENSIONAMIENTO SISTEMA FOTOVOLTAICO ===

DATOS DE ENTRADA:
  Consumo mensual:          {self.consumo_kwh_mes:.2f} kWh/mes
  Horas Sol Pico (HSP):     {self.hsp:.2f} h/día
  Eficiencia del sistema:   {self.eficiencia_sistema*100:.0f}%
  Potencia por panel:       {self.potencia_panel_wp:.0f} Wp

RESULTADOS:
  Energía diaria requerida: {self.energia_diaria_kwh:.3f} kWh/día
  Potencia requerida:       {self.potencia_sistema_kwp:.3f} kWp
  Número de paneles:        {self.cantidad_paneles} unidades
  Potencia real instalada:  {self.potencia_real_kwp:.3f} kWp
  Generación estimada:      {self.generacion_mensual_kwh:.2f} kWh/mes
  Cobertura:                {self.cobertura_porcentaje:.1f}%
  Área aproximada:          {self.area_aproximada_m2:.1f} m²

NOTA: Cálculos bajo norma RETIE y estándares IEC 62446.
"""


def obtener_radiacion(departamento: str) -> float:
    """Retorna la radiación solar promedio para un departamento colombiano."""
    return RADIACION_COLOMBIA.get(departamento, 4.5)


def calcular_dimensionamiento(
    consumo_kwh_mes: float,
    potencia_panel_wp: float = 550.0,
    departamento: Optional[str] = None,
    hsp_manual: Optional[float] = None,
    eficiencia_sistema: float = FACTOR_DESEMPENO_DEFAULT,
    incluir_autonomia: float = 1.0,
) -> ResultadoDimensionamiento:
    """
    Calcula el dimensionamiento de un sistema fotovoltaico.

    Args:
        consumo_kwh_mes: Consumo eléctrico mensual en kWh
        potencia_panel_wp: Potencia pico del panel en Watts
        departamento: Departamento colombiano para radiación automática
        hsp_manual: Horas Sol Pico manual (sobrescribe departamento)
        eficiencia_sistema: Factor de rendimiento del sistema (0.0-1.0)
        incluir_autonomia: Factor de autonomía (1.0 = 100% cobertura)

    Returns:
        ResultadoDimensionamiento con todos los parámetros calculados
    """
    # Validaciones
    if consumo_kwh_mes <= 0:
        raise ValueError("El consumo debe ser mayor a 0 kWh/mes")
    if potencia_panel_wp <= 0:
        raise ValueError("La potencia del panel debe ser mayor a 0 Wp")
    if not 0.5 <= eficiencia_sistema <= 1.0:
        raise ValueError("La eficiencia debe estar entre 50% y 100%")

    # Determinar HSP
    if hsp_manual and hsp_manual > 0:
        hsp = hsp_manual
    elif departamento:
        hsp = obtener_radiacion(departamento)
    else:
        hsp = 4.5  # Valor conservador para Colombia

    # Cálculos principales
    energia_diaria_kwh = (consumo_kwh_mes / 30.0) * incluir_autonomia
    potencia_panel_kwp = potencia_panel_wp / 1000.0

    # Potencia pico requerida del sistema
    potencia_sistema_kwp = energia_diaria_kwh / (hsp * eficiencia_sistema)

    # Número de paneles (redondeado hacia arriba)
    cantidad_paneles = math.ceil(potencia_sistema_kwp / potencia_panel_kwp)
    if cantidad_paneles < 1:
        cantidad_paneles = 1

    # Potencia real instalada
    potencia_real_kwp = cantidad_paneles * potencia_panel_kwp

    # Generación estimada mensual
    generacion_mensual_kwh = potencia_real_kwp * hsp * eficiencia_sistema * 30

    # Cobertura del sistema
    cobertura_porcentaje = (generacion_mensual_kwh / consumo_kwh_mes) * 100

    # Área aproximada (panel estándar ~2.2 m², eficiencia ~20%)
    area_por_panel_m2 = 2.2
    area_aproximada_m2 = cantidad_paneles * area_por_panel_m2

    return ResultadoDimensionamiento(
        consumo_kwh_mes=consumo_kwh_mes,
        hsp=hsp,
        eficiencia_sistema=eficiencia_sistema,
        potencia_panel_wp=potencia_panel_wp,
        energia_diaria_kwh=energia_diaria_kwh,
        potencia_sistema_kwp=potencia_sistema_kwp,
        cantidad_paneles=cantidad_paneles,
        potencia_real_kwp=potencia_real_kwp,
        generacion_mensual_kwh=generacion_mensual_kwh,
        cobertura_porcentaje=min(cobertura_porcentaje, 200.0),
        area_aproximada_m2=area_aproximada_m2,
    )


def calcular_conductores(potencia_kwp: float, tension_vdc: float = 600.0) -> dict:
    """
    Recomienda calibre de conductores para el sistema FV.

    Args:
        potencia_kwp: Potencia total del sistema en kWp
        tension_vdc: Tensión del sistema en VDC

    Returns:
        Diccionario con recomendaciones de conductores
    """
    corriente = (potencia_kwp * 1000) / tension_vdc

    # Tabla simplificada AWG vs amperios (con 125% de la Isc)
    corriente_diseno = corriente * 1.25

    calibre_map = [
        (15, "14 AWG"), (20, "12 AWG"), (25, "10 AWG"), (35, "8 AWG"),
        (50, "6 AWG"), (65, "4 AWG"), (85, "3 AWG"), (100, "2 AWG"),
        (130, "1 AWG"), (150, "1/0 AWG"), (175, "2/0 AWG"), (200, "3/0 AWG"),
        (230, "4/0 AWG"), (999, "350 kcmil"),
    ]

    calibre = "14 AWG"
    for amp_max, cal in calibre_map:
        if corriente_diseno <= amp_max:
            calibre = cal
            break

    return {
        "corriente_nominal_a": round(corriente, 2),
        "corriente_diseno_a": round(corriente_diseno, 2),
        "calibre_recomendado": calibre,
        "tipo_conductor": "THW-LS / THWN-2 90°C para circuitos DC",
        "proteccion_breaker": f"{int(corriente_diseno * 1.25)} A",
    }


def generar_resumen_calculo(resultado: ResultadoDimensionamiento, proyecto_nombre: str = "") -> str:
    """Genera un texto de memoria de cálculo para el documento técnico."""
    hsp = resultado.hsp
    eta = resultado.eficiencia_sistema
    consumo = resultado.consumo_kwh_mes

    return f"""MEMORIA DE CÁLCULO - SISTEMA FOTOVOLTAICO
Proyecto: {proyecto_nombre}
Fecha: Generado automáticamente

1. DATOS DE PARTIDA
   Consumo mensual del usuario: {consumo:.2f} kWh/mes
   Consumo diario promedio: {consumo/30:.3f} kWh/día
   Horas Sol Pico (HSP) zona: {hsp:.2f} h/día
   Factor de rendimiento (PR): {eta:.0%}

2. ENERGÍA DIARIA REQUERIDA
   Ed = Consumo mensual / 30 días
   Ed = {consumo:.2f} / 30 = {consumo/30:.4f} kWh/día

3. POTENCIA PICO REQUERIDA
   Ppico = Ed / (HSP × PR)
   Ppico = {consumo/30:.4f} / ({hsp:.2f} × {eta:.2f})
   Ppico = {resultado.potencia_sistema_kwp:.4f} kWp

4. NÚMERO DE PANELES
   N_paneles = Ppico / P_panel = {resultado.potencia_sistema_kwp:.4f} kWp / {resultado.potencia_panel_wp/1000:.3f} kWp
   N_paneles = {resultado.cantidad_paneles} paneles (redondeado al entero superior)

5. POTENCIA REAL INSTALADA
   P_real = N_paneles × P_panel = {resultado.cantidad_paneles} × {resultado.potencia_panel_wp:.0f} Wp
   P_real = {resultado.potencia_real_kwp*1000:.0f} Wp = {resultado.potencia_real_kwp:.3f} kWp

6. GENERACIÓN ESTIMADA MENSUAL
   G_mes = P_real × HSP × PR × 30 días
   G_mes = {resultado.potencia_real_kwp:.3f} × {hsp:.2f} × {eta:.2f} × 30
   G_mes = {resultado.generacion_mensual_kwh:.2f} kWh/mes

7. INDICADOR DE COBERTURA
   Cobertura = G_mes / Consumo = {resultado.generacion_mensual_kwh:.2f} / {consumo:.2f}
   Cobertura = {resultado.cobertura_porcentaje:.1f}%

8. ÁREA APROXIMADA
   Área = N_paneles × 2.2 m²/panel = {resultado.area_aproximada_m2:.1f} m²

NORMATIVA APLICADA:
- RETIE: Reglamento Técnico de Instalaciones Eléctricas (Resolución 90708 de 2013 y sus modificaciones)
- NTC 2050: Código Eléctrico Colombiano
- IEC 62446: Sistemas fotovoltaicos - Requisitos para pruebas y documentación
- CREG 030 de 2018: Generación distribuida en Colombia
"""
