from pathlib import Path
p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
mark='<div class="assistant-widget">'
credit='''  <p class="photo-credit">Chicago skyline photo by <a href="https://unsplash.com/photos/chicago-skyline-across-lake-michigan-xOj6_Ha1_R8" target="_blank" rel="noopener noreferrer">Jeff Brown on Unsplash</a>. Additional background photography is served from <a href="https://unsplash.com/license" target="_blank" rel="noopener noreferrer">Unsplash</a>.</p>\n'''
assert mark in s
if '<p class="photo-credit">' not in s:
    s=s.replace(mark,credit+mark,1)
p.write_text(s,encoding='utf-8')
print('Photo attribution placed in the page footer.')
