from pathlib import Path
p=Path('outputs/api/chat.js')
s=p.read_text(encoding='utf-8')
anchor="const json = (res, status, body) => res.status(status).setHeader('Content-Type', 'application/json; charset=utf-8').send(JSON.stringify(body));\n"
func="""const json = (res, status, body) => res.status(status).setHeader('Content-Type', 'application/json; charset=utf-8').send(JSON.stringify(body));
function localSection(url = '') {
  const path = String(url).toLowerCase();
  if (/testimonial|review/.test(path)) return 'reviews';
  if (/about|bio|founder|owner/.test(path)) return 'john';
  if (/contact|location|map|direction/.test(path)) return 'location';
  if (/faq|question/.test(path)) return 'faq';
  if (/irs|notice|resolution/.test(path)) return 'irs';
  if (/service|account|tax|payroll|quickbooks|industry|incorporat/.test(path)) return 'services';
  return 'top';
}
"""
assert anchor in s
s=s.replace(anchor,func,1)
s=s.replace("`[Source ${i + 1}: ${chunk.metadata.title || 'Business page'} | ${chunk.metadata.url} | indexed ${chunk.metadata.last_indexed || 'date unavailable'} | ${chunk.metadata.priority || 'website'}]", "`[Source ${i + 1}: ${chunk.metadata.title || 'Business page'} | local link #${localSection(chunk.metadata.url)} | indexed ${chunk.metadata.last_indexed || 'date unavailable'} | ${chunk.metadata.priority || 'website'}]")
s=s.replace('When a source is useful, cite it with a short markdown link using the exact source URL.', 'When a source is useful, cite it with a short markdown link using the local link fragment supplied with that source. Never send a visitor to the original firm website.')
p.write_text(s,encoding='utf-8')

p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8').replace('<section class="faq">','<section class="faq" id="faq">',1)
p.write_text(s,encoding='utf-8')
print('Assistant citations now point to sections on the redesigned site.')
