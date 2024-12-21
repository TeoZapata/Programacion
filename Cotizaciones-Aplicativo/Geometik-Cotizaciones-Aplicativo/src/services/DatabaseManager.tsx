import React from "react";
import Dexie, { Table } from "dexie";

// Interfaces
export interface Consumos {
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

export interface Cotizacion {
  id?: number;
  nombreCliente: string;
  numeroFactura: string;
  latitud: string;
  longitud: string;
  valorKilovatio: string;
  consumos: Consumos;
  consumoTotal: number;
  costoTotal: number;
  fechaCreacion: Date;
  estado: "pendiente" | "aprobada" | "rechazada";
  notas?: string;
}

export interface EstadisticasCotizacion {
  totalCotizaciones: number;
  consumoTotalGeneral: number;
  costoTotalGeneral: number;
  promedioConsumo: number;
  promedioCosto: number;
}

// Clase principal de la base de datos
class CotizacionesDatabase extends Dexie {
  cotizaciones!: Table<Cotizacion>;

  constructor() {
    super("CotizacionesDB");

    this.version(1).stores({
      cotizaciones: "++id, nombreCliente, numeroFactura, fechaCreacion, estado",
    });
  }
}

// Contexto para el gestor de base de datos
export const DatabaseContext = React.createContext<DatabaseManager | null>(
  null
);

// Hook personalizado para usar el gestor de base de datos
export const useDatabaseManager = () => {
  const context = React.useContext(DatabaseContext);
  if (!context) {
    throw new Error(
      "useDatabaseManager debe ser usado dentro de un DatabaseProvider"
    );
  }
  return context;
};

// Componente proveedor para el contexto de la base de datos
interface DatabaseProviderProps {
  children: React.ReactNode;
}

export const DatabaseProvider: React.FC<DatabaseProviderProps> = ({
  children,
}) => {
  const [dbManager] = React.useState(() => new DatabaseManager());

  return (
    <DatabaseContext.Provider value={dbManager}>
      {children}
    </DatabaseContext.Provider>
  );
};

// Clase gestora de la base de datos
export class DatabaseManager {
  private db: CotizacionesDatabase;

  constructor() {
    this.db = new CotizacionesDatabase();
  }

  // Métodos básicos CRUD
  async crearCotizacion(
    cotizacion: Omit<Cotizacion, "id" | "fechaCreacion">
  ): Promise<number> {
    try {
      const nuevaCotizacion = {
        ...cotizacion,
        fechaCreacion: new Date(),
      };

      const id = await this.db.cotizaciones.add(nuevaCotizacion);
      return id;
    } catch (error) {
      console.error("Error al crear cotización:", error);
      throw new Error("No se pudo crear la cotización");
    }
  }

  async obtenerCotizacion(id: number): Promise<Cotizacion | undefined> {
    try {
      const cotizacion = await this.db.cotizaciones.get(id);
      return cotizacion;
    } catch (error) {
      console.error("Error al obtener cotización:", error);
      throw new Error("No se pudo obtener la cotización");
    }
  }

  async actualizarCotizacion(
    id: number,
    datos: Partial<Cotizacion>
  ): Promise<void> {
    try {
      await this.db.cotizaciones.update(id, datos);
    } catch (error) {
      console.error("Error al actualizar cotización:", error);
      throw new Error("No se pudo actualizar la cotización");
    }
  }

  async eliminarCotizacion(id: number): Promise<void> {
    try {
      await this.db.cotizaciones.delete(id);
    } catch (error) {
      console.error("Error al eliminar cotización:", error);
      throw new Error("No se pudo eliminar la cotización");
    }
  }

  // Métodos de consulta avanzados
  async obtenerTodasLasCotizaciones(): Promise<Cotizacion[]> {
    try {
      return await this.db.cotizaciones.toArray();
    } catch (error) {
      console.error("Error al obtener cotizaciones:", error);
      throw new Error("No se pudieron obtener las cotizaciones");
    }
  }

  async buscarCotizaciones(criterio: {
    texto?: string;
    estado?: "pendiente" | "aprobada" | "rechazada";
    fechaInicio?: Date;
    fechaFin?: Date;
  }): Promise<Cotizacion[]> {
    try {
      let cotizaciones = await this.db.cotizaciones.toArray();

      if (criterio.texto) {
        const textoBusqueda = criterio.texto.toLowerCase();
        cotizaciones = cotizaciones.filter(
          (c) =>
            c.nombreCliente.toLowerCase().includes(textoBusqueda) ||
            c.numeroFactura.toLowerCase().includes(textoBusqueda)
        );
      }

      if (criterio.estado) {
        cotizaciones = cotizaciones.filter((c) => c.estado === criterio.estado);
      }

      if (criterio.fechaInicio) {
        cotizaciones = cotizaciones.filter(
          (c) => new Date(c.fechaCreacion) >= criterio.fechaInicio!
        );
      }

      if (criterio.fechaFin) {
        cotizaciones = cotizaciones.filter(
          (c) => new Date(c.fechaCreacion) <= criterio.fechaFin!
        );
      }

      return cotizaciones;
    } catch (error) {
      console.error("Error al buscar cotizaciones:", error);
      throw new Error("No se pudieron buscar las cotizaciones");
    }
  }

  // Métodos de estadísticas
  async obtenerEstadisticas(): Promise<EstadisticasCotizacion> {
    try {
      const cotizaciones = await this.db.cotizaciones.toArray();
      const totalCotizaciones = cotizaciones.length;

      if (totalCotizaciones === 0) {
        return {
          totalCotizaciones: 0,
          consumoTotalGeneral: 0,
          costoTotalGeneral: 0,
          promedioConsumo: 0,
          promedioCosto: 0,
        };
      }

      const consumoTotalGeneral = cotizaciones.reduce(
        (sum, cot) => sum + cot.consumoTotal,
        0
      );

      const costoTotalGeneral = cotizaciones.reduce(
        (sum, cot) => sum + cot.costoTotal,
        0
      );

      return {
        totalCotizaciones,
        consumoTotalGeneral,
        costoTotalGeneral,
        promedioConsumo: consumoTotalGeneral / totalCotizaciones,
        promedioCosto: costoTotalGeneral / totalCotizaciones,
      };
    } catch (error) {
      console.error("Error al obtener estadísticas:", error);
      throw new Error("No se pudieron obtener las estadísticas");
    }
  }

  // Métodos de exportación
  async exportarCotizacionesCSV(): Promise<string> {
    try {
      const cotizaciones = await this.db.cotizaciones.toArray();
      const headers =
        "ID,Cliente,Factura,Consumo Total,Costo Total,Estado,Fecha\n";

      const rows = cotizaciones
        .map(
          (c) =>
            `${c.id},${c.nombreCliente},${c.numeroFactura},${c.consumoTotal},${c.costoTotal},${c.estado},${c.fechaCreacion}`
        )
        .join("\n");

      return headers + rows;
    } catch (error) {
      console.error("Error al exportar cotizaciones:", error);
      throw new Error("No se pudieron exportar las cotizaciones");
    }
  }

  // Métodos de mantenimiento
  async limpiarCotizacionesAntiguas(diasAntiguedad: number): Promise<number> {
    try {
      const fechaLimite = new Date();
      fechaLimite.setDate(fechaLimite.getDate() - diasAntiguedad);

      const cotizacionesAntiguasIds = await this.db.cotizaciones
        .where("fechaCreacion")
        .below(fechaLimite)
        .primaryKeys();

      await this.db.cotizaciones.bulkDelete(cotizacionesAntiguasIds);

      return cotizacionesAntiguasIds.length;
    } catch (error) {
      console.error("Error al limpiar cotizaciones antiguas:", error);
      throw new Error("No se pudieron limpiar las cotizaciones antiguas");
    }
  }
}

// Exportar una instancia única del gestor
export const dbManager = new DatabaseManager();
