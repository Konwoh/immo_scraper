import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { favoritesApi } from "@/entities/favorites/favorites.api";
import type { EstateType, Favorite } from "@/entities/favorites/favorites.types";
import { houseApi } from "@/entities/houses/house.api";
import { apartmentApi } from "@/entities/apartments/apartment.api";
import { propertyApi } from "@/entities/property/property.api";
import { FavoriteButton } from "@/components/favorites/FavoriteButton";

type FavoriteTile = {
  favoriteId: number;
  estateType: EstateType;
  estateId: number;
  title?: string | null;
  price?: string | number | null;
  area?: string | number | null;
  rooms?: string | number | null;
  city?: string | null;
  address?: string | null;
  images?: string[] | null;
  detailPath: string;
};

const formatPrice = (price?: string | number | null) => {
  if (typeof price === "number") {
    return `${price.toLocaleString("de-DE")} €`;
  }

  return price?.trim() || "-";
};

const formatArea = (area?: string | number | null) => {
  if (typeof area === "number") {
    return `${area} m²`;
  }

  const value = area?.trim();

  if (!value) {
    return "-";
  }

  return value.toLocaleLowerCase().includes("m") ? value : `${value} m²`;
};

const formatRooms = (rooms?: string | number | null) => rooms ?? "-";

const formatTitle = (title?: string | null) =>
  title?.replace(/\s+/g, " ").trim() || "Ohne Titel";

const firstImage = (images?: string[] | null) => images?.[0] ?? null;

async function loadFavoriteTile(favorite: Favorite): Promise<FavoriteTile> {
  if (favorite.house_id !== null) {
    const house = await houseApi.get(favorite.house_id);

    return {
      favoriteId: favorite.id,
      estateType: "house",
      estateId: house.id,
      title: house.title,
      price: house.price,
      area: house.living_space ?? house.size,
      rooms: house.rooms,
      city: house.city,
      address: house.address,
      images: house.images,
      detailPath: `/tiles/houses/${house.id}`,
    };
  }

  if (favorite.apartment_id !== null) {
    const apartment = await apartmentApi.get(favorite.apartment_id);

    return {
      favoriteId: favorite.id,
      estateType: "apartment",
      estateId: apartment.id,
      title: apartment.title,
      price: apartment.price,
      area: apartment.living_space ?? apartment.size,
      rooms: apartment.rooms,
      city: apartment.city,
      address: apartment.address,
      images: apartment.images,
      detailPath: `/tiles/apartments/${apartment.id}`,
    };
  }

  const property = await propertyApi.get(favorite.property_id as number);

  return {
    favoriteId: favorite.id,
    estateType: "property",
    estateId: property.id,
    title: property.title,
    price: property.price,
    area: property.space,
    rooms: null,
    city: property.city,
    address: property.address,
    images: property.images,
    detailPath: `/tiles/properties/${property.id}`,
  };
}

export function FavoritesTilesPage() {
  const [tiles, setTiles] = useState<FavoriteTile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadTiles = async () => {
      setLoading(true);
      setError(null);

      try {
        const favorites = await favoritesApi.list();
        const results = await Promise.allSettled(
          favorites.map(loadFavoriteTile),
        );

        if (!isMounted) {
          return;
        }

        setTiles(
          results
            .filter(
              (result): result is PromiseFulfilledResult<FavoriteTile> =>
                result.status === "fulfilled",
            )
            .map((result) => result.value),
        );
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Favoriten konnten nicht geladen werden",
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    void loadTiles();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleUnfavorite = (favoriteId: number) => {
    setTiles((current) =>
      current.filter((tile) => tile.favoriteId !== favoriteId),
    );
  };

  return (
    <main className="listing-page">
      <header className="listing-page-header">
        <div>
          <h1>Favoriten</h1>
          <p>{tiles.length} Favoriten</p>
        </div>
      </header>

      {error && (
        <p className="crud-error" role="alert">
          {error}
        </p>
      )}

      <section className="listing-grid" aria-label="Favoriten als Kacheln">
        {loading
          ? Array.from({ length: 8 }).map((_, index) => (
              <div className="listing-card listing-card-loading" key={index}>
                <div className="crud-skeleton listing-card-media-skeleton" />
                <div className="crud-skeleton listing-card-title-skeleton" />
                <div className="listing-card-meta">
                  <div className="crud-skeleton" />
                  <div className="crud-skeleton" />
                  <div className="crud-skeleton" />
                </div>
              </div>
            ))
          : tiles.map((tile) => {
              const imageUrl = firstImage(tile.images);

              return (
                <article className="listing-card" key={tile.favoriteId}>
                  <FavoriteButton
                    className="favorite-button-overlay"
                    estateType={tile.estateType}
                    estateId={tile.estateId}
                    initialIsFavorite
                    onChange={(isFavorite) => {
                      if (!isFavorite) {
                        handleUnfavorite(tile.favoriteId);
                      }
                    }}
                  />

                  <Link className="listing-card-link" to={tile.detailPath}>
                    <div
                      className={
                        imageUrl
                          ? "listing-card-media"
                          : "listing-card-media is-empty"
                      }
                    >
                      {imageUrl && (
                        <img
                          className="listing-card-image"
                          src={imageUrl}
                          alt={formatTitle(tile.title)}
                          loading="lazy"
                          decoding="async"
                          referrerPolicy="no-referrer"
                          onError={(event) => {
                            event.currentTarget.parentElement?.classList.add(
                              "is-empty",
                            );
                            event.currentTarget.remove();
                          }}
                        />
                      )}
                    </div>

                    <div className="listing-card-header">
                      <h2>{formatTitle(tile.title)}</h2>
                      {tile.city && <span>{tile.city}</span>}
                    </div>

                    <dl className="listing-card-meta">
                      <div>
                        <dt>Preis</dt>
                        <dd>{formatPrice(tile.price)}</dd>
                      </div>
                      <div>
                        <dt>Fläche</dt>
                        <dd>{formatArea(tile.area)}</dd>
                      </div>
                      <div>
                        <dt>Zimmer</dt>
                        <dd>{formatRooms(tile.rooms)}</dd>
                      </div>
                    </dl>

                    {tile.address && (
                      <p className="listing-card-address">{tile.address}</p>
                    )}
                  </Link>
                </article>
              );
            })}
      </section>

      {!loading && tiles.length === 0 && (
        <p className="listing-empty">Keine Favoriten vorhanden</p>
      )}
    </main>
  );
}
