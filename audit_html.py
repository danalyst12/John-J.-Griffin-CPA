from pathlib import Path
s=Path('outputs/index.html').read_text(encoding='utf-8')
print('photo markup', '<p class="photo-credit">' in s)
print('codepoint sentinels', *(f'{x:x}:{chr(x) in s}' for x in [0xc2,0xe2,0x2020,0xfffd]))
start=s.index('<footer class="footer">')
end=s.index('</footer>',start)
print('footer div closures',s[start:end].count('</div>'))
print('assistant widget offset',s.find('<div class="assistant-widget">'))
print('photo text exists','Chicago skyline photo by' in s)
