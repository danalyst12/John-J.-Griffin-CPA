from pathlib import Path
p=Path('outputs/api/ingest.js')
s=p.read_text(encoding='utf-8')
old="""      const rows = batch.map((doc, index) => ({ ...doc, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata: { url: doc.url, title: doc.title, section: doc.section, content_type: doc.content_type, last_indexed: doc.last_indexed, priority: doc.manual ? 'owner-verified' : 'website' } }));"""
new="""      const rows = batch.map((doc, index) => {
        const { manual, ...columns } = doc;
        return { ...columns, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata: { url: doc.url, title: doc.title, section: doc.section, content_type: doc.content_type, last_indexed: doc.last_indexed, priority: manual ? 'owner-verified' : 'website' } };
      });"""
assert old in s
p.write_text(s.replace(old,new),encoding='utf-8')

p=Path('outputs/api/chat.js')
s=p.read_text(encoding='utf-8').replace("${chunk.metadata.last_indexed || 'date unavailable'}]", "${chunk.metadata.last_indexed || 'date unavailable'} | ${chunk.metadata.priority || 'website'}]")
p.write_text(s,encoding='utf-8')

p=Path('outputs/supabase/schema.sql')
s=p.read_text(encoding='utf-8').replace("create index if not exists business_chunks_business_idx", "alter table public.business_chunks add column if not exists indexed_at timestamptz not null default now();\ncreate index if not exists business_chunks_business_idx")
p.write_text(s,encoding='utf-8')

p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
if '<p class="photo-credit">' not in s:
  s=s.replace('  <div class="assistant-widget">','  <p class="photo-credit">Chicago skyline photo by <a href="https://unsplash.com/photos/chicago-skyline-across-lake-michigan-xOj6_Ha1_R8" target="_blank" rel="noopener noreferrer">Jeff Brown on Unsplash</a>. Additional background photography is served from <a href="https://unsplash.com/license" target="_blank" rel="noopener noreferrer">Unsplash</a>.</p>\n  <div class="assistant-widget">',1)
s=s.replace("const rows = batch.map((doc, index) => ({ ...doc, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata:", "const rows = batch.map((doc, index) => ({ ...doc, business_id: business.id, indexed_at: ingestionStartedAt, embedding: vectors[index], metadata:")
p.write_text(s,encoding='utf-8')
print('Fixed manual-ingest columns and ensured the visible image-credit line is present.')
