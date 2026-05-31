import { CrudPage } from "@/components/crud/CrudPage";

import { propertyApi } from "@/entities/property/property.api";
import { propertyConfig } from "@/entities/property/property.config";

export function PropertyPage() {
  return (
    <CrudPage
      config={propertyConfig}
      api={propertyApi}
      show_table={true}
      show_button={true}
      hideCancel={false}
      keepFormOpenAfterCreate={false}
    />
  );
}