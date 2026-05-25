import type { Apartment } from "./apartment.types";

const API_BASE = import.meta.env.VITE_BASE_URL
const API_URL = `http://${API_BASE}:8000/apartments`;

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export const apartmentApi = {
  async list(): Promise<Apartment[]> {
    const response = await fetch(`${API_URL}/`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<Apartment> {
    const response = await fetch(`${API_URL}/${id}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async delete(id: number): Promise<void> {
    const response = await fetch(`${API_URL}/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim Löschen");
    }
  },
};
