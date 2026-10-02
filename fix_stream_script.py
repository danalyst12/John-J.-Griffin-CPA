from pathlib import Path
import re
p=Path('outputs/index.html')
s=p.read_text(encoding='utf-8')
s,n1=re.subn(r"buffer\.split\('\s*'\)", r"buffer.split('\\n\\n')", s, count=1)
s,n2=re.subn(r"frame\.split\('\s*'\)", r"frame.split('\\n')", s, count=1)
assert n1==1 and n2==1,(n1,n2)
p.write_text(s,encoding='utf-8')
print('Restored escaped newline delimiters in the assistant event-stream parser.')
