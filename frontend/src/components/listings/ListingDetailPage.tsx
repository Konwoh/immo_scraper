import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getPredictionPayloadFromUrl,
  predictPrice,
} from "@/entities/predict/predict.api";
import type { ListingTileItem } from "./ListingTilesPage";

type ListingDetailItem = ListingTileItem & {
  description?: string | null;
  general_description?: string | null;
  object_description?: string | null;
  place_description?: string | null;
  other_description?: string | null;
  coldRent?: string | number | null;
  rent_cold?: string | number | null;
  additionalCosts?: string | number | null;
  rent_extra_costs?: string | number | null;
  floor?: string | number | null;
  zipCode?: string | null;
  zip_code?: string | null;
  source?: string | null;
  sourceUrl?: string | null;
  url?: string | null;
  images?: string[] | null;
  is_online?: boolean | null;
};

type ListingDetailApi<T extends ListingDetailItem> = {
  get: (id: number) => Promise<T>;
};

type ListingDetailPageProps<T extends ListingDetailItem> = {
  api: ListingDetailApi<T>;
  backPath: string;
  backLabel: string;
};

type PredictionState = {
  loading: boolean;
  error?: string;
  predictedPrice?: number;
  comparison?: "higher" | "lower" | "equal" | "unknown";
};

const formatOptionalPrice = (price?: string | number | null) => {
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

const formatOnlineStatus = (isOnline?: boolean | null) => {
  if (isOnline === true) {
    return "Online";
  }

  if (isOnline === false) {
    return "Nicht mehr online";
  }

  return "-";
};

const parsePrice = (price?: string | number | null) => {
  if (typeof price === "number") {
    return price;
  }

  const value = price?.replace(/[^\d,.]/g, "");

  if (!value) {
    return null;
  }

  const normalizedValue = value.includes(",")
    ? value.replace(/\./g, "").replace(",", ".")
    : value.replace(/\./g, "");
  const parsedValue = Number(normalizedValue);

  return Number.isFinite(parsedValue) ? parsedValue : null;
};

const getPredictionClassName = (comparison?: PredictionState["comparison"]) => {
  if (comparison === "higher") {
    return "listing-prediction-result listing-prediction-result-high";
  }

  if (comparison === "lower") {
    return "listing-prediction-result listing-prediction-result-low";
  }

  return "listing-prediction-result";
};

const getComparisonLabel = (comparison?: PredictionState["comparison"]) => {
  if (comparison === "higher") {
    return "über aktuellem Preis";
  }

  if (comparison === "lower") {
    return "unter aktuellem Preis";
  }

  if (comparison === "equal") {
    return "entspricht aktuellem Preis";
  }

  return "kein Vergleich möglich";
};

const normalizeUrl = (url?: string | null) => {
  const value = url?.trim();

  if (!value) {
    return null;
  }

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value;
  }

  return `https://${value}`;
};

export function ListingDetailPage<T extends ListingDetailItem>({
  api,
  backPath,
  backLabel,
}: ListingDetailPageProps<T>) {
  const { id } = useParams();
  const [item, setItem] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<PredictionState | null>(null);
  const [activeImage, setActiveImage] = useState(0);
  const images = item?.images ?? [];
  const description =
    item?.description ??
    item?.object_description ??
    item?.general_description ??
    item?.place_description ??
    item?.other_description;
  const sourceUrl = normalizeUrl(item?.sourceUrl ?? item?.url);

  const handlePredictPrice = async () => {
    if (!sourceUrl || !item) {
      setPrediction({
        loading: false,
        error: "Keine URL vorhanden",
      });
      return;
    }

    setPrediction({ loading: true });

    try {
      const payload = await getPredictionPayloadFromUrl(sourceUrl);
      const result = await predictPrice(payload);
      const actualPrice = parsePrice(item.price);
      const comparison =
        actualPrice === null
          ? "unknown"
          : result.predicted_price_all > actualPrice
            ? "higher"
            : result.predicted_price_all < actualPrice
              ? "lower"
              : "equal";

      setPrediction({
        loading: false,
        predictedPrice: result.predicted_price_all,
        comparison,
      });
    } catch (predictionError) {
      setPrediction({
        loading: false,
        error:
          predictionError instanceof Error
            ? predictionError.message
            : "Preisvorhersage fehlgeschlagen",
      });
    }
  };

  useEffect(() => {
    let isMounted = true;
    const numericId = Number(id);

    const loadItem = async () => {
      if (!Number.isInteger(numericId) || numericId <= 0) {
        setError("Ungültige ID");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await api.get(numericId);

        if (isMounted) {
          setItem(response);
          setActiveImage(0);
        }
      } catch (loadError) {
        if (isMounted) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Datensatz konnte nicht geladen werden",
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    void loadItem();

    return () => {
      isMounted = false;
    };
  }, [api, id]);

  return (
    <main className="listing-detail-page">
      <Link className="listing-back-link" to={backPath}>
        Zurück zu {backLabel}
      </Link>

      {loading && (
        <section className="listing-detail-panel">
          <div className="crud-skeleton listing-detail-title-skeleton" />
          <div className="listing-detail-meta">
            <div className="crud-skeleton" />
            <div className="crud-skeleton" />
            <div className="crud-skeleton" />
          </div>
        </section>
      )}

      {error && (
        <p className="crud-error" role="alert">
          {error}
        </p>
      )}

      {!loading && item && (
        <section className="listing-detail-panel">
          <header className="listing-detail-header">
            <div>
              <h1>{formatTitle(item.title)}</h1>
              <p>
                {[item.address, item.zip_code ?? item.zipCode, item.city]
                  .filter(Boolean)
                  .join(", ")}
              </p>
            </div>
          </header>

          {images.length > 0 && (
            <figure className="listing-detail-gallery">
              <img
                className="listing-detail-gallery-main"
                src={images[activeImage] ?? images[0]}
                alt={formatTitle(item.title)}
                loading="lazy"
                decoding="async"
                referrerPolicy="no-referrer"
              />

              {images.length > 1 && (
                <div className="listing-detail-gallery-thumbs">
                  {images.map((src, index) => (
                    <button
                      type="button"
                      key={`${src}-${index}`}
                      className={index === activeImage ? "is-active" : undefined}
                      onClick={() => setActiveImage(index)}
                      aria-label={`Bild ${index + 1} von ${images.length}`}
                    >
                      <img
                        src={src}
                        alt=""
                        loading="lazy"
                        decoding="async"
                        referrerPolicy="no-referrer"
                      />
                    </button>
                  ))}
                </div>
              )}
            </figure>
          )}

          <dl className="listing-detail-meta">
            <div>
              <dt>Preis</dt>
              <dd>{formatOptionalPrice(item.price)}</dd>
            </div>
            <div>
              <dt>Fläche</dt>
              <dd>{formatArea(item.living_space ?? item.size)}</dd>
            </div>
            <div>
              <dt>Zimmer</dt>
              <dd>{formatRooms(item.rooms)}</dd>
            </div>
            <div>
              <dt>Kaltmiete</dt>
              <dd>{formatOptionalPrice(item.rent_cold ?? item.coldRent)}</dd>
            </div>
            <div>
              <dt>Nebenkosten</dt>
              <dd>
                {formatOptionalPrice(
                  item.rent_extra_costs ?? item.additionalCosts,
                )}
              </dd>
            </div>
            <div>
              <dt>Etage</dt>
              <dd>{item.floor ?? "-"}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{formatOnlineStatus(item.is_online)}</dd>
            </div>
          </dl>

          <section className="listing-detail-prediction">
            <button
              className="crud-primary-button"
              type="button"
              disabled={!sourceUrl || prediction?.loading}
              onClick={() => void handlePredictPrice()}
            >
              {prediction?.loading
                ? "Berechnung läuft..."
                : "Preis vorhersagen"}
            </button>

            {prediction?.predictedPrice !== undefined && (
              <p className={getPredictionClassName(prediction.comparison)}>
                <strong>
                  {prediction.predictedPrice.toLocaleString("de-DE")} €
                </strong>
                <span>{getComparisonLabel(prediction.comparison)}</span>
              </p>
            )}

            {prediction?.error && (
              <p className="listing-prediction-error">{prediction.error}</p>
            )}
          </section>

          {description && (
            <div className="listing-detail-description">
              <h2>Beschreibung</h2>
              <p>{description}</p>
            </div>
          )}

          {(item.source || sourceUrl) && (
            <div className="listing-detail-source">
              {item.source && <span>{item.source}</span>}
              {sourceUrl && (
                <div className="listing-detail-url">
                  <span>Originalanzeige</span>
                  <a href={sourceUrl} target="_blank" rel="noreferrer">
                    {sourceUrl}
                  </a>
                </div>
              )}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
