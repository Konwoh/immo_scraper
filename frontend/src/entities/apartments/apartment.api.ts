import { apiFetch, API_BASE } from "@/api/client";
import type { Apartment } from "./apartment.types";

const API_URL = `${API_BASE}/apartments`;

export const apartmentApi = {
  async list(): Promise<Apartment[]> {
    const response = await apiFetch(`${API_URL}/`);

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
