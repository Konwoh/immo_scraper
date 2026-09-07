import { API_BASE, apiFetch } from "@/api/client";
import type {
  RecommendationEstateType,
  RecommendationListResponse,
} from "./recommendations.types";

export const recommendationsApi = {
  async list(
    estateType: RecommendationEstateType,
    topN = 50,
  ): Promise<RecommendationListResponse> {
    const response = await apiFetch(
      `${API_BASE}/recommendations/${estateType}?top_n=${topN}`,
    );

    if (!response.ok) {
      throw new Error("Empfehlungen konnten nicht geladen werden");
    }

    return response.json();
  },
};
