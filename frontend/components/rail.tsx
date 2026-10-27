"use client";

import { AlertCircle, Check, FilePlus2, FileText, Loader2, Trash2 } from "lucide-react";
import { useRef, useState } from "react";
import { Doc, HistoryItem } from "@/lib/api";
import { bytes, dayLabel, fa, timeLabel } from "@/lib/format";
import { IconButton } from "./ui";

type Tab = "docs" | "history";

/* ── Documents ─────────────────────────────────────────────────────── */
function Documents({
  docs,
  scope,
  toggleScope,
  uploading,
  onFiles,
  onDelete,
  maxMb,
}: {
  docs: Doc[];
  scope: number[];
  toggleScope: (id: number) => void;
  uploading: string[];
  onFiles: (files: File[]) => void;
  onDelete: (id: number) => void;
  maxMb: number;
}) {
  const input = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);
  const [confirm, setConfirm] = useState<number | null>(null);

  return (
    <div className="space-y-5">
      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          onFiles(Array.from(e.dataTransfer.files));
        }}
        className={`flex cursor-pointer items-center gap-3 rounded-2xl border-2 border-dashed px-4 py-4 transition-colors ${
          drag ? "border-accent bg-accent/10" : "border-line hover:border-accent/60"
        }`}
      >
        <input
          ref={input}
          type="file"
          multiple
          accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          className="sr-only"
          data-upload-input
          onChange={(e) => {
            onFiles(Array.from(e.target.files ?? []));
            e.target.value = "";
          }}
        />
        <FilePlus2 size={22} className="shrink-0 text-accent" />
        <span className="text-sm leading-7">
          <b className="font-semibold">فایل Word اضافه کن</b>
          <br />
          <span className="text-muted">بکشش اینجا یا انتخاب کن (تا {fa(maxMb)} مگابایت)</span>
        </span>
      </label>

      <ul className="space-y-0.5">
        {uploading.map((name) => (
          <li key={name} className="flex items-center gap-3 rounded-xl px-2 py-2.5 text-sm text-muted">
            <Loader2 size={18} className="animate-spin" />
            <span className="truncate">{name}</span>
          </li>
        ))}

        {docs.map((d) => {
          const ready = d.status === "ready";
          const on = scope.includes(d.id);
          return (
            <li key={d.id} className="group flex items-start gap-3 rounded-xl px-2 py-2.5 hover:bg-line/40">
              {ready ? (
                <button
                  onClick={() => toggleScope(d.id)}
                  aria-pressed={on}
                  aria-label={`فقط از «${d.title}» بپرس`}
                  title="فقط از همین سند بپرس"
                  className={`mt-1 grid size-5 shrink-0 place-items-center rounded-full border-2 transition-colors ${
                    on ? "border-accent bg-accent text-on-accent" : "border-line text-transparent hover:border-accent"
                  }`}
                >
                  <Check size={12} strokeWidth={3.5} />
                </button>
              ) : (
                <AlertCircle size={20} className="mt-0.5 shrink-0 text-danger" />
              )}

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <FileText size={14} className="shrink-0 text-muted" />
                  <span className="truncate text-sm font-semibold">{d.title}</span>
                </div>
                {confirm === d.id ? (
                  <div className="mt-1.5 flex items-center gap-3 text-xs">
                    <span className="text-muted">حذف بشه؟</span>
                    <button className="font-bold text-danger" onClick={() => onDelete(d.id)}>
                      آره، حذف کن
                    </button>
                    <button className="text-muted hover:text-ink" onClick={() => setConfirm(null)}>
                      نه
                    </button>
                  </div>
                ) : (
                  <p className={`mt-0.5 text-xs leading-6 ${ready ? "text-muted" : "text-danger"}`}>
                    {ready ? `${fa(d.text_length)} نویسه · ${bytes(d.size)}` : d.error_message || "پردازش فایل ناموفق بود"}
                  </p>
                )}
              </div>

              {confirm !== d.id && (
                <IconButton
                  label={`حذف ${d.title}`}
                  className="size-8 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 focus-visible:opacity-100"
                  onClick={() => setConfirm(d.id)}
                >
                  <Trash2 size={16} />
                </IconButton>
              )}
            </li>
          );
        })}
      </ul>

      {!docs.length && !uploading.length && (
        <p className="px-2 text-sm leading-7 text-muted">هنوز سندی نداری. با اضافه کردن اولین فایل شروع کن.</p>
      )}
    </div>
  );
}

/* ── History ───────────────────────────────────────────────────────── */
function History({
  items,
  onOpen,
  onDelete,
  onClear,
}: {
  items: HistoryItem[];
  onOpen: (h: HistoryItem) => void;
  onDelete: (id: number) => void;
  onClear: () => void;
}) {
  const [confirmClear, setConfirmClear] = useState(false);

  if (!items.length) return <p className="px-2 text-sm leading-7 text-muted">هنوز سوالی نپرسیدی.</p>;

  const groups: { label: string; rows: HistoryItem[] }[] = [];
  for (const h of items) {
    const label = dayLabel(h.created_at);
    const last = groups[groups.length - 1];
    if (last?.label === label) last.rows.push(h);
    else groups.push({ label, rows: [h] });
  }

  return (
    <div className="space-y-6">
      {groups.map((g) => (
        <section key={g.label}>
          <h3 className="mb-1 px-2 text-xs font-semibold text-muted">{g.label}</h3>
          <ul>
            {g.rows.map((h) => (
              <li key={h.id} className="group flex items-start gap-1 rounded-xl hover:bg-line/40">
                <button onClick={() => onOpen(h)} className="min-w-0 flex-1 px-2 py-2.5 text-start">
                  <span className="line-clamp-2 text-sm leading-7">{h.question}</span>
                  <span className="text-xs text-muted">{timeLabel(h.created_at)}</span>
                </button>
                <IconButton
                  label="حذف از سابقه"
                  className="mt-1.5 size-8 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 focus-visible:opacity-100"
                  onClick={() => onDelete(h.id)}
                >
                  <Trash2 size={15} />
                </IconButton>
              </li>
            ))}
          </ul>
        </section>
      ))}

      <div className="px-2 text-xs">
        {confirmClear ? (
          <span className="flex items-center gap-3">
            <span className="text-muted">همه‌ی سابقه پاک بشه؟</span>
            <button
              className="font-bold text-danger"
              onClick={() => {
                onClear();
                setConfirmClear(false);
              }}
            >
              آره، پاک کن
            </button>
            <button className="text-muted hover:text-ink" onClick={() => setConfirmClear(false)}>
              نه
            </button>
          </span>
        ) : (
          <button className="text-muted hover:text-danger" onClick={() => setConfirmClear(true)}>
            پاک کردن همه‌ی سابقه
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Rail ──────────────────────────────────────────────────────────── */
export default function Rail({
  tab,
  setTab,
  historyCount,
  docCount,
  ...rest
}: {
  tab: Tab;
  setTab: (t: Tab) => void;
  historyCount: number;
  docCount: number;
} & React.ComponentProps<typeof Documents> &
  Pick<React.ComponentProps<typeof History>, "onOpen" | "onClear"> & {
    items: HistoryItem[];
    onDeleteHistory: (id: number) => void;
  }) {
  const tabs: { id: Tab; label: string; n: number }[] = [
    { id: "docs", label: "اسناد", n: docCount },
    { id: "history", label: "سابقه", n: historyCount },
  ];
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div role="tablist" className="flex gap-6 border-b border-line px-5">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`-mb-px border-b-2 py-3 text-sm font-semibold transition-colors ${
              tab === t.id ? "border-accent text-ink" : "border-transparent text-muted hover:text-ink"
            }`}
          >
            {t.label} <span className="font-normal text-muted">{fa(t.n)}</span>
          </button>
        ))}
      </div>
      <div className="scroll-thin min-h-0 flex-1 overflow-y-auto p-3">
        {tab === "docs" ? (
          <Documents
            docs={rest.docs}
            scope={rest.scope}
            toggleScope={rest.toggleScope}
            uploading={rest.uploading}
            onFiles={rest.onFiles}
            onDelete={rest.onDelete}
            maxMb={rest.maxMb}
          />
        ) : (
          <History items={rest.items} onOpen={rest.onOpen} onDelete={rest.onDeleteHistory} onClear={rest.onClear} />
        )}
      </div>
    </div>
  );
}
