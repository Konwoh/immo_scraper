import { apiFetch, API_BASE } from "@/api/client";
import type { Job } from "./job.types";

const API_URL = `${API_BASE}/jobs`;

export const jobApi = {
  async list(): Promise<Job[]> {
    const response = await apiFetch(`${API_URL}/`);

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<Job> {
    const response = await apiFetch(`${API_URL}/${id}`);

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async create(data: Partial<Job>): Promise<Job> {
    const response = await apiFetch(`${API_URL}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_type: data.job_type,
        status: data.status ?? "open",
        search_params_id: data.search_params_id,
      }),
    });

    if (!response.ok) {
      throw new Error("Konnte nicht erstellt werden");
    }

    return response.json();
  },
};
