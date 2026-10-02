from urllib.request import Request, urlopen
from pathlib import Path
from PIL import Image
from io import BytesIO

photos = {
    'chicago-skyline.jpg': 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=2200&q=86',
    'accounting-workspace.jpg': 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1800&q=86',
    'construction-business.jpg': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1800&q=86',
    'chicago-buildings.jpg': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1800&q=86',
}
directory = Path('outputs/assets')
for filename, url in photos.items():
    request = Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; website-redesign/1.0)'})
    data = urlopen(request, timeout=30).read()
    image = Image.open(BytesIO(data))
    image.verify()
    (directory / filename).write_bytes(data)
    check = Image.open(directory / filename)
    print(filename, check.format, check.size, len(data))
