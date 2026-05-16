export type Job = {
  id: number;
  search_params_id: number;
  job_type: "scraper" | "crawler";
  status: "open" | "processing" | "done" | "failed";
  claimed_at: string | null;
  created_at: string;
  updated_at: string;
};
