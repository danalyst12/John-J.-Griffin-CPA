# Griffin Business Assistant

The floating assistant is wired to a reusable website-crawling and retrieval backend. The static site alone cannot run a private AI service: deploy this folder as a Vercel project and configure the secrets below. Before deployment, the widget answers common questions from verified facts embedded in the page and offers phone/email for unknowns. Deploying the configured API, database, and secrets activates the live retrieval-based AI.

## One-time setup

1. Create a Supabase project and run [`supabase/schema.sql`](supabase/schema.sql) in its SQL editor.
2. Create a private OpenAI API key. Add it only in Vercel server environment variables; never put it in browser code.
3. Add the variables from [`.env.example`](.env.example) to the Vercel project. Generate different random values for `INGEST_SECRET` and `RATE_LIMIT_SECRET`.
4. Deploy `outputs/` as the Vercel project root. The `/api/chat` endpoint streams answers; `/api/ingest` is protected by `INGEST_SECRET`.
5. Re-index after publishing verified business updates from PowerShell:

   ```powershell
   $env:SITE_URL = "https://your-deployment.example"
   $env:INGEST_SECRET = "your-ingest-secret"
   npm run reindex
   ```

   The indexer follows only HTTPS links on the configured business website's own host, checks that site's `robots.txt`, limits pages, and stores URL, title, section, content type, and indexing date.

The indexer uses the configured official site as its source of truth. Add owner-verified FAQs, corrections, announcements, or policies to the `manualKnowledge` array in `business.config.json`; re-index to apply them. These entries are labeled as owner-verified in retrieval metadata and outrank website content when facts conflict. Add another business by replacing `business.config.json`, setting a distinct `BUSINESS_ID` and `BUSINESS_WEBSITE_URL`, and running ingestion again. The vector table can hold multiple business IDs.

## Operating notes

- API keys and the Supabase service-role key stay server-side.
- Chat turns are short-lived (`store: false` at the model provider); the app does not save conversation transcripts.
- Semantic retrieval returns a small number of matching website chunks, and the assistant is instructed to treat retrieved page text as untrusted data.
- Business answers cite retrieved source URLs when useful and state when facts such as hours or prices were not verified.
- Rate limiting is enforced through a database function using a keyed hash of the request network address; raw addresses are not stored.
- Keep secrets out of Git and the static client. Use HTTPS and review your AI/database provider retention settings before serving visitors.

This is an implementation scaffold, not a live connected AI service. It becomes operational when the private provider keys, Supabase schema, and deployment environment are configured.
