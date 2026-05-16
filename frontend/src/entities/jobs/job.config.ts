import type { CrudConfig } from "@/components/crud/CrudPage";
import type { Job } from "./job.types";

const formatDateTime = (value: unknown) => {
  if (!value) {
    return "-";
  }

  const date = new Date(String(value));

  return Number.isNaN(date.getTime())
    ? "-"
    : date.toLocaleString("de-DE");
};

export const jobConfig = {
  name: "Jobs",
  route: "/jobs",
  idField: "id",

  columns: [
    {
      key: "id",
      label: "ID",
    },
    {
      key: "search_params_id",
      label: "Suchparameter",
    },
    {
      key: "job_type",
      label: "Typ",
    },
    {
      key: "status",
      label: "Status",
    },
    {
      key: "claimed_at",
      label: "Beansprucht am",
      render: formatDateTime,
    },
  ],

  formFields: [
    {
      key: "search_params_id",
      label: "Suchparameter-ID",
      type: "number",
      required: true,
    },
    {
      key: "job_type",
      label: "Typ",
      type: "select",
      required: true,
      options: [
        {
          label: "Scraper",
          value: "scraper",
        },
        {
          label: "Crawler",
          value: "crawler",
        },
      ],
    },
    {
      key: "status",
      label: "Status",
      type: "select",
      options: [
        {
          label: "Offen",
          value: "open",
        },
        {
          label: "In Bearbeitung",
          value: "processing",
        },
        {
          label: "Erledigt",
          value: "done",
        },
        {
          label: "Fehlgeschlagen",
          value: "failed",
        },
      ],
    },
  ],
} satisfies CrudConfig<Job>;
