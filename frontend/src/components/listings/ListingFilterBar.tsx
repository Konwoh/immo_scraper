import { useState, type FormEvent } from "react";
import type {
  EstateFilterValues,
  EstateTypeOption,
} from "@/entities/estates/estateFilters";

type ListingFilterBarProps = {
  estateTypeLabel: string;
  estateTypeOptions: EstateTypeOption[];
  value: EstateFilterValues;
  onApply: (values: EstateFilterValues) => void;
  onReset: () => void;
};

type DraftKey =
  | "city"
  | "min_price"
  | "max_price"
  | "min_living_space"
  | "max_living_space"
  | "min_rooms"
  | "max_rooms"
  | "estate_type";

type Draft = Record<DraftKey, string>;

const EMPTY_DRAFT: Draft = {
  city: "",
  min_price: "",
  max_price: "",
  min_living_space: "",
  max_living_space: "",
  min_rooms: "",
  max_rooms: "",
  estate_type: "",
};

const RANGE_PAIRS: {
  min: "min_price" | "min_living_space" | "min_rooms";
  max: "max_price" | "max_living_space" | "max_rooms";
  label: string;
}[] = [
  { min: "min_price", max: "max_price", label: "Preis (€)" },
  { min: "min_living_space", max: "max_living_space", label: "Wohnfläche (m²)" },
  { min: "min_rooms", max: "max_rooms", label: "Zimmer" },
];

const toDraft = (value: EstateFilterValues): Draft => ({
  city: value.city ?? "",
  min_price: value.min_price?.toString() ?? "",
  max_price: value.max_price?.toString() ?? "",
  min_living_space: value.min_living_space?.toString() ?? "",
  max_living_space: value.max_living_space?.toString() ?? "",
  min_rooms: value.min_rooms?.toString() ?? "",
  max_rooms: value.max_rooms?.toString() ?? "",
  estate_type: value.estate_type ?? "",
});

const parseNumber = (raw: string): number | undefined => {
  if (raw.trim() === "") {
    return undefined;
  }
  const parsed = Number(raw);
  return Number.isNaN(parsed) ? undefined : parsed;
};

export function ListingFilterBar({
  estateTypeLabel,
  estateTypeOptions,
  value,
  onApply,
  onReset,
}: ListingFilterBarProps) {
  const [draft, setDraft] = useState<Draft>(() => toDraft(value));
  const [localError, setLocalError] = useState<string | null>(null);

  const updateDraft = (key: DraftKey, next: string) => {
    setDraft((current) => ({ ...current, [key]: next }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const values: EstateFilterValues = {
      city: draft.city.trim() === "" ? undefined : draft.city.trim(),
      min_price: parseNumber(draft.min_price),
      max_price: parseNumber(draft.max_price),
      min_living_space: parseNumber(draft.min_living_space),
      max_living_space: parseNumber(draft.max_living_space),
      min_rooms: parseNumber(draft.min_rooms),
      max_rooms: parseNumber(draft.max_rooms),
      estate_type: draft.estate_type === "" ? undefined : draft.estate_type,
    };

    for (const pair of RANGE_PAIRS) {
      const min = values[pair.min];
      const max = values[pair.max];
      if (min !== undefined && max !== undefined && min > max) {
        setLocalError(
          `${pair.label}: Mindestwert darf nicht größer als Höchstwert sein.`,
        );
        return;
      }
    }

    setLocalError(null);
    onApply(values);
  };

  const handleReset = () => {
    setDraft(EMPTY_DRAFT);
    setLocalError(null);
    onReset();
  };

  return (
    <form
      className="listing-filter-bar"
      onSubmit={handleSubmit}
      aria-label={`${estateTypeLabel} filtern`}
    >
      <label className="listing-filter-field">
        <span>Stadt</span>
        <input
          type="text"
          value={draft.city}
          placeholder="z. B. Berlin"
          onChange={(event) => updateDraft("city", event.target.value)}
        />
      </label>

      {RANGE_PAIRS.map((pair) => (
        <fieldset className="listing-filter-range" key={pair.min}>
          <legend>{pair.label}</legend>
          <input
            type="number"
            min="0"
            inputMode="numeric"
            placeholder="von"
            aria-label={`${pair.label} von`}
            value={draft[pair.min]}
            onChange={(event) => updateDraft(pair.min, event.target.value)}
          />
          <span aria-hidden="true">–</span>
          <input
            type="number"
            min="0"
            inputMode="numeric"
            placeholder="bis"
            aria-label={`${pair.label} bis`}
            value={draft[pair.max]}
            onChange={(event) => updateDraft(pair.max, event.target.value)}
          />
        </fieldset>
      ))}

      <label className="listing-filter-field">
        <span>{estateTypeLabel}</span>
        <select
          value={draft.estate_type}
          onChange={(event) => updateDraft("estate_type", event.target.value)}
        >
          <option value="">Alle</option>
          {estateTypeOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>

      <div className="listing-filter-actions">
        <button type="submit" className="crud-primary-button">
          Filtern
        </button>
        <button
          type="button"
          className="crud-secondary-button"
          onClick={handleReset}
        >
          Zurücksetzen
        </button>
      </div>

      {localError && (
        <p className="crud-error listing-filter-error" role="alert">
          {localError}
        </p>
      )}
    </form>
  );
}
