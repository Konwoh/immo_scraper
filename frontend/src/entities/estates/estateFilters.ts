import type { PaginationParams } from "@/api/pagination";

/**
 * Filterwerte für die Kachelansicht von Häusern & Wohnungen. Die Schlüssel
 * entsprechen exakt den Query-Parametern von `HouseFilter` / `ApartmentFilter`
 * im Backend (`backend/api/filter/{house,apartment}_filter.py`).
 */
export type EstateFilterValues = {
  city?: string;
  min_price?: number;
  max_price?: number;
  min_living_space?: number;
  max_living_space?: number;
  min_rooms?: number;
  max_rooms?: number;
  estate_type?: string;
};

export type EstateTypeOption = { label: string; value: string };

/** Werte exakt wie in `houses.estate_type` gespeichert. */
export const HOUSE_ESTATE_TYPES: EstateTypeOption[] = [
  { label: "Einfamilienhaus (freistehend)", value: "Einfamilienhaus freistehend" },
  { label: "Doppelhaushälfte", value: "Doppelhaushälfte" },
  { label: "Reihenhaus", value: "Reihenhaus" },
  { label: "Reihenmittelhaus", value: "Reihenmittelhaus" },
  { label: "Reiheneckhaus", value: "Reiheneckhaus" },
  { label: "Mehrfamilienhaus", value: "Mehrfamilienhaus" },
  { label: "Bungalow", value: "Bungalow" },
  { label: "Villa", value: "Villa" },
  { label: "Bauernhaus", value: "Bauernhaus" },
  { label: "Wohnimmobilie (sonstige)", value: "Wohnimmobilie (sonstige)" },
  { label: "Andere Haustypen", value: "Andere Haustypen" },
];

/** Werte exakt wie in `apartments.estate_type` gespeichert. */
export const APARTMENT_ESTATE_TYPES: EstateTypeOption[] = [
  { label: "Etagenwohnung", value: "Etagenwohnung" },
  { label: "Erdgeschosswohnung", value: "Erdgeschosswohnung" },
  { label: "Dachgeschoss", value: "Dachgeschoss" },
  { label: "Dachgeschosswohnung", value: "Dachgeschosswohnung" },
  { label: "Souterrain", value: "Souterrain" },
  { label: "Hochparterre", value: "Hochparterre" },
  { label: "Maisonette", value: "Maisonette" },
  { label: "Terrassenwohnung", value: "Terrassenwohnung" },
  { label: "Penthouse", value: "Penthouse" },
  { label: "Loft", value: "Loft" },
  { label: "Andere Wohnungstypen", value: "Andere Wohnungstypen" },
  { label: "Sonstige", value: "Sonstige" },
];

const FILTER_KEYS: (keyof EstateFilterValues)[] = [
  "city",
  "min_price",
  "max_price",
  "min_living_space",
  "max_living_space",
  "min_rooms",
  "max_rooms",
  "estate_type",
];

/**
 * Baut den Query-String für die Estate-Listen-Endpunkte: Pagination + alle
 * gesetzten Filter. Leere / ungültige Werte (`undefined`, `null`, `""`, `NaN`)
 * werden weggelassen – ein leerer `estate_type=""` würde sonst ein 422 auslösen.
 */
export function buildEstateListQuery(
  params?: PaginationParams & EstateFilterValues,
): string {
  const searchParams = new URLSearchParams();

  if (params?.page !== undefined) {
    searchParams.set("page", String(params.page));
  }
  if (params?.page_size !== undefined) {
    searchParams.set("page_size", String(params.page_size));
  }

  for (const key of FILTER_KEYS) {
    const value = params?.[key];
    if (
      value === undefined ||
      value === null ||
      value === "" ||
      (typeof value === "number" && Number.isNaN(value))
    ) {
      continue;
    }
    searchParams.set(key, String(value));
  }

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}
