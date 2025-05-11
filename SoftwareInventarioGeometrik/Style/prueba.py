import pandas as pd
import plotly.express as px

# Datos del cronograma
gantt_data = {
    "Tarea": [
        "Diseño e ingeniería del sistema",
        "Trámites y permisos",
        "Adquisición de equipos y materiales",
        "Transporte y logística",
        "Preparación del sitio",
        "Instalación de paneles solares",
        "Instalación eléctrica",
        "Puesta en marcha y pruebas",
        "Inspección y aprobación final (si aplica)",
        "Capacitación y entrega al cliente",
        "Mantenimiento y seguimiento (opcional)"
    ],
    "Inicio": [
        "2025-05-12", "2025-05-12", "2025-05-19", "2025-05-26", "2025-05-26",
        "2025-06-02", "2025-06-02", "2025-06-09", "2025-06-16", "2025-06-16",
        "2025-12-16"
    ],
    "Fin": [
        "2025-05-16", "2025-05-23", "2025-05-23", "2025-05-30", "2025-06-06",
        "2025-06-06", "2025-06-13", "2025-06-13", "2025-06-20", "2025-06-20",
        "2025-12-20"
    ]
}

# Crear DataFrame
df_gantt = pd.DataFrame(gantt_data)
df_gantt["Inicio"] = pd.to_datetime(df_gantt["Inicio"])
df_gantt["Fin"] = pd.to_datetime(df_gantt["Fin"])

# Crear gráfico Gantt
fig = px.timeline(df_gantt, x_start="Inicio", x_end="Fin", y="Tarea", title="Cronograma Gantt - Sistema Fotovoltaico 20kW")
fig.update_yaxes(categoryorder="total ascending")
fig.update_layout(xaxis_title="Fecha", yaxis_title="Actividades", height=600)
fig.show()