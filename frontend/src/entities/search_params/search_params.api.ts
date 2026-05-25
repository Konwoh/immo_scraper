import type { SearchParams } from "./search_params.types";

const API_BASE = import.meta.env.VITE_BASE_URL
const API_URL = `http://${API_BASE}:8000/search_params`;

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export const searchParamsApi = {
  async list(): Promise<SearchParams[]> {
    const response = await fetch(`${API_URL}/`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<SearchParams> {
    const response = await fetch(`${API_URL}/${id}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async create(data: Partial<SearchParams>): Promise<SearchParams> {
    const response = await fetch(`${API_URL}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
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
    const response = await fetch(`${API_URL}/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim löschen");
    }
  },
  async update(id: number): Promise<SearchParams> {
    const response = await fetch(`${API_URL}/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim löschen");
    }

    return response.json();
  },
};
