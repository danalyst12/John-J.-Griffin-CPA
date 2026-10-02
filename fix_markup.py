from pathlib import Path
p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
s=s.replace('<header class="wrap nav"><a class="brand" href="#top" aria-label="Back to top">','<header class="wrap nav"><a class="brand" href="#top" aria-label="John Griffin CPA home">')
s=s.replace("'Show fewer reviews <span aria-hidden=\"true\">âˆ’</span>'", "'Show fewer reviews <span aria-hidden=\"true\">-</span>'")
s=s.replace('</iframe></div></div></div></section>', '</iframe></div></div></section>')
p.write_text(s,encoding='utf-8')
print('header label fixed; malformed minus removed; map section nesting corrected')
