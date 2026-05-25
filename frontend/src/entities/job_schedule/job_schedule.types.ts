export type JobSchedule = {
    id: number;
    search_params_id: number;
    job_type: string;
    interval: string;
    enabled: boolean;
    last_run: string;
    next_run: string;
}