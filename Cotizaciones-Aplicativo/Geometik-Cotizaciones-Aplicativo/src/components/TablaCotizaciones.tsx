import React, { useState } from "react";
import * as XLSX from "xlsx";

const ComponenteCotizacion = () => {
  const [paso, setPaso] = useState(1);
  const [datos, setDatos] = useState({
    nombreCliente: "",
    numeroFactura: "",
    latitud: "",
    longitud: "",
    consumos: {
      enero: "",
      febrero: "",
      marzo: "",
      abril: "",
      mayo: "",
      junio: "",
      julio: "",
      agosto: "",
      septiembre: "",
      octubre: "",
      noviembre: "",
      diciembre: "",
    },
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    if (name.startsWith("consumo_")) {
      const mes = name.split("_")[1];
      setDatos((prev) => ({
        ...prev,
        consumos: {
          ...prev.consumos,
          [mes]: value,
        },
      }));
    } else {
      setDatos((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const validarPrimerPaso = () => {
    return (
      datos.nombreCliente &&
      datos.numeroFactura &&
      datos.latitud &&
      datos.longitud
    );
  };

  const generarExcel = () => {
    // Crear arreglo de datos para el Excel
    const datosExcel = [
      ["Información del Cliente"],
      ["Nombre del Cliente", datos.nombreCliente],
      ["Número de Factura", datos.numeroFactura],
      ["Latitud", datos.latitud],
      ["Longitud", datos.longitud],
      [],
      ["Consumos Mensuales (kW)"],
      ["Mes", "Consumo"],
      ...Object.entries(datos.consumos).map(([mes, consumo]) => [
        mes.charAt(0).toUpperCase() + mes.slice(1),
        consumo,
      ]),
    ];

    // Crear libro de trabajo y hoja
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(datosExcel);

    // Agregar hoja al libro
    XLSX.utils.book_append_sheet(wb, ws, "Cotización");

    // Guardar archivo
    XLSX.writeFile(wb, `Cotizacion_${datos.numeroFactura}.xlsx`);
  };

  if (paso === 1) {
    return (
      <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
        <h2 style={{ marginBottom: "20px" }}>Datos del Cliente</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <input
            type="text"
            name="nombreCliente"
            value={datos.nombreCliente}
            onChange={handleChange}
            placeholder="Nombre del Cliente"
            style={inputStyle}
          />
          <input
            type="text"
            name="numeroFactura"
            value={datos.numeroFactura}
            onChange={handleChange}
            placeholder="Número de Factura"
            style={inputStyle}
          />
          <input
            type="number"
            name="latitud"
            value={datos.latitud}
            onChange={handleChange}
            placeholder="Latitud"
            style={inputStyle}
          />
          <input
            type="number"
            name="longitud"
            value={datos.longitud}
            onChange={handleChange}
            placeholder="Longitud"
            style={inputStyle}
          />
          <button
            onClick={() => validarPrimerPaso() && setPaso(2)}
            style={buttonStyle}
          >
            Siguiente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
      <h2 style={{ marginBottom: "20px" }}>Consumo Mensual (kW)</h2>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "15px",
        }}
      >
        {Object.keys(datos.consumos).map((mes) => (
          <input
            key={mes}
            type="number"
            name={`consumo_${mes}`}
            value={mes}
            onChange={handleChange}
            placeholder={mes.charAt(0).toUpperCase() + mes.slice(1)}
            style={inputStyle}
          />
        ))}
      </div>
      <div
        style={{
          marginTop: "20px",
          display: "flex",
          gap: "10px",
          justifyContent: "space-between",
        }}
      >
        <button
          onClick={() => setPaso(1)}
          style={{ ...buttonStyle, backgroundColor: "#666" }}
        >
          Anterior
        </button>
        <button
          onClick={generarExcel}
          style={{ ...buttonStyle, backgroundColor: "#28a745" }}
        >
          Generar Excel
        </button>
      </div>
    </div>
  );
};

// Estilos en línea para mantenerlo simple
const inputStyle = {
  padding: "8px",
  border: "1px solid #ccc",
  borderRadius: "4px",
  fontSize: "16px",
  width: "100%",
};

const buttonStyle = {
  padding: "10px 20px",
  backgroundColor: "#007bff",
  color: "white",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer",
  fontSize: "16px",
};

export default ComponenteCotizacion;
