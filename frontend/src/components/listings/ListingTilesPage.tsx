import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  isPaginatedResponse,
  type ListResponse,
  type PaginatedResponse,
  type PaginationParams,
} from "@/api/pagination";

export type ListingTileItem = {
  id: number;
  title?: string | null;
  price?: string | number | null;
  size?: string | number | null;
  living_space?: string | number | null;
  rooms?: string | number | null;
  city?: string | null;
  address?: string | null;
  sourceUrl?: string | null;
  url?: string | null;
};

type ListingTilesApi<T extends ListingTileItem> = {
  list: (params?: PaginationParams) => Promise<ListResponse<T>>;
};

type ListingTilesPageProps<T extends ListingTileItem> = {
  title: string;
  api: ListingTilesApi<T>;
  getDetailPath: (item: T) => string;
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

export function ListingTilesPage<T extends ListingTileItem>({
  title,
  api,
  getDetailPath,
}: ListingTilesPageProps<T>) {
  const [data, setData] = useState<T[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<PaginatedResponse<T> | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.list({ page: currentPage });

        if (!isMounted) {
          return;
        }

        if (isPaginatedResponse(response)) {
          setData(response.items);
          setPagination(response);
          setCurrentPage(response.current_page);
          return;
        }

        setData(response);
        setPagination(null);
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Daten konnten nicht geladen werden",
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    void loadData();

    return () => {
      isMounted = false;
    };
  }, [api, currentPage]);

  const totalPages = pagination?.total_pages ?? 1;
  const totalItems = pagination?.total_items ?? data.length;
  const loadedItems = pagination?.current_page_size ?? data.length;

  const handlePageChange = (page: number) => {
    setCurrentPage(Math.min(Math.max(page, 1), totalPages));
  };

  return (
    <main className="listing-page">
      <header className="listing-page-header">
        <div>
          <h1>{title}</h1>
          <p>
            {loadedItems} von {totalItems} Einträge geladen
          </p>
        </div>
      </header>

      {error && (
        <p className="crud-error" role="alert">
          {error}
        </p>
      )}

      <section className="listing-grid" aria-label={`${title} als Kacheln`}>
        {loading
          ? Array.from({ length: 8 }).map((_, index) => (
              <div className="listing-card listing-card-loading" key={index}>
                <div className="crud-skeleton listing-card-title-skeleton" />
                <div className="listing-card-meta">
                  <div className="crud-skeleton" />
                  <div className="crud-skeleton" />
                  <div className="crud-skeleton" />
                </div>
              </div>
            ))
          : data.map((item) => {
              return (
                <article className="listing-card" key={item.id}>
                  <Link className="listing-card-link" to={getDetailPath(item)}>
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
                        <dd>{formatArea(item.living_space ?? item.size)}</dd>
                      </div>
                      <div>
                        <dt>Zimmer</dt>
                        <dd>{formatRooms(item.rooms)}</dd>
                      </div>
                    </dl>

                    {item.address && (
                      <p className="listing-card-address">{item.address}</p>
                    )}
                  </Link>
                </article>
              );
            })}
      </section>

      {!loading && data.length === 0 && (
        <p className="listing-empty">Keine Daten vorhanden</p>
      )}

      <footer className="listing-pagination">
        <p>
          Seite {currentPage} von {totalPages}
        </p>

        <div className="crud-pagination">
          <button
            type="button"
            disabled={currentPage <= 1}
            onClick={() => handlePageChange(currentPage - 1)}
            className="crud-icon-button"
            aria-label="Vorherige Seite"
          >
            <span aria-hidden="true">‹</span>
          </button>

          <button
            type="button"
            disabled={currentPage >= totalPages}
            onClick={() => handlePageChange(currentPage + 1)}
            className="crud-icon-button"
            aria-label="Nächste Seite"
          >
            <span aria-hidden="true">›</span>
          </button>
        </div>
      </footer>
    </main>
  );
}
