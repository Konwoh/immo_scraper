import type { CrudConfig } from "@/components/crud/CrudPage";
import type { SearchParams } from "./search_params.types";

export const searchParamsConfig = {
  name: "SearchParams",
  route: "/search_params",
  idField: "id",

  columns: [
    {
        key: "id",
        label: "ID",
    },
    {
        key: "site",
        label: "Seite",
    },
    {
        key: "country",
        label: "Land",
    },
    {
        key: "state",
        label: "Bundesland",
    },
    {
        key: "city",
        label: "Stadt",
    },
    {
        key: "distance",
        label: "Entfernung",
    },
    {
        key: "zip_code",
        label: "PLZ",
    },
    {
        key: "estate_type",
        label: "Art der Immobilie",
    },
    {
        key: "rent_or_buy",
        label: "Mieten order Kaufen?",
    },
    {
        key: "page",
        label: "Seite",
    },
    {
        key: "listing_count",
        label: "Anzahl der Inserate",
    }
  ],

  formFields: [
    {
      key: "site",
      label: "Seite",
      type: "select",
      required: true,
      options: [
        {
          label: "ImmoScout",
          value: "immoScout",
        },
        {
          label: "Kleinanzeigen",
          value: "kleinanzeigen",
        },
      ],
    },
    {
      key: "country",
      label: "Land",
      type: "text",
      required: true,
      placeholder: "de",
    },
    {
      key: "state",
      label: "Bundesland",
      type: "text",
      required: true,
      placeholder: "sachsen",
    },
    {
      key: "city",
      label: "Stadt",
      type: "text",
      required: true,
      placeholder: "leipzig",
    },
    {
      key: "distance",
      label: "Entfernung",
      type: "number",
    },
    {
      key: "zip_code",
      label: "PLZ",
      type: "text",
    },
    {
      key: "estate_type",
      label: "Art der Immobilie",
      type: "select",
      required: true,
      options: [
        {
          label: "Wohnung",
          value: "apartment",
        },
        {
          label: "Haus",
          value: "house",
        },
        {
          label: "Grundstück",
          value: "property",
        },
      ],
    },
    {
      key: "rent_or_buy",
      label: "Mieten oder Kaufen?",
      type: "select",
      required: true,
      options: [
        {
          label: "Mieten",
          value: "rent",
        },
        {
          label: "Kaufen",
          value: "buy",
        },
      ],
    },
    {
      key: "page",
      label: "Seite",
      type: "number",
      required: true,
    },
    {
      key: "listing_count",
      label: "Anzahl der Inserate",
      type: "number",
      required: true,
    },
  ],
} satisfies CrudConfig<SearchParams>;
