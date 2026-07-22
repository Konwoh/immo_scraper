export type PredictionPayload = {
  estate_type: "house" | "apartment" | "property";
  rent_cold: number;
  rent_complete: number;
  house_money: number;
  rent_heating_costs: number;
  zip_code: string;
  rooms: number;
  sleeping_rooms: number;
  bathrooms: number;
  floor: number;
  living_space: number;
  garage_parking_slots: number;
  lift: boolean;
  barrier_free: boolean;
  garden: boolean;
  internet_speed_telekom: number;
  fitted_kitchen: boolean;
  basement: boolean;
  rented: boolean;
  provision: string;
  rent_income: number;
  building_year: number;
  estate_condition: string;
  interior_quality: string;
  heating_type: string;
  energy_performance_certificate_type: string;
  energy_source: string;
  energy_demand: number;
  energy_efficiency_class: string;
  is_online: boolean;
  property_space: number;
};

export type PredictionResponse = {
  predicted_price: number;
};
