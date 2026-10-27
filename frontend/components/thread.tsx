"use client";

import { AlertTriangle, ChevronDown, Plus } from "lucide-react";
import { useState } from "react";
import Markdown from "react-markdown";
import { API_URL, Source } from "@/lib/api";
import { markEvidence } from "@/lib/evidence";
import { fa } from "@/lib/format";

export type Turn = {
  id: string;
  question: string;
  answer?: string;
  sources?: Source[];
  error?: string;
  pending?: boolean;
};

function Passages({ sources, answer }: { sources: Source[]; answer: string }) {
  const [all, setAll] = useState(false);
  const shown = all ? sources : sources.slice(0, 3);
  return (
    <div>
      <ol className="mt-4 space-y-7">
        {shown.map((s, i) => (
          <li key={i} className="border-s-2 border-line ps-4">
            <div className="mb-1.5 text-xs font-semibold text-muted">{s.title}</div>
            <p className="max-w-[68ch] text-[0.95rem] leading-[2.25]">
              {markEvidence(s.snippet, answer).map((piece, j) =>
                piece.evidence ? (
                  <span key={j} className="marker" style={{ animationDelay: `${i * 120 + j * 60}ms` }}>
                    {piece.text}
                  </span>
                ) : (
                  <span key={j} className="text-ink/50">
                    {" "}{piece.text}{" "}
                  </span>
                )
              )}
            </p>
          </li>
        ))}
      </ol>
      {sources.length > 3 && (
        <button onClick={() => setAll((v) => !v)} className="mt-5 text-sm text-muted hover:text-ink">
          {all ? "نمایش کمتر" : `نمایش ${fa(sources.length - 3)} منبع دیگر`}
        </button>
      )}
    </div>
  );
}

function TurnView({ turn, defaultOpen }: { turn: Turn; defaultOpen: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  const docs = new Set(turn.sources?.map((s) => s.doc_id)).size;

  return (
    <article className="py-8 first:pt-2">
      <h2 className="mb-5 text-[1.65rem] font-bold leading-[1.6] text-pretty">{turn.question}</h2>

      {turn.pending && (
        <div className="max-w-md space-y-3" role="status" aria-label="در حال جست‌وجو در اسناد">
          <div className="thinking-line w-full" />
          <div className="thinking-line w-5/6" style={{ animationDelay: "120ms" }} />
          <div className="thinking-line w-2/3" style={{ animationDelay: "240ms" }} />
        </div>
      )}

      {turn.error && (
        <div className="flex max-w-xl items-start gap-3 rounded-2xl border border-danger/40 px-4 py-3 text-danger">
          <AlertTriangle size={18} className="mt-1.5 shrink-0" />
          <p className="leading-8">{turn.error}</p>
        </div>
      )}

      {turn.answer && (
        <div className="answer">
          <Markdown>{turn.answer}</Markdown>
        </div>
      )}

      {!!turn.sources?.length && (
        <div className="mt-6">
          <button
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            className="flex items-center gap-1.5 text-sm font-semibold text-accent"
          >
            منبع‌ها: {fa(turn.sources.length)} بخش از {fa(docs)} سند
            <ChevronDown size={16} className={`transition-transform ${open ? "rotate-180" : ""}`} />
          </button>
          {open && <Passages sources={turn.sources} answer={turn.answer ?? ""} />}
        </div>
      )}
    </article>
  );
}

const SUGGESTIONS = [
  "خلاصه‌ی این سند چیه؟",
  "مهم‌ترین تعهدات و شرایط کدومه؟",
  "چه تاریخ‌ها و مبلغ‌هایی ذکر شده؟",
];

function Empty({
  hasDocs,
  offline,
  configured,
  onPick,
  onUpload,
}: {
  hasDocs: boolean;
  offline: boolean;
  configured: boolean;
  onPick: (q: string) => void;
  onUpload: () => void;
}) {
  return (
    <div className="flex min-h-full flex-col justify-center py-10">
      <h1 className="text-[clamp(2.6rem,7vw,4.9rem)] font-extrabold leading-[1.25] text-balance">
        از اسنادت بپرس.
      </h1>
      <p className="mt-6 max-w-[34ch] text-lg leading-9 text-muted text-pretty">
        فایل Word بده و سوالت رو بپرس. جواب فقط از متن همون فایل‌ها میاد و هر بخشی که ازش استفاده شده،{" "}
        <span className="marker text-ink">با ماژیک علامت می‌خوره.</span>
      </p>

      {offline ? (
        <div className="mt-10 max-w-md rounded-2xl border border-danger/40 px-4 py-3 text-sm leading-8 text-danger">
          سرور جواب نمی‌ده. بک‌اند باید روی <span dir="ltr" className="font-mono">{API_URL.replace(/\/api$/, "")}</span> اجرا باشه.
        </div>
      ) : !configured ? (
        <div className="mt-10 max-w-md rounded-2xl border border-danger/40 px-4 py-3 text-sm leading-8 text-danger">
          کلید <span dir="ltr" className="font-mono">OPENROUTER_API_KEY</span> تنظیم نشده. توی فایل <span dir="ltr" className="font-mono">.env</span> بذارش، یا با <span dir="ltr" className="font-mono">RAG_DEMO_MODE=True</span> بدون کلید امتحانش کن.
        </div>
      ) : hasDocs ? (
        <ul className="mt-10 space-y-1">
          {SUGGESTIONS.map((q) => (
            <li key={q}>
              <button
                onClick={() => onPick(q)}
                className="py-1.5 text-lg text-ink/80 underline decoration-line decoration-2 underline-offset-8 transition-colors hover:text-accent hover:decoration-accent"
              >
                {q}
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <button
          onClick={onUpload}
          className="mt-10 flex w-fit items-center gap-2 rounded-full bg-ink px-6 py-3.5 font-semibold text-paper transition-transform hover:scale-[1.03] active:scale-95"
        >
          <Plus size={18} />
          افزودن اولین سند
        </button>
      )}
    </div>
  );
}

export default function Thread({
  turns,
  hasDocs,
  offline,
  configured,
  onPick,
  onUpload,
}: {
  turns: Turn[];
  hasDocs: boolean;
  offline: boolean;
  configured: boolean;
  onPick: (q: string) => void;
  onUpload: () => void;
}) {
  if (!turns.length) {
    return <Empty hasDocs={hasDocs} offline={offline} configured={configured} onPick={onPick} onUpload={onUpload} />;
  }
  return (
    <div className="divide-y divide-line">
      {turns.map((t, i) => (
        <TurnView key={t.id} turn={t} defaultOpen={i === turns.length - 1} />
      ))}
    </div>
  );
}
