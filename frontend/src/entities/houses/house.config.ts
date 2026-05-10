// entities/houses/house.config.ts

import type { CrudConfig } from "@/components/crud/CrudPage";
import type { House } from "./house.types";

export const houseConfig = {
  name: "Häuser",
  route: "/houses",
  idField: "id",

  columns: [
    {
      key: "title",
      label: "Titel",
    },
    {
      key: "price",
      label: "Preis",
      render: (value) =>
        typeof value === "number"
          ? `${value.toLocaleString("de-DE")} €`
          : "-",
    },
    {
      key: "size",
      label: "Fläche",
      render: (value) =>
        typeof value === "number" ? `${value} m²` : "-",
    },
    {
      key: "rooms",
      label: "Zimmer",
    },
    {
      key: "city",
      label: "Stadt",
    },
    {
      key: "address",
      label: "Addresse",
    },
  ],

  formFields: [
    {
      key: "title",
      label: "Titel",
      type: "text",
      required: true,
      placeholder: "Modernes Einfamilienhaus",
    },

    {
      key: "description",
      label: "Beschreibung",
      type: "textarea",
      placeholder: "Beschreibung eingeben...",
    },

    {
      key: "price",
      label: "Preis",
      type: "number",
      required: true,
    },

    {
      key: "coldRent",
      label: "Kaltmiete",
      type: "number",
    },

    {
      key: "additionalCosts",
      label: "Nebenkosten",
      type: "number",
    },

    {
      key: "size",
      label: "Fläche (m²)",
      type: "number",
      required: true,
    },

    {
      key: "rooms",
      label: "Zimmer",
      type: "number",
      required: true,
    },

    {
      key: "floor",
      label: "Etage",
      type: "number",
    },

    {
      key: "city",
      label: "Stadt",
      type: "text",
      required: true,
    },

    {
      key: "zipCode",
      label: "PLZ",
      type: "text",
    },

    {
      key: "address",
      label: "Addresse",
      type: "text",
    },

    {
      key: "source",
      label: "Quelle",
      type: "select",
      required: true,
      options: [
        {
          label: "ImmoScout24",
          value: "immoscout24",
        },
        {
          label: "Immowelt",
          value: "immowelt",
        },
        {
          label: "Kleinanzeigen",
          value: "kleinanzeigen",
        },
      ],
    },

    {
      key: "sourceUrl",
      label: "Quell-URL",
      type: "text",
    },
  ],
} satisfies CrudConfig<House>;
