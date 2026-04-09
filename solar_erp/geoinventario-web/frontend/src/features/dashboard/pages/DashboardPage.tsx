import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/features/auth/context/AuthContext";
import {
  fetchInventorySummary,
  fetchMaterials,
  fetchPermissions,
} from "@/features/inventory/services/inventoryService";
import type {
  InventorySummary,
  Material,
  PermissionSummary,
} from "@/features/inventory/types";

export function DashboardPage() {
  const { logout, token, user } = useAuth();
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [permissions, setPermissions] = useState<PermissionSummary | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    void Promise.all([
      fetchInventorySummary(token),
      fetchPermissions(token),
      fetchMaterials(token),
    ])
      .then(([summaryResponse, permissionsResponse, materialsResponse]) => {
        setSummary(summaryResponse);
        setPermissions(permissionsResponse);
        setMaterials(materialsResponse.slice(0, 5));
      })
      .catch((requestError) => {
        const message = requestError instanceof Error ? requestError.message : "No se pudo cargar el dashboard";
        setError(message);
      });
  }, [token]);

  return (
    <AppShell
      title="Panel inicial autenticado"
      subtitle="Base inicial del modulo de usuarios y autenticacion para el nuevo GeoInventario Web."
    >
      <div className="stack">
        <p>
          Sesion activa como <strong>{user?.full_name}</strong> ({user?.email}) con rol{" "}
          <strong>{permissions?.role ?? user?.role}</strong>.
        </p>
        <div className="info-grid">
          <article className="info-card">
            <h2>Inventario</h2>
            <p>Materiales: {summary?.total_materials ?? 0}</p>
            <p>Stock total: {summary?.total_stock_units ?? 0}</p>
            <p>Bajo minimo: {summary?.low_stock_materials ?? 0}</p>
          </article>
          <article className="info-card">
            <h2>Permisos</h2>
            <p>Gestionar inventario: {permissions?.can_manage_inventory ? "Si" : "No"}</p>
            <p>Registrar movimientos: {permissions?.can_record_movements ? "Si" : "No"}</p>
            <p>Gestionar usuarios: {permissions?.can_manage_users ? "Si" : "No"}</p>
          </article>
        </div>
        {error ? <p className="error-message">{error}</p> : null}
        <section className="stack">
          <h2 className="section-title">Materiales recientes</h2>
          {materials.length === 0 ? (
            <p className="hint-text">Todavia no hay materiales creados. El backend ya esta listo para recibirlos.</p>
          ) : (
            <div className="table-like">
              {materials.map((material) => (
                <article className="row-card" key={material.id}>
                  <div>
                    <strong>{material.name}</strong>
                    <p>{material.sku}</p>
                  </div>
                  <div>
                    <strong>{material.stock}</strong>
                    <p>{material.unit}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
        <div className="inline-actions">
          <button type="button" onClick={logout}>
            Cerrar sesion
          </button>
          <Link className="button-link ghost-link" to="/login">
            Ir a auth
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
