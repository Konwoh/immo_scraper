export type House = {
  id: number;

  title: string;
  description?: string | null;
  general_description?: string | null;
  object_description?: string | null;
  place_description?: string | null;
  other_description?: string | null;

  price?: string | number | null;
  price_m2?: string | null;
  coldRent?: string | number | null;
  rent_cold?: string | number | null;
  additionalCosts?: string | number | null;
  rent_extra_costs?: string | number | null;
  rent_complete?: string | null;

  size?: string | number | null;
  living_space?: string | number | null;
  property_space?: string | null;
  rooms?: number | null;
  floor?: string | number | null;

  city?: string | null;
  zipCode?: string | null;
  zip_code?: string | null;
  address?: string | null;

  latitude?: number;
  longitude?: number;

  source?: string | null;
  sourceUrl?: string | null;
  url?: string | null;

  images?: string[] | null;

  isFavorite?: boolean;
  is_online?: boolean;

  createdAt?: string;
  updatedAt?: string;
  created_at?: string;
  updated_at?: string;
};
