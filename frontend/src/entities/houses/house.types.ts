export type House = {
  id: number;

  title: string;
  description?: string;

  price: number;
  coldRent?: number;
  additionalCosts?: number;

  size: number;
  rooms: number;
  floor?: number;

  city: string;
  zipCode?: string;
  address?: string;

  latitude?: number;
  longitude?: number;

  source: string;
  sourceUrl?: string;

  isFavorite: boolean;

  createdAt: string;
  updatedAt: string;
};