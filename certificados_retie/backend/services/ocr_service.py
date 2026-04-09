"""
==============================================================
backend/services/ocr_service.py
Servicio de OCR: convierte PDF → imagen → texto → datos clave
==============================================================
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Importaciones opcionales (degradan graciosamente) ──────

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.warning("PyMuPDF no disponible. Instala: pip install PyMuPDF")

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR no disponible. Instala: pytesseract, Pillow, opencv-python-headless")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class OCRService:
    """
    Servicio completo de extracción de información de certificados PDF.

    Pipeline:
    1. PDF → Imagen de alta resolución (PyMuPDF)
    2. Preprocesado de imagen (OpenCV)
    3. OCR con Tesseract
    4. Extracción de campos específicos con regex/NLP
    5. Fallback: extracción directa de texto del PDF (pdfplumber)
    """

    # Patrones regex para detectar datos en certificados colombianos
    PATTERNS = {
        "numero_certificado": [
            r"(?:N[°oúu]\.?\s*(?:de\s+)?[Cc]ertificado|[Cc]ert\.?\s*N[°o]\.?|[Cc][Oo][Nn][Cc])\s*[:\-]?\s*([A-Z0-9\-/\.]{4,30})",
            r"\b([A-Z]{2,5}[-/]\d{4,8}[-/]?\d{0,4})\b",
            r"CERTIFICADO\s+N[°O]\s*[:\.]?\s*([A-Z0-9\-/]{5,25})",
        ],
        "organismo_certificador": [
            r"(?:[Oo]rganismo\s+[Cc]ertificador|[Ee]xpedido\s+por|[Cc]ertificado\s+por|[Ee]ntidad)\s*[:\-]?\s*([A-ZÁÉÍÓÚa-záéíóú\s,\.S\.A]{5,80})",
            r"(?:ICONTEC|SGS|Bureau\s+Veritas|INTERTEK|TUVSUD|TÜV|COTECNA|LATU|ICA)",
        ],
        "producto": [
            r"(?:[Pp]roducto|[Dd]escripci[oó]n\s+del\s+[Pp]roducto|[Ee]quipo|[Dd]ispositivo)\s*[:\-]?\s*([A-ZÁÉÍÓÚa-záéíóúñ\s,/\.]{5,120})",
        ],
        "fecha_emision": [
            r"(?:[Ff]echa\s+de\s+[Ee]xpedici[oó]n|[Ff]echa\s+[Ee]misi[oó]n|[Ff]echa\s+de\s+[Ee]misi[oó]n|[Ee]xpedido\s+el)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
            r"(\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+\d{4})",
        ],
        "fecha_vencimiento": [
            r"(?:[Ff]echa\s+de\s+[Vv]encimiento|[Vv]igencia\s+hasta|[Vv][áa]lido\s+hasta|[Ee]xpira|[Vv]ence\s+el)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})",
            r"(?:[Ff]echa\s+de\s+[Vv]encimiento|[Vv]igente\s+hasta)\s*[:\-]?\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})",
        ],
    }

    MESES_ES = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    }

    def __init__(self, tesseract_cmd: str = None):
        if OCR_AVAILABLE and tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # ── MÉTODO PRINCIPAL ───────────────────────────────────

    def procesar_pdf(self, pdf_path: str, images_folder: str) -> dict:
        """
        Procesa un PDF completo y extrae todos los datos disponibles.

        Returns:
            dict con: texto_ocr, imagen_path, datos_extraidos, confianza, metodo
        """
        resultado = {
            "texto_ocr": "",
            "imagen_path": None,
            "datos_extraidos": {},
            "confianza": 0.0,
            "metodo": "ninguno",
            "error": None,
        }

        try:
            # 1. Intentar extracción directa de texto (más rápido y preciso)
            texto_directo = self._extraer_texto_directo(pdf_path)
            if texto_directo and len(texto_directo.strip()) > 100:
                resultado["texto_ocr"] = texto_directo
                resultado["metodo"] = "pdfplumber"
                resultado["confianza"] = 0.85
            else:
                # 2. OCR desde imagen si el PDF no tiene texto seleccionable
                img_path, texto_ocr = self._ocr_desde_imagen(pdf_path, images_folder)
                resultado["texto_ocr"] = texto_ocr
                resultado["imagen_path"] = img_path
                resultado["metodo"] = "tesseract_ocr"
                resultado["confianza"] = 0.65

            # 3. Extraer campos con regex
            if resultado["texto_ocr"]:
                resultado["datos_extraidos"] = self._extraer_campos(resultado["texto_ocr"])

        except Exception as e:
            resultado["error"] = str(e)
            logger.error(f"Error procesando PDF {pdf_path}: {e}")

        return resultado

    # ── EXTRACCIÓN DIRECTA DE TEXTO ────────────────────────

    def _extraer_texto_directo(self, pdf_path: str) -> str:
        """Extrae texto directamente del PDF usando pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            return ""
        try:
            import pdfplumber
            texto = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:3]:  # Máximo 3 páginas
                    t = page.extract_text()
                    if t:
                        texto.append(t)
            return "\n".join(texto)
        except Exception as e:
            logger.warning(f"pdfplumber falló: {e}")
            return ""

    # ── OCR DESDE IMAGEN ───────────────────────────────────

    def _ocr_desde_imagen(self, pdf_path: str, images_folder: str) -> tuple:
        """
        Convierte la primera página del PDF a imagen y aplica OCR.
        Returns: (image_path, texto_ocr)
        """
        if not PYMUPDF_AVAILABLE or not OCR_AVAILABLE:
            logger.warning("PyMuPDF o OCR no disponibles.")
            return None, ""

        try:
            # Renderizar primera página con alta resolución
            doc = fitz.open(pdf_path)
            page = doc[0]
            mat = fitz.Matrix(2.5, 2.5)  # 2.5x zoom = ~180 DPI
            pix = page.get_pixmap(matrix=mat)
            doc.close()

            # Guardar imagen PNG
            pdf_name = Path(pdf_path).stem
            img_filename = f"{pdf_name}_ocr.png"
            img_path = os.path.join(images_folder, img_filename)
            pix.save(img_path)

            # Preprocesar y aplicar OCR
            texto = self._aplicar_ocr(img_path)
            return img_path, texto

        except Exception as e:
            logger.error(f"OCR desde imagen falló: {e}")
            return None, ""

    def _aplicar_ocr(self, img_path: str) -> str:
        """Preprocesa imagen y aplica Tesseract OCR."""
        try:
            # Cargar con OpenCV para preprocesar
            img = cv2.imread(img_path)
            if img is None:
                return ""

            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Eliminación de ruido
            denoised = cv2.fastNlMeansDenoising(gray, h=10)

            # Umbralización adaptativa (mejora texto en fondos complejos)
            thresh = cv2.adaptiveThreshold(
                denoised, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # Convertir a PIL para Tesseract
            pil_img = Image.fromarray(thresh)

            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.5)

            # Configuración Tesseract para español
            config = "--oem 3 --psm 6 -l spa+eng"
            texto = pytesseract.image_to_string(pil_img, config=config)
            return texto

        except Exception as e:
            logger.error(f"Tesseract OCR falló: {e}")
            return ""

    # ── EXTRACCIÓN DE CAMPOS CON REGEX ─────────────────────

    def _extraer_campos(self, texto: str) -> dict:
        """
        Aplica expresiones regulares al texto OCR para extraer
        los campos clave del certificado.
        """
        datos = {
            "numero_certificado": None,
            "organismo_certificador": None,
            "producto": None,
            "fecha_emision": None,
            "fecha_vencimiento": None,
        }

        for campo, patrones in self.PATTERNS.items():
            for patron in patrones:
                match = re.search(patron, texto, re.IGNORECASE | re.MULTILINE)
                if match:
                    valor = match.group(1).strip() if match.lastindex and match.lastindex >= 1 else match.group(0).strip()
                    valor = re.sub(r'\s+', ' ', valor).strip()
                    if valor:
                        # Normalizar fechas
                        if "fecha" in campo:
                            valor = self._normalizar_fecha(valor)
                        datos[campo] = valor
                        break

        return datos

    def _normalizar_fecha(self, texto_fecha: str) -> str | None:
        """Convierte varios formatos de fecha a YYYY-MM-DD."""
        if not texto_fecha:
            return None
        texto_fecha = texto_fecha.strip().lower()

        # Formato: 15 de marzo de 2023
        m = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', texto_fecha)
        if m:
            dia = int(m.group(1))
            mes = self.MESES_ES.get(m.group(2), 0)
            anio = int(m.group(3))
            if mes:
                try:
                    return datetime(anio, mes, dia).strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Formatos: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
        for sep in ["/", "-", "."]:
            partes = texto_fecha.split(sep)
            if len(partes) == 3:
                try:
                    d, m_, y = partes
                    if len(y) == 2:
                        y = "20" + y
                    return datetime(int(y), int(m_), int(d)).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    continue

        return None

    # ── ANÁLISIS ADICIONAL ─────────────────────────────────

    def detectar_organismo_conocido(self, texto: str) -> str | None:
        """
        Detecta organismos certificadores conocidos en Colombia
        por nombre directo en el texto.
        """
        organismos = [
            "ICONTEC", "SGS", "Bureau Veritas", "Intertek",
            "TÜV SÜD", "TUV SUD", "TUVSUD", "Cotecna", "LATU",
            "IQNET", "AENOR", "BV", "DNV",
        ]
        for org in organismos:
            if org.upper() in texto.upper():
                return org
        return None


# Instancia singleton del servicio
ocr_service = OCRService()
