import React, { useState, ChangeEvent } from "react";
import * as XLSX from "xlsx";
import { Card, CardBody, CardHeader } from "@nextui-org/react";
import { Input } from "@nextui-org/react";
import { Button } from "@nextui-org/react";

interface Consumos {
  enero: string;
  febrero: string;
  marzo: string;
  abril: string;
  mayo: string;
  junio: string;
  julio: string;
  agosto: string;
  septiembre: string;
  octubre: string;
  noviembre: string;
  diciembre: string;
}

interface DatosCotizacion {
  nombreCliente: string;
  numeroFactura: number;
  latitud: number;
  longitud: number;
  valorKilovatio: string;
  consumos: Consumos;
}

const datosIniciales: DatosCotizacion = {
  nombreCliente: "",
  numeroFactura: 0,
  latitud: 0,
  longitud: 0,
  valorKilovatio: "",
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
};

const ComponenteCotizacion: React.FC = () => {
  const [paso, setPaso] = useState<number>(1);
  const [datos, setDatos] = useState<DatosCotizacion>(datosIniciales);

  const handleChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    if (name.startsWith("consumo_")) {
      const mes = name.split("_")[1] as keyof Consumos;
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

  const validarPrimerPaso = (): boolean => {
    return Boolean(
      datos.nombreCliente &&
        datos.numeroFactura &&
        datos.latitud &&
        datos.longitud
    );
  };

  const validarSegundoPaso = (): boolean => {
    return Object.values(datos.consumos).some((consumo) => consumo !== "");
  };

  const calcularConsumoTotal = (): number => {
    return Object.values(datos.consumos).reduce(
      (total, consumo) => total + (Number(consumo) || 0),
      0
    );
  };

  const calcularCostoTotal = (): number => {
    const consumoTotal = calcularConsumoTotal();
    return consumoTotal * Number(datos.valorKilovatio);
  };

  const generarExcel = (): void => {
    const consumoTotal = calcularConsumoTotal();
    const costoTotal = calcularCostoTotal();

    const datosExcel = [
      ["Información del Cliente"],
      ["Nombre del Cliente", datos.nombreCliente],
      ["Número de Factura", datos.numeroFactura],
      ["Latitud", datos.latitud],
      ["Longitud", datos.longitud],
      ["Valor del Kilovatio", datos.valorKilovatio],
      [],
      ["Consumos Mensuales (kW)"],
      ["Mes", "Consumo", "Costo"],
      ...Object.entries(datos.consumos).map(([mes, consumo]) => [
        mes.charAt(0).toUpperCase() + mes.slice(1),
        consumo,
        Number(consumo) * Number(datos.valorKilovatio),
      ]),
      [],
      ["Totales"],
      ["Consumo Total (kW)", consumoTotal],
      ["Costo Total", costoTotal],
    ];

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(datosExcel);
    XLSX.utils.book_append_sheet(wb, ws, "Cotización");
    XLSX.writeFile(wb, `Cotizacion_${datos.numeroFactura}.xlsx`);
  };

  const renderPaso1 = (): JSX.Element => (
    <Card className="max-w-lg mx-auto">
      <CardHeader className="flex flex-col gap-2">
        <h2 className="text-xl font-bold">Datos del Cliente</h2>
      </CardHeader>
      <CardBody className="flex flex-col gap-4">
        <Input
          type="text"
          name="nombreCliente"
          value={datos.nombreCliente}
          onChange={handleChange}
          label="Nombre del Cliente"
          variant="bordered"
        />
        <Input
          type="text"
          name="numeroFactura"
          value={String(datos.numeroFactura)}
          onChange={handleChange}
          label="Número de Factura"
          variant="bordered"
        />
        <Input
          type="number"
          name="latitud"
          value={String(datos.latitud)}
          onChange={handleChange}
          label="Latitud"
          variant="bordered"
        />
        <Input
          type="number"
          name="longitud"
          value={String(datos.longitud)}
          onChange={handleChange}
          label="Longitud"
          variant="bordered"
        />
        <Button
          color="primary"
          onClick={() => validarPrimerPaso() && setPaso(2)}
        >
          Siguiente
        </Button>
      </CardBody>
    </Card>
  );

  const renderPaso2 = (): JSX.Element => (
    <Card className="max-w-4xl mx-auto">
      <CardHeader className="flex flex-col gap-2">
        <h2 className="text-xl font-bold">Consumo Mensual (kW)</h2>
      </CardHeader>
      <CardBody>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(Object.entries(datos.consumos) as [keyof Consumos, string][]).map(
            ([mes, consumo]) => (
              <Input
                key={mes}
                type="number"
                name={`consumo_${mes}`}
                value={datos.consumos[mes]}
                onChange={handleChange}
                label={mes.charAt(0).toUpperCase() + mes.slice(1)}
                variant="bordered"
              />
            )
          )}
        </div>
        <div className="flex justify-between mt-6">
          <Button color="default" onClick={() => setPaso(1)}>
            Anterior
          </Button>
          <Button
            color="primary"
            onClick={() => validarSegundoPaso() && setPaso(3)}
          >
            Siguiente
          </Button>
        </div>
      </CardBody>
    </Card>
  );

  const renderPaso3 = (): JSX.Element => (
    <Card className="max-w-lg mx-auto">
      <CardHeader className="flex flex-col gap-2">
        <h2 className="text-xl font-bold">Valor del Kilovatio</h2>
      </CardHeader>
      <CardBody className="flex flex-col gap-4">
        <Input
          type="number"
          name="valorKilovatio"
          value={datos.valorKilovatio}
          onChange={handleChange}
          label="Valor del Kilovatio"
          variant="bordered"
        />
        <div className="flex justify-between">
          <Button color="default" onClick={() => setPaso(2)}>
            Anterior
          </Button>
          <Button
            color="primary"
            onClick={() => datos.valorKilovatio && setPaso(4)}
          >
            Siguiente
          </Button>
        </div>
      </CardBody>
    </Card>
  );

  const renderResumen = (): JSX.Element => (
    <Card className="max-w-2xl mx-auto">
      <CardHeader className="flex flex-col gap-2">
        <h2 className="text-xl font-bold">Resumen de la Cotización</h2>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <strong>Cliente:</strong>
            <span>{datos.nombreCliente}</span>
            <strong>Factura:</strong>
            <span>{datos.numeroFactura}</span>
            <strong>Ubicación:</strong>
            <span>
              {datos.latitud}, {datos.longitud}
            </span>
            <strong>Valor Kilovatio:</strong>
            <span>${datos.valorKilovatio}</span>
            <strong>Consumo Total:</strong>
            <span>{calcularConsumoTotal()} kW</span>
            <strong>Costo Total Estimado:</strong>
            <span>${calcularCostoTotal().toFixed(2)}</span>
          </div>
          <div className="mt-6 flex justify-between">
            <Button color="default" onClick={() => setPaso(3)}>
              Anterior
            </Button>
            <Button color="success" onClick={generarExcel}>
              Confirmar y Generar Excel
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );

  const renderPaso = (): JSX.Element => {
    switch (paso) {
      case 1:
        return renderPaso1();
      case 2:
        return renderPaso2();
      case 3:
        return renderPaso3();
      case 4:
        return renderResumen();
      default:
        return renderPaso1();
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex justify-center items-center gap-4">
          {[1, 2, 3, 4].map((stepNumber) => (
            <div
              key={stepNumber}
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                paso >= stepNumber ? "bg-blue-500 text-white" : "bg-gray-200"
              }`}
            >
              {stepNumber}
            </div>
          ))}
        </div>
      </div>
      {renderPaso()}
    </div>
  );
};

export default ComponenteCotizacion;
