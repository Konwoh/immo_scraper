export type Property = {
  id: number;

  title: string;
  url: string;
  listing_type?: string | null;

  city?: string | null;
  zip_code?: string | null;
  address?: string | null;

  price?: string | null;
  price_m2?: string | null;
  space?: string | null;

  development?: string | null;
  building_permit?: boolean | null;
  available_from?: string | null;
  recommended_use?: string | null;
  floor_area_ratio?: string | null;
  floor_space_index?: string | null;

  provision?: string | null;
  incidental_purchase_costs?: string | null;
  property_acquisition_tax?: string | null;
  brokerage_commission?: string | null;
  notary_fees?: string | null;
  land_registry_entry?: string | null;
  land_transfer_tax?: string | null;
  total_costs?: number | null;

  general_description?: string | null;
  object_description?: string | null;
  place_description?: string | null;
  other_description?: string | null;

  agency_id?: number | null;
  is_online: boolean;

  created_at: string;
  updated_at: string;
};
