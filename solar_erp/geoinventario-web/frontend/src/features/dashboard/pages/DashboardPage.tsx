import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/features/auth/context/AuthContext";
import {
  createMaterial,
  createMovement,
  fetchMovements,
  fetchInventorySummary,
  fetchMaterials,
  fetchPermissions,
} from "@/features/inventory/services/inventoryService";
import type {
  CreateMaterialPayload,
  CreateMovementPayload,
  InventoryMovement,
  InventorySummary,
  Material,
  PermissionSummary,
} from "@/features/inventory/types";

export function DashboardPage() {
  const { logout, token, user } = useAuth();
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [permissions, setPermissions] = useState<PermissionSummary | null>(null);
  const [materials, setMaterials] = useState<Material[]>([]);
  const [movements, setMovements] = useState<InventoryMovement[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmittingMaterial, setIsSubmittingMaterial] = useState(false);
  const [isSubmittingMovement, setIsSubmittingMovement] = useState(false);
  const [materialForm, setMaterialForm] = useState<CreateMaterialPayload>({
    description: "",
    minimum_stock: 0,
    name: "",
    sku: "",
    unit: "unidad",
  });
  const [movementForm, setMovementForm] = useState<CreateMovementPayload>({
    material_id: 0,
    movement_type: "in",
    note: "",
    quantity: 1,
    unit_cost: 0,
  });

  async function loadDashboard(currentToken: string) {
    const [summaryResponse, permissionsResponse, materialsResponse, movementsResponse] = await Promise.all([
      fetchInventorySummary(currentToken),
      fetchPermissions(currentToken),
      fetchMaterials(currentToken),
      fetchMovements(currentToken),
    ]);

    setSummary(summaryResponse);
    setPermissions(permissionsResponse);
    setMaterials(materialsResponse);
    setMovements(movementsResponse.slice(0, 6));
    setMovementForm((previous) => ({
      ...previous,
      material_id: previous.material_id || materialsResponse[0]?.id || 0,
    }));
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    void loadDashboard(token)
      .catch((requestError) => {
        const message = requestError instanceof Error ? requestError.message : "No se pudo cargar el dashboard";
        setError(message);
      });
  }, [token]);

  async function handleCreateMaterial(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) {
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsSubmittingMaterial(true);

    try {
      await createMaterial(token, {
        ...materialForm,
        description: materialForm.description?.trim() || undefined,
      });
      await loadDashboard(token);
      setMaterialForm({
        description: "",
        minimum_stock: 0,
        name: "",
        sku: "",
        unit: "unidad",
      });
      setSuccessMessage("Material creado correctamente.");
    } catch (submissionError) {
      const message = submissionError instanceof Error ? submissionError.message : "No se pudo crear el material";
      setError(message);
    } finally {
      setIsSubmittingMaterial(false);
    }
  }

  async function handleCreateMovement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !movementForm.material_id) {
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsSubmittingMovement(true);

    try {
      await createMovement(token, {
        ...movementForm,
        note: movementForm.note?.trim() || undefined,
        unit_cost: movementForm.unit_cost && movementForm.unit_cost > 0 ? movementForm.unit_cost : undefined,
      });
      await loadDashboard(token);
      setMovementForm((previous) => ({
        ...previous,
        movement_type: "in",
        note: "",
        quantity: 1,
        unit_cost: 0,
      }));
      setSuccessMessage("Movimiento registrado correctamente.");
    } catch (submissionError) {
      const message = submissionError instanceof Error ? submissionError.message : "No se pudo registrar el movimiento";
      setError(message);
    } finally {
      setIsSubmittingMovement(false);
    }
  }

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
        {successMessage ? <p className="success-message">{successMessage}</p> : null}
        <section className="stack">
          <h2 className="section-title">Materiales recientes</h2>
          {materials.length === 0 ? (
            <p className="hint-text">Todavia no hay materiales creados. El backend ya esta listo para recibirlos.</p>
          ) : (
            <div className="table-like">
              {materials.slice(0, 6).map((material) => (
                <article className="row-card" key={material.id}>
                  <div>
                    <strong>{material.name}</strong>
                    <p>
                      {material.sku} · Min {material.minimum_stock}
                    </p>
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
        <section className="feature-grid">
          <article className="panel-card">
            <h2 className="section-title">Crear material</h2>
            {permissions?.can_manage_inventory ? (
              <form className="stack" onSubmit={handleCreateMaterial}>
                <label>
                  Nombre
                  <input
                    value={materialForm.name}
                    onChange={(event) =>
                      setMaterialForm((previous) => ({ ...previous, name: event.target.value }))
                    }
                    required
                  />
                </label>
                <label>
                  SKU
                  <input
                    value={materialForm.sku}
                    onChange={(event) =>
                      setMaterialForm((previous) => ({ ...previous, sku: event.target.value }))
                    }
                    required
                  />
                </label>
                <div className="compact-grid">
                  <label>
                    Unidad
                    <input
                      value={materialForm.unit}
                      onChange={(event) =>
                        setMaterialForm((previous) => ({ ...previous, unit: event.target.value }))
                      }
                    />
                  </label>
                  <label>
                    Stock minimo
                    <input
                      min="0"
                      type="number"
                      value={materialForm.minimum_stock}
                      onChange={(event) =>
                        setMaterialForm((previous) => ({
                          ...previous,
                          minimum_stock: Number(event.target.value),
                        }))
                      }
                    />
                  </label>
                </div>
                <label>
                  Descripcion
                  <textarea
                    className="text-area"
                    value={materialForm.description ?? ""}
                    onChange={(event) =>
                      setMaterialForm((previous) => ({ ...previous, description: event.target.value }))
                    }
                    rows={3}
                  />
                </label>
                <button disabled={isSubmittingMaterial} type="submit">
                  {isSubmittingMaterial ? "Guardando..." : "Crear material"}
                </button>
              </form>
            ) : (
              <p className="hint-text">Tu rol no tiene permiso para crear materiales.</p>
            )}
          </article>
          <article className="panel-card">
            <h2 className="section-title">Registrar movimiento</h2>
            {permissions?.can_record_movements ? (
              materials.length > 0 ? (
                <form className="stack" onSubmit={handleCreateMovement}>
                  <label>
                    Material
                    <select
                      value={movementForm.material_id}
                      onChange={(event) =>
                        setMovementForm((previous) => ({
                          ...previous,
                          material_id: Number(event.target.value),
                        }))
                      }
                    >
                      {materials.map((material) => (
                        <option key={material.id} value={material.id}>
                          {material.name} ({material.sku})
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="compact-grid">
                    <label>
                      Tipo
                      <select
                        value={movementForm.movement_type}
                        onChange={(event) =>
                          setMovementForm((previous) => ({
                            ...previous,
                            movement_type: event.target.value as CreateMovementPayload["movement_type"],
                          }))
                        }
                      >
                        <option value="in">Entrada</option>
                        <option value="out">Salida</option>
                        <option value="adjustment">Ajuste</option>
                      </select>
                    </label>
                    <label>
                      Cantidad
                      <input
                        min="1"
                        type="number"
                        value={movementForm.quantity}
                        onChange={(event) =>
                          setMovementForm((previous) => ({
                            ...previous,
                            quantity: Number(event.target.value),
                          }))
                        }
                      />
                    </label>
                  </div>
                  <label>
                    Costo unitario
                    <input
                      min="0"
                      step="0.01"
                      type="number"
                      value={movementForm.unit_cost ?? 0}
                      onChange={(event) =>
                        setMovementForm((previous) => ({
                          ...previous,
                          unit_cost: Number(event.target.value),
                        }))
                      }
                    />
                  </label>
                  <label>
                    Nota
                    <textarea
                      className="text-area"
                      value={movementForm.note ?? ""}
                      onChange={(event) =>
                        setMovementForm((previous) => ({ ...previous, note: event.target.value }))
                      }
                      rows={3}
                    />
                  </label>
                  <button disabled={isSubmittingMovement} type="submit">
                    {isSubmittingMovement ? "Guardando..." : "Registrar movimiento"}
                  </button>
                </form>
              ) : (
                <p className="hint-text">Primero crea al menos un material para poder registrar movimientos.</p>
              )
            ) : (
              <p className="hint-text">Tu rol no tiene permiso para registrar movimientos.</p>
            )}
          </article>
        </section>
        <section className="stack">
          <h2 className="section-title">Movimientos recientes</h2>
          {movements.length === 0 ? (
            <p className="hint-text">Todavia no hay movimientos registrados.</p>
          ) : (
            <div className="table-like">
              {movements.map((movement) => {
                const material = materials.find((item) => item.id === movement.material_id);

                return (
                  <article className="row-card" key={movement.id}>
                    <div>
                      <strong>{material?.name ?? `Material #${movement.material_id}`}</strong>
                      <p>
                        {movement.movement_type} · Usuario {movement.user_id}
                      </p>
                    </div>
                    <div>
                      <strong>{movement.quantity}</strong>
                      <p>{movement.note || "Sin nota"}</p>
                    </div>
                  </article>
                );
              })}
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
