import { ListingDetailPage } from "@/components/listings/ListingDetailPage";
import { ListingTilesPage } from "@/components/listings/ListingTilesPage";
import { houseApi } from "@/entities/houses/house.api";
import type { House } from "@/entities/houses/house.types";
import { HOUSE_ESTATE_TYPES } from "@/entities/estates/estateFilters";

export function HouseTilesPage() {
  return (
    <ListingTilesPage<House>
      title="Häuser"
      api={houseApi}
      getDetailPath={(house) => `/tiles/houses/${house.id}`}
      filterOptions={{
        estateTypeLabel: "Haustyp",
        estateTypeOptions: HOUSE_ESTATE_TYPES,
      }}
    />
  );
}

export function HouseTileDetailPage() {
  return (
    <ListingDetailPage<House>
      api={houseApi}
      backPath="/tiles/houses"
      backLabel="Häuser"
      estateType="house"
    />
  );
}
