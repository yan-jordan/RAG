"use client";

import { Files, SquarePen, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError, Doc, HistoryItem, Status } from "@/lib/api";
import AskBar from "./ask-bar";
import Rail from "./rail";
import Thread, { Turn } from "./thread";
import { IconButton, Logo, ThemeToggle, Toast, Toasts } from "./ui";

let uid = 0;
const nextId = () => `t${++uid}`;

function StatusPill({ status, offline }: { status: Status | null; offline: boolean }) {
  let dot = "bg-muted";
  let text = "در حال اتصال…";
  if (offline) [dot, text] = ["bg-danger", "سرور در دسترس نیست"];
  else if (status && !status.configured) [dot, text] = ["bg-danger", "کلید API تنظیم نشده"];
  else if (status?.demo_mode) [dot, text] = ["bg-[#f5b400]", "حالت دمو (آفلاین)"];
  else if (status) [dot, text] = ["bg-ok", "آماده"];
  return (
    <span
      className="flex items-center gap-2 rounded-full border border-line px-3 py-1.5 text-xs text-muted"
      title={status ? `مدل: ${status.chat_model} · بردارسازی: ${status.embedding_model}` : undefined}
    >
      <span className={`size-2 rounded-full ${dot}`} />
      {text}
    </span>
  );
}

export default function AppShell() {
  const [status, setStatus] = useState<Status | null>(null);
  const [offline, setOffline] = useState(false);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [scope, setScope] = useState<number[]>([]);
  const [uploading, setUploading] = useState<string[]>([]);
  const [tab, setTab] = useState<"docs" | "history">("docs");
  const [sheet, setSheet] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [seed, setSeed] = useState({ text: "", n: 0 });
  const scroller = useRef<HTMLDivElement>(null);

  const toast = useCallback((text: string, tone: Toast["tone"] = "error") => {
    const id = ++uid;
    setToasts((t) => [...t, { id, text, tone }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 6000);
  }, []);

  const refreshStatus = useCallback(() => api.status().then(setStatus).catch(() => {}), []);
  const refreshHistory = useCallback(() => api.history().then(setHistory).catch(() => {}), []);

  useEffect(() => {
    Promise.all([api.status(), api.documents(), api.history()])
      .then(([s, d, h]) => {
        setStatus(s);
        setDocs(d);
        setHistory(h);
      })
      .catch(() => setOffline(true));
  }, []);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [turns.length]);

  const busy = turns.some((t) => t.pending);

  async function ask(question: string) {
    const id = nextId();
    setTurns((t) => [...t, { id, question, pending: true }]);
    const live = scope.filter((s) => docs.some((d) => d.id === s));
    try {
      const res = await api.ask(question, live);
      setTurns((t) => t.map((x) => (x.id === id ? { ...x, pending: false, answer: res.answer, sources: res.sources } : x)));
      refreshHistory();
      refreshStatus();
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "مشکلی پیش اومد. دوباره امتحان کن.";
      setTurns((t) => t.map((x) => (x.id === id ? { ...x, pending: false, error: msg } : x)));
    }
  }

  async function addFiles(files: File[]) {
    for (const file of files) {
      if (!file.name.toLowerCase().endsWith(".docx")) {
        toast(`«${file.name}» فایل Word (.docx) نیست.`);
        continue;
      }
      setUploading((u) => [...u, file.name]);
      try {
        const doc = await api.upload(file);
        setDocs((d) => [doc, ...d]);
        if (doc.status === "failed") toast(`«${doc.title}»: ${doc.error_message}`);
      } catch (e) {
        toast(e instanceof ApiError ? e.message : "آپلود ناموفق بود.");
      } finally {
        setUploading((u) => u.filter((n) => n !== file.name));
      }
    }
    refreshStatus();
  }

  async function removeDoc(id: number) {
    try {
      await api.deleteDocument(id);
      setDocs((d) => d.filter((x) => x.id !== id));
      setScope((s) => s.filter((x) => x !== id));
      refreshStatus();
    } catch (e) {
      toast(e instanceof ApiError ? e.message : "حذف ناموفق بود.");
    }
  }

  const openHistory = (h: HistoryItem) => {
    setTurns([{ id: nextId(), question: h.question, answer: h.answer, sources: h.sources }]);
    setSheet(false);
  };

  const rail = (
    <Rail
      tab={tab}
      setTab={setTab}
      docCount={docs.length}
      historyCount={history.length}
      docs={docs}
      scope={scope}
      toggleScope={(id) => setScope((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]))}
      uploading={uploading}
      onFiles={addFiles}
      onDelete={removeDoc}
      maxMb={status?.max_upload_mb ?? 10}
      items={history}
      onOpen={openHistory}
      onDeleteHistory={(id) => api.deleteHistory(id).then(() => setHistory((h) => h.filter((x) => x.id !== id))).catch(() => toast("حذف ناموفق بود."))}
      onClear={() => api.clearHistory().then(() => setHistory([])).catch(() => toast("پاک کردن ناموفق بود."))}
    />
  );

  const readyDocs = docs.filter((d) => d.status === "ready").length;

  return (
    <div className="grid h-dvh lg:grid-cols-[360px_1fr]">
      {/* Desktop rail (right side in RTL) */}
      <aside className="hidden min-h-0 flex-col border-e border-line bg-surface lg:flex">
        <div className="px-5 pb-4 pt-6">
          <Logo />
        </div>
        {rail}
      </aside>

      <main className="relative flex min-h-0 flex-col">
        <header className="flex items-center justify-between gap-3 px-4 py-3 sm:px-8">
          <div className="lg:hidden">
            <Logo size={28} />
          </div>
          <div className="hidden lg:block">
            <StatusPill status={status} offline={offline} />
          </div>
          <div className="flex items-center gap-1">
            <span className="lg:hidden">
              <StatusPill status={status} offline={offline} />
            </span>
            {turns.length > 0 && (
              <IconButton label="گفتگوی جدید" onClick={() => setTurns([])}>
                <SquarePen size={18} />
              </IconButton>
            )}
            <ThemeToggle />
            <IconButton label="اسناد و سابقه" className="lg:hidden" onClick={() => setSheet(true)}>
              <Files size={18} />
            </IconButton>
          </div>
        </header>

        <div ref={scroller} className="scroll-thin min-h-0 flex-1 overflow-y-auto px-5 sm:px-8">
          <div className="mx-auto min-h-full max-w-3xl">
            <Thread
              turns={turns}
              hasDocs={readyDocs > 0}
              offline={offline}
              configured={status?.configured ?? true}
              onPick={(q) => setSeed({ text: q, n: seed.n + 1 })}
              onUpload={() => {
                setSheet(true);
                setTab("docs");
                document.querySelector<HTMLInputElement>("[data-upload-input]")?.click();
              }}
            />
          </div>
        </div>

        <AskBar
          busy={busy}
          scopeCount={scope.length}
          clearScope={() => setScope([])}
          onAsk={ask}
          seed={seed}
        />
      </main>

      {/* Mobile sheet */}
      {sheet && (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="اسناد و سابقه">
          <button aria-label="بستن" className="absolute inset-0 bg-ink/40" onClick={() => setSheet(false)} />
          <div className="absolute inset-x-0 bottom-0 flex max-h-[85dvh] min-h-[55dvh] flex-col rounded-t-[28px] bg-surface pt-2 shadow-2xl">
            <div className="flex items-center justify-between px-5 py-3">
              <Logo size={26} />
              <IconButton label="بستن" onClick={() => setSheet(false)}>
                <X size={18} />
              </IconButton>
            </div>
            {rail}
          </div>
        </div>
      )}

      <Toasts items={toasts} dismiss={(id) => setToasts((t) => t.filter((x) => x.id !== id))} />
    </div>
  );
}
