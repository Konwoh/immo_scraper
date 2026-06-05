import { useEffect, useState, type ReactNode } from "react";
import {
  DEFAULT_PAGE_SIZE,
  isPaginatedResponse,
  type ListResponse,
  type PaginatedResponse,
  type PaginationParams,
} from "@/api/pagination";
import { CrudForm } from "./CrudForm";
import { CrudTable } from "./CrudTable";

export type CrudColumn<T> = {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T) => ReactNode;
};

export type CrudField<T> = {
  key: keyof T;
  label: string;
  type: "text" | "number" | "datetime-local" | "textarea" | "select";
  required?: boolean;
  placeholder?: string;
  options?: { label: string; value: string | number | boolean }[];
};

export type CrudConfig<T> = {
  name: string;
  route: string;
  idField: keyof T;
  columns: CrudColumn<T>[];
  formFields: CrudField<T>[];
};

type CrudApi<T extends { id: string | number }> = {
  list: (params?: PaginationParams) => Promise<ListResponse<T>>;
  create?: (data: Partial<T>) => Promise<T>;
  delete?: (id: number) => Promise<void>;
};

type CrudPageProps<T extends { id: string | number }> = {
  config: CrudConfig<T>;
  api: CrudApi<T>;
  show_table: boolean;
  show_button: boolean;
  hideCancel: boolean;
  keepFormOpenAfterCreate: boolean;
  extraActions?: (row: T, reloadData: () => Promise<void>) => ReactNode;
};

export function CrudPage<T extends { id: string | number }>({
  config,
  api,
  show_table,
  show_button,
  hideCancel,
  keepFormOpenAfterCreate,
  extraActions,
}: CrudPageProps<T>) {
  const [data, setData] = useState<T[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pagination, setPagination] = useState<PaginatedResponse<T> | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(!show_table);
  const [error, setError] = useState<string | null>(null);

  const applyLoadError = (loadError: unknown) => {
    setError(
      loadError instanceof Error
        ? loadError.message
        : "Daten konnten nicht geladen werden",
    );
  };

  const applyListResponse = (response: ListResponse<T>) => {
    if (isPaginatedResponse(response)) {
      setData(response.items);
      setPagination(response);
      setCurrentPage(response.current_page);
      return;
    }

    setData(response);
    setPagination(null);
  };

  const reloadData = async (page = currentPage) => {
    setError(null);
    setLoading(true);

    try {
      const response = await api.list({
        page,
        page_size: DEFAULT_PAGE_SIZE,
      });
      applyListResponse(response);
    } catch (loadError) {
      applyLoadError(loadError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialData = async () => {
      setError(null);
      setLoading(true);

      try {
        const response = await api.list({
          page: currentPage,
          page_size: DEFAULT_PAGE_SIZE,
        });

        if (isMounted) {
          applyListResponse(response);
        }
      } catch (loadError) {
        if (isMounted) {
          applyLoadError(loadError);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    void loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [api, currentPage]);

  const handleDelete = api.delete
    ? async (row: T) => {
        const id = row[config.idField];

        if (typeof id !== "number") {
          setError("Dieser Datensatz kann nicht gelöscht werden.");
          return;
        }

        try {
          await api.delete?.(id);
          await reloadData();
        } catch (deleteError) {
          setError(
            deleteError instanceof Error
              ? deleteError.message
              : "Datensatz konnte nicht gelöscht werden",
          );
        }
      }
    : undefined;

  const handleCreate = api.create
    ? async (formData: Partial<T>) => {
        setError(null);

        try {
          await api.create?.(formData);
          if (!keepFormOpenAfterCreate) {
            setShowCreateForm(false);
          }
          await reloadData();
        } catch (createError) {
          setError(
            createError instanceof Error
              ? createError.message
              : "Datensatz konnte nicht erstellt werden",
          );
        }
      }
    : undefined;

  const handlePageChange = (page: number) => {
    setLoading(true);
    setCurrentPage(page);
  };

  return (
    <main className="crud-page">
      <header className="crud-page-header">
        <div>
          <h1>{config.name}</h1>
        </div>

        {api.create && show_button &&(
          <button
            className="crud-primary-button"
            type="button"
            onClick={() => setShowCreateForm(true)}
          >
            {config.name} hinzufügen
          </button>
        )}
      </header>

      {error && <p className="crud-error" role="alert">{error}</p>}

      {showCreateForm && handleCreate && (
        <section className="crud-form-panel">
          <CrudForm
            title={`${config.name} hinzufügen`}
            fields={config.formFields}
            mode="create"
            onSubmit={handleCreate}
            onCancel={hideCancel ? undefined : () => setShowCreateForm(false)}
          />
        </section>
      )}
      {show_table && (
        <CrudTable
          columns={config.columns}
          data={data}
          loading={loading}
          onDelete={handleDelete}
          currentPage={currentPage}
          totalPages={pagination?.total_pages ?? 1}
          totalItems={pagination?.total_items}
          startIndex={pagination?.start_index}
          endIndex={pagination?.end_index}
          currentPageSize={pagination?.current_page_size}
          onPageChange={pagination ? handlePageChange : undefined}
          extraActions={
            extraActions ? (row) => extraActions(row, reloadData) : undefined
          }
        />
      )}
    </main>
  );
}
