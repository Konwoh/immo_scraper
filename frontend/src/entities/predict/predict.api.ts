import { apiFetch, API_BASE } from "@/api/client";
import type { PredictionPayload, PredictionResponse } from "./predict.types";

export async function predictPrice(
  payload: PredictionPayload,
): Promise<PredictionResponse> {
  const response = await apiFetch(`${API_BASE}/predict/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Preisvorhersage fehlgeschlagen");
  }

  return response.json();
}
