# AI Trust Validator Frontend

Next.js 14 frontend for the AI Trust Validator platform.

## Development

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Variables

Copy `.env.local` and update the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages

- `/submit` — Submit an agent for validation (URL or file upload)
- `/validating/[id]` — Real-time validation progress with step tracker
- `/results/[id]` — Full results dashboard (Overview, Defects, Corrections, Evidence, AI Insights)
- `/history` — Paginated validation history

## Build

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t ai-trust-validator-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api:8000 ai-trust-validator-frontend
```
