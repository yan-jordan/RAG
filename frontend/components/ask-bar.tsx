"use client";

import { ArrowUp, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { fa } from "@/lib/format";

export default function AskBar({
  busy,
  scopeCount,
  clearScope,
  onAsk,
  seed,
}: {
  busy: boolean;
  scopeCount: number;
  clearScope: () => void;
  onAsk: (q: string) => void;
  seed: { text: string; n: number };
}) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  // a suggestion was picked: take its text during render, then move focus
  const [seenSeed, setSeenSeed] = useState(seed.n);
  if (seed.n !== seenSeed) {
    setSeenSeed(seed.n);
    setValue(seed.text);
  }
  useEffect(() => {
    if (seed.n) ref.current?.focus();
  }, [seed.n]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [value]);

  const valid = value.trim().length >= 3 && !busy;
  const submit = () => {
    if (!valid) return;
    onAsk(value.trim());
    setValue("");
  };

  return (
    <div className="px-4 pb-4 pt-2 sm:px-8">
      <div className="mx-auto max-w-3xl">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit();
          }}
          className="flex items-end gap-2 rounded-[28px] border border-line bg-surface p-2 ps-5 shadow-[0_8px_30px_-12px_rgba(18,20,43,0.25)] transition-colors focus-within:border-accent"
        >
          <textarea
            ref={ref}
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault();
                submit();
              }
            }}
            placeholder="یه سوال از اسنادت بپرس…"
            aria-label="سوال"
            className="max-h-[180px] min-h-11 flex-1 resize-none bg-transparent py-2.5 text-base leading-7 outline-none! placeholder:text-muted"
          />
          <button
            type="submit"
            disabled={!valid}
            aria-label="ارسال سوال"
            className="grid size-11 shrink-0 place-items-center rounded-full bg-accent text-on-accent transition-[transform,opacity] hover:scale-105 active:scale-95 disabled:scale-100 disabled:opacity-30"
          >
            <ArrowUp size={20} strokeWidth={2.4} />
          </button>
        </form>
        <div className="mt-2 flex items-center justify-between gap-3 px-3 text-xs text-muted">
          {scopeCount > 0 ? (
            <button onClick={clearScope} className="flex items-center gap-1 rounded-full bg-line/70 px-2.5 py-1 hover:text-ink">
              فقط از {fa(scopeCount)} سند انتخاب‌شده
              <X size={12} />
            </button>
          ) : (
            <span>از همه‌ی اسناد</span>
          )}
          <span className="hidden sm:inline">Enter برای ارسال، Shift+Enter برای خط بعد</span>
        </div>
      </div>
    </div>
  );
}
