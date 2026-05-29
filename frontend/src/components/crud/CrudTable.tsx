// components/crud/CrudTable.tsx

import { useState, type ReactNode } from "react";

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
  extraActions?: (row: T) => ReactNode;
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
  extraActions,
  currentPage = 1,
  totalPages = 1,
  onPageChange,
}: CrudTableProps<T>) {
  const itemsPerPage = 25;
  const [localCurrentPage, setLocalCurrentPage] = useState(1);
  const hasControlledPagination = Boolean(onPageChange);
  const computedTotalPages = Math.max(1, Math.ceil(data.length / itemsPerPage));
  const pageCount = hasControlledPagination
    ? Math.max(1, totalPages)
    : computedTotalPages;
  const activePage = Math.min(
    Math.max(hasControlledPagination ? currentPage : localCurrentPage, 1),
    pageCount,
  );
  const visibleRows = hasControlledPagination
    ? data
    : data.slice((activePage - 1) * itemsPerPage, activePage * itemsPerPage);

  const handlePageChange = (page: number) => {
    const nextPage = Math.min(Math.max(page, 1), pageCount);

    if (hasControlledPagination) {
      onPageChange?.(nextPage);
      return;
    }

    setLocalCurrentPage(nextPage);
  };

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
              visibleRows.map((row) => (
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
                      {extraActions?.(row)}

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
          Seite {activePage} von {pageCount}
        </p>

        <div className="crud-pagination">
          <button
            disabled={activePage <= 1}
            onClick={() => handlePageChange(activePage - 1)}
            className="crud-icon-button"
          >
            <span aria-hidden="true">‹</span>
          </button>

          <button
            disabled={activePage >= pageCount}
            onClick={() => handlePageChange(activePage + 1)}
            className="crud-icon-button"
          >
            <span aria-hidden="true">›</span>
          </button>
        </div>
      </div>
    </div>
  );
}
