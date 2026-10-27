# پرسند · frontend

Next.js (App Router) + Tailwind CSS v4. A single-page, RTL, Persian interface for the Django RAG API.

```bash
cp .env.example .env.local   # point NEXT_PUBLIC_API_URL at the API
npm install
npm run dev                  # http://localhost:3000
```

| Path | What lives there |
| --- | --- |
| `app/globals.css` | design tokens (light/dark), the highlighter-pen `.marker`, answer typography |
| `components/app-shell.tsx` | all state: documents, history, thread, scope, toasts |
| `components/thread.tsx` | question/answer turns, evidence passages |
| `components/rail.tsx` | documents + history side panel (bottom sheet on mobile) |
| `lib/evidence.ts` | decides which sentences of a retrieved passage the answer actually used |
| `lib/api.ts` | typed API client |
