const url = process.env.SITE_URL;
const secret = process.env.INGEST_SECRET;
if (!url || !secret) throw new Error('Set SITE_URL and INGEST_SECRET before reindexing.');
const response = await fetch(new URL('/api/ingest', url), { method: 'POST', headers: { Authorization: `Bearer ${secret}` } });
const body = await response.json();
console.log(JSON.stringify(body, null, 2));
if (!response.ok) process.exitCode = 1;
