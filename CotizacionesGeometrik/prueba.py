import streamlit as st
import tempfile
import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import easyocr
import io
import base64

# Configuración de la página
st.set_page_config(page_title="Extractor de Texto", layout="wide")

def extract_text_with_tesseract(image_path):
    """Extrae texto usando Tesseract OCR (gratuito)"""
    try:
        # Configurar Tesseract para español
        custom_config = r'--oem 3 --psm 6 -l spa'
        text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
        return text.strip()
    except Exception as e:
        return f"Error con Tesseract: {str(e)}"

def extract_text_with_easyocr(image_path):
    """Extrae texto usando EasyOCR (gratuito)"""
    try:
        reader = easyocr.Reader(['es', 'en'])  # Español e inglés
        results = reader.readtext(image_path)
        
        # Combinar todo el texto extraído
        text_parts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Solo texto con confianza > 50%
                text_parts.append(text)
        
        return '\n'.join(text_parts)
    except Exception as e:
        return f"Error con EasyOCR: {str(e)}"

def extract_text_from_pdf(pdf_path):
    """Extrae texto directamente del PDF si es posible"""
    try:
        doc = fitz.open(pdf_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        
        doc.close()
        return text_content.strip()
    except Exception as e:
        return f"Error extrayendo texto del PDF: {str(e)}"

def pdf_to_image(pdf_path, page_num=0):
    """Convierte una página del PDF a imagen"""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Mayor resolución
        img_data = pix.tobytes("png")
        doc.close()
        return img_data
    except Exception as e:
        st.error(f"Error convirtiendo PDF a imagen: {str(e)}")
        return None

def analyze_chart_data(text):
    """Analiza el texto extraído para identificar datos de gráficas"""
    if not text or len(text.strip()) < 10:
        return "No se pudo extraer texto suficiente de la imagen."
    
    # Buscar patrones comunes en gráficas
    lines = text.split('\n')
    chart_data = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Buscar números y posibles etiquetas
            if any(char.isdigit() for char in line):
                chart_data.append(line)
    
    if chart_data:
        analysis = "**Datos extraídos de la gráfica:**\n\n"
        for data in chart_data:
            analysis += f"• {data}\n"
        
        analysis += "\n**Análisis:**\n"
        analysis += "Los datos mostrados parecen corresponder a valores numéricos "
        analysis += "que podrían representar consumos, fechas, o categorías de la gráfica."
        
        return analysis
    else:
        return "No se pudieron identificar datos numéricos en la imagen."

# Interfaz principal
with st.container():
    st.title("🔍 Extractor de Texto Gratuito")
    st.markdown("Extrae texto de imágenes y PDFs usando tecnologías gratuitas")

    # Selección del método de extracción
    col1, col2 = st.columns(2)
    
    with col1:
        ocr_method = st.selectbox(
            "Selecciona el método OCR:",
            ["EasyOCR (Recomendado)", "Tesseract OCR"],
            help="EasyOCR suele ser más preciso para gráficas y texto en imágenes"
        )
    
    with col2:
        analyze_charts = st.checkbox(
            "Analizar datos de gráficas",
            value=True,
            help="Intenta identificar y analizar datos numéricos en gráficas"
        )

    # Subida de archivos
    uploaded_file = st.file_uploader(
        "📁 Selecciona un PDF o una imagen",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Formatos soportados: PDF, PNG, JPG, JPEG"
    )

    if uploaded_file is not None:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        # Mostrar progreso
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            if uploaded_file.type == "application/pdf":
                status_text.text("Procesando PDF...")
                progress_bar.progress(25)
                
                # Intentar extraer texto directamente del PDF
                pdf_text = extract_text_from_pdf(temp_path)
                
                if pdf_text and len(pdf_text.strip()) > 50:
                    progress_bar.progress(100)
                    status_text.text("✅ Texto extraído directamente del PDF")
                    
                    st.success("Texto extraído del PDF:")
                    st.text_area("Contenido:", pdf_text, height=200)
                    
                    if analyze_charts:
                        chart_analysis = analyze_chart_data(pdf_text)
                        st.markdown("---")
                        st.markdown(chart_analysis)
                else:
                    # Si no hay texto, convertir a imagen y usar OCR
                    status_text.text("Convirtiendo PDF a imagen...")
                    progress_bar.progress(50)
                    
                    img_data = pdf_to_image(temp_path)
                    if img_data:
                        # Guardar imagen temporal
                        img_path = temp_path + ".png"
                        with open(img_path, "wb") as f:
                            f.write(img_data)
                        
                        # Mostrar imagen
                        st.image(img_data, caption="Primera página del PDF", use_column_width=True)
                        
                        # Extraer texto con OCR
                        status_text.text("Extrayendo texto con OCR...")
                        progress_bar.progress(75)
                        
                        if ocr_method == "EasyOCR (Recomendado)":
                            extracted_text = extract_text_with_easyocr(img_path)
                        else:
                            extracted_text = extract_text_with_tesseract(img_path)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Procesamiento completado")
                        
                        # Mostrar resultados
                        st.success("Texto extraído con OCR:")
                        st.text_area("Contenido:", extracted_text, height=200)
                        
                        if analyze_charts and extracted_text:
                            chart_analysis = analyze_chart_data(extracted_text)
                            st.markdown("---")
                            st.markdown(chart_analysis)
                        
                        # Limpiar archivo temporal de imagen
                        try:
                            os.unlink(img_path)
                        except:
                            pass
            
            else:
                # Procesar imagen directamente
                status_text.text("Procesando imagen...")
                progress_bar.progress(50)
                
                # Mostrar imagen
                st.image(temp_path, caption="Imagen seleccionada", use_column_width=True)
                
                # Extraer texto
                status_text.text("Extrayendo texto...")
                progress_bar.progress(75)
                
                if ocr_method == "EasyOCR (Recomendado)":
                    extracted_text = extract_text_with_easyocr(temp_path)
                else:
                    extracted_text = extract_text_with_tesseract(temp_path)
                
                progress_bar.progress(100)
                status_text.text("✅ Procesamiento completado")
                
                # Mostrar resultados
                st.success("Texto extraído:")
                st.text_area("Contenido:", extracted_text, height=200)
                
                if analyze_charts and extracted_text:
                    chart_analysis = analyze_chart_data(extracted_text)
                    st.markdown("---")
                    st.markdown(chart_analysis)

        except Exception as e:
            st.error(f"Error durante el procesamiento: {str(e)}")
        
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Limpiar barra de progreso
            progress_bar.empty()
            status_text.empty()

    else:
        st.info("📋 Por favor, selecciona un archivo PDF o una imagen para comenzar.")

# Información adicional
with st.expander("ℹ️ Información sobre los métodos OCR"):
    st.markdown("""
    ### **EasyOCR (Recomendado)**
    - ✅ Mejor precisión para texto en español
    - ✅ Maneja mejor las gráficas y tablas
    - ✅ Funciona bien con diferentes fuentes
    - ❌ Requiere más recursos computacionales
    
    ### **Tesseract OCR**  
    - ✅ Muy rápido
    - ✅ Funciona bien con texto simple
    - ❌ Menor precisión en gráficas complejas
    - ❌ Puede tener problemas con fuentes especiales
    
    ### **Consejos para mejores resultados:**
    - Usa imágenes con buena resolución
    - Asegúrate de que el texto tenga buen contraste
    - Para PDFs, el texto se extrae directamente cuando es posible
    """)

with st.expander("🛠️ Instalación de dependencias"):
    st.code("""
            # Instalar las librerías necesarias
            pip install streamlit
            pip install PyMuPDF  # Para PDFs
            pip install pytesseract  # Para Tesseract OCR
            pip install easyocr  # Para EasyOCR (recomendado)
            pip install Pillow  # Para manejo de imágenes

            # Para Tesseract, también necesitas instalar el binario:
            # Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-spa
            # Windows: Descargar desde https://github.com/UB-Mannheim/tesseract/wiki
            # macOS: brew install tesseract
                """, language="bash")