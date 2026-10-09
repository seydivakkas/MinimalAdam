#!/usr/bin/env python3
"""P2: Türkçe yazıları çizimden ayrı, denetlenebilir katmana işler.

Üretilenler: .text.png (şeffaf), .png (birleşik), .labels.svg (metin katmanı)
ve .manifest.json (etiketler, font, SHA256, kontrol sonucu).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
import sys
import unicodedata
from xml.sax.saxutils import escape as xml_escape

from PIL import Image, ImageDraw, ImageFont

MAX_LABELS = 8
DESIGN_WIDTH = 1600
COLORS = {"black": "#171717", "red": "#d74b3c", "orange": "#ed8832", "blue": "#3a79ad"}
DEFAULT_FONT_PATHS = [
    "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/Library/Fonts/Arial Unicode.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"
]
TURKISH_GLYPHS = "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"


@dataclass(frozen=True)
class Label:
    text: str
    x: float
    y: float
    color: str
    size: int
    anchor: str


def get_font_path(custom=None):
    if custom:
        path = Path(custom).expanduser()
        if not path.is_file():
            raise ValueError(f"Yazı tipi dosyası bulunamadı: {path}")
        return path
    for candidate in DEFAULT_FONT_PATHS:
        if Path(candidate).is_file():
            return Path(candidate)
    raise ValueError("Türkçe glifleri olan font bulunamadı. --font ile bir TTF/OTF belirtin.")


def verify_glyphs(path: Path, texts: list[str]):
    """TrueType/OpenType cmap üzerinden kullanılan tüm harfleri doğrula."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError as e:
        raise RuntimeError("Font glif kontrolü için 'fonttools' gerekli (pip install fonttools).") from e
    f = TTFont(str(path))
    try:
        chars = set().union(*(set(t) for t in texts)) if texts else set()
        # Fontta boşluk ve kontrol karakterlerinin görünür glifi olmayabilir.
        cmap = set().union(*(set(c.cmap) for c in f['cmap'].tables if c.isUnicode()))
        missing = sorted(c for c in chars if (not c.isspace() and ord(c) not in cmap))
        if missing:
            raise ValueError(f"Fontta glifi bulunmayan karakter(ler): {''.join(missing)}")
    finally:
        f.close()


def parse_labels(spec: dict) -> list[Label]:
    if spec.get("version") != 1:
        raise ValueError("Etiket şeması 'version: 1' olmalı.")
    raw = spec.get("labels")
    if not isinstance(raw, list) or len(raw) > MAX_LABELS:
        raise ValueError(f"labels bir liste olmalı ve en fazla {MAX_LABELS} etiket içermeli.")
    result = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"{i}: etiket nesne olmalı.")
        val = item.get("text")
        if not isinstance(val, str) or not val.strip() or len(val) > 24 or "\n" in val:
            raise ValueError(f"{i}: metin 1-24 karakter uzunluğunda, tek satır olmalı.")
        if unicodedata.normalize("NFC", val) != val:
            raise ValueError(f"{i}: Unicode NFC biçimine dönüştürülmeli.")
        if any("\u3400" <= c <= "\u9fff" or c == "\ufffd" for c in val):
            raise ValueError(f"{i}: beklenmeyen Çince/bozuk Unicode karakteri.")
        x, y = item.get("x"), item.get("y")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1 for v in (x, y)):
            raise ValueError(f"{i}: x/y değerleri 0..1 aralığında olmalı.")
        color = item.get("color", "black")
        size = item.get("size", 35)
        anchor = item.get("anchor", "center")
        if color not in COLORS or anchor not in ("left", "center", "right") or not isinstance(size, int) or not 18 <= size <= 72:
            raise ValueError(f"{i}: geçersiz renk, hizalama veya font boyutu.")
        result.append(Label(val, float(x), float(y), color, size, anchor))
    return result


def intersects(a, b, padding=8):
    return not (a[2] + padding <= b[0] or b[2] + padding <= a[0] or
                a[3] + padding <= b[1] or b[3] + padding <= a[1])


def rectangles(labels, font_path, width, height):
    rects = []
    scaled = width / DESIGN_WIDTH
    pad = max(10, int(12 * scaled))
    for label in labels:
        size = max(1, round(label.size * scaled))
        font = ImageFont.truetype(str(font_path), size)
        # Bbox sabit anchor davranışı için gerçek piksel bbox'undan türetilir.
        b = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), label.text, font=font)
        ww, hh = b[2] - b[0], b[3] - b[1]
        xx, yy = round(label.x * width), round(label.y * height)
        left = xx - (ww if label.anchor == 'right' else ww // 2 if label.anchor == 'center' else 0)
        top = yy - hh // 2
        bounds = (left, top, left + ww, top + hh)
        if left < pad or top < pad or bounds[2] > width - pad or bounds[3] > height - pad:
            raise ValueError(f"Etiket kenardan taşıyor: {label.text!r}; kutu={bounds}")
        rects.append((bounds, font, (left - b[0], top - b[1])))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if intersects(rects[i][0], rects[j][0], padding=8):
                raise ValueError(f"Etiket çakışması: {labels[i].text!r} ve {labels[j].text!r}")
    return rects


def render(base_png: Path, spec_file: Path, output: Path, font_arg=None):
    if not base_png.is_file():
        raise ValueError(f"Temel görsel yok: {base_png}")
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    labels = parse_labels(spec)
    font_path = get_font_path(font_arg)
    verify_glyphs(font_path, [item.text for item in labels])
    with Image.open(base_png) as base_img:
        base = base_img.convert("RGBA")
    width, height = base.size
    if width * 9 != height * 16:
        raise ValueError(f"Temel görsel 16:9 olmalı, mevcut: {width}x{height}")
    rects = rectangles(labels, font_path, width, height)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for lab, (_, font, position) in zip(labels, rects):
        d.text(position, lab.text, font=font, fill=COLORS[lab.color])
    output.parent.mkdir(parents=True, exist_ok=True)
    overlay_path = output.with_name(output.stem + ".text.png")
    svg_path = output.with_name(output.stem + ".labels.svg")
    meta_path = output.with_name(output.stem + ".manifest.json")
    layer.save(overlay_path)
    Image.alpha_composite(base, layer).convert("RGB").save(output, optimize=True)
    # SVG yalnızca yazı katmanıdır; bitmap tabanın vektöre dönüştürüldüğü iddia edilmez.
    elements = []
    for lab, (box, _, _) in zip(labels, rects):
        style_anchor = {"left":"start", "center":"middle", "right":"end"}[lab.anchor]
        elements.append(f'<text x="{lab.x * width:.3f}" y="{lab.y * height:.3f}" '
                        f'font-family="sans-serif" font-size="{lab.size * width / DESIGN_WIDTH:.3f}" '
                        f'text-anchor="{style_anchor}" dominant-baseline="middle" '
                        f'fill="{COLORS[lab.color]}">{xml_escape(lab.text)}</text>')
    svg_path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">' + ''.join(elements) + '</svg>\n', encoding='utf-8')
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {"version": 1, "dimensions": [width, height], "font_file": font_path.name,
                "font_sha256": digest(font_path), "base_sha256": digest(base_png),
                "labels_sha256": digest(spec_file), "labels": [x.__dict__ for x in labels],
                "outputs": {"image": output.name, "text_png": overlay_path.name, "text_svg": svg_path.name},
                "qa": {"turkish_glyphs_present": True, "no_label_collisions": True, "no_clipping": True,
                       "visual_quality_not_automatically_verified": True}}
    meta_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    return {"image": output, "overlay": overlay_path, "svg": svg_path, "manifest": meta_path}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Yazısız 16:9 PNG")
    parser.add_argument("--labels", type=Path, required=True, help="UTF-8 etiket JSON")
    parser.add_argument("--output", type=Path, required=True, help="Çıktı PNG yolu")
    parser.add_argument("--font", help="Türkçe glifleri destekleyen TTF/OTF")
    args = parser.parse_args(argv)
    try:
        outputs = render(args.base, args.labels, args.output, args.font)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print("HATA:", error, file=sys.stderr)
        return 1
    for key, path in outputs.items():
        print(f"{key}: {path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
