import type { House } from "./house.types";

const API_URL = "http://localhost:8000/houses";

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export const houseApi = {
  async list(): Promise<House[]> {
    const response = await fetch(`${API_URL}/`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<House> {
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
