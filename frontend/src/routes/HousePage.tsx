import { CrudPage } from "@/components/crud/CrudPage";

import { houseApi } from "@/entities/houses/house.api";
import { houseConfig } from "@/entities/houses/house.config";

export function HousesPage() {
  return (
    <CrudPage
      config={houseConfig}
      api={houseApi}
    />
  );
}