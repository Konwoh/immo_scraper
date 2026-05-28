import { useEffect, useMemo, useState } from "react";
import { CrudPage, type CrudConfig } from "@/components/crud/CrudPage";

import { jobScheduleApi } from "@/entities/job_schedule/job_schedule.api";
import { jobScheduleConfig } from "@/entities/job_schedule/job_schedule.config";
import type { JobSchedule } from "@/entities/job_schedule/job_schedule.types";
import { searchParamsApi } from "@/entities/search_params/search_params.api";
import type { SearchParams } from "@/entities/search_params/search_params.types";

type JobSchedulePageProps = {
  show_table?: boolean;
  show_button?: boolean;
};

const formatSearchParamsOption = (searchParams: SearchParams) => {
  const parts = [
    searchParams.city,
    searchParams.zip_code,
    searchParams.site,
    searchParams.estate_type,
    searchParams.rent_or_buy,
  ].filter(Boolean);

  return `${parts.length > 0 ? parts.join(" | ") : "Suchparameter"} | ID ${searchParams.id}`;
};

export function JobSchedulePage({
  show_table = true,
  show_button = false,
}: JobSchedulePageProps = {}) {
  const [searchParams, setSearchParams] = useState<SearchParams[]>([]);
  const [searchParamsError, setSearchParamsError] = useState<string | null>(
    null,
  );
  const [actionError, setActionError] = useState<string | null>(null);
  const [updatingScheduleId, setUpdatingScheduleId] = useState<number | null>(
    null,
  );

  useEffect(() => {
    let isMounted = true;

    const loadSearchParams = async () => {
      try {
        const items = await searchParamsApi.list();

        if (isMounted) {
          setSearchParams(items);
        }
      } catch (loadError) {
        if (isMounted) {
          setSearchParamsError(
            loadError instanceof Error
              ? loadError.message
              : "Suchparameter konnten nicht geladen werden",
          );
        }
      }
    };

    void loadSearchParams();

    return () => {
      isMounted = false;
    };
  }, []);

  const config = useMemo<CrudConfig<JobSchedule>>(
    () => ({
      ...jobScheduleConfig,
      formFields: jobScheduleConfig.formFields.map((field) =>
        field.key === "search_params_id"
          ? {
              ...field,
              options: searchParams.map((item) => ({
                label: formatSearchParamsOption(item),
                value: item.id,
              })),
            }
          : field,
      ),
    }),
    [searchParams],
  );

  const updateScheduleEnabled = async (
    row: JobSchedule,
    enabled: boolean,
    reloadData: () => Promise<void>,
  ) => {
    setActionError(null);
    setUpdatingScheduleId(row.id);

    try {
      await jobScheduleApi.update({ enabled }, row.id);
      await reloadData();
    } catch (updateError) {
      setActionError(
        updateError instanceof Error
          ? updateError.message
          : "Job-Schedule konnte nicht aktualisiert werden",
      );
    } finally {
      setUpdatingScheduleId(null);
    }
  };

  return (
    <>
      {searchParamsError && (
        <p className="crud-error" role="alert">
          {searchParamsError}
        </p>
      )}

      {actionError && (
        <p className="crud-error" role="alert">
          {actionError}
        </p>
      )}

      <CrudPage
        config={config}
        api={jobScheduleApi}
        show_table={show_table}
        show_button={show_button}
        hideCancel={true}
        keepFormOpenAfterCreate={true}
        extraActions={(row, reloadData) => {
          const isUpdating = updatingScheduleId === row.id;

          return (
            <>
              <button
                type="button"
                className="crud-secondary-button crud-row-action-button"
                disabled={row.enabled || isUpdating}
                onClick={() => updateScheduleEnabled(row, true, reloadData)}
              >
                Aktivieren
              </button>

              <button
                type="button"
                className="crud-secondary-button crud-row-action-button"
                disabled={!row.enabled || isUpdating}
                onClick={() => updateScheduleEnabled(row, false, reloadData)}
              >
                Deaktivieren
              </button>
            </>
          );
        }}
      />
    </>
  );
}
