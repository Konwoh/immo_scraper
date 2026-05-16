import { CrudPage } from "@/components/crud/CrudPage";

import { jobApi } from "@/entities/jobs/job.api";
import { jobConfig } from "@/entities/jobs/job.config";

export function JobPage() {
  return (
    <CrudPage
      config={jobConfig}
      api={jobApi}
    />
  );
}
