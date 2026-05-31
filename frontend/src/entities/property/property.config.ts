import type { CrudConfig } from "@/components/crud/CrudPage";
import type { Property } from "./property.types";

const renderValue = (value: unknown) =>
  value === null || value === undefined || value === "" ? "-" : String(value);

const renderBoolean = (value: unknown) => {
  if (value === true) {
    return "Ja";
  }

  if (value === false) {
    return "Nein";
  }

  return "-";
};

export const propertyConfig = {
  name: "Grundstuecke",
  route: "/properties",
  idField: "id",

  columns: [
    {
      key: "title",
      label: "Titel",
    },
    {
      key: "price",
      label: "Preis",
      render: renderValue,
    },
    {
      key: "price_m2",
      label: "Preis/m2",
      render: renderValue,
    },
    {
      key: "space",
      label: "Flaeche",
      render: renderValue,
    },
    {
      key: "city",
      label: "Stadt",
      render: renderValue,
    },
    {
      key: "address",
      label: "Adresse",
      render: renderValue,
    },
    {
      key: "development",
      label: "Erschliessung",
      render: renderValue,
    },
    {
      key: "building_permit",
      label: "Baugenehmigung",
      render: renderBoolean,
    },
    {
      key: "is_online",
      label: "Online",
      render: renderBoolean,
    },
  ],

  formFields: [
    {
      key: "title",
      label: "Titel",
      type: "text",
      required: true,
      placeholder: "Baugrundstueck",
    },
    {
      key: "url",
      label: "URL",
      type: "text",
      required: true,
    },
    {
      key: "listing_type",
      label: "Inseratstyp",
      type: "text",
    },
    {
      key: "price",
      label: "Preis",
      type: "text",
    },
    {
      key: "price_m2",
      label: "Preis/m2",
      type: "text",
    },
    {
      key: "space",
      label: "Flaeche",
      type: "text",
    },
    {
      key: "city",
      label: "Stadt",
      type: "text",
    },
    {
      key: "zip_code",
      label: "PLZ",
      type: "text",
    },
    {
      key: "address",
      label: "Adresse",
      type: "text",
    },
    {
      key: "development",
      label: "Erschliessung",
      type: "text",
    },
    {
      key: "building_permit",
      label: "Baugenehmigung",
      type: "select",
      options: [
        {
          label: "Ja",
          value: true,
        },
        {
          label: "Nein",
          value: false,
        },
      ],
    },
    {
      key: "available_from",
      label: "Verfuegbar ab",
      type: "text",
    },
    {
      key: "recommended_use",
      label: "Empfohlene Nutzung",
      type: "text",
    },
    {
      key: "floor_area_ratio",
      label: "Grundflaechenzahl",
      type: "text",
    },
    {
      key: "floor_space_index",
      label: "Geschossflaechenzahl",
      type: "text",
    },
    {
      key: "provision",
      label: "Provision",
      type: "text",
    },
    {
      key: "general_description",
      label: "Beschreibung",
      type: "textarea",
    },
    {
      key: "object_description",
      label: "Objektbeschreibung",
      type: "textarea",
    },
    {
      key: "place_description",
      label: "Lage",
      type: "textarea",
    },
    {
      key: "other_description",
      label: "Sonstiges",
      type: "textarea",
    },
  ],
} satisfies CrudConfig<Property>;
