import { apiFetch, API_BASE } from "@/api/client";
import type { SearchParams } from "./search_params.types";

const API_URL = `${API_BASE}/search_params`;

export const searchParamsApi = {
  async list(): Promise<SearchParams[]> {
    const response = await apiFetch(`${API_URL}/`);

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<SearchParams> {
    const response = await apiFetch(`${API_URL}/${id}`);

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async create(data: Partial<SearchParams>): Promise<SearchParams> {
    const response = await apiFetch(`${API_URL}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        site: data.site,
        country: data.country, 
        state: data.state, 
        city: data.city, 
        distance: data.distance, 
        zip_code: data.zip_code, 
        estate_type: data.estate_type, 
        rent_or_buy: data.rent_or_buy, 
        page: data.page, 
        listing_count: data.listing_count 
      }),
    });

    if (!response.ok) {
      throw new Error("Konnte nicht erstellt werden");
    }

    return response.json();
  },
  async delete(id: number): Promise<void> {
    const response = await apiFetch(`${API_URL}/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("Fehler beim löschen");
    }
  },
  async update(id: number): Promise<SearchParams> {
    const response = await apiFetch(`${API_URL}/${id}`, {
      method: "PUT",
    });

    if (!response.ok) {
      throw new Error("Fehler beim löschen");
    }

    return response.json();
  },
};
