// components/crud/CrudForm.tsx

import { useState, type FormEvent } from "react";

export type CrudField<T> = {
  key: keyof T;
  label: string;
  type?: "text" | "number" | "email" | "password" | "textarea" | "select";
  placeholder?: string;
  required?: boolean;
  options?: { label: string; value: string | number }[];
};

type CrudFormProps<T> = {
  title: string;
  fields: CrudField<T>[];
  initialData?: Partial<T> | null;
  mode?: "create" | "edit";

  onSubmit: (data: Partial<T>) => void;
  onDelete?: (data: Partial<T>) => void;
  onCancel?: () => void;
};

export function CrudForm<T>({
  title,
  fields,
  initialData = null,
  mode = "create",
  onSubmit,
  onDelete,
  onCancel,
}: CrudFormProps<T>) {
  const [formData, setFormData] = useState<Partial<T>>(initialData ?? {});

  function handleChange(key: keyof T, value: string | number) {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
    }));
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit(formData);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="crud-form"
    >
      {/* Header */}
      <div className="crud-form-header">
        <div>
          <h2>{title}</h2>
          <p>
            {mode === "create"
              ? "Neuen Eintrag erstellen"
              : "Eintrag bearbeiten"}
          </p>
        </div>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            aria-label="Schließen"
            className="crud-icon-button"
          >
            <span aria-hidden="true">×</span>
          </button>
        )}
      </div>

      {/* Fields */}
      <div className="crud-form-grid">
        {fields.map((field) => {
          const value = formData[field.key] ?? "";

          return (
            <div
              key={String(field.key)}
              className={field.type === "textarea" ? "crud-form-wide" : ""}
            >
              <label>
                {field.label}
                {field.required && (
                  <span aria-hidden="true">*</span>
                )}
              </label>

              {field.type === "textarea" ? (
                <textarea
                  required={field.required}
                  placeholder={field.placeholder}
                  value={String(value)}
                  onChange={(e) =>
                    handleChange(field.key, e.target.value)
                  }
                />
              ) : field.type === "select" ? (
                <select
                  required={field.required}
                  value={String(value)}
                  onChange={(e) =>
                    handleChange(field.key, e.target.value)
                  }
                >
                  <option value="">Bitte auswählen</option>
                  {field.options?.map((option) => (
                    <option
                      key={String(option.value)}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  required={field.required}
                  type={field.type ?? "text"}
                  placeholder={field.placeholder}
                  value={String(value)}
                  onChange={(e) =>
                    handleChange(
                      field.key,
                      field.type === "number"
                        ? Number(e.target.value)
                        : e.target.value
                    )
                  }
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div className="crud-form-actions">
        <div>
          {mode === "edit" && onDelete && (
            <button
              type="button"
              onClick={() => onDelete(formData)}
              className="crud-danger-button"
            >
              <span aria-hidden="true">×</span>
              Löschen
            </button>
          )}
        </div>

        <div className="crud-form-action-group">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="crud-secondary-button"
            >
              Abbrechen
            </button>
          )}

          <button
            type="submit"
            className="crud-primary-button"
          >
            <span aria-hidden="true">✓</span>
            {mode === "create" ? "Hinzufügen" : "Speichern"}
          </button>
        </div>
      </div>
    </form>
  );
}
