from pathlib import Path
import re
p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8', errors='replace')
# Replace footer brand markup with the same clean local mark and HTML wordmark.
s,n=re.subn(r'<footer class="footer">.*?</footer>', lambda m: re.sub(r'<a class="brand"[^>]*>.*?</a>', '<a class="brand" href="#top" aria-label="Back to top"><span class="logo-crop"><img src="assets/jjg-mark.png" alt="" width="60" height="60"></span><span class="brand-name"><strong>John J. Griffin, CPA, P.C.</strong><small>Chicago - Illinois</small></span></a>', m.group(0), count=1, flags=re.S), s, count=1, flags=re.S)
assert n==1
# Remove the trailing remnants of the former illustrated map.
s=re.sub(r'(</iframe></div>)<div class="street v"></div>.*?<div class="map-caption">.*?</div>', r'\1', s, count=1, flags=re.S)
# Keep the expansion control plain and readable even in restricted encodings.
s=re.sub(r'>See all 15 reviews <span[^>]*>.*?</span>', '>See all 15 reviews <span aria-hidden="true">+</span>', s, count=1)
s=s.replace('>Show fewer reviews <span aria-hidden="true">−</span>', '>Show fewer reviews <span aria-hidden="true">-</span>')
# Repair common mojibake remnants from the original Windows edit.
for a,b in [('Â·','-'),('â€™',"'"),('â€”','-'),('â†—','->'),('â†’','->'),('ï¼‹','+'),('ï¼','')]: s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
print('old firm website href/src:', len(re.findall(r'(?:href|src)="https?://(?:www\\.)?johngriffincpa\\.com',s)))
print('testimonial cards:', len(re.findall(r'class="quote review-card',s)))
print('map frames:', s.count('<iframe title="Map to John Griffin'))
