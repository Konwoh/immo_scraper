import { useEffect, useState, type ReactNode } from "react";
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
  list: () => Promise<T[]>;
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
};

export function CrudPage<T extends { id: string | number }>({
  config,
  api,
  show_table,
  show_button,
  hideCancel,
  keepFormOpenAfterCreate,
}: CrudPageProps<T>) {
  const [data, setData] = useState<T[]>([]);
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

  const reloadData = async () => {
    setError(null);
    setLoading(true);

    try {
      const items = await api.list();
      setData(items);
    } catch (loadError) {
      applyLoadError(loadError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    const loadInitialData = async () => {
      try {
        const items = await api.list();

        if (isMounted) {
          setData(items);
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
  }, [api]);

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
        />
      )}
    </main>
  );
}
