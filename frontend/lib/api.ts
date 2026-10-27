export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export type Status = {
  configured: boolean;
  demo_mode: boolean;
  chat_model: string;
  embedding_model: string;
  max_upload_mb: number;
  documents: { total: number; ready: number; failed: number };
  questions: number;
};

export type Doc = {
  id: number;
  title: string;
  size: number | null;
  uploaded_at: string;
  status: "ready" | "failed";
  error_message: string;
  text_length: number;
  preview: string;
};

export type Source = { doc_id: number; title: string; snippet: string };

export type HistoryItem = {
  id: number;
  question: string;
  answer: string;
  sources: Source[];
  created_at: string;
};

export type AskResult = {
  history_id: number | null;
  question: string;
  answer: string;
  sources: Source[];
  created_at: string | null;
};

export class ApiError extends Error {
  constructor(message: string, public status = 0, public code?: string) {
    super(message);
  }
}

function messageFrom(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const b = body as Record<string, unknown>;
  if (typeof b.detail === "string") return b.detail;
  for (const value of Object.values(b)) {
    const first = Array.isArray(value) ? value[0] : value;
    if (typeof first === "string") return first;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError("اتصال به سرور برقرار نشد. مطمئن شو بک‌اند روشنه.");
  }
  if (res.status === 204) return undefined as T;
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(messageFrom(body) ?? `خطای ${res.status}`, res.status, (body as { code?: string })?.code);
  }
  return body as T;
}

const json = (data: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(data),
});

export const api = {
  status: () => request<Status>("/status/"),
  documents: () => request<Doc[]>("/documents/"),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    // Django sanitises uploaded file names (it drops the Persian half-space), so send the title ourselves.
    form.append("title", file.name.replace(/\.docx$/i, ""));
    return request<Doc>("/documents/", { method: "POST", body: form });
  },
  deleteDocument: (id: number) => request<void>(`/documents/${id}/`, { method: "DELETE" }),
  history: () => request<{ results: HistoryItem[] }>("/history/?page_size=60").then((r) => r.results),
  deleteHistory: (id: number) => request<void>(`/history/${id}/`, { method: "DELETE" }),
  clearHistory: () => request<{ deleted: number }>("/history/clear/", { method: "DELETE" }),
  ask: (question: string, documentIds: number[]) =>
    request<AskResult>("/ask/", json({ question, document_ids: documentIds })),
};
