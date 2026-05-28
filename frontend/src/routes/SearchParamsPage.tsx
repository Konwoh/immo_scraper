import { CrudPage } from "@/components/crud/CrudPage";

import { searchParamsApi } from "@/entities/search_params/search_params.api";
import { searchParamsConfig } from "@/entities/search_params/search_params.config";

export function SearchParamsPage() {
  return (
    <CrudPage
      config={searchParamsConfig}
      api={searchParamsApi}
      show_table={true}
      show_button={true}
    />
  );
}
