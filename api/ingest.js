import { createHash, timingSafeEqual } from 'node:crypto';
import * as cheerio from 'cheerio';
import robotsParser from 'robots-parser';
import { getBusiness, requiredEnv } from './_lib/config.js';
import { db } from './_lib/db.js';
import { embed } from './_lib/openai.js';

const hash = (value) => createHash('sha256').update(value).digest('hex');
const sameSecret = (provided, expected) => {
  const a = Buffer.from(provided || ''); const b = Buffer.from(expected || '');
  return a.length === b.length && timingSafeEqual(a, b);
};
const canonical = (raw, origin) => {
  try { const u = new URL(raw, origin); if (u.protocol !== 'https:' || u.origin !== origin) return null; u.hash = ''; u.search = ''; u.pathname = u.pathname.replace(/index\.html?$/i, ''); return u.href.replace(/\/$/, '') || origin; } catch { return null; }
};
function extractChunks(html, url, now) {
  const $ = cheerio.load(html);
  $('script,style,nav,header,footer,aside,noscript,svg,form,[aria-hidden="true"]').remove();
  const title = $('title').first().text().trim() || $('h1').first().text().trim() || url;
  const root = $('main').length ? $('main').first() : $('article').length ? $('article').first() : $('body');
  const pieces = [];
  let section = title;
  root.find('h1,h2,h3,p,li,dt,dd').each((_, element) => {
    const text = $(element).text().replace(/\s+/g, ' ').trim();
    if (!text) return;
    if (/^h[1-3]$/i.test(element.tagName)) section = text;
    else pieces.push({ section, text });
  });
  let chunks = [];
  let current = '';
  let currentSection = title;
  for (const piece of pieces) {
    if (current && (piece.section !== currentSection || current.length + piece.text.length > 1250)) {
      chunks.push({ section: currentSection, content: current.trim() }); current = '';
    }
    currentSection = piece.section;
    current += `${piece.text}\n`;
  }
  if (current.trim()) chunks.push({ section: currentSection, content: current.trim() });
  return chunks.map((chunk, index) => ({
    id: hash(`${url}#${index}`),
    url,
    title,
    section: chunk.section,
    content_type: 'website',
    content: chunk.content,
    last_indexed: now,
  }));
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Use POST.' });
  const expected = requiredEnv('INGEST_SECRET');
  if (!sameSecret(req.headers.authorization?.replace(/^Bearer\s+/i, ''), expected)) return res.status(401).json({ error: 'Unauthorized.' });
  try {
    const business = getBusiness();
    const ingestionStartedAt = new Date().toISOString();
    const start = new URL(business.websiteUrl);
    if (start.protocol !== 'https:') return res.status(400).json({ error: 'The configured website must use HTTPS.' });
    const origin = start.origin;
    const agent = 'GriffinBusinessAssistantIndexer/1.0';
    const robotsResponse = await fetch(new URL('/robots.txt', origin), { headers: { 'User-Agent': agent }, signal: AbortSignal.timeout(10000) });
    const robotsText = robotsResponse.ok ? await robotsResponse.text() : '';
    const robots = robotsParser(new URL('/robots.txt', origin).href, robotsText);
    const sitemapUrls = [...robotsText.matchAll(/Sitemap:\s*(\S+)/gi)].map((m) => m[1]);
    const queue = [canonical(start.href, origin)];
    for (const mapUrl of sitemapUrls.slice(0, 3)) {
      try {
        const map = await fetch(mapUrl, { headers: { 'User-Agent': agent }, signal: AbortSignal.timeout(10000) });
        if (map.ok) for (const match of (await map.text()).matchAll(/<loc>(.*?)<\/loc>/gi)) {
          const candidate = canonical(match[1].trim(), origin); if (candidate) queue.push(candidate);
        }
      } catch { /* Keep the homepage/link crawl available if a sitemap fails. */ }
    }
    const visited = new Set();
    const docs = [];
    const maxPages = Math.max(1, Math.min(Number(process.env.MAX_CRAWL_PAGES || 40), 80));
    while (queue.length && visited.size < maxPages) {
      const url = queue.shift();
      if (!url || visited.has(url)) continue;
      visited.add(url);
      if (!robots.isAllowed(url, agent) || /\.(?:pdf|jpg|jpeg|png|gif|zip|xml)$/i.test(url)) continue;
      try {
        const response = await fetch(url, { headers: { 'User-Agent': agent, Accept: 'text/html' }, signal: AbortSignal.timeout(12000), redirect: 'follow' });
        if (!response.ok || !response.headers.get('content-type')?.includes('text/html')) continue;
        if (new URL(response.url).origin !== origin) continue;
        const html = (await response.text()).slice(0, 2_500_000);
        const $ = cheerio.load(html);
        $('a[href]').each((_, anchor) => { const link = canonical($(anchor).attr('href'), origin); if (link && !visited.has(link)) queue.push(link); });
        docs.push(...extractChunks(html, url, new Date().toISOString()));
      } catch (error) { console.warn('crawl page skipped', url, error?.message || 'fetch error'); }
    }
    for (const item of (business.manualKnowledge || [])) {
      if (!item || typeof item.text !== 'string' || !item.text.trim()) continue;
      const updated = item.updatedAt || new Date().toISOString();
      const url = `${business.websiteUrl.replace(/\/$/, '')}#manual-${encodeURIComponent(item.id || hash(item.section || item.text).slice(0, 12))}`;
      docs.push({ id: hash(`${business.id}:${item.id || url}`), url, title: item.title || 'Owner-verified business information', section: item.section || 'Manually maintained facts', content_type: 'manual', content: item.text.trim().slice(0, 6000), last_indexed: updated, manual: true });
    }
    if (!docs.length) return res.status(422).json({ error: 'No readable pages or manual facts were found. Check the URL and robots.txt.' });
    const table = db().from('business_chunks');
    for (let offset = 0; offset < docs.length; offset += 64) {
      const batch = docs.slice(offset, offset + 64);
      const vectors = await embed(batch.map((doc) => `${doc.title}\n${doc.section}\n${doc.content}`));
      const rows = batch.map((doc, index) => {
        const { manual, ...columns } = doc;
        return { ...columns, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata: { url: doc.url, title: doc.title, section: doc.section, content_type: doc.content_type, last_indexed: doc.last_indexed, priority: manual ? 'owner-verified' : 'website' } };
      });
      const { error } = await table.upsert(rows, { onConflict: 'id' });
      if (error) throw error;
    }
    const { error: cleanupError } = await table.delete().eq('business_id', business.id).lt('indexed_at', ingestionStartedAt);
    if (cleanupError) throw cleanupError;
    return res.status(200).json({ status: 'indexed', businessId: business.id, pagesCrawled: visited.size, chunksStored: docs.length, indexedAt: new Date().toISOString() });
  } catch (error) {
    console.error('knowledge ingest failed', error?.message || 'unknown error');
    return res.status(503).json({ error: 'Indexing could not complete. Check server logs and configuration.' });
  }
}
