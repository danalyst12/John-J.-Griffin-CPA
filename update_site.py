from pathlib import Path
import re

page = Path('outputs/index.html')
html = page.read_text(encoding='utf-8', errors='replace')

# Use a locally stored mark and render the wordmark as accessible text.
brand = '<a class="brand" href="#top" aria-label="John Griffin CPA home"><span class="logo-crop"><img src="assets/jjg-mark.png" alt="" width="60" height="60"></span><span class="brand-name"><strong>John J. Griffin, CPA, P.C.</strong><small>Chicago Â· Illinois</small></span></a>'
html, n = re.subn(r'<a class="brand"[^>]*>.*?</a>', brand, html, count=1, flags=re.S)
assert n == 1
footer_brand = '<a class="brand" href="#top" aria-label="Back to top"><span class="logo-crop"><img src="assets/jjg-mark.png" alt="" width="60" height="60"></span><span class="brand-name"><strong>John J. Griffin, CPA, P.C.</strong><small>Chicago Â· Illinois</small></span></a>'
html, n = re.subn(r'<a class="brand"[^>]*>.*?</a>', footer_brand, html, count=1, flags=re.S)
assert n == 1

# The main visual is an animated Chicago scene; the owner's portrait belongs beside the bio.
hero = '<div class="hero-art reveal delay2" aria-hidden="true"><img class="hero-scene" src="assets/chicago-evening.svg" alt=""><img class="ledger-scene" src="assets/ledger-stilllife.svg" alt=""><div class="hero-tag"><b>Independent. Local.</b><br>Here when a question comes up.</div></div>'
html, n = re.subn(r'<figure class="hero-art.*?</figure>', hero, html, count=1, flags=re.S)
assert n == 1
owner = '''<section class="owner" id="john"><div class="wrap owner-grid"><figure class="owner-visual photo-portrait reveal"><img src="assets/john-griffin-portrait.webp" alt="John Griffin at his desk" width="740" height="916" loading="lazy"><figcaption class="owner-caption">John Griffin, CPA</figcaption></figure><div class="reveal delay1"><div class="eyebrow">A real person on the other end</div><h2>Small firm. Direct answers.</h2><p class="owner-copy">Before accounting, John ran a landscaping business. He passed the CPA exam in 2001 and established this firm in 2010. Today, he gives local businesses and individuals personal, steady support through the year.</p><p class="owner-copy">He worked at two CPA firms before opening his practice. The firm serves construction, real estate, and technology businesses, as well as individuals.</p><div class="owner-sign">John Griffin, CPA</div></div></div></section>'''
html, n = re.subn(r'<section class="owner".*?</section>', owner, html, count=1, flags=re.S)
assert n == 1

reviews = [
 ('Shamrock B.', 'Described the service as timely, fairly priced, and free of problems.'),
 ('Christine M.', 'Said John prepared and corrected a personal return professionally and promptly.'),
 ('Francesca C.', 'Praised his warmth, availability for questions, and help with a complicated tax situation.'),
 ('Marjorie D.', 'Valued the thorough organizer, clear estimate, and availability through the year.'),
 ('Steven R.', 'Described diligent, discreet help working through sensitive IRS correspondence.'),
 ('Tricia A.', 'Praised knowledgeable, professional guidance during a complex tax matter.'),
 ('Cesar R.', 'Credited John with helping address IRS matters and errors on earlier returns.'),
 ('Tony F.', 'Described tax filing as efficient and professional.'),
 ('Joe B.', 'Valued business-focused help, an office visit, and follow-through.'),
 ('Richard L.', 'Praised quick, professional tax preparation.'),
 ('Melina F.', 'Highlighted accessibility, persistence with IRS correspondence, and fair fees.'),
 ('Andrew K.', 'Praised accurate, responsive tax service.'),
 ('Trista K.', 'Said John helped bring small-business finances up to date and stayed engaged.'),
 ('Maria C.', 'Praised quick replies and accurate, fairly priced tax preparation.'),
 ('Maritza C.', 'Valued clear communication and work completed sooner than expected.'),
]
def card(item, cls=''):
    who, summary = item
    return f'<article class="quote review-card reveal {cls}"><div><p>{summary}</p></div><footer>{who} <span>Â· Review summary</span></footer></article>'
proof = '<section class="proof"><div class="wrap"><div class="proof-top reveal"><div><div class="eyebrow">From clients</div><h2>People want someone who responds.</h2></div><div class="proof-rating"><strong>15 client reviews</strong>Summaries of the testimonials published by the firm</div></div><div class="quotes review-featured">' + card(reviews[0]) + card(reviews[1], 'delay1') + card(reviews[2], 'delay2') + '</div><div id="review-list" class="quotes review-list" hidden>' + ''.join(card(r) for r in reviews[3:]) + '</div><button class="review-toggle" id="reviews-toggle" type="button" aria-expanded="false" aria-controls="review-list">See all 15 reviews <span aria-hidden="true">ï¼‹</span></button><p class="proof-note">Reviewer initials and review summaries reflect the firmâ€™s published testimonials. The source page provides no review dates or links to original review platforms. Summaries are paraphrased.</p></div></section>'
html, n = re.subn(r'<section class="proof">.*?</section>', proof, html, count=1, flags=re.S)
assert n == 1

# A live, interactive map rather than the decorative map illustration.
html, n = re.subn(r'<div class="map-art.*?</div>', '<div class="map-frame reveal delay1"><iframe title="Map to John Griffin CPA at 5240-B West Irving Park Road, Chicago" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.google.com/maps?q=5240-B%20W%20Irving%20Park%20Rd%2C%20Chicago%2C%20IL%2060641&amp;output=embed"></iframe></div>', html, count=1, flags=re.S)
assert n == 1

# Older-site links are replaced with local content; client portal/payment and map services remain functional destinations.
html = html.replace('https://www.johngriffincpa.com/testimonials.htm', '#reviews')
html = html.replace('<section class="proof">', '<section class="proof" id="reviews">')
html = re.sub(r'<a href="#reviews">Firm testimonial page</a>\s*-\s*Date not shown there', 'Firm testimonial, date not shown', html)
html = html.replace('https://www.johngriffincpa.com/site_images/Logo.jpg', 'assets/jjg-mark.png')
html = html.replace('https://www.johngriffincpa.com/site_images/bio.jpg', 'assets/john-griffin-portrait.webp')

extra_css = '''
    .brand{gap:11px}.logo-crop{width:48px;height:48px;display:block;overflow:hidden;flex:0 0 48px;box-shadow:0 5px 15px #a63a2230;transition:transform .35s var(--ease)}.brand:hover .logo-crop{transform:rotate(-5deg) scale(1.06)}.logo-crop img{display:block;width:48px;height:48px;object-fit:cover}.brand-name strong{display:block;font:600 15px var(--serif);line-height:1.2}.brand-name small{display:block;font-size:10px;color:var(--muted);letter-spacing:.11em;text-transform:uppercase}.firm-logo,.brand strong:not(.brand-name strong),.brand small:not(.brand-name small){display:none}
    .hero{position:relative;background:#e9efe7 url("assets/chicago-evening.svg") center/cover no-repeat;isolation:isolate}.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#f4f5f1f2 0%,#f4f5f1d9 48%,#f4f5f180 100%);z-index:-1}.hero-grid{position:relative}.hero-art{height:480px}.hero-scene{position:absolute;inset:16px 0 0 20px;width:calc(100% - 20px);height:calc(100% - 16px);object-fit:cover;border-radius:44% 44% 3px 3px;box-shadow:0 22px 58px #223a2c25;animation:sceneDrift 24s ease-in-out infinite alternate}.ledger-scene{position:absolute;width:57%;height:auto;right:-2%;bottom:1%;filter:drop-shadow(0 20px 20px #1a1d1b30);animation:float 7s ease-in-out infinite}.hero-tag{z-index:2}.photo-portrait{margin:0;background:#d5e0d1;height:auto;min-height:390px;box-shadow:0 23px 50px #1a1d1b18}.photo-portrait img{display:block;width:100%;height:430px;object-fit:cover;object-position:center 28%;filter:contrast(1.04) saturate(1.04);transition:transform .8s var(--ease)}.photo-portrait:hover img{transform:scale(1.035)}.photo-portrait .owner-caption{position:relative;display:block}.services-full{background:#e6ede3 url("assets/ledger-paper.svg") repeat;background-size:480px}.industries{background:linear-gradient(#f4f5f1e8,#f4f5f1e8),url("assets/ledger-stilllife.svg") right center/340px auto no-repeat}.closing{background:linear-gradient(90deg,#173b2dF2,#1f4d3aD9),url("assets/chicago-evening.svg") center 58%/cover no-repeat}.map-frame{height:340px;overflow:hidden;background:#e6ede3;box-shadow:0 18px 44px #1a1d1b18}.map-frame iframe{width:100%;height:100%;border:0;filter:saturate(.82) contrast(1.02)}.review-list[hidden]{display:none}.review-toggle{margin-top:24px;border:1px solid var(--green);background:transparent;color:var(--green);padding:13px 18px;font-weight:700;cursor:pointer;transition:background .25s,color .25s,transform .25s}.review-toggle:hover{background:var(--green);color:#fff;transform:translateY(-2px)}.review-toggle span{padding-left:8px}.review-card{min-height:175px}.review-card p{font:500 16px/1.6 var(--serif);margin:0 0 20px}.review-card footer span{color:#777}.proof-note{max-width:780px}
    @keyframes sceneDrift{from{transform:scale(1.02) translate3d(-1%,0,0)}to{transform:scale(1.09) translate3d(1%,-1%,0)}}
    @media(max-width:800px){.hero{background-position:61% center}.hero-art{height:390px}.hero-scene{inset:12px 0 0 8px;width:calc(100% - 8px)}.owner-grid{gap:34px}.photo-portrait img{height:390px}.map-frame{height:300px}}
    @media(max-width:600px){.hero:before{background:linear-gradient(90deg,#f4f5f1ed,#f4f5f1cc)}.hero-art{height:350px}.hero-tag{left:-1px}.ledger-scene{width:62%}.owner-grid{grid-template-columns:1fr;gap:34px}.photo-portrait{max-width:390px}.photo-portrait img{height:390px}.review-featured,.review-list{grid-template-columns:1fr}.review-card{min-height:150px}.map-frame{height:260px}.brand-name strong{font-size:13px}}
    @media(prefers-reduced-motion:reduce){.hero-scene,.ledger-scene,.photo-portrait img{animation:none;transition:none}.brand:hover .logo-crop{transform:none}}
'''
html = html.replace('</style>', extra_css + '\n  </style>', 1)

toggle_js = '''
    const reviewToggle = document.getElementById('reviews-toggle');
    const reviewList = document.getElementById('review-list');
    reviewToggle.addEventListener('click', () => {
      const expanded = reviewToggle.getAttribute('aria-expanded') === 'true';
      reviewToggle.setAttribute('aria-expanded', String(!expanded));
      reviewList.hidden = expanded;
      reviewToggle.innerHTML = expanded ? 'See all 15 reviews <span aria-hidden="true">ï¼‹</span>' : 'Show fewer reviews <span aria-hidden="true">âˆ’</span>';
      if (!expanded) reviewList.querySelectorAll('.reveal').forEach(card => card.classList.add('visible'));
    });
'''
html = html.replace("    const items = document.querySelectorAll('.reveal');", toggle_js + "\n    const items = document.querySelectorAll('.reveal');", 1)

# Replace known mojibake caused by an earlier Windows terminal edit, and clean accidental replacement glyphs.
for bad, good in [('Ã¢Å“Â³', '*'), ('Ã¢â€ â€”', 'â†’'), ('Ã¢â€ â€™', 'â†’'), ('Ã¢â‚¬â„¢', 'â€™'), ('Ã¢â‚¬â€', 'â€”'), ('Ã‚Â·', 'Â·'), ('Ã‚Â©', 'Â©'), ('ï¿½', '')]:
    html = html.replace(bad, good)
page.write_text(html, encoding='utf-8')
print('Updated', page, 'bytes', len(html.encode('utf-8')))
print('Old firm-site URL references:', html.count('johngriffincpa.com'))

