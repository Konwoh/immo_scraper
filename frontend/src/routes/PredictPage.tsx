import { useState, type FormEvent } from "react";
import { predictPrice } from "@/entities/predict/predict.api";
import type { PredictionPayload } from "@/entities/predict/predict.types";

type PredictionFormValues = Record<keyof PredictionPayload, string>;

type PredictionField = {
  key: keyof PredictionPayload;
  label: string;
  type: "text" | "number" | "select";
  options?: { label: string; value: string }[];
  min?: number;
  step?: string;
};

const numericFields = [
  "rent_cold",
  "rent_complete",
  "house_money",
  "rent_heating_costs",
  "rooms",
  "sleeping_rooms",
  "bathrooms",
  "floor",
  "living_space",
  "garage_parking_slots",
  "internet_speed_telekom",
  "rent_income",
  "building_year",
  "energy_demand",
  "property_space",
] satisfies (keyof PredictionPayload)[];

const booleanFields = [
  "lift",
  "barrier_free",
  "garden",
  "fitted_kitchen",
  "basement",
  "rented",
  "is_online",
] satisfies (keyof PredictionPayload)[];

const booleanOptions = [
  { label: "Ja", value: "true" },
  { label: "Nein", value: "false" },
];

const predictionFields = [
  {
    key: "estate_type",
    label: "Immobilientyp",
    type: "select",
    options: [
      { label: "Wohnung", value: "apartment" },
      { label: "Haus", value: "house" },
      { label: "Grundstück", value: "property" },
    ],
  },
  { key: "rent_cold", label: "Kaltmiete", type: "number", min: 0 },
  { key: "rent_complete", label: "Warmmiete", type: "number", min: 0 },
  { key: "house_money", label: "Hausgeld", type: "number", min: 0 },
  { key: "rent_heating_costs", label: "Heizkosten", type: "number", min: 0 },
  { key: "zip_code", label: "PLZ", type: "text" },
  { key: "rooms", label: "Zimmer", type: "number", min: 0, step: "0.5" },
  { key: "sleeping_rooms", label: "Schlafzimmer", type: "number", min: 0 },
  { key: "bathrooms", label: "Badezimmer", type: "number", min: 0 },
  { key: "floor", label: "Etage", type: "number" },
  { key: "living_space", label: "Wohnfläche", type: "number", min: 0 },
  { key: "garage_parking_slots", label: "Garagenstellplätze", type: "number", min: 0 },
  { key: "lift", label: "Aufzug", type: "select", options: booleanOptions },
  { key: "barrier_free", label: "Barrierefrei", type: "select", options: booleanOptions },
  { key: "garden", label: "Garten", type: "select", options: booleanOptions },
  { key: "internet_speed_telekom", label: "Internetgeschwindigkeit", type: "number", min: 0 },
  { key: "fitted_kitchen", label: "Einbauküche", type: "select", options: booleanOptions },
  { key: "basement", label: "Keller", type: "select", options: booleanOptions },
  { key: "rented", label: "Vermietet", type: "select", options: booleanOptions },
  { key: "provision", label: "Provision", type: "text" },
  { key: "rent_income", label: "Mieteinnahmen", type: "number", min: 0 },
  { key: "building_year", label: "Baujahr", type: "number", min: 0 },
  { key: "estate_condition", label: "Zustand", type: "text" },
  { key: "interior_quality", label: "Ausstattungsqualität", type: "text" },
  { key: "heating_type", label: "Heizungsart", type: "text" },
  {
    key: "energy_performance_certificate_type",
    label: "Energieausweistyp",
    type: "text",
  },
  { key: "energy_source", label: "Energieträger", type: "text" },
  { key: "energy_demand", label: "Energiebedarf", type: "number", min: 0 },
  {
    key: "energy_efficiency_class",
    label: "Energieeffizienzklasse",
    type: "select",
    options: ["A+", "A", "B", "C", "D", "E", "F", "G", "H"].map((value) => ({
      label: value,
      value,
    })),
  },
  { key: "is_online", label: "Online", type: "select", options: booleanOptions },
  { key: "property_space", label: "Grundstücksfläche", type: "number", min: 0 },
] satisfies PredictionField[];

const initialFormData: PredictionFormValues = {
  estate_type: "",
  rent_cold: "",
  rent_complete: "",
  house_money: "",
  rent_heating_costs: "",
  zip_code: "",
  rooms: "",
  sleeping_rooms: "",
  bathrooms: "",
  floor: "",
  living_space: "",
  garage_parking_slots: "",
  lift: "",
  barrier_free: "",
  garden: "",
  internet_speed_telekom: "",
  fitted_kitchen: "",
  basement: "",
  rented: "",
  provision: "",
  rent_income: "",
  building_year: "",
  estate_condition: "",
  interior_quality: "",
  heating_type: "",
  energy_performance_certificate_type: "",
  energy_source: "",
  energy_demand: "",
  energy_efficiency_class: "",
  is_online: "",
  property_space: "",
};

function isNumericField(key: keyof PredictionPayload) {
  return (numericFields as readonly (keyof PredictionPayload)[]).includes(key);
}

function isBooleanField(key: keyof PredictionPayload) {
  return (booleanFields as readonly (keyof PredictionPayload)[]).includes(key);
}

function createPredictionPayload(formData: PredictionFormValues): PredictionPayload {
  const payload = Object.entries(formData).reduce<Record<string, string | number | boolean>>(
    (data, [key, value]) => {
      const payloadKey = key as keyof PredictionPayload;

      if (isNumericField(payloadKey)) {
        data[key] = Number(value);
      } else if (isBooleanField(payloadKey)) {
        data[key] = value === "true";
      } else {
        data[key] = value.trim();
      }

      return data;
    },
    {},
  );

  return payload as PredictionPayload;
}

export function PredictPage() {
  const [formData, setFormData] = useState<PredictionFormValues>(initialFormData);
  const [price, setPrice] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setPrice(null);

    if (Object.values(formData).some((value) => value.trim() === "")) {
      setError("Bitte alle Felder ausfüllen.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await predictPrice(createPredictionPayload(formData));
      setPrice(result.predicted_price);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Die Preisvorhersage konnte nicht berechnet werden.";

      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleChange(key: keyof PredictionPayload, value: string) {
    setFormData((currentFormData) => ({
      ...currentFormData,
      [key]: value,
    }));
  }

  function renderInput(field: PredictionField) {
    const value = formData[field.key];

    if (field.type === "select") {
      return (
        <select
          required
          value={value}
          onChange={(event) => handleChange(field.key, event.target.value)}
        >
          <option value="">Bitte auswählen</option>
          {field.options?.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }

    return (
      <input
        required
        type={field.type}
        min={field.min}
        step={field.step ?? (field.type === "number" ? "any" : undefined)}
        value={value}
        onChange={(event) => handleChange(field.key, event.target.value)}
      />
    );
  }

  return (
    <section className="crud-page">
      <div className="crud-page-header">
        <div>
          <h1>Preisvorhersage</h1>
        </div>
      </div>

      {error && <p className="crud-error">{error}</p>}

      <form className="crud-form" onSubmit={handleSubmit}>
        <div className="crud-form-header">
          <div>
            <h2>Immobiliendaten</h2>
            <p>Alle Felder sind erforderlich.</p>
          </div>
        </div>

        <div className="crud-form-grid">
          {predictionFields.map((field) => (
            <div key={field.key}>
              <label>
                {field.label}
                <span aria-hidden="true">*</span>
                {renderInput(field)}
              </label>
            </div>
          ))}
        </div>

        <div className="crud-form-actions">
          <div />
          <button className="crud-primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Berechnung läuft..." : "Berechnen"}
          </button>
        </div>
      </form>

      {price !== null && (
        <section className="prediction-result" aria-live="polite">
          <span>Geschätzter Preis</span>
          <strong>{price.toLocaleString("de-DE")} €</strong>
        </section>
      )}
    </section>
  );
}
