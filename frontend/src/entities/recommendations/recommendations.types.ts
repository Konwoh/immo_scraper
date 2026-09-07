export type RecommendationEstateType = "house" | "apartment";

export type RecommendationItem = {
  id: number;
  title: string;
  url: string;
  price: number | null;
  city: string | null;
  zip_code: string | null;
  living_space: number | null;
  rooms: number | null;
  estate_type: string | null;
  images: string[];
  similarity: number;
};

export type RecommendationListResponse = {
  count: number;
  items: RecommendationItem[];
};
