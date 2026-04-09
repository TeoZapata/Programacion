import { apiGet, apiPost } from "@/services/http";

import type {
  CreateMaterialPayload,
  CreateMovementPayload,
  InventoryMovement,
  InventorySummary,
  Material,
  PermissionSummary,
} from "@/features/inventory/types";

export function fetchInventorySummary(token: string): Promise<InventorySummary> {
  return apiGet<InventorySummary>("/inventory/summary", token);
}

export function fetchPermissions(token: string): Promise<PermissionSummary> {
  return apiGet<PermissionSummary>("/inventory/permissions", token);
}

export function fetchMaterials(token: string): Promise<Material[]> {
  return apiGet<Material[]>("/inventory/materials", token);
}

export function fetchMovements(token: string): Promise<InventoryMovement[]> {
  return apiGet<InventoryMovement[]>("/inventory/movements", token);
}

export function createMaterial(token: string, payload: CreateMaterialPayload): Promise<Material> {
  return apiPost<Material>("/inventory/materials", payload, token);
}

export function createMovement(
  token: string,
  payload: CreateMovementPayload,
): Promise<InventoryMovement> {
  return apiPost<InventoryMovement>("/inventory/movements", payload, token);
}
