import type { UserRole } from "@/features/auth/types";

export type InventorySummary = {
  low_stock_materials: number;
  total_materials: number;
  total_stock_units: number;
};

export type PermissionSummary = {
  can_manage_inventory: boolean;
  can_manage_users: boolean;
  can_record_movements: boolean;
  role: UserRole;
};

export type Material = {
  created_at: string;
  description: string | null;
  id: number;
  minimum_stock: number;
  name: string;
  sku: string;
  stock: number;
  unit: string;
};
