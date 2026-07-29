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

export async function getPredictionPayloadFromUrl(
  url: string,
): Promise<PredictionPayload> {
  const response = await apiFetch(
    `${API_BASE}/predict/get_prediction_payload?url=${encodeURIComponent(url)}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error("Inseratsdaten konnten nicht geladen werden");
  }

  return response.json();
}
