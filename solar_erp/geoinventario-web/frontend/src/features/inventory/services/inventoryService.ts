import { apiGet } from "@/services/http";

import type { InventorySummary, Material, PermissionSummary } from "@/features/inventory/types";

export function fetchInventorySummary(token: string): Promise<InventorySummary> {
  return apiGet<InventorySummary>("/inventory/summary", token);
}

export function fetchPermissions(token: string): Promise<PermissionSummary> {
  return apiGet<PermissionSummary>("/inventory/permissions", token);
}

export function fetchMaterials(token: string): Promise<Material[]> {
  return apiGet<Material[]>("/inventory/materials", token);
}
