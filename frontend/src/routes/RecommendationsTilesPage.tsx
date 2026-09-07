import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FavoriteButton } from "@/components/favorites/FavoriteButton";
import { recommendationsApi } from "@/entities/recommendations/recommendations.api";
import type {
  RecommendationEstateType,
  RecommendationItem,
} from "@/entities/recommendations/recommendations.types";

const formatPrice = (price?: number | null) =>
  typeof price === "number" ? `${price.toLocaleString("de-DE")} €` : "-";

const formatArea = (area?: number | null) =>
  typeof area === "number" ? `${area} m²` : "-";

const formatRooms = (rooms?: number | null) => rooms ?? "-";

const formatTitle = (title?: string | null) =>
  title?.replace(/\s+/g, " ").trim() || "Ohne Titel";

const firstImage = (images?: string[] | null) => images?.[0] ?? null;

type RecommendationsTilesPageProps = {
  estateType: RecommendationEstateType;
  title: string;
};

const TILES_BASE: Record<RecommendationEstateType, string> = {
  house: "/tiles/houses",
  apartment: "/tiles/apartments",
};

function RecommendationsTilesPage({
  estateType,
  title,
}: RecommendationsTilesPageProps) {
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadItems = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await recommendationsApi.list(estateType);

        if (isMounted) {
          setItems(response.items);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Empfehlungen konnten nicht geladen werden",
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    void loadItems();

    return () => {
      isMounted = false;
    };
  }, [estateType]);

  const tilesBase = TILES_BASE[estateType];

  return (
    <main className="listing-page">
      <header className="listing-page-header">
        <div>
          <h1>Empfehlungen · {title}</h1>
          <p>{items.length} Empfehlungen</p>
        </div>
      </header>

      {error && (
        <p className="crud-error" role="alert">
          {error}
        </p>
      )}

      <section className="listing-grid" aria-label={`Empfehlungen ${title}`}>
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
          : items.map((item) => {
              const imageUrl = firstImage(item.images);

              return (
                <article className="listing-card" key={item.id}>
                  <span className="listing-card-similarity">
                    {Math.round(item.similarity * 100)}%
                  </span>

                  <FavoriteButton
                    className="favorite-button-overlay"
                    estateType={estateType}
                    estateId={item.id}
                    initialIsFavorite={false}
                  />

                  <Link
                    className="listing-card-link"
                    to={`${tilesBase}/${item.id}`}
                  >
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
                          alt={formatTitle(item.title)}
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
                      <h2>{formatTitle(item.title)}</h2>
                      {item.city && <span>{item.city}</span>}
                    </div>

                    <dl className="listing-card-meta">
                      <div>
                        <dt>Preis</dt>
                        <dd>{formatPrice(item.price)}</dd>
                      </div>
                      <div>
                        <dt>Fläche</dt>
                        <dd>{formatArea(item.living_space)}</dd>
                      </div>
                      <div>
                        <dt>Zimmer</dt>
                        <dd>{formatRooms(item.rooms)}</dd>
                      </div>
                    </dl>
                  </Link>
                </article>
              );
            })}
      </section>

      {!loading && !error && items.length === 0 && (
        <p className="listing-empty">
          Noch keine Empfehlungen. Markiere zuerst einige {title} als Favoriten
          (<Link to={tilesBase}>zur Übersicht</Link>).
        </p>
      )}
    </main>
  );
}

export function HouseRecommendationsPage() {
  return <RecommendationsTilesPage estateType="house" title="Häuser" />;
}

export function ApartmentRecommendationsPage() {
  return <RecommendationsTilesPage estateType="apartment" title="Wohnungen" />;
}
