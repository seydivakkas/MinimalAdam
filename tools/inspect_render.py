#!/usr/bin/env python3
"""P5 raster-only QA: reproducible pixel heuristics, NOT text OCR or aesthetic judgment.

Reads local PNG; never uploads data, fetches fonts, or makes network requests.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image, UnidentifiedImageError

EXPECTED = (1600, 900)
PALETTE = ((29, 33, 38), (238, 135, 51), (200, 78, 60), (63, 126, 175))
MAX_BYTES = 32 * 1024 * 1024


def inspect_png(path: Path) -> dict:
    path=Path(path)
    issues=[]
    def add(code, level, message): issues.append(dict(code=code, severity=level, message=message))
    if not path.is_file():
        return dict(version='p5-png-v1', file=path.name, summary=dict(status='FAIL', errors=1, warnings=0), issues=[dict(code='PNG_MISSING',severity='error',message='PNG dosyası bulunamadı')])
    if path.stat().st_size > MAX_BYTES:
        return dict(version='p5-png-v1', file=path.name, summary=dict(status='FAIL',errors=1,warnings=0),issues=[dict(code='PNG_TOO_BIG',severity='error',message='32 MiB üzerindeki dosyalar işlenmez')])
    try:
        with Image.open(path) as opened:
            if opened.format!='PNG':add('PNG_FORMAT','error','Dosya gerçekten PNG biçiminde değil')
            if opened.size!=EXPECTED:add('PNG_DIMENSIONS','error',f'Çözünürlük {opened.size}; beklenen {EXPECTED}')
            if opened.width*opened.height>6_000_000:
                add('PNG_PIXEL_LIMIT','error','Çok büyük PNG piksel sınırını aşıyor (6 milyon)')
                return dict(version='p5-png-v1',file=path.name,summary=dict(status='FAIL',errors=len([i for i in issues if i['severity']=='error']),warnings=0),issues=issues)
            # Pixel scan on a fixed 4px grid to cap resource consumption; alpha composited on white.
            im=opened.convert('RGBA')
            sample=im.crop((0,0,im.width,im.height)).resize((max(1,im.width//4),max(1,im.height//4)),resample=Image.Resampling.NEAREST)
            raw=sample.tobytes(); px=[tuple(raw[i:i+4]) for i in range(0,len(raw),4)]; sw,sh=sample.size
    except (OSError,UnidentifiedImageError,ValueError) as exc:
        return dict(version='p5-png-v1',file=path.name,summary=dict(status='FAIL',errors=1,warnings=0),issues=[dict(code='PNG_DECODE',severity='error',message=f'PNG okunamıyor: {exc}')])
    total=len(px);white=0;dark=0;accent=0;offpalette=0;nonwhite=[]; corners=0;corner_total=0
    for idx,(r,g,b,a) in enumerate(px):
        if a<255:
            r=(r*a+255*(255-a))//255;g=(g*a+255*(255-a))//255;b=(b*a+255*(255-a))//255
        bright=min(r,g,b)>=245
        if bright:white+=1
        else:nonwhite.append((idx%sw,idx//sw))
        if max(r,g,b)<120:dark+=1
        saturation=max(r,g,b)-min(r,g,b)
        if saturation>40 and not bright:
            accent+=1
            def palette_error(c):
                # Best alpha composite between white and each permitted pigment.
                v=[255-c[0],255-c[1],255-c[2]];target=[255-r,255-g,255-b]
                den=sum(q*q for q in v);alpha=max(0,min(1,sum(v[i]*target[i] for i in range(3))/den)) if den else 0
                return sum((target[i]-alpha*v[i])**2 for i in range(3))
            if min(palette_error(c) for c in PALETTE)>48**2:offpalette+=1
        x,y=idx%sw,idx//sw
        if ((x<sw*.065 or x>sw*.935) and (y<sh*.1 or y>sh*.9)):
            corner_total+=1
            if bright:corners+=1
    blank=white/total if total else 0
    wrong=offpalette/accent if accent else 0
    if blank<0.35:add('PNG_DENSE','warning',f'Beyaz alan oranı %{blank*100:.1f}, hedef en az %35')
    if corner_total and corners/corner_total <.9:add('PNG_CORNERS','warning','Köşe örneklerinde temiz beyaz zemin oranı düşük')
    if accent and wrong>.10:add('PNG_PALETTE','warning',f'Doygun renkli piksellerin %{wrong*100:.1f} kısmı izin verilen palete yakın değil')
    if not nonwhite:add('PNG_EMPTY','error','Tuval tamamen boş veya çok soluk; görünür çizim bulunamadı')
    if nonwhite:
        minx=min(x for x,y in nonwhite);maxx=max(x for x,y in nonwhite)
        miny=min(y for x,y in nonwhite);maxy=max(y for x,y in nonwhite)
        coverage=(maxx-minx+1)*(maxy-miny+1)/total
    else:coverage=0
    errors=sum(i['severity']=='error' for i in issues)
    warnings=sum(i['severity']=='warning' for i in issues)
    return dict(version='p5-png-v1',file=path.name,metrics=dict(size=[im.width,im.height],blankFraction=round(blank,5),darkPixelFraction=round(dark/total,5),accentPixelFraction=round(accent/total,5),offPaletteAccentFraction=round(wrong,5),inkBoundingBoxFraction=round(coverage,5),sampleCount=total),
                summary=dict(status='FAIL' if errors else 'REVIEW' if warnings else 'PASS',errors=errors,warnings=warnings),issues=issues,
                limitations=['Altörnekleme nedeniyle piksel yüzdeleri yaklaşıktır.','OCR, yazı doğruluğu, anlam, özgünlük ve karakterin gerçekten çalışması kontrol edilmez.'])


def main():
    p=argparse.ArgumentParser(description='Çevrimdışı PNG kalite ölçümü (P5)')
    p.add_argument('png',type=Path);p.add_argument('--report',type=Path)
    args=p.parse_args();result=inspect_png(args.png)
    payload=json.dumps(result,ensure_ascii=False,indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(payload+'\n',encoding='utf-8')
    print(payload)
    return 2 if result['summary']['status']=='FAIL' else 0

if __name__=='__main__':raise SystemExit(main())
