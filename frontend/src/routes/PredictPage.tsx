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

function toOptions(values: string[]) {
  return values.map((value) => ({
    label: value,
    value,
  }));
}

const estateTypeOptions = toOptions([
  "Andere Haustypen",
  "Andere Wohnungstypen",
  "Bauernhaus",
  "Bungalow",
  "Dachgeschoss",
  "Dachgeschosswohnung",
  "Doppelhaushälfte",
  "Einfamilienhaus (freistehend)",
  "Einfamilienhaus freistehend",
  "Erdgeschosswohnung",
  "Etagenwohnung",
  "Hochparterre",
  "Loft",
  "Maisonette",
  "Mehrfamilienhaus",
  "Penthouse",
  "Reihenhaus",
  "Sonstige",
  "Souterrain",
  "Terrassenwohnung",
  "Villa",
]);

const zipCodeOptions = toOptions([
  "01429",
  "04000",
  "04103",
  "04105",
  "04107",
  "04109",
  "04129",
  "04135",
  "04155",
  "04157",
  "04158",
  "04159",
  "04175",
  "04177",
  "04178",
  "04179",
  "04205",
  "04207",
  "04209",
  "04229",
  "04249",
  "04255",
  "04275",
  "04277",
  "04279",
  "04288",
  "04289",
  "04299",
  "04315",
  "04316",
  "04317",
  "04318",
  "04319",
  "04328",
  "04329",
  "04347",
  "04349",
  "04356",
  "04357",
  "04374",
  "04416",
  "04420",
  "04425",
  "04435",
  "04442",
  "04451",
  "04463",
  "04509",
  "04519",
  "04564",
  "04571",
  "04683",
  "04736",
  "04755",
  "04824",
  "04838",
  "06237",
  "06258",
  "06686",
  "4129",
]);

const estateConditionOptions = toOptions([
  "Erstbezug",
  "Erstbezug nach Sanierung",
  "Gepflegt",
  "Modernisiert",
  "Nach Vereinbarung",
  "Neuwertig",
  "Renovierungsbedürftig",
  "Saniert",
  "Vollständig renoviert",
]);

const interiorQualityOptions = toOptions([
  "Einfach",
  "Gehoben",
  "Luxus",
  "Normal",
]);

const heatingTypeOptions = toOptions([
  "Blockheizkraftwerk",
  "Elektro-Heizung",
  "Etagenheizung",
  "Fernwärme",
  "Fußbodenheizung",
  "Gas-Heizung",
  "Holz-Pelletheizung",
  "Nachtspeicherofen",
  "Ofenheizung",
  "Ölheizung",
  "Wärmepumpe",
  "Zentralheizung",
]);

const energyPerformanceCertificateTypeOptions = toOptions([
  "Bedarfsausweis",
  "Verbrauchsausweis",
]);

const energySourceOptions = toOptions([
  "Erdgas leicht",
  "Erdgas schwer",
  "Erdwärme",
  "Erdwärme, Gas",
  "Erdwärme, Solar",
  "Fernwärme",
  "Fernwärme-Dampf",
  "Fernwärme, Flüssiggas",
  "Fernwärme, Nahwärme",
  "Fernwärme, Nahwärme, KWK fossil",
  "Flüssiggas",
  "Gas",
  "Gas, Erdgas leicht",
  "Gas, Fernwärme",
  "Gas, Kohle",
  "Gas, Strom",
  "Holz",
  "Holzpellets",
  "Holzpellets, Holz",
  "Keine Angabe",
  "Kohle",
  "KWK erneuerbar",
  "KWK fossil",
  "Nahwärme",
  "Öl",
  "Öl, Fernwärme",
  "Solar",
  "Solar, Erdgas leicht",
  "Solar, Gas",
  "Strom",
  "Strom, Umweltwärme",
  "Umweltwärme",
  "Wärmelieferung",
]);

const energyEfficiencyClassOptions = toOptions([
  "A+",
  "A",
  "B",
  "C",
  "D",
  "E",
  "F",
  "G",
  "H",
]);

const predictionFields = [
  {
    key: "estate_type",
    label: "Immobilientyp",
    type: "select",
    options: estateTypeOptions,
  },
  { key: "rent_cold", label: "Kaltmiete", type: "number", min: 0 },
  { key: "rent_complete", label: "Warmmiete", type: "number", min: 0 },
  { key: "house_money", label: "Hausgeld", type: "number", min: 0 },
  { key: "rent_heating_costs", label: "Heizkosten", type: "number", min: 0 },
  { key: "zip_code", label: "PLZ", type: "text", options: zipCodeOptions },
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
  { key: "provision", label: "Provision", type: "select", options: [] },
  { key: "rent_income", label: "Mieteinnahmen", type: "number", min: 0 },
  { key: "building_year", label: "Baujahr", type: "number", min: 0 },
  { key: "estate_condition", label: "Zustand", type: "select", options: estateConditionOptions },
  {
    key: "interior_quality",
    label: "Ausstattungsqualität",
    type: "select",
    options: interiorQualityOptions,
  },
  { key: "heating_type", label: "Heizungsart", type: "select", options: heatingTypeOptions },
  {
    key: "energy_performance_certificate_type",
    label: "Energieausweistyp",
    type: "select",
    options: energyPerformanceCertificateTypeOptions,
  },
  { key: "energy_source", label: "Energieträger", type: "select", options: energySourceOptions },
  { key: "energy_demand", label: "Energiebedarf", type: "number", min: 0 },
  {
    key: "energy_efficiency_class",
    label: "Energieeffizienzklasse",
    type: "select",
    options: energyEfficiencyClassOptions,
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
      const trimmedValue = value.trim();

      if (trimmedValue === "") {
        return data;
      }

      if (isNumericField(payloadKey)) {
        data[key] = Number(trimmedValue);
      } else if (isBooleanField(payloadKey)) {
        data[key] = trimmedValue === "true";
      } else {
        data[key] = trimmedValue;
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

    const listId = field.options ? `prediction-options-${field.key}` : undefined;

    return (
      <>
      <input
        type={field.type}
        list={listId}
        min={field.min}
        step={field.step ?? (field.type === "number" ? "any" : undefined)}
        value={value}
        onChange={(event) => handleChange(field.key, event.target.value)}
      />
        {field.options && (
          <datalist id={listId}>
            {field.options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </datalist>
        )}
      </>
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
            <p>Leere Felder werden vom Backend mit Standardwerten ergänzt.</p>
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
