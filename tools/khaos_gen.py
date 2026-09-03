#!/usr/bin/env python3
"""Erzeugt die Pixel-Raster für Khaos (flauschig, schlank) und schreibt sie als JS-Array.
Zeichen: . leer | o Umriss | b Fell | d Fellschatten | l helles Fell/Bauch | h Horn/Schleife | e Augenweiß | p Pupille | t Zahn | a Rüstung
Aufruf: python3 tools/khaos_gen.py > /tmp/khaos.js
"""
import math, json, sys

def grid(W,H): return [['.']*W for _ in range(H)]

def ellipse_mask(W,H,cx,cy,rx,ry):
    m=[[False]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            dx=(x+0.5-cx)/rx; dy=(y+0.5-cy)/ry
            m[y][x]=dx*dx+dy*dy<=1.0
    return m

def fur_edge(m, W, H, seed=3):
    """Fellkante: Randpixel bekommen versetzt einen Büschel nach außen (oben und unten stärker)."""
    out=[row[:] for row in m]
    for y in range(H):
        for x in range(W):
            if not m[y][x]: continue
            for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H and not m[ny][nx]:
                    k=(x*7+y*3+seed)%5
                    vertical = dy!=0
                    if (vertical and k in (0,2)) or (not vertical and k==1):
                        out[ny][nx]=True
    return out

def outline(m,W,H):
    o=[[False]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if m[y][x]: continue
            for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H and m[ny][nx]: o[y][x]=True
    return o

def stamp(g, rows, x0, y0, mirror=False):
    for j,row in enumerate(rows):
        r=row[::-1] if mirror else row
        for i,ch in enumerate(r):
            if ch=='.': continue
            x,y=x0+i,y0+j
            if 0<=y<len(g) and 0<=x<len(g[0]): g[y][x]=ch

def paint_mask(g, m, ch):
    for y,row in enumerate(m):
        for x,v in enumerate(row):
            if v: g[y][x]=ch

def build(W,H,cx,body_top,body_h,rx, horns, bow, eyes_y, eye, arms=None, legs=None, tail=None, wings=None, mane=False, armor=False, teeth=False, seed=3):
    """Ein Sprite. body_top = obere Kante des Rumpfs, body_h = Höhe. Alles relativ zur Mittelspalte cx."""
    ry=body_h/2.0; cy=body_top+ry
    base=ellipse_mask(W,H,cx+0.5,cy,rx,ry)
    fur=fur_edge(base,W,H,seed)
    if mane:  # zweite Fellkante nur am Kopf (obere Hälfte) -> buschiger Kragen
        fur2=fur_edge(fur,W,H,seed+2)
        for y in range(H):
            if y<cy-ry*0.15:
                fur[y]=fur2[y]
    ol=outline(fur,W,H)
    def draw(headgear):
        g=grid(W,H)
        # Hinten: Flügel, Schwanz
        if wings: stamp(g,wings['rows'],cx-wings['dx']-len(wings['rows'][0])+1,wings['y']); stamp(g,wings['rows'],cx+wings['dx'],wings['y'],mirror=True)
        if tail: stamp(g,tail['rows'],cx+tail['dx'],tail['y'])
        # Rumpf
        paint_mask(g,fur,'b')
        # Bauch (helles Fell), Schatten rechts unten, Fellstriche
        belly=ellipse_mask(W,H,cx+0.5,cy+ry*0.35,rx*0.5,ry*0.42)
        for y in range(H):
            for x in range(W):
                if belly[y][x] and base[y][x]: g[y][x]='l'
        for y in range(H):
            for x in range(W):
                if not base[y][x] or g[y][x]!='b': continue
                dx=(x+0.5-cx-0.5)/rx; dy=(y+0.5-cy)/ry; r=dx*dx+dy*dy
                if r>0.72 and dx>0.15 and dy>-0.2: g[y][x]='d'          # Schatten rechts/unten
                elif r>0.55 and (x*5+y*11+seed)%9==0: g[y][x]='d'          # einzelne Fellstriche
                elif r<0.35 and dx<-0.1 and dy<-0.2 and (x+y)%4==0: g[y][x]='l'  # Glanz oben links
        if armor:
            ar=ellipse_mask(W,H,cx+0.5,cy+ry*0.30,rx*0.42,ry*0.26)
            for y in range(H):
                for x in range(W):
                    if ar[y][x] and base[y][x]: g[y][x]='a'
            ao=outline(ar,W,H)
            for y in range(H):
                for x in range(W):
                    if ao[y][x] and base[y][x]: g[y][x]='o'
        paint_mask(g,ol,'o')
        # Augen
        ex=eye['gap']
        stamp(g,eye['rows'],cx-ex-len(eye['rows'][0])+1,eyes_y); stamp(g,eye['rows'],cx+ex,eyes_y,mirror=True)
        # Mund
        my=eyes_y+len(eye['rows'])+1
        mw=eye.get('mouth',3)
        for i in range(mw): g[my][cx-mw//2+i]='o'
        if teeth:
            g[my+1][cx-mw//2]='t'; g[my+1][cx+mw//2]='t'
        # Kopfschmuck
        stamp(g,headgear['rows'],cx-headgear['dx']-len(headgear['rows'][0])+1,headgear['y'])
        if headgear.get('mirror',True): stamp(g,headgear['rows'],cx+headgear['dx'],headgear['y'],mirror=True)
        # Vorne: Arme, Beine
        if arms: stamp(g,arms['rows'],cx-arms['dx']-len(arms['rows'][0])+1,arms['y']); stamp(g,arms['rows'],cx+arms['dx'],arms['y'],mirror=True)
        if legs: stamp(g,legs['rows'],cx-legs['dx']-len(legs['rows'][0])+1,legs['y']); stamp(g,legs['rows'],cx+legs['dx'],legs['y'],mirror=True)
        return [''.join(r) for r in g]
    return draw(horns), draw(bow)

# ---- Stempel ----
EYE3={'rows':["eee","epp","epp"],'gap':2,'mouth':3}
EYE4={'rows':["eeee","eepp","eppp","eppp"],'gap':2,'mouth':3}
EYE4W={'rows':["eeee","eepp","eppp","eppp"],'gap':3,'mouth':5}
HORN_S={'rows':["h..",".h.","hh."],'dx':3,'y':0}                 # klein
HORN_M={'rows':["h...",".h..","hh..",".hh."],'dx':3,'y':0}
HORN_L={'rows':["hh...",".hh..","..hh.","..hhh",".hhh."],'dx':3,'y':0}
HORN_XL={'rows':["hhh....",".hhh...","..hhh..","...hhh.","...hhhh","..hhhh."],'dx':3,'y':0}
def bow(w):  # Schleife: zwei Flügel + Knoten, nicht gespiegelt
    if w==7: rows=["hh...hh","hhh.hhh",".hhhhh.","..hhh.."]
    elif w==9: rows=["hh.....hh","hhh...hhh",".hhhhhhh.","..hhhhh..","...hhh..."]
    else: rows=["hhh.....hhh","hhhh...hhhh",".hhhhhhhhh.","..hhhhhhh..","...hhhhh...","....hhh...."]
    return {'rows':rows,'dx':-(w//2),'y':0,'mirror':False}
ARM_S={'rows':["obo","ob.",".o."],'dx':0,'y':0}
ARM_M={'rows':["obbo","obb.","obb.",".oo."],'dx':0,'y':0}
LEG_S={'rows':["obbo","oooo"],'dx':1,'y':0}
LEG_M={'rows':["obbbo","obbbo","ooooo"],'dx':1,'y':0}
TAIL={'rows':[".ob","obb","bbo","oo."],'dx':0,'y':0}
WING_M={'rows':["....o","...ob","..obb",".obbb","obbbb","odbbb",".oddb","..ooo"],'dx':0,'y':0}
WING_L={'rows':[".....o","....ob","...obb","..obbb",".obbbb","obbbbb","obbbbb","oddbbb",".odddb","..oddb","...ooo"],'dx':0,'y':0}

STAGES=[]
def add(**k): STAGES.append(k)
# W,H,cx | body_top, body_h, rx | eyes_y
add(lvl=1,  name='Winzling',    cell=6, W=19,H=23,cx=9, body_top=4, body_h=16, rx=6.2, horns=dict(HORN_S,y=1,dx=2), bow=dict(bow(7),y=1), eyes_y=9,  eye=EYE3, legs=dict(LEG_S,y=20,dx=1), seed=3,
    flavor='Khaos ist gerade erst geschlüpft – ein Fellknäuel mit Hörnchen.')
add(lvl=10, name='Wächst',      cell=6, W=21,H=27,cx=10, body_top=4, body_h=19, rx=6.4, horns=dict(HORN_M,y=0,dx=2), bow=dict(bow(7),y=1), eyes_y=10, eye=EYE3, arms=dict(ARM_S,y=15,dx=6), legs=dict(LEG_S,y=23,dx=1), seed=5,
    flavor='Er streckt sich, bekommt Arme und Beine – die Reise beginnt.')
add(lvl=20, name='Kräftig',     cell=5, W=27,H=33,cx=13, body_top=5, body_h=23, rx=7.6, horns=dict(HORN_M,y=1,dx=3), bow=dict(bow(9),y=1), eyes_y=12, eye=EYE4, arms=dict(ARM_M,y=18,dx=7), legs=dict(LEG_M,y=28,dx=1), tail=dict(TAIL,y=24,dx=7), seed=7,
    flavor='Schlanker, aufrechter, mit Schwanz – man sieht deinen Fortschritt.')
add(lvl=30, name='Stark',       cell=5, W=29,H=35,cx=14, body_top=6, body_h=24, rx=8.0, horns=dict(HORN_L,y=1,dx=3), bow=dict(bow(9),y=2), eyes_y=13, eye=EYE4, arms=dict(ARM_M,y=19,dx=8), legs=dict(LEG_M,y=30,dx=1), tail=dict(TAIL,y=25,dx=8), mane=True, teeth=True, seed=11,
    flavor='Mähne, Zähne, größere Hörner. Stark und treu an deiner Seite.')
add(lvl=40, name='Mächtig',     cell=5, W=31,H=37,cx=15, body_top=7, body_h=25, rx=8.2, horns=dict(HORN_L,y=2,dx=3), bow=dict(bow(11),y=2), eyes_y=14, eye=EYE4, arms=dict(ARM_M,y=20,dx=8), legs=dict(LEG_M,y=32,dx=1), tail=dict(TAIL,y=26,dx=8), wings=dict(WING_M,y=13,dx=10), mane=True, teeth=True, seed=13,
    flavor='Flügel im Fell – mächtig und kaum wiederzuerkennen.')
add(lvl=50, name='Kampfbestie', cell=5, W=33,H=39,cx=16, body_top=8, body_h=26, rx=8.4, horns=dict(HORN_XL,y=2,dx=3), bow=dict(bow(11),y=3), eyes_y=15, eye=EYE4W, arms=dict(ARM_M,y=21,dx=8), legs=dict(LEG_M,y=34,dx=1), tail=dict(TAIL,y=27,dx=8), wings=dict(WING_L,y=12,dx=10), mane=True, teeth=True, armor=True, seed=17,
    flavor='Die Kampfbestie ist erwacht – gepanzert, geflügelt, flauschig. Genau wie du.')

def main():
    out=[]
    for s in STAGES:
        rows,bowrows=build(s['W'],s['H'],s['cx'],s['body_top'],s['body_h'],s['rx'],s['horns'],s['bow'],s['eyes_y'],s['eye'],
                           arms=s.get('arms'),legs=s.get('legs'),tail=s.get('tail'),wings=s.get('wings'),mane=s.get('mane',False),armor=s.get('armor',False),teeth=s.get('teeth',False),seed=s.get('seed',3))
        out.append({'lvl':s['lvl'],'name':s['name'],'cell':s['cell'],'flavor':s['flavor'],'body':rows,'bowBody':bowrows})
    print('  var COMPANION='+json.dumps(out,ensure_ascii=False,indent=None).replace('},{','},\n   {').replace('"body":','\n    "body":').replace('"bowBody":','\n    "bowBody":')+';')
if __name__=='__main__': main()
