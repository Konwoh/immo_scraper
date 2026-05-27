import type { JobSchedule } from "./job_schedule.types";

const API_BASE = import.meta.env.VITE_BASE_URL
const API_URL = `http://${API_BASE}:8000/jobs_schedules`;

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export const jobScheduleApi = {
  async list(): Promise<JobSchedule[]> {
    const response = await fetch(`${API_URL}/`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Fehler beim Laden");
    }

    return response.json();
  },

  async get(id: number): Promise<JobSchedule> {
    const response = await fetch(`${API_URL}/${id}`, {
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Nicht gefunden");
    }

    return response.json();
  },

  async create(data: Partial<JobSchedule>): Promise<JobSchedule> {
    const response = await fetch(`${API_URL}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        job_type: data.job_type,
        interval: data.interval,
        search_params_id: data.search_params_id,
        enabled: data.enabled,
        next_run: data.next_run
      }),
    });

    if (!response.ok) {
      throw new Error("Konnte nicht erstellt werden");
    }

    return response.json();
  },
};
