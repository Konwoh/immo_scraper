export type EstateType = "house" | "apartment" | "property";

export type Favorite = {
  id: number;
  user_id: number;
  house_id: number | null;
  apartment_id: number | null;
  property_id: number | null;
  created_at: string;
};

export const ESTATE_FK_FIELD: Record<EstateType, keyof Favorite> = {
  house: "house_id",
  apartment: "apartment_id",
  property: "property_id",
};
