"""
RETIE Manager - Generador de Documentos
Reemplaza variables {{variable}} en plantillas Word con datos reales del proyecto.
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from docx import Document
    from docx.shared import Inches, Pt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Directorio raíz de proyectos
PROYECTOS_DIR = os.environ.get("RETIE_PROYECTOS_DIR",
                               str(Path.home() / "RETIE_Manager" / "Proyectos"))


def construir_contexto(proyecto: dict, cliente: dict, ingeniero: dict,
                       sistema_fv: Optional[dict] = None) -> dict:
    """
    Construye el diccionario de variables para reemplazar en la plantilla.

    Returns:
        dict con todas las variables {{clave}} disponibles
    """
    now = datetime.now()
    ctx = {
        # Fechas
        "fecha_actual": now.strftime("%d de %B de %Y"),
        "fecha_actual_corta": now.strftime("%d/%m/%Y"),
        "año_actual": str(now.year),
        "mes_actual": now.strftime("%B"),

        # Ingeniero / Empresa
        "ingeniero_nombre": ingeniero.get("nombre", ""),
        "ingeniero_cedula": ingeniero.get("cedula", ""),
        "ingeniero_matricula": ingeniero.get("matricula_profesional", ""),
        "empresa_nombre": ingeniero.get("empresa", ""),
        "empresa_nit": ingeniero.get("nit", ""),
        "empresa_direccion": ingeniero.get("direccion", ""),
        "empresa_telefono": ingeniero.get("telefono", ""),
        "empresa_correo": ingeniero.get("correo", ""),

        # Cliente
        "cliente_nombre": cliente.get("nombre", ""),
        "cliente_cedula": cliente.get("cedula_nit", ""),
        "cliente_cedula_nit": cliente.get("cedula_nit", ""),
        "cliente_direccion": cliente.get("direccion", ""),
        "cliente_telefono": cliente.get("telefono", ""),
        "cliente_correo": cliente.get("correo", ""),

        # Proyecto
        "nombre_proyecto": proyecto.get("nombre", ""),
        "proyecto_nombre": proyecto.get("nombre", ""),
        "proyecto_direccion": proyecto.get("direccion", ""),
        "proyecto_ciudad": proyecto.get("ciudad", ""),
        "proyecto_departamento": proyecto.get("departamento", ""),
        "proyecto_tipo": proyecto.get("tipo", ""),
        "fecha_inicio": proyecto.get("fecha_inicio", ""),
        "fecha_fin": proyecto.get("fecha_fin", ""),
        "consumo_kwh_mes": str(proyecto.get("consumo_kwh_mes", "")),
        "proyecto_estado": proyecto.get("estado", "activo"),
    }

    # Sistema fotovoltaico
    if sistema_fv:
        ctx.update({
            # Paneles
            "cantidad_paneles": str(sistema_fv.get("cantidad_paneles", "")),
            "potencia_panel": str(sistema_fv.get("potencia_panel", "")),
            "potencia_panel_wp": str(sistema_fv.get("potencia_panel", "")),
            "marca_panel": sistema_fv.get("marca_panel", ""),
            "referencia_panel": sistema_fv.get("referencia_panel", ""),
            # Inversores
            "cantidad_inversores": str(sistema_fv.get("cantidad_inversores", "")),
            "marca_inversor": sistema_fv.get("marca_inversor", ""),
            "referencia_inversor": sistema_fv.get("referencia_inversor", ""),
            "potencia_inversor": str(sistema_fv.get("potencia_inversor", "")),
            # Eléctricos
            "calibre_conductor": sistema_fv.get("calibre_conductor", ""),
            "tipo_conductor": sistema_fv.get("tipo_conductor", ""),
            "proteccion_breaker": sistema_fv.get("proteccion_breaker", ""),
            # Calculados
            "potencia_total_kwp": str(sistema_fv.get("potencia_total_kwp", "")),
            "generacion_estimada_kwh": str(sistema_fv.get("generacion_estimada_kwh", "")),
            "irradiacion_zona": str(sistema_fv.get("irradiacion_zona", "")),
            "eficiencia_sistema": str(sistema_fv.get("eficiencia_sistema", "")),
        })

    return ctx


def reemplazar_en_texto(texto: str, contexto: dict) -> str:
    """Reemplaza variables {{clave}} en una cadena de texto."""
    def replace_match(match):
        key = match.group(1).strip()
        return str(contexto.get(key, match.group(0)))

    return re.sub(r'\{\{([^}]+)\}\}', replace_match, texto)


def procesar_docx(ruta_plantilla: str, contexto: dict, ruta_salida: str) -> bool:
    """
    Procesa una plantilla Word reemplazando todas las variables.

    Args:
        ruta_plantilla: Ruta al archivo .docx de plantilla
        contexto: Diccionario con variables a reemplazar
        ruta_salida: Ruta donde guardar el documento generado

    Returns:
        True si el proceso fue exitoso
    """
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx no está instalado. Ejecuta: pip install python-docx")

    if not os.path.exists(ruta_plantilla):
        raise FileNotFoundError(f"Plantilla no encontrada: {ruta_plantilla}")

    doc = Document(ruta_plantilla)

    # Procesar párrafos en el cuerpo principal
    for para in doc.paragraphs:
        _procesar_parrafo(para, contexto)

    # Procesar encabezados y pies de página
    for section in doc.sections:
        for para in section.header.paragraphs:
            _procesar_parrafo(para, contexto)
        for para in section.footer.paragraphs:
            _procesar_parrafo(para, contexto)

    # Procesar tablas
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for para in celda.paragraphs:
                    _procesar_parrafo(para, contexto)

    # Procesar cuadros de texto (text boxes en shapes)
    for shape in doc.inline_shapes:
        pass  # La mayoría no son accesibles directamente con python-docx

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    doc.save(ruta_salida)
    return True


def _procesar_parrafo(para, contexto: dict):
    """
    Reemplaza variables en un párrafo preservando el formato de los runs.
    Maneja el caso donde la variable está dividida entre múltiples runs.
    """
    # Primero intentar reemplazar run por run
    texto_completo = "".join(run.text for run in para.runs)

    if "{{" not in texto_completo:
        return

    # Reemplazar en el texto completo
    texto_nuevo = reemplazar_en_texto(texto_completo, contexto)

    if texto_completo == texto_nuevo:
        return

    # Aplicar el texto nuevo al primer run y vaciar los demás
    if para.runs:
        para.runs[0].text = texto_nuevo
        for run in para.runs[1:]:
            run.text = ""


def crear_carpeta_proyecto(nombre_proyecto: str) -> str:
    """Crea la estructura de carpetas para un proyecto."""
    nombre_limpio = _limpiar_nombre_carpeta(nombre_proyecto)
    carpeta = os.path.join(PROYECTOS_DIR, nombre_limpio)

    os.makedirs(os.path.join(carpeta, "documentos"), exist_ok=True)
    os.makedirs(os.path.join(carpeta, "imagenes"), exist_ok=True)
    os.makedirs(os.path.join(carpeta, "plantillas"), exist_ok=True)

    return carpeta


def guardar_json_proyecto(carpeta: str, proyecto: dict, cliente: dict,
                          ingeniero: dict, sistema_fv: Optional[dict] = None):
    """Guarda un JSON con todos los datos del proyecto en su carpeta."""
    datos = {
        "exportado": datetime.now().isoformat(),
        "version": "1.0",
        "proyecto": proyecto,
        "cliente": cliente,
        "ingeniero": ingeniero,
        "sistema_fotovoltaico": sistema_fv or {},
    }
    ruta = os.path.join(carpeta, "datos_proyecto.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    return ruta


def copiar_imagen_proyecto(ruta_origen: str, carpeta_proyecto: str, nombre: str) -> str:
    """Copia una imagen a la carpeta del proyecto y retorna la nueva ruta."""
    ext = os.path.splitext(ruta_origen)[1]
    nombre_archivo = _limpiar_nombre_carpeta(nombre) + ext
    destino = os.path.join(carpeta_proyecto, "imagenes", nombre_archivo)
    shutil.copy2(ruta_origen, destino)
    return destino


def listar_variables_plantilla(ruta_plantilla: str) -> list:
    """Extrae todas las variables {{variable}} de una plantilla Word."""
    if not DOCX_AVAILABLE:
        return []
    if not os.path.exists(ruta_plantilla):
        return []

    doc = Document(ruta_plantilla)
    variables = set()
    patron = re.compile(r'\{\{([^}]+)\}\}')

    textos = []
    for para in doc.paragraphs:
        textos.append(para.text)
    for tabla in doc.tables:
        for fila in tabla.rows:
            for celda in fila.cells:
                for para in celda.paragraphs:
                    textos.append(para.text)

    for texto in textos:
        for match in patron.finditer(texto):
            variables.add(match.group(1).strip())

    return sorted(list(variables))


def _limpiar_nombre_carpeta(nombre: str) -> str:
    """Limpia un nombre para usarlo como carpeta/archivo."""
    chars_invalidos = r'\/:*?"<>|'
    resultado = nombre
    for c in chars_invalidos:
        resultado = resultado.replace(c, "_")
    return resultado.strip()


def crear_plantillas_ejemplo(directorio_plantillas: str):
    """Crea plantillas Word de ejemplo si python-docx está disponible."""
    if not DOCX_AVAILABLE:
        return

    os.makedirs(directorio_plantillas, exist_ok=True)

    plantillas = [
        {
            "nombre": "acta_inicio.docx",
            "titulo": "ACTA DE INICIO DE OBRA",
            "cuerpo": _contenido_acta_inicio(),
        },
        {
            "nombre": "declaracion_construccion_retie.docx",
            "titulo": "DECLARACIÓN DE CONSTRUCCIÓN RETIE",
            "cuerpo": _contenido_declaracion_construccion(),
        },
        {
            "nombre": "declaracion_diseno_retie.docx",
            "titulo": "DECLARACIÓN DE DISEÑO RETIE",
            "cuerpo": _contenido_declaracion_diseno(),
        },
        {
            "nombre": "memoria_calculo.docx",
            "titulo": "MEMORIA DE CÁLCULO",
            "cuerpo": _contenido_memoria_calculo(),
        },
    ]

    creadas = []
    for p in plantillas:
        ruta = os.path.join(directorio_plantillas, p["nombre"])
        if not os.path.exists(ruta):
            _crear_plantilla_word(ruta, p["titulo"], p["cuerpo"])
            creadas.append(ruta)

    return creadas


def _crear_plantilla_word(ruta: str, titulo: str, parrafos: list):
    """Crea un documento Word básico con el contenido dado."""
    doc = Document()
    # Título
    t = doc.add_heading(titulo, level=1)
    # Párrafos
    for texto in parrafos:
        if texto.startswith("##"):
            doc.add_heading(texto[2:].strip(), level=2)
        elif texto == "---":
            doc.add_paragraph("_" * 60)
        else:
            doc.add_paragraph(texto)
    doc.save(ruta)


def _contenido_acta_inicio() -> list:
    return [
        "Fecha: {{fecha_actual}}",
        "",
        "## 1. PARTES",
        "CONTRATANTE: {{cliente_nombre}}, identificado con C.C./NIT {{cliente_cedula_nit}}, "
        "con dirección en {{cliente_direccion}}, teléfono {{cliente_telefono}}.",
        "",
        "CONTRATISTA: {{empresa_nombre}}, NIT {{empresa_nit}}, representado por "
        "{{ingeniero_nombre}}, con matrícula profesional {{ingeniero_matricula}}.",
        "",
        "## 2. OBJETO DEL CONTRATO",
        "El presente documento hace constar que en la fecha arriba indicada, se da inicio formal "
        "a la ejecución del proyecto denominado '{{nombre_proyecto}}', ubicado en "
        "{{proyecto_direccion}}, municipio de {{proyecto_ciudad}}, departamento de {{proyecto_departamento}}.",
        "",
        "## 3. DATOS DEL PROYECTO",
        "Tipo de proyecto: {{proyecto_tipo}}",
        "Consumo mensual estimado: {{consumo_kwh_mes}} kWh/mes",
        "Fecha estimada de finalización: {{fecha_fin}}",
        "",
        "## 4. SISTEMA FOTOVOLTAICO (SI APLICA)",
        "Cantidad de paneles: {{cantidad_paneles}} unidades de {{potencia_panel}} Wp",
        "Marca de paneles: {{marca_panel}} - Referencia: {{referencia_panel}}",
        "Inversores: {{cantidad_inversores}} × {{marca_inversor}} {{referencia_inversor}} de {{potencia_inversor}} kW",
        "",
        "## 5. FIRMAS",
        "---",
        "{{cliente_nombre}}                    {{ingeniero_nombre}}",
        "CONTRATANTE                           CONTRATISTA / INGENIERO",
        "C.C./NIT {{cliente_cedula_nit}}       Matrícula: {{ingeniero_matricula}}",
    ]


def _contenido_declaracion_construccion() -> list:
    return [
        "Ciudad y fecha: {{proyecto_ciudad}}, {{fecha_actual}}",
        "",
        "El suscrito {{ingeniero_nombre}}, con matrícula profesional No. {{ingeniero_matricula}}, "
        "actuando en nombre de {{empresa_nombre}} con NIT {{empresa_nit}},",
        "",
        "DECLARA:",
        "",
        "Que la instalación eléctrica del proyecto '{{nombre_proyecto}}', ubicado en "
        "{{proyecto_direccion}}, municipio de {{proyecto_ciudad}}, departamento de "
        "{{proyecto_departamento}}, ha sido construida en cumplimiento de:",
        "",
        "• El Reglamento Técnico de Instalaciones Eléctricas – RETIE (Resolución 90708 de 2013 "
        "y sus modificaciones).",
        "• La Norma Técnica Colombiana NTC 2050 – Código Eléctrico Colombiano.",
        "• Las demás normas técnicas nacionales e internacionales aplicables.",
        "",
        "## DATOS TÉCNICOS DE LA INSTALACIÓN",
        "Cliente: {{cliente_nombre}} - C.C./NIT: {{cliente_cedula_nit}}",
        "Consumo mensual: {{consumo_kwh_mes}} kWh/mes",
        "",
        "## SISTEMA FOTOVOLTAICO",
        "Paneles solares: {{cantidad_paneles}} unidades — {{marca_panel}} {{referencia_panel}} {{potencia_panel}} Wp",
        "Inversores: {{cantidad_inversores}} unidades — {{marca_inversor}} {{referencia_inversor}} {{potencia_inversor}} kW",
        "Conductor: {{calibre_conductor}} — {{tipo_conductor}}",
        "Protección: Breaker {{proteccion_breaker}}",
        "Potencia total instalada: {{potencia_total_kwp}} kWp",
        "",
        "---",
        "Firma: __________________________________",
        "{{ingeniero_nombre}}",
        "Matrícula Profesional No. {{ingeniero_matricula}}",
        "{{empresa_nombre}}",
        "NIT: {{empresa_nit}}",
        "Tel: {{empresa_telefono}} | {{empresa_correo}}",
    ]


def _contenido_declaracion_diseno() -> list:
    return [
        "Ciudad y fecha: {{proyecto_ciudad}}, {{fecha_actual}}",
        "",
        "El suscrito {{ingeniero_nombre}}, Ingeniero con matrícula profesional No. {{ingeniero_matricula}}, "
        "certifica que el diseño de la instalación eléctrica del proyecto:",
        "",
        "PROYECTO: {{nombre_proyecto}}",
        "PROPIETARIO: {{cliente_nombre}} — C.C./NIT: {{cliente_cedula_nit}}",
        "UBICACIÓN: {{proyecto_direccion}}, {{proyecto_ciudad}}, {{proyecto_departamento}}",
        "",
        "Ha sido elaborado en cumplimiento de los requisitos técnicos establecidos en el RETIE "
        "(Resolución 90708 de 2013), la NTC 2050 y demás normas aplicables.",
        "",
        "## PARÁMETROS DE DISEÑO",
        "Consumo mensual base: {{consumo_kwh_mes}} kWh/mes",
        "Tipo de instalación: {{proyecto_tipo}}",
        "",
        "## DATOS SISTEMA FV",
        "Potencia total sistema: {{potencia_total_kwp}} kWp",
        "Paneles: {{cantidad_paneles}} × {{potencia_panel}} Wp — {{marca_panel}} ({{referencia_panel}})",
        "Inversores: {{cantidad_inversores}} × {{potencia_inversor}} kW — {{marca_inversor}} ({{referencia_inversor}})",
        "Generación estimada: {{generacion_estimada_kwh}} kWh/mes",
        "",
        "---",
        "{{ingeniero_nombre}}",
        "Matrícula Profesional No. {{ingeniero_matricula}}",
        "{{empresa_nombre}} — NIT {{empresa_nit}}",
    ]


def _contenido_memoria_calculo() -> list:
    return [
        "Proyecto: {{nombre_proyecto}}",
        "Elaboró: {{ingeniero_nombre}} — Matrícula: {{ingeniero_matricula}}",
        "Fecha: {{fecha_actual}}",
        "",
        "## 1. DATOS GENERALES",
        "Cliente: {{cliente_nombre}}",
        "Ubicación: {{proyecto_direccion}}, {{proyecto_ciudad}}, {{proyecto_departamento}}",
        "Consumo mensual: {{consumo_kwh_mes}} kWh/mes",
        "",
        "## 2. DIMENSIONAMIENTO DEL SISTEMA FOTOVOLTAICO",
        "Irradiación solar de la zona: {{irradiacion_zona}} HSP (kWh/m²/día)",
        "Eficiencia del sistema: {{eficiencia_sistema}}",
        "",
        "## 3. COMPONENTES SELECCIONADOS",
        "PANELES FOTOVOLTAICOS:",
        "  Marca: {{marca_panel}}",
        "  Referencia: {{referencia_panel}}",
        "  Potencia unitaria: {{potencia_panel}} Wp",
        "  Cantidad: {{cantidad_paneles}} unidades",
        "  Potencia total: {{potencia_total_kwp}} kWp",
        "",
        "INVERSORES:",
        "  Marca: {{marca_inversor}}",
        "  Referencia: {{referencia_inversor}}",
        "  Potencia unitaria: {{potencia_inversor}} kW",
        "  Cantidad: {{cantidad_inversores}} unidades",
        "",
        "## 4. SISTEMA ELÉCTRICO",
        "  Calibre conductor: {{calibre_conductor}}",
        "  Tipo conductor: {{tipo_conductor}}",
        "  Protección (breaker): {{proteccion_breaker}}",
        "",
        "## 5. RESULTADOS",
        "  Generación estimada mensual: {{generacion_estimada_kwh}} kWh/mes",
        "",
        "## 6. NORMATIVA APLICADA",
        "  - RETIE: Resolución 90708 de 2013 y modificaciones",
        "  - NTC 2050: Código Eléctrico Colombiano",
        "  - IEC 62446: Sistemas fotovoltaicos",
        "  - CREG 030 de 2018: Generación distribuida",
        "",
        "---",
        "{{ingeniero_nombre}} — Matrícula {{ingeniero_matricula}}",
        "{{empresa_nombre}} | {{empresa_correo}} | {{empresa_telefono}}",
    ]
