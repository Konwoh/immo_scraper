import { CrudPage } from "@/components/crud/CrudPage";

import { apartmentApi } from "@/entities/apartments/apartment.api";
import { apartmentConfig } from "@/entities/apartments/apartment.config";

export function ApartmentPage() {
  return (
    <CrudPage
      config={apartmentConfig}
      api={apartmentApi}
      show_table={true}
      show_button={true}
      hideCancel={false}
      keepFormOpenAfterCreate={false}
    />
  );
}