from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

assets = Path("outputs/assets")
logo = Image.open(assets / "logo-original.jpg").convert("RGB")
# The original wordmark is 267 × 60; its red JJG symbol occupies the first 60 px.
logo.crop((0, 0, 60, 60)).save(assets / "jjg-mark.png", optimize=True)

portrait = Image.open(assets / "john-griffin-original.jpg").convert("RGB")
portrait = ImageOps.autocontrast(portrait, cutoff=0.4)
portrait = ImageEnhance.Color(portrait).enhance(1.04)
portrait = ImageEnhance.Contrast(portrait).enhance(1.05)
portrait = portrait.resize((740, 916), Image.Resampling.LANCZOS)
portrait = portrait.filter(ImageFilter.UnsharpMask(radius=1.4, percent=105, threshold=3))
portrait.save(assets / "john-griffin-portrait.webp", "WEBP", quality=94, method=6)

print("Created local JJG mark and enhanced 4× portrait.")
