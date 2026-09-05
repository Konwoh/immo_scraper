import { ListingDetailPage } from "@/components/listings/ListingDetailPage";
import { ListingTilesPage } from "@/components/listings/ListingTilesPage";
import { propertyApi } from "@/entities/property/property.api";
import type { Property } from "@/entities/property/property.types";

export function PropertyTilesPage() {
  return (
    <ListingTilesPage<Property>
      title="Grundstücke"
      api={propertyApi}
      getDetailPath={(property) => `/tiles/properties/${property.id}`}
    />
  );
}

export function PropertyTileDetailPage() {
  return (
    <ListingDetailPage<Property>
      api={propertyApi}
      backPath="/tiles/properties"
      backLabel="Grundstücke"
      estateType="property"
    />
  );
}
