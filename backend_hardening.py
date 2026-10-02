from pathlib import Path
import re

config=Path('outputs/api/_lib/config.js')
config.write_text("""import { readFileSync } from 'node:fs';
import businessConfig from '../../business.config.json' assert { type: 'json' };

export function getBusiness() {
  return {
    ...businessConfig,
    id: process.env.BUSINESS_ID || businessConfig.id,
    websiteUrl: process.env.BUSINESS_WEBSITE_URL || businessConfig.websiteUrl,
  };
}

export function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing server configuration: ${name}`);
  return value;
}
""",encoding='utf-8')
# Node 22/Vercel supports import assertions, while Node 20 paths vary by patch version: load JSON directly.
config.write_text("""import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const configPath = fileURLToPath(new URL('../../business.config.json', import.meta.url));
const businessConfig = JSON.parse(readFileSync(configPath, 'utf8'));

export function getBusiness() {
  return {
    ...businessConfig,
    id: process.env.BUSINESS_ID || businessConfig.id,
    websiteUrl: process.env.BUSINESS_WEBSITE_URL || businessConfig.websiteUrl,
  };
}

export function requiredEnv(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing server configuration: ${name}`);
  return value;
}
""",encoding='utf-8')

p=Path('outputs/api/chat.js')
s=p.read_text(encoding='utf-8').replace("{ key_hash: clientKey, max_requests: 18, window_seconds: 60 }","{ request_key: clientKey, max_requests: 18, window_seconds: 60 }")
p.write_text(s,encoding='utf-8')

p=Path('outputs/supabase/schema.sql')
s=p.read_text(encoding='utf-8').replace('  last_indexed timestamptz not null default now()\n);','  last_indexed timestamptz not null default now(),\n  indexed_at timestamptz not null default now()\n);')
s=s.replace('function public.consume_chat_rate_limit(key_hash text, max_requests integer, window_seconds integer)','function public.consume_chat_rate_limit(request_key text, max_requests integer, window_seconds integer)')
s=s.replace('values (key_hash, now(), 1)','values (request_key, now(), 1)')
s=s.replace('where chat_rate_limits.key_hash = consume_chat_rate_limit.key_hash','where chat_rate_limits.key_hash = request_key')
s=s.replace('function public.consume_chat_rate_limit(text, integer, integer)','function public.consume_chat_rate_limit(text, integer, integer)')
p.write_text(s,encoding='utf-8')

p=Path('outputs/api/ingest.js')
s=p.read_text(encoding='utf-8')
s=s.replace("    const business = getBusiness();\n    const start = new URL(business.websiteUrl);", "    const business = getBusiness();\n    const ingestionStartedAt = new Date().toISOString();\n    const start = new URL(business.websiteUrl);")
s=s.replace("        const html = (await response.text()).slice(0, 2_500_000);", "        if (new URL(response.url).origin !== origin) continue;\n        const html = (await response.text()).slice(0, 2_500_000);")
s=s.replace("const rows = batch.map((doc, index) => ({ ...doc, business_id: business.id, embedding: vectors[index], metadata:", "const rows = batch.map((doc, index) => ({ ...doc, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata:")
s=s.replace("      if (error) throw error;\n    }\n    return res.status(200).json", "      if (error) throw error;\n    }\n    const { error: cleanupError } = await table.delete().eq('business_id', business.id).lt('indexed_at', ingestionStartedAt);\n    if (cleanupError) throw cleanupError;\n    return res.status(200).json")
p.write_text(s,encoding='utf-8')

p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
# Rebuild the footer close sequence and add source credits for the local photo assets.
start=s.index('  <footer class="footer">')
end=s.index('</footer>',start)+len('</footer>')
old=s[start:end]
social_match=re.search(r'<div class="footer-social".*?</div>',old,re.S)
social=social_match.group(0) if social_match else ''
footer='''  <footer class="footer"><div class="wrap footer-row"><a class="brand" href="#top" aria-label="Back to top"><span class="logo-crop"><img src="assets/jjg-mark.png" alt="" width="60" height="60"></span><span class="brand-name"><strong>John J. Griffin, CPA, P.C.</strong><small>Chicago · Illinois</small></span></a><span>© 2026 John Joseph Griffin, CPA, P.C.</span><div class="footer-links"><a href="https://www.clientportal.com/">Client portal</a><a href="https://portal.bizpayo.com/">Payments</a><a href="mailto:john@johngriffincpa.com">Contact</a></div>'''+social+'''</div></footer>'''
s=s[:start]+footer+s[end:]
if '<p class="photo-credit">' not in s:
    s=s.replace('  <div class="assistant-widget">','  <p class="photo-credit">Chicago skyline photo by <a href="https://unsplash.com/photos/chicago-skyline-across-lake-michigan-xOj6_Ha1_R8" target="_blank" rel="noopener noreferrer">Jeff Brown on Unsplash</a>. Additional background photography is served from <a href="https://unsplash.com/license" target="_blank" rel="noopener noreferrer">Unsplash</a>.</p>\n  <div class="assistant-widget">',1)
# Last-in-cascade photo settings override the earlier illustrative artwork.
overrides='''\n    .services-full{background:linear-gradient(90deg,#e6ede3f7 0%,#e6ede3ef 62%,#e6ede3a8 100%),url("assets/accounting-workspace.webp") right center/cover no-repeat}.industries{background:linear-gradient(90deg,#f4f5f1f5 0%,#f4f5f1ec 62%,#f4f5f180 100%),url("assets/construction-business.webp") center/cover no-repeat}.photo-credit{padding:0 16px 20px;background:#1a1d1b;color:#d1d9d2}\n'''
s=s.replace('.services-full{background:#e6ede3 url("assets/ledger-paper.svg") repeat;background-size:480px}', '.services-full{background:linear-gradient(90deg,#e6ede3f7 0%,#e6ede3ef 62%,#e6ede3a8 100%),url("assets/accounting-workspace.webp") right center/cover no-repeat}')
s=s.replace('.industries{background:linear-gradient(#f4f5f1e8,#f4f5f1e8),url("assets/ledger-stilllife.svg") right center/340px auto no-repeat}', '.industries{background:linear-gradient(90deg,#f4f5f1f5 0%,#f4f5f1ec 62%,#f4f5f180 100%),url("assets/construction-business.webp") center/cover no-repeat}')
s=s.replace('</style>',overrides+'</style>',1)
# Render only safe links from assistant markdown and keep external links constrained to HTTPS.
link_helper="""    function renderAssistantLinks(node,text){node.replaceChildren();const pattern=/\\[([^\\]]+)\\]\\((https:\\/\\/[^\\s)]+|mailto:[^\\s)]+|tel:[^\\s)]+|#[a-zA-Z0-9_-]+)\\)/g;let last=0,match;while((match=pattern.exec(text))){node.append(document.createTextNode(text.slice(last,match.index)));const link=document.createElement('a');link.textContent=match[1];link.href=match[2];if(/^https:\\/\\//i.test(match[2])){link.target='_blank';link.rel='noopener noreferrer'}node.append(link);last=pattern.lastIndex;}node.append(document.createTextNode(text.slice(last)));}\n"""
s=s.replace("    document.getElementById('assistant-form').addEventListener('submit'",link_helper+"    document.getElementById('assistant-form').addEventListener('submit'",1)
s=s.replace("reply.classList.remove('pending');assistantHistory.push({role:'assistant',content:answer});", "renderAssistantLinks(reply,answer);reply.classList.remove('pending');assistantHistory.push({role:'assistant',content:answer});")
p.write_text(s,encoding='utf-8')
print('Hardened origin/crawl cleanup, rate-limit arguments, assistant links, and footer markup.')
