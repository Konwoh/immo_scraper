import { useState } from "react";
import { favoritesApi } from "@/entities/favorites/favorites.api";
import type { EstateType } from "@/entities/favorites/favorites.types";

type FavoriteButtonProps = {
  estateType: EstateType;
  estateId: number;
  initialIsFavorite: boolean;
  className?: string;
  onChange?: (isFavorite: boolean) => void;
};

export function FavoriteButton({
  estateType,
  estateId,
  initialIsFavorite,
  className,
  onChange,
}: FavoriteButtonProps) {
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite);
  const [pending, setPending] = useState(false);

  const handleClick = async () => {
    if (pending) {
      return;
    }

    const nextIsFavorite = !isFavorite;
    setPending(true);
    setIsFavorite(nextIsFavorite);

    try {
      if (nextIsFavorite) {
        await favoritesApi.add(estateType, estateId);
      } else {
        await favoritesApi.remove(estateType, estateId);
      }
      onChange?.(nextIsFavorite);
    } catch {
      setIsFavorite(!nextIsFavorite);
    } finally {
      setPending(false);
    }
  };

  return (
    <button
      type="button"
      className={`favorite-button${isFavorite ? " is-favorite" : ""}${className ? ` ${className}` : ""}`}
      onClick={() => void handleClick()}
      disabled={pending}
      aria-pressed={isFavorite}
      aria-label={
        isFavorite ? "Aus Favoriten entfernen" : "Zu Favoriten hinzufügen"
      }
      title={isFavorite ? "Aus Favoriten entfernen" : "Zu Favoriten hinzufügen"}
    >
      {isFavorite ? "★" : "☆"}
    </button>
  );
}
