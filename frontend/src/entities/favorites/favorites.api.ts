import { apiFetch, API_BASE } from "@/api/client";
import { MAX_PAGE_SIZE, type PaginatedResponse } from "@/api/pagination";
import type { EstateType, Favorite } from "./favorites.types";

const API_URL = `${API_BASE}/favorites`;

export const favoritesApi = {
  async list(): Promise<Favorite[]> {
    const favorites: Favorite[] = [];
    let page = 1;

    while (true) {
      const response = await apiFetch(
        `${API_URL}/?page=${page}&page_size=${MAX_PAGE_SIZE}`,
      );

      if (!response.ok) {
        throw new Error("Fehler beim Laden der Favoriten");
      }

      const data: PaginatedResponse<Favorite> = await response.json();
      favorites.push(...data.items);

      if (data.current_page >= data.total_pages) {
        break;
      }

      page += 1;
    }

    return favorites;
  },

  async add(estateType: EstateType, estateId: number): Promise<void> {
    const response = await apiFetch(`${API_URL}/${estateType}/${estateId}`, {
      method: "POST",
    });

    if (!response.ok && response.status !== 409) {
      throw new Error("Fehler beim Hinzufügen zu Favoriten");
    }
  },

  async remove(estateType: EstateType, estateId: number): Promise<void> {
    const response = await apiFetch(`${API_URL}/${estateType}/${estateId}`, {
      method: "DELETE",
    });

    if (!response.ok && response.status !== 404) {
      throw new Error("Fehler beim Entfernen aus Favoriten");
    }
  },
};
