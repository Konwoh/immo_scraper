import type { CrudConfig } from "@/components/crud/CrudPage";
import type { JobSchedule } from "./job_schedule.types";

const formatDateTime = (value: unknown) => {
  if (!value) {
    return "-";
  }

  const date = new Date(String(value));

  return Number.isNaN(date.getTime())
    ? "-"
    : date.toLocaleString("de-DE");
};

export const jobScheduleConfig = {
  name: "Jobs Schedule",
  route: "/jobs_schedules",
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
      key: "interval",
      label: "Interval",
    },
    {
      key: "enabled",
      label: "Aktiviert",
    },
    {
      key: "last_run",
      label: "Letzter Run",
      render: formatDateTime,
    },
    {
      key: "next_run",
      label: "Nächster Run",
      render: formatDateTime,
    },
  ],

  formFields: [
    {
      key: "search_params_id",
      label: "Suchparameter",
      type: "select",
      required: true,
      options: [],
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
      key: "interval",
      label: "Interval",
      type: "select",
      required: true,
      options: [
        {
          label: "Stündlich",
          value: "hourly",
        },
        {
          label: "Täglich",
          value: "daily",
        },
        {
          label: "Wöchentlich",
          value: "weekly",
        },
      ],
    },
    {
      key: "enabled",
      label: "Aktiviert",
      type: "select",
      required: true,
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
      key: "next_run",
      label: "Nächster Run",
      type: "datetime-local",
      required: true,
    },
  ],
} satisfies CrudConfig<JobSchedule>;
