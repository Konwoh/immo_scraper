import { apiFetch, API_BASE } from "@/api/client";
import { type PaginatedResponse, type PaginationParams } from "@/api/pagination";
import {
  buildEstateListQuery,
  type EstateFilterValues,
} from "@/entities/estates/estateFilters";
import type { Apartment } from "./apartment.types";

const API_URL = `${API_BASE}/apartments`;

export const apartmentApi = {
  async list(
    params?: PaginationParams & EstateFilterValues,
  ): Promise<PaginatedResponse<Apartment>> {
    const response = await apiFetch(
      `${API_URL}/${buildEstateListQuery(params)}`,
    );

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<Apartment> {
    const response = await apiFetch(`${API_URL}/${id}`);

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async delete(id: number): Promise<void> {
    const response = await apiFetch(`${API_URL}/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Fehler beim Löschen");
    }
  },
};
