import { CrudPage } from "@/components/crud/CrudPage";

import { jobScheduleApi } from "@/entities/job_schedule/job_schedule.api";
import { jobScheduleConfig } from "@/entities/job_schedule/job_schedule.config";

export function JobSchedulePage() {
  return (
    <CrudPage
      config={jobScheduleConfig}
      api={jobScheduleApi}
    />
  );
}
