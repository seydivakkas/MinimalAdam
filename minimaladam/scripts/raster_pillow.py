"""P3 SVG ile aynı JSON spesifikasyonundan Cairo/GTK gerektirmeyen PNG.

Pillow raster katmanı; SVG vektör çıktı sözleşmesini değiştirmez.
Yerel işletim sistemi fontu kullanılır. Farklı fontlardaki piksel özdeşliği
beklenmez ve rastgele tasarım elemanı eklenmez.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 900
INK = '#1d2126'
ORANGE = '#ee8733'
RED = '#c84e3c'
BLUE = '#3f7eaf'
PALETTE = {'black':INK, 'orange':ORANGE, 'red':RED, 'blue':BLUE}
EDGE_COLORS = {'data':ORANGE,'control':INK,'feedback':BLUE,'physical':RED}
ARMS={'connect':(43,-15),'inspect':(38,-27),'carry':(45,-5),'guard':(28,-35)}


def _line(draw, pts, color, width=3, dash=None):
    # Boşluklu çizgilerde aralık, tüm çizim hattı boyunca sürdürülür.
    if not dash:
        draw.line(pts, fill=color, width=width, joint='curve')
        return
    period=sum(dash)
    offset=0.0
    for a,b in zip(pts,pts[1:]):
        length=math.dist(a,b)
        if not length: continue
        current=0.0
        while current < length:
            pos=(offset+current) % period
            remaining=dash[0]-pos if pos<dash[0] else period-pos
            end=min(length,current+remaining)
            if pos<dash[0]:
                t=current/length; u=end/length
                draw.line([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),
                           (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],
                          fill=color,width=width)
            current=end
        offset=(offset+length)%period


def _curve(p0,p1,p2, steps=12):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],
             (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in (i/steps for i in range(steps+1))]


def _edge(draw, edge, points):
    color=EDGE_COLORS[edge.kind]
    dash={'feedback':(7,7),'physical':(2,5)}.get(edge.kind)
    _line(draw, points, color, 3,dash)
    a,b=points[-2:]
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    length=13
    for delta in (-.47,.47):
        p=(b[0]-length*math.cos(angle+delta),b[1]-length*math.sin(angle+delta))
        draw.line([p,b],fill=color,width=3)


def _node(draw,n):
    left,top,right,bottom=n.box
    draw.rounded_rectangle((left,top,right,bottom), radius=20,fill='white',outline=INK,width=3)
    _line(draw,_curve((left+15,top+11),((left+right)/2,top+7),(right-17,top+11)), '#bdc0c2', 1)
    color=PALETTE[n.accent]
    x,y=left+27,top+25
    if n.kind=='data':
        draw.ellipse((x-13,y-12,x+13,y-2),outline=color,width=2)
        draw.line([(x-13,y-7),(x-13,y+8)],fill=color,width=2)
        draw.line([(x+13,y-7),(x+13,y+8)],fill=color,width=2)
        _line(draw,_curve((x-13,y+8),(x,y+18),(x+13,y+8)),color,2)
    elif n.kind=='model':
        _line(draw,[(x-13,y),(x,y-13),(x+13,y),(x,y+13),(x-13,y)],color,2)
        draw.ellipse((x-3,y-3,x+3,y+3),fill=color)
    elif n.kind in ('system','actuator'):
        draw.ellipse((x-11,y-11,x+11,y+11),outline=color,width=2)
        _line(draw,[(x-4,y+2),(x+1,y-7),(x+6,y+3)],color,2)
    elif n.kind in ('client','sensor'):
        _line(draw,_curve((x-13,y+7),(x,y-13),(x+13,y+7)),color,2)
        draw.ellipse((x-3,y+4,x+3,y+10),fill=color)
    elif n.kind=='result':
        _line(draw,[(x-12,y),(x-4,y+8),(x+12,y-10)],color,3)
    else:
        draw.rounded_rectangle((x-11,y-11,x+11,y+11),radius=4,outline=color,width=2)
        draw.ellipse((x-3,y-3,x+3,y+3),fill=color)


def _character(draw,c):
    s=c.scale
    def p(x,y):return (c.x+x*s,c.y+y*s)
    _line(draw,[p(-17,21),p(-25,41)],INK,max(1,round(3*s)))
    _line(draw,[p(13,21),p(19,41)],INK,max(1,round(3*s)))
    # SVG siluetinin eğriyi takip eden sade çizim karşılığı
    body=[p(-16,-14),p(-24,-6),p(-24,8),p(-18,19),p(3,26),p(20,20),p(28,3),p(26,-17),p(4,-31),p(-15,-32)]
    draw.polygon(body,fill=INK)
    for ex,ey in [(-3,-9),(13,-8)]:
        draw.ellipse((c.x+(ex-3.2)*s,c.y+(ey-4.5)*s,c.x+(ex+3.2)*s,c.y+(ey+4.5)*s),fill='white')
    arm=ARMS[c.action]
    _line(draw,_curve(p(22,5),p(31,-1),p(*arm)),INK,max(1,round(3*s)))
    x,y=p(*arm)
    draw.ellipse((x-3.2*s,y-3.2*s,x+3.2*s,y+3.2*s),fill=INK)


def render_png(diagram,routes,labels,font_path,path):
    """Create offline PNG from validated P3 graph. All primitives drawn with Pillow."""
    canvas=Image.new('RGB',(WIDTH,HEIGHT),'white')
    draw=ImageDraw.Draw(canvas)
    for edge,pts in zip(diagram.edges,routes): _edge(draw,edge,pts)
    for node in diagram.nodes: _node(draw,node)
    if diagram.minimaladam: _character(draw,diagram.minimaladam)
    for label in labels:
        font=ImageFont.truetype(str(font_path),label['size'])
        draw.text((label['x'],label['y']),label['text'],font=font,
                  fill=PALETTE[label['color']],anchor='mm')
    canvas.save(path,format='PNG',optimize=False)
    return Path(path)
