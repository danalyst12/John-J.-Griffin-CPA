from pathlib import Path
import re

p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('.services-full{background:#e6ede3 url("assets/ledger-paper.svg") repeat;background-size:480px}', '.services-full{background:linear-gradient(90deg,#e6ede3f7 0%,#e6ede3ef 62%,#e6ede3a8 100%),url("assets/accounting-workspace.jpg") right center/cover no-repeat}')
s=s.replace('.industries{background:linear-gradient(#f4f5f1e8,#f4f5f1e8),url("assets/ledger-stilllife.svg") right center/340px auto no-repeat}', '.industries{background:linear-gradient(90deg,#f4f5f1f5 0%,#f4f5f1ec 62%,#f4f5f180 100%),url("assets/construction-business.jpg") center/cover no-repeat}')
s=s.replace('</div></div></div></footer>\n  <div class="assistant-widget">','</div></div></footer>\n  <p class="photo-credit">Chicago skyline photo by <a href="https://unsplash.com/photos/chicago-skyline-across-lake-michigan-xOj6_Ha1_R8" target="_blank" rel="noopener noreferrer">Jeff Brown on Unsplash</a>. Additional background photography is served from <a href="https://unsplash.com/license" target="_blank" rel="noopener noreferrer">Unsplash</a>.</p>\n  <div class="assistant-widget">')
s=s.replace("quote:'wanted to meet us on our turf, in our business, so that he could better serve us.'", "quote:'wanted to meet us on our turf, in our business.'")
p.write_text(s,encoding='utf-8')

# Add a simple, explicitly maintained owner knowledge area for facts that are not on the site.
config=Path('outputs/business.config.json')
import json
business=json.loads(config.read_text(encoding='utf-8'))
business['manualKnowledge']=[]
config.write_text(json.dumps(business,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

ingest=Path('outputs/api/ingest.js')
code=ingest.read_text(encoding='utf-8')
anchor="    if (!docs.length) return res.status(422).json({ error: 'No readable pages were found. Check the URL and robots.txt.' });"
replacement="""    for (const item of (business.manualKnowledge || [])) {
      if (!item || typeof item.text !== 'string' || !item.text.trim()) continue;
      const updated = item.updatedAt || new Date().toISOString();
      const url = `${business.websiteUrl.replace(/\\/$/, '')}#manual-${encodeURIComponent(item.id || hash(item.section || item.text).slice(0, 12))}`;
      docs.push({ id: hash(`${business.id}:${item.id || url}`), url, title: item.title || 'Owner-verified business information', section: item.section || 'Manually maintained facts', content_type: 'manual', content: item.text.trim().slice(0, 6000), last_indexed: updated, manual: true });
    }
    if (!docs.length) return res.status(422).json({ error: 'No readable pages or manual facts were found. Check the URL and robots.txt.' });"""
assert anchor in code
code=code.replace(anchor,replacement)
code=code.replace("metadata: { url: doc.url, title: doc.title, section: doc.section, content_type: doc.content_type, last_indexed: doc.last_indexed }", "metadata: { url: doc.url, title: doc.title, section: doc.section, content_type: doc.content_type, last_indexed: doc.last_indexed, priority: doc.manual ? 'owner-verified' : 'website' }")
ingest.write_text(code,encoding='utf-8')

guide=Path('outputs/ASSISTANT-SETUP.md')
text=guide.read_text(encoding='utf-8')
text=text.replace('The indexer uses the configured official site as its source of truth. Add another business by replacing `business.config.json`, setting a distinct `BUSINESS_ID` and `BUSINESS_WEBSITE_URL`, and running ingestion again. The vector table can hold multiple business IDs.', 'The indexer uses the configured official site as its source of truth. Add owner-verified FAQs, corrections, announcements, or policies to the `manualKnowledge` array in `business.config.json`; re-index to apply them. These entries are labeled as owner-verified in retrieval metadata. Add another business by replacing `business.config.json`, setting a distinct `BUSINESS_ID` and `BUSINESS_WEBSITE_URL`, and running ingestion again. The vector table can hold multiple business IDs.')
guide.write_text(text,encoding='utf-8')
print('Added photographic overrides, local photo credits, and owner-maintained knowledge support.')
