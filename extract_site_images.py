from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

pages = [
    "https://www.johngriffincpa.com/index.htm",
    "https://www.johngriffincpa.com/about-us.htm",
    "https://www.johngriffincpa.com/small-business-accounting-services.htm",
    "https://www.johngriffincpa.com/income-tax-preparation-services.htm",
    "https://www.johngriffincpa.com/tax-planning-services.htm",
    "https://www.johngriffincpa.com/industries-we-serve.htm",
]

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img" and attrs.get("src"):
            self.items.append((attrs.get("alt", ""), attrs["src"]))

for page in pages:
    try:
        req = Request(page, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req, timeout=20).read().decode("utf-8", "replace")
        parser = Images()
        parser.feed(html)
        print("PAGE", page)
        for alt, src in parser.items:
            print("IMAGE", alt, urljoin(page, src))
    except Exception as exc:
        print("ERROR", page, str(exc))
