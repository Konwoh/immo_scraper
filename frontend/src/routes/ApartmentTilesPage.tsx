import { ListingDetailPage } from "@/components/listings/ListingDetailPage";
import { ListingTilesPage } from "@/components/listings/ListingTilesPage";
import { apartmentApi } from "@/entities/apartments/apartment.api";
import type { Apartment } from "@/entities/apartments/apartment.types";

export function ApartmentTilesPage() {
  return (
    <ListingTilesPage<Apartment>
      title="Wohnungen"
      api={apartmentApi}
      getDetailPath={(apartment) => `/tiles/apartments/${apartment.id}`}
    />
  );
}

export function ApartmentTileDetailPage() {
  return (
    <ListingDetailPage<Apartment>
      api={apartmentApi}
      backPath="/tiles/apartments"
      backLabel="Wohnungen"
    />
  );
}
