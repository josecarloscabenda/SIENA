import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Search, X } from "lucide-react";
import api from "@/shared/api/client";
import s from "./EntitySelect.module.css";

interface EntitySelectProps<T extends { id: string }> {
  endpoint: string;
  value: string;
  onChange: (id: string, item: T | null) => void;
  getLabel: (item: T) => string;
  getSecondary?: (item: T) => string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchParam?: string;
  params?: Record<string, string | number | boolean | undefined>;
  limit?: number;
  className?: string;
}

export default function EntitySelect<T extends { id: string }>({
  endpoint,
  value,
  onChange,
  getLabel,
  getSecondary,
  placeholder = "Pesquise...",
  disabled,
  required,
  searchParam = "nome",
  params,
  limit = 20,
  className,
}: EntitySelectProps<T>) {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<T[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<T | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const queryString = useMemo(() => {
    const sp = new URLSearchParams();
    sp.set("limit", String(limit));
    if (query) sp.set(searchParam, query);
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
      }
    }
    return sp.toString();
  }, [query, limit, searchParam, params]);

  /* Resolve initial label when value is set externally without `selected` populated */
  useEffect(() => {
    if (!value) {
      setSelected(null);
      return;
    }
    if (selected?.id === value) return;
    /* Try to find in current items first */
    const found = items.find((i) => i.id === value);
    if (found) {
      setSelected(found);
      return;
    }
    /* Last resort: fetch the same endpoint with a high limit and look up */
    api
      .get<T[]>(`${endpoint}?limit=500`)
      .then(({ data }) => {
        const match = data.find((i) => i.id === value);
        if (match) setSelected(match);
      })
      .catch(() => {});
  }, [value, endpoint, items, selected]);

  /* Debounced fetch on open / query / params change */
  useEffect(() => {
    if (!open) return;
    setLoading(true);
    const t = setTimeout(() => {
      api
        .get<T[]>(`${endpoint}?${queryString}`)
        .then(({ data }) => setItems(data))
        .catch(() => setItems([]))
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [endpoint, queryString, open]);

  /* Close on outside click */
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const handlePick = (item: T) => {
    setSelected(item);
    onChange(item.id, item);
    setOpen(false);
    setQuery("");
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelected(null);
    onChange("", null);
    setQuery("");
    inputRef.current?.focus();
  };

  const openAndFocus = () => {
    if (disabled) return;
    setOpen(true);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  return (
    <div ref={wrapperRef} className={`${s.wrapper} ${className ?? ""}`}>
      {/* Hidden native input for form validation (required) */}
      {required && (
        <input
          tabIndex={-1}
          aria-hidden="true"
          className={s.hidden}
          value={value}
          onChange={() => {}}
          required
        />
      )}

      <button
        type="button"
        className={`${s.trigger} ${disabled ? s.triggerDisabled : ""}`}
        onClick={openAndFocus}
        disabled={disabled}
      >
        <span className={selected ? s.selectedLabel : s.placeholder}>
          {selected ? getLabel(selected) : placeholder}
        </span>
        <span className={s.actions}>
          {selected && !disabled && (
            <span
              role="button"
              aria-label="Limpar selecção"
              className={s.clearBtn}
              onClick={handleClear}
            >
              <X size={14} />
            </span>
          )}
          <ChevronDown size={16} className={s.chevron} />
        </span>
      </button>

      {open && (
        <div className={s.popup}>
          <div className={s.searchRow}>
            <Search size={14} className={s.searchIcon} />
            <input
              ref={inputRef}
              type="text"
              className={s.searchInput}
              placeholder="Filtrar por nome..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoComplete="off"
            />
          </div>
          <div className={s.list}>
            {loading ? (
              <div className={s.empty}>A carregar...</div>
            ) : items.length === 0 ? (
              <div className={s.empty}>Sem resultados</div>
            ) : (
              items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`${s.item} ${value === item.id ? s.itemSelected : ""}`}
                  onClick={() => handlePick(item)}
                >
                  <span className={s.itemPrimary}>{getLabel(item)}</span>
                  {getSecondary && (
                    <span className={s.itemSecondary}>{getSecondary(item)}</span>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
