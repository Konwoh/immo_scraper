// components/crud/CrudTable.tsx

import type { ReactNode } from "react";

type Column<T> = {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T) => ReactNode;
};

type CrudTableProps<T> = {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;

  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;

  currentPage?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
};

export function CrudTable<T extends { id: string | number }>({
  columns,
  data,
  loading = false,
  onEdit,
  onDelete,
  currentPage = 1,
  totalPages = 1,
  onPageChange,
}: CrudTableProps<T>) {
  return (
    <div className="crud-table-shell">
      {/* Header */}
      <div className="crud-table-header">
        <div>
          <h2>
            Tabellenansicht
          </h2>

          <p>
            {data.length} Einträge geladen
          </p>
        </div>

        <button className="crud-secondary-button">
          Exportieren
        </button>
      </div>

      {/* Table */}
      <div className="crud-table-scroll">
        <table className="crud-table">
          <thead>
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                >
                  <button className="crud-column-button">
                    {column.label}
                    <span aria-hidden="true">↕</span>
                  </button>
                </th>
              ))}

              <th className="crud-actions-heading">
                Aktionen
              </th>
            </tr>
          </thead>

          <tbody>
            {loading ? (
              [...Array(6)].map((_, index) => (
                <tr
                  key={index}
                >
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                    >
                      <div className="crud-skeleton" />
                    </td>
                  ))}

                  <td>
                    <div className="crud-skeleton crud-skeleton-actions" />
                  </td>
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  className="crud-empty-cell"
                >
                  Keine Daten vorhanden
                </td>
              </tr>
            ) : (
              data.map((row) => (
                <tr
                  key={String(row.id)}
                >
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                    >
                      {column.render
                        ? column.render(row[column.key], row)
                        : String(row[column.key] ?? "-")}
                    </td>
                  ))}

                  <td>
                    <div className="crud-row-actions">
                      {onEdit && (
                        <button
                          onClick={() => onEdit(row)}
                          aria-label="Bearbeiten"
                          className="crud-icon-button"
                        >
                          <span aria-hidden="true">✎</span>
                        </button>
                      )}

                      {onDelete && (
                        <button
                          onClick={() => onDelete(row)}
                          aria-label="Löschen"
                          className="crud-icon-button crud-icon-button-danger"
                        >
                          <span aria-hidden="true">×</span>
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer / Pagination */}
      <div className="crud-table-footer">
        <p>
          Seite {currentPage} von {totalPages}
        </p>

        <div className="crud-pagination">
          <button
            disabled={currentPage <= 1}
            onClick={() => onPageChange?.(currentPage - 1)}
            className="crud-icon-button"
          >
            <span aria-hidden="true">‹</span>
          </button>

          <button
            disabled={currentPage >= totalPages}
            onClick={() => onPageChange?.(currentPage + 1)}
            className="crud-icon-button"
          >
            <span aria-hidden="true">›</span>
          </button>
        </div>
      </div>
    </div>
  );
}
