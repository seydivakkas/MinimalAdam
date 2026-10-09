#!/usr/bin/env python3
"""P3: Türkçe, kaynak tanımlı ve katmanlı teknik şema motoru.

Girdi: onaylanmış mimariyi tarif eden JSON (otomatik yapı uydurmaz).
Çıktı: bağımsız vektör taban + vektör yazı + düzenlenebilir tam SVG + PNG + QA manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape as esc

from PIL import ImageFont
from render_turkish_labels import get_font_path, verify_glyphs

WIDTH, HEIGHT = 1600, 900
INK = '#1d2126'
ORANGE = '#ee8733'
RED = '#c84e3c'
BLUE = '#3f7eaf'
SOFT = '#e0e2e2'
ALLOWED_MODES = {'architecture', 'data-flow', 'ml-pipeline', 'engineering-system'}
NODE_TYPES = {'client', 'process', 'service', 'data', 'model', 'sensor', 'actuator', 'system', 'result'}
EDGE_TYPES = {'data', 'control', 'feedback', 'physical'}
PORTS = {'top', 'bottom', 'left', 'right'}
PALETTE = {'black': INK, 'orange': ORANGE, 'red': RED, 'blue': BLUE}
SVG_PREFIX = '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">'


@dataclass(frozen=True)
class Node:
    ident: str
    label: str
    kind: str
    x: float
    y: float
    w: float
    h: float
    accent: str

    @property
    def box(self):
        return ((self.x-self.w/2)*WIDTH, (self.y-self.h/2)*HEIGHT,
                (self.x+self.w/2)*WIDTH, (self.y+self.h/2)*HEIGHT)


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    kind: str
    port_from: str | None
    port_to: str | None
    via: tuple[tuple[float, float], ...]
    label: str


@dataclass(frozen=True)
class MinimalAdam:
    x: float
    y: float
    scale: float
    action: str
    edge: int


@dataclass(frozen=True)
class Diagram:
    mode: str
    concept: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    minimaladam: MinimalAdam | None


def _fraction(value, location):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f'{location}: 0..1 arasında sonlu sayı gerekli')
    return float(value)


def _label(value, location, max_chars=32):
    if (not isinstance(value, str) or not 1 <= len(value.strip()) <= max_chars or
            unicodedata.normalize('NFC', value) != value or
            any(c in value for c in '\n\t\r<>') or
            any('\u3400' <= c <= '\u9fff' or c == '\ufffd' for c in value)):
        raise ValueError(f'{location}: kısa, tek satırlı, NFC Türkçe metin gerekli')
    return value.strip()


def overlap(a, b, pad=0):
    return not (a[2]+pad <= b[0] or b[2]+pad <= a[0] or a[3]+pad <= b[1] or b[3]+pad <= a[1])


def _check_exact_keys(item, allowed, loc):
    extra = set(item) - set(allowed)
    if extra:
        raise ValueError(f'{loc}: tanınmayan anahtarlar: {sorted(extra)}')


def read_spec(raw):
    if not isinstance(raw, dict):
        raise ValueError('Şema nesne olmalı')
    if 'xiaohei' in raw:
        if 'minimaladam' in raw:
            raise ValueError('Karakter hem xiaohei hem minimaladam olarak verilmiş')
        raw={**raw, 'minimaladam':raw['xiaohei']}
        del raw['xiaohei']
    _check_exact_keys(raw, ('version','mode','concept','nodes','edges','minimaladam'), 'şema')
    if raw.get('version') != 1 or raw.get('mode') not in ALLOWED_MODES:
        raise ValueError('version=1 ve geçerli mode gerekli')
    concept = _label(raw.get('concept'), 'concept', 120)
    ns = raw.get('nodes')
    es = raw.get('edges')
    if not isinstance(ns, list) or not 2 <= len(ns) <= 8:
        raise ValueError('2..8 node gerekli; karmaşık grafikleri ayrı şemalara bölün')
    if not isinstance(es, list) or not 1 <= len(es) <= 12:
        raise ValueError('1..12 edge gerekli')
    nodes = []
    seen = set()
    for i, n in enumerate(ns):
        if not isinstance(n, dict):
            raise ValueError(f'nodes[{i}]: nesne gerekli')
        _check_exact_keys(n, ('id','label','kind','x','y','w','h','accent'), f'nodes[{i}]')
        ident = n.get('id')
        if not isinstance(ident, str) or not ident.isascii() or not ident.replace('_','').isalnum() or ident in seen or len(ident)>32:
            raise ValueError(f'nodes[{i}]: benzersiz ASCII id gerekli')
        seen.add(ident)
        kind = n.get('kind')
        accent = n.get('accent','black')
        if kind not in NODE_TYPES or accent not in PALETTE:
            raise ValueError(f'nodes[{i}]: geçersiz kind veya accent')
        x = _fraction(n.get('x'), f'{ident}.x')
        y = _fraction(n.get('y'), f'{ident}.y')
        w = _fraction(n.get('w',0.16),f'{ident}.w')
        h = _fraction(n.get('h',0.16),f'{ident}.h')
        if not (.115 <= w <= .285 and .13 <= h <= .235):
            raise ValueError(f'{ident}: düğüm genişliği/yüksekliği sınırı aşıldı')
        node = Node(ident, _label(n.get('label'), ident+'.label'), kind, x, y, w, h, accent)
        left, top, right, bottom = node.box
        if left < 64 or right > WIDTH-64 or top < 70 or bottom > HEIGHT-70:
            raise ValueError(f'{ident}: düğüm kadraj dışı/güvenli kenar boşluğu dışında')
        for old in nodes:
            if overlap(node.box, old.box, 26):
                raise ValueError(f'Düğüm çakışması: {ident} ve {old.ident}')
        nodes.append(node)
    edges=[]
    pairs=set()
    for i,e in enumerate(es):
        if not isinstance(e,dict):
            raise ValueError(f'edges[{i}]: nesne gerekli')
        _check_exact_keys(e, ('from','to','kind','from_port','to_port','via','label'), f'edges[{i}]')
        src,dst = e.get('from'),e.get('to')
        if src not in seen or dst not in seen or src==dst:
            raise ValueError(f'edges[{i}]: kaynak/hedef düğüm hatalı')
        kind = e.get('kind','data')
        if kind not in EDGE_TYPES:
            raise ValueError(f'edges[{i}]: geçersiz kind')
        ports=(e.get('from_port'),e.get('to_port'))
        if any(p is not None and p not in PORTS for p in ports):
            raise ValueError(f'edges[{i}]: geçersiz port')
        via = e.get('via',[])
        if not isinstance(via,list) or len(via)>6:
            raise ValueError(f'edges[{i}]: via en fazla 6 nokta')
        points=[]
        for j,p in enumerate(via):
            if not isinstance(p,list) or len(p)!=2:
                raise ValueError(f'edges[{i}].via[{j}]: [x,y] gerekli')
            px=_fraction(p[0],'via x')*WIDTH
            py=_fraction(p[1],'via y')*HEIGHT
            if not 28 < px < WIDTH-28 or not 28 < py < HEIGHT-28:
                raise ValueError('Ara nokta kenara çok yakın')
            points.append((px,py))
        label = _label(e['label'], f'edges[{i}].label',22) if e.get('label') is not None else ''
        key=(src,dst,kind)
        if key in pairs:
            raise ValueError(f'Tekrarlanan bağlantı: {key}')
        pairs.add(key)
        edges.append(Edge(src,dst,kind,*ports,tuple(points),label))
    creature=None
    if raw.get('minimaladam') is None:
        raise ValueError("Teknik modda karakter ana bağlantıyı işaret etmeli: minimaladam + edge gerekli")
    if raw.get('minimaladam') is not None:
        c=raw['minimaladam']
        if not isinstance(c,dict):
            raise ValueError('minimaladam nesne olmalı')
        _check_exact_keys(c,('x','y','scale','action','edge'),'minimaladam')
        action=c.get('action','connect')
        if action not in {'connect','inspect','carry','guard'}:
            raise ValueError('MinimalAdam eylemi geçersiz')
        sc=c.get('scale',1)
        if isinstance(sc,bool) or not isinstance(sc,(int,float)) or not .65<=sc<=1.5:
            raise ValueError('minimaladam.scale 0.65..1.5 olmalı')
        x=_fraction(c.get('x'),'minimaladam.x')*WIDTH
        y=_fraction(c.get('y'),'minimaladam.y')*HEIGHT
        if not 65<x<WIDTH-65 or not 105<y<HEIGHT-65:
            raise ValueError('MinimalAdam kenara çok yakın')
        edge_ref=c.get('edge')
        if isinstance(edge_ref,bool) or not isinstance(edge_ref,int) or not 0<=edge_ref<len(edges):
            raise ValueError('minimaladam.edge tanımlı bir bağlantının sıfır tabanlı dizini olmalı')
        creature=MinimalAdam(x,y,float(sc),action,edge_ref)
    return Diagram(raw['mode'],concept,tuple(nodes),tuple(edges),creature)


def port_pt(n, port):
    a,b,c,d=n.box
    return {'left':(a,(b+d)/2),'right':(c,(b+d)/2),
            'top':((a+c)/2,b),'bottom':((a+c)/2,d)}[port]


def _default_ports(a,b):
    dx=(b.x-a.x)*WIDTH
    dy=(b.y-a.y)*HEIGHT
    if abs(dx)>=abs(dy):
        return ('right','left') if dx>0 else ('left','right')
    return ('bottom','top') if dy>0 else ('top','bottom')


def points_for(edge, lookup):
    a,b=lookup[edge.source],lookup[edge.target]
    pf,pt=_default_ports(a,b)
    pf=edge.port_from or pf
    pt=edge.port_to or pt
    start=port_pt(a,pf)
    end=port_pt(b,pt)
    if edge.via:
        points=[start,*edge.via,end]
    elif abs(start[0]-end[0])<.01 or abs(start[1]-end[1])<.01:
        points=[start,end]
    elif pf in ('left','right') and pt in ('left','right'):
        mid=(start[0]+end[0])/2
        points=[start,(mid,start[1]),(mid,end[1]),end]
    elif pf in ('top','bottom') and pt in ('top','bottom'):
        mid=(start[1]+end[1])/2
        points=[start,(start[0],mid),(end[0],mid),end]
    else:
        points=[start,(end[0],start[1]),end]
    # El çizimi stilini yalnız geometrik özelliği bozmayan ufak kırıklar ifade eder;
    # her ok tam olarak kullanıcının belirttiği kaynaktan hedefe gider.
    return points


def segment_hits_box(a,b,rect,pad=8):
    # Dik açı ağırlıklı ağ için eksen hizalı segment/kutu çakışma kontrolü.
    x1,y1=a; x2,y2=b
    left,top,right,bottom=rect
    left-=pad;top-=pad;right+=pad;bottom+=pad
    if abs(x1-x2)<.01:
        return left <= x1 <= right and max(min(y1,y2),top)<min(max(y1,y2),bottom)
    if abs(y1-y2)<.01:
        return top <= y1 <= bottom and max(min(x1,x2),left)<min(max(x1,x2),right)
    # Diagonal bağlantı varsa küçük adımla çarpışmayı kontrol et.
    for i in range(1,40):
        r=i/40
        x=x1+(x2-x1)*r;y=y1+(y2-y1)*r
        if left<x<right and top<y<bottom:
            return True
    return False


def _line_path(points):
    return 'M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in points)


def _node_shape(n):
    a,b,c,d=n.box
    x=a;y=b;w=c-a;h=d-b
    # Hafif düzensiz ikinci kontur çizimi mekanik kart hissini yumuşatır.
    rect=(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'rx="20" fill="white" stroke="{INK}" stroke-width="2.5"/>')
    details=(f'<path d="M {x+15:.1f},{y+11:.1f} Q {x+w/2:.1f},{y+7:.1f} {x+w-17:.1f},{y+11:.1f}" '
             f'fill="none" stroke="{INK}" opacity="0.27" stroke-width="1.1"/>')
    color=PALETTE[n.accent]
    icon_x=x+27;icon_y=y+25
    if n.kind in ('data','model'):
        if n.kind=='data':
            icon=(f'<ellipse cx="{icon_x:.1f}" cy="{icon_y-7:.1f}" rx="13" ry="5" fill="none" stroke="{color}" stroke-width="2"/>'
                  f'<path d="M {icon_x-13:.1f},{icon_y-7:.1f} v15 q13,10 26,0 v-15" fill="none" stroke="{color}" stroke-width="2"/>')
        else:
            icon=(f'<path d="M {icon_x-13:.1f},{icon_y:.1f} l13,-13 13,13 -13,13 z" stroke="{color}" fill="none" stroke-width="2"/>'
                  f'<circle cx="{icon_x:.1f}" cy="{icon_y:.1f}" r="3" fill="{color}"/>')
    elif n.kind in ('actuator','system'):
        icon=(f'<circle cx="{icon_x:.1f}" cy="{icon_y:.1f}" r="11" stroke="{color}" fill="none" stroke-width="2"/>'
              f'<path d="M {icon_x-4},{icon_y+2} l5,-9 5,10" fill="none" stroke="{color}" stroke-width="2"/>')
    elif n.kind in ('sensor','client'):
        icon=(f'<path d="M {icon_x-13},{icon_y+7} q13,-20 26,0" fill="none" stroke="{color}" stroke-width="2"/>'
              f'<circle cx="{icon_x}" cy="{icon_y+7}" r="3" fill="{color}"/>')
    elif n.kind=='result':
        icon=(f'<path d="M {icon_x-12},{icon_y} l8,8 16,-18" stroke="{color}" stroke-width="2.8" fill="none"/>')
    else:
        icon=(f'<rect x="{icon_x-11}" y="{icon_y-11}" width="22" height="22" rx="4" '
              f'fill="none" stroke="{color}" stroke-width="2"/>'
              f'<circle cx="{icon_x}" cy="{icon_y}" r="3" fill="{color}"/>')
    return f'<g id="node-{n.ident}" data-kind="{n.kind}">{rect}{details}{icon}</g>'


ARMS={'connect':(43,-15),'inspect':(38,-27),'carry':(45,-5),'guard':(28,-35)}


def _point_segment_distance(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    m=vx*vx+vy*vy
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/m)) if m else 0
    return math.dist(p,(a[0]+vx*t,a[1]+vy*t))


def check_creature_contact(creature,routes):
    ax,ay=ARMS[creature.action]
    p=(creature.x+ax*creature.scale, creature.y+ay*creature.scale)
    pts=routes[creature.edge]
    distance=min(_point_segment_distance(p,a,b) for a,b in zip(pts,pts[1:]))
    if distance>28:
        raise ValueError(f'MinimalAdam seçilen bağlantıdan uzak: {distance:.1f}px; karakter eylemi çizgiye değmeli')


def _minimaladam(c):
    # Ian'ın görsel karakterine referans veren basit, yeniden çizilmiş stilize figür.
    # Tekrarlanabilir SVG vektör; orijinal görsel varlığı kopyalanmaz.
    x,y=c.x,c.y;s=c.scale
    arm=ARMS[c.action]
    return (f'<g id="minimaladam" transform="translate({x:.1f},{y:.1f}) scale({s:.2f})">'
            f'<path d="M -17,21 l-8,20 M 13,21 l6,20" stroke="{INK}" stroke-width="3" stroke-linecap="round" fill="none"/>'
            f'<path d="M -16,-14 Q -28,-13 -24,8 Q -18,27 3,26 Q 27,25 28,3 Q 26,-26 4,-31 Q -15,-32 -16,-14 Z" fill="{INK}"/>'
            '<ellipse cx="-3" cy="-9" rx="3.2" ry="4.5" fill="white"/>'
            '<ellipse cx="13" cy="-8" rx="3.2" ry="4.5" fill="white"/>'
            f'<path d="M 22,5 Q 31,-1 {arm[0]},{arm[1]}" stroke="{INK}" fill="none" stroke-width="3" stroke-linecap="round"/>'
            f'<circle cx="{arm[0]}" cy="{arm[1]}" r="3.2" fill="{INK}"/>'
            '</g>')


def _font_labels(diagram,font_path, routes):
    """SVG text bounding geometry estimated with selected installed TTF (no raster OCR)."""
    font_path=Path(font_path)
    node_font=ImageFont.truetype(str(font_path),24)
    edge_font=ImageFont.truetype(str(font_path),19)
    labels=[]
    for n in diagram.nodes:
        # Node labels are central, below their icon, clipped/overflow checked in pixels.
        center_x=n.x*WIDTH
        center_y=n.y*HEIGHT+12
        bbox=node_font.getbbox(n.label)
        width=bbox[2]-bbox[0]
        if width > n.w*WIDTH-28:
            raise ValueError(f'Düğüm yazısı kutuya sığmıyor ({n.ident}): {n.label!r}; düğümü genişletin veya kısaltın')
        text_height=bbox[3]-bbox[1]
        labels.append({'text':n.label,'x':center_x,'y':center_y,'size':24,'color':'black','anchor':'middle',
                       'box':(center_x-width/2,center_y-text_height/2,center_x+width/2,center_y+text_height/2),
                       'owner':n.ident})
    for idx,(e,pts) in enumerate(zip(diagram.edges,routes)):
        if not e.label: continue
        # En uzun segmentte orta noktadan +18 dik uzaklıkla açıklama.
        segments=list(zip(pts,pts[1:]))
        a,b=max(segments,key=lambda pair:math.dist(pair[0],pair[1]))
        x=(a[0]+b[0])/2
        y=(a[1]+b[1])/2
        if abs(a[0]-b[0])>=abs(a[1]-b[1]):
            y-=21
        else:
            x+=17
        bb=edge_font.getbbox(e.label)
        width=bb[2]-bb[0]
        height=bb[3]-bb[1]
        rect=(x-width/2-4,y-height/2-4,x+width/2+4,y+height/2+4)
        if rect[0]<20 or rect[2]>WIDTH-20 or rect[1]<20 or rect[3]>HEIGHT-20:
            raise ValueError(f'Bağlantı etiketi kadraj dışı: {e.label}')
        for node in diagram.nodes:
            if overlap(rect,node.box,5):
                raise ValueError(f'Bağlantı etiketi düğüme temas ediyor: {e.label} / {node.ident}; via ile düzeltin veya kaldırın')
        labels.append({'text':e.label,'x':x,'y':y,'size':19,
                       'color':'blue' if e.kind=='feedback' else 'black','anchor':'middle',
                       'box':rect,'owner':f'edge-{idx}'})
    for i,a in enumerate(labels):
        if a['box'][0]<20 or a['box'][2]>WIDTH-20 or a['box'][1]<20 or a['box'][3]>HEIGHT-20:
            raise ValueError('Metin kadraj dışı: '+a['text'])
        for b in labels[i+1:]:
            if overlap(a['box'],b['box'],8):
                raise ValueError(f'Metin çakışması: {a["text"]!r} / {b["text"]!r}')
    verify_glyphs(font_path,[l['text'] for l in labels])
    return labels


def _text_layer(labels, font_family):
    family=esc(font_family)
    out=[]
    for l in labels:
        out.append(f'<text x="{l["x"]:.2f}" y="{l["y"]:.2f}" '
                   f'fill="{PALETTE[l["color"]]}" font-family="{family}" '
                   f'font-size="{l["size"]}" font-weight="500" text-anchor="middle" '
                   f'dominant-baseline="central">{esc(l["text"])}</text>')
    return '\n'.join(out)


def _font_family(font_path):
    from fontTools.ttLib import TTFont
    f=TTFont(str(font_path))
    try:
        for record in f['name'].names:
            if record.nameID==1:
                return record.toUnicode()
    finally:
        f.close()
    return 'DejaVu Sans'


def _edge_svg(e,points,idx):
    style={'data':(ORANGE,''),'control':(INK,''),'feedback':(BLUE,'7 7'),'physical':(RED,'2 5')}[e.kind]
    color,dash=style
    dash_attr=f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path id="edge-{idx}" d="{_line_path(points)}" fill="none" stroke="{color}" '
            f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"'
            f'{dash_attr} marker-end="url(#arrow-{e.kind})"/>')


def _markers():
    els=[]
    for kind,color in [('data',ORANGE),('control',INK),('feedback',BLUE),('physical',RED)]:
        els.append(f'<marker id="arrow-{kind}" viewBox="0 0 14 14" refX="12" refY="7" '
                   f'markerWidth="5" markerHeight="5" orient="auto-start-reverse" markerUnits="strokeWidth">'
                   f'<path d="M 2 2 L 12 7 L 2 12" fill="none" stroke="{color}" stroke-width="2.2"/>'
                   '</marker>')
    return '<defs>'+''.join(els)+'</defs>'


def render(spec_path:Path,output_dir:Path,font_arg=None,slug=None):
    try:
        raw=json.loads(spec_path.read_text(encoding='utf-8'))
    except UnicodeDecodeError as err:
        raise ValueError('JSON UTF-8 olmalı') from err
    diagram=read_spec(raw)
    lookup={n.ident:n for n in diagram.nodes}
    routes=[]
    for e in diagram.edges:
        pts=points_for(e,lookup)
        for other in diagram.nodes:
            if other.ident in (e.source,e.target): continue
            if any(segment_hits_box(p,q,other.box) for p,q in zip(pts,pts[1:])):
                raise ValueError(f'Bağlantı üçüncü düğümün üzerinden geçiyor: {e.source}->{e.target} / {other.ident}; via kullanın')
        routes.append(pts)
    check_creature_contact(diagram.minimaladam,routes)
    font=get_font_path(font_arg)
    labels=_font_labels(diagram,font,routes)
    slug=slug or spec_path.stem
    if not isinstance(slug,str) or not slug or not all(c.isascii() and (c.isalnum() or c in '_-') for c in slug):
        raise ValueError('Çıktı slug alfanümerik olmalı')
    output_dir.mkdir(parents=True,exist_ok=True)
    background='<rect width="1600" height="900" fill="white"/>'
    paths='\n'.join(_edge_svg(edge,p,i) for i,(edge,p) in enumerate(zip(diagram.edges,routes)))
    shapes='\n'.join(_node_shape(n) for n in diagram.nodes)
    figure=_minimaladam(diagram.minimaladam) if diagram.minimaladam else ''
    bg_contents=f'{background}\n{_markers()}\n{paths}\n{shapes}\n{figure}'
    label_contents=_text_layer(labels,_font_family(font))
    base=SVG_PREFIX+f'<g id="technical-base">{bg_contents}</g>'+'</svg>\n'
    text_svg=SVG_PREFIX+f'<g id="turkish-label-layer">{label_contents}</g>'+'</svg>\n'
    combined=SVG_PREFIX+f'<g id="technical-base">{bg_contents}</g>\n<g id="turkish-label-layer">{label_contents}</g>'+'</svg>\n'
    paths_out={key:output_dir/f'{slug}{suffix}' for key,suffix in [
        ('base','.base.svg'),('labels','.labels.svg'),('svg','.svg'),('png','.png'),('manifest','.manifest.json')]}
    for key,contents in [('base',base),('labels',text_svg),('svg',combined)]:
        ET.fromstring(contents)
        paths_out[key].write_text(contents,encoding='utf-8')
    # Windows'ta Cairo/GTK DLL zorunlu değil: aynı doğrulanmış JSON'dan
    # Pillow ile PNG üret. SVG çıktısı düzenlenebilir vektör olarak korunur.
    from raster_pillow import render_png
    render_png(diagram, routes, labels, font, paths_out['png'])
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={
        'version':1,'mode':diagram.mode,'concept':diagram.concept,
        'source_spec':spec_path.name,'source_sha256':digest(spec_path),
        'font':font.name,'font_sha256':digest(font),
        'dimension':[WIDTH,HEIGHT],
        'counts':{'nodes':len(diagram.nodes),'edges':len(diagram.edges),'labels':len(labels),'minimaladam':int(diagram.minimaladam is not None)},
        'outputs':{k:v.name for k,v in paths_out.items() if k!='manifest'},
        'sha256':{k:digest(v) for k,v in paths_out.items() if k!='manifest'},
        'qa':{'nfc_strings':True,'glyphs_checked':True,'node_collisions_checked':True,
              'edge_hits_other_nodes_checked':True,'label_bounds_checked':True,
              'label_label_collisions_checked':True,'minimaladam_action_contact_checked':True,
              'semantic_structure_not_automatically_verified':True,
              'manual_visual_review_required':True}}
    paths_out['manifest'].write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return paths_out


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec',required=True,type=Path,help='UTF-8 JSON teknik mimari')
    ap.add_argument('--output-dir',required=True,type=Path,help='Çıktı klasörü')
    ap.add_argument('--font',help='Türkçe destekli TTF/OTF yolu')
    ap.add_argument('--slug',help='Dosya öneki')
    args=ap.parse_args(argv)
    try:
        paths=render(args.spec,args.output_dir,args.font,args.slug)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as e:
        print('HATA:',e,file=sys.stderr)
        return 1
    for key,val in paths.items():print(f'{key}: {val}')
    return 0

if __name__=='__main__':
    sys.exit(main())
