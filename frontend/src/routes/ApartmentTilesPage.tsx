import { ListingDetailPage } from "@/components/listings/ListingDetailPage";
import { ListingTilesPage } from "@/components/listings/ListingTilesPage";
import { apartmentApi } from "@/entities/apartments/apartment.api";
import type { Apartment } from "@/entities/apartments/apartment.types";
import { APARTMENT_ESTATE_TYPES } from "@/entities/estates/estateFilters";

export function ApartmentTilesPage() {
  return (
    <ListingTilesPage<Apartment>
      title="Wohnungen"
      api={apartmentApi}
      getDetailPath={(apartment) => `/tiles/apartments/${apartment.id}`}
      filterOptions={{
        estateTypeLabel: "Wohnungstyp",
        estateTypeOptions: APARTMENT_ESTATE_TYPES,
      }}
    />
  );
}

export function ApartmentTileDetailPage() {
  return (
    <ListingDetailPage<Apartment>
      api={apartmentApi}
      backPath="/tiles/apartments"
      backLabel="Wohnungen"
      estateType="apartment"
    />
  );
}
