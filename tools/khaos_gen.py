#!/usr/bin/env python3
"""Erzeugt die Pixel-Raster für Khaos (flauschig, schlank) in 6 Wachstumsstufen, je männlich und weiblich.
Männlich: breitere Schultern, kräftige Arme, Brust-/Bauchmuskeln. Weiblich: schmaler, Taille und Hüfte, Wimpern, feinere Arme.
Zeichen: . leer | o Umriss | b Fell | d Fellschatten | l helles Fell/Bauch | h Horn | e Augenweiß | p Pupille | t Zahn | a Rüstung
Aufruf: python3 tools/khaos_gen.py > /tmp/khaos.js   (Ausgabe in docs/index.html einsetzen)
"""
import math, json

def grid(W,H): return [['.']*W for _ in range(H)]

def body_mask(W,H,cx,cy,rx,ry,sex):
    m=[[False]*W for _ in range(H)]
    for y in range(H):
        t=(y+0.5-cy)/ry
        if abs(t)>1: continue
        w=rx*math.sqrt(1-t*t)
        if sex=='f':
            w*=1-0.22*math.exp(-((t-0.12)/0.28)**2)   # Taille
            w*=1+0.10*math.exp(-((t-0.62)/0.25)**2)   # Hüfte
        else:
            w*=1+0.18*math.exp(-((t+0.30)/0.30)**2)   # Schultern
            w*=1-0.05*math.exp(-((t-0.35)/0.30)**2)   # leichte Taille
        for x in range(W):
            if abs(x+0.5-cx)<=w: m[y][x]=True
    return m

def ellipse_mask(W,H,cx,cy,rx,ry):
    m=[[False]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            dx=(x+0.5-cx)/rx; dy=(y+0.5-cy)/ry
            m[y][x]=dx*dx+dy*dy<=1.0
    return m

def fur_edge(m, W, H, seed=3):
    out=[row[:] for row in m]
    for y in range(H):
        for x in range(W):
            if not m[y][x]: continue
            for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H and not m[ny][nx]:
                    k=(x*7+y*3+seed)%5
                    if (dy!=0 and k in (0,2)) or (dy==0 and k==1): out[ny][nx]=True
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

def put(g,x,y,ch,only=None):
    if 0<=y<len(g) and 0<=x<len(g[0]) and (only is None or g[y][x] in only): g[y][x]=ch

def build(sex, W,H,cx,body_top,body_h,rx, horns, eyes_y, eye, arms=None, legs=None, tail=None, wings=None, mane=False, armor=False, teeth=False, muscles=0, seed=3):
    ry=body_h/2.0; cy=body_top+ry
    rxs = rx*0.92 if sex=='f' else rx*1.06
    base=body_mask(W,H,cx+0.5,cy,rxs,ry,sex)
    fur=fur_edge(base,W,H,seed)
    if mane:
        fur2=fur_edge(fur,W,H,seed+2)
        for y in range(H):
            if y<cy-ry*0.15: fur[y]=fur2[y]
    ol=outline(fur,W,H)
    g=grid(W,H)
    if wings: stamp(g,wings['rows'],cx-wings['dx']-len(wings['rows'][0])+1,wings['y']); stamp(g,wings['rows'],cx+wings['dx'],wings['y'],mirror=True)
    if tail: stamp(g,tail['rows'],cx+tail['dx'],tail['y'])
    paint_mask(g,fur,'b')
    belly=ellipse_mask(W,H,cx+0.5,cy+ry*0.38,rxs*(0.42 if sex=='f' else 0.5),ry*0.40)
    for y in range(H):
        for x in range(W):
            if belly[y][x] and base[y][x]: g[y][x]='l'
    for y in range(H):
        for x in range(W):
            if not base[y][x] or g[y][x]!='b': continue
            dx=(x+0.5-cx-0.5)/rxs; dy=(y+0.5-cy)/ry; r=dx*dx+dy*dy
            if r>0.72 and dx>0.15 and dy>-0.2: g[y][x]='d'
            elif r>0.55 and (x*5+y*11+seed)%9==0: g[y][x]='d'
            elif r<0.35 and dx<-0.1 and dy<-0.2 and (x+y)%4==0: g[y][x]='l'
    if armor:
        ar=ellipse_mask(W,H,cx+0.5,cy+ry*0.30,rxs*0.42,ry*0.26)
        for y in range(H):
            for x in range(W):
                if ar[y][x] and base[y][x]: g[y][x]='a'
        ao=outline(ar,W,H)
        for y in range(H):
            for x in range(W):
                if ao[y][x] and base[y][x]: g[y][x]='o'
    paint_mask(g,ol,'o')
    # Augen (+ Wimpern weiblich)
    ex=eye['gap']; ew=len(eye['rows'][0])
    lx=cx-ex-ew+1; rx0=cx+ex
    stamp(g,eye['rows'],lx,eyes_y); stamp(g,eye['rows'],rx0,eyes_y,mirror=True)
    if sex=='f':
        put(g,lx-1,eyes_y,'o','bdl'); put(g,lx,eyes_y-1,'o','bdl'); put(g,lx-1,eyes_y-1,'o','bdl')
        put(g,rx0+ew,eyes_y,'o','bdl'); put(g,rx0+ew-1,eyes_y-1,'o','bdl'); put(g,rx0+ew,eyes_y-1,'o','bdl')
    # Mund, Zähne
    my=eyes_y+len(eye['rows'])+1; mw=eye.get('mouth',3)
    for i in range(mw): g[my][cx-mw//2+i]='o'
    if teeth: g[my+1][cx-mw//2]='t'; g[my+1][cx+mw//2]='t'
    # Muskeln (männlich): Brustlinien unter dem Mund, ab Stufe 3 Bauchlinien
    if sex=='m' and muscles>=1:
        py=my+3
        for i in range(2,5): put(g,cx-i,py,'d','bl'); put(g,cx+i,py,'d','bl')
        put(g,cx-1,py+1,'d','bl'); put(g,cx+1,py+1,'d','bl')
        if muscles>=2:
            for j in range(2,7): put(g,cx,py+j,'d','bl')
            for j in (3,5): put(g,cx-2,py+j,'d','bl'); put(g,cx+2,py+j,'d','bl')
    # Kopfschmuck
    stamp(g,horns['rows'],cx-horns['dx']-len(horns['rows'][0])+1,horns['y']); stamp(g,horns['rows'],cx+horns['dx'],horns['y'],mirror=True)
    # Vorne: Arme, Beine
    if arms:
        a=arms[sex]
        stamp(g,a['rows'],cx-a['dx']-len(a['rows'][0])+1,a['y']); stamp(g,a['rows'],cx+a['dx'],a['y'],mirror=True)
    if legs: stamp(g,legs['rows'],cx-legs['dx']-len(legs['rows'][0])+1,legs['y']); stamp(g,legs['rows'],cx+legs['dx'],legs['y'],mirror=True)
    return [''.join(r) for r in g]

EYE3={'rows':["eee","epp","epp"],'gap':2,'mouth':3}
EYE4={'rows':["eeee","eepp","eppp","eppp"],'gap':2,'mouth':3}
EYE4W={'rows':["eeee","eepp","eppp","eppp"],'gap':3,'mouth':5}
HORN_S={'rows':["h..",".h.","hh."],'dx':3}
HORN_M={'rows':["h...",".h..","hh..",".hh."],'dx':3}
HORN_L={'rows':["hh...",".hh..","..hh.","..hhh",".hhh."],'dx':3}
HORN_XL={'rows':["hhh....",".hhh...","..hhh..","...hhh.","...hhhh","..hhhh."],'dx':3}
# Arme: männlich kräftig mit Bizeps-Glanz, weiblich schmal
ARM_MS={'rows':["obbo","oblb","obbo",".oo."]}          # Stufe 2 männlich
ARM_ML={'rows':["obbbo.","obblbo","obbbbo",".obbo.","..oo.."]}
ARM_FS={'rows':["obo","ob.",".o."]}
ARM_FL={'rows':["obo.","obbo","obo.",".o.."]}
LEG_S={'rows':["obbo","oooo"],'dx':1}
LEG_M={'rows':["obbbo","obbbo","ooooo"],'dx':1}
TAIL={'rows':[".ob","obb","bbo","oo."]}
WING_M={'rows':["....o","...ob","..obb",".obbb","obbbb","odbbb",".oddb","..ooo"]}
WING_L={'rows':[".....o","....ob","...obb","..obbb",".obbbb","obbbbb","obbbbb","oddbbb",".odddb","..oddb","...ooo"]}
def d(base,**k): x=dict(base); x.update(k); return x

STAGES=[
 dict(lvl=1,  name='Winzling',    cell=6, W=19,H=23,cx=9,  body_top=4, body_h=16, rx=6.2, horns=d(HORN_S,y=1,dx=2), eyes_y=9,  eye=EYE3, legs=d(LEG_S,y=20), seed=3,
      flavor='Khaos ist gerade erst geschlüpft – ein Fellknäuel mit Hörnchen.'),
 dict(lvl=10, name='Wächst',      cell=6, W=21,H=27,cx=10, body_top=4, body_h=19, rx=6.4, horns=d(HORN_M,y=0,dx=2), eyes_y=10, eye=EYE3, arms={'m':d(ARM_MS,y=14,dx=6),'f':d(ARM_FS,y=15,dx=5)}, legs=d(LEG_S,y=23), muscles=1, seed=5,
      flavor='Er streckt sich, bekommt Arme und Beine – die Reise beginnt.'),
 dict(lvl=20, name='Kräftig',     cell=5, W=27,H=33,cx=13, body_top=5, body_h=23, rx=7.6, horns=d(HORN_M,y=1,dx=3), eyes_y=12, eye=EYE4, arms={'m':d(ARM_ML,y=17,dx=8),'f':d(ARM_FL,y=18,dx=5)}, legs=d(LEG_M,y=28), tail=d(TAIL,y=24,dx=7), muscles=2, seed=7,
      flavor='Schlanker, aufrechter, mit Schwanz – man sieht deinen Fortschritt.'),
 dict(lvl=30, name='Stark',       cell=5, W=29,H=35,cx=14, body_top=6, body_h=24, rx=8.0, horns=d(HORN_L,y=1,dx=3), eyes_y=13, eye=EYE4, arms={'m':d(ARM_ML,y=18,dx=9),'f':d(ARM_FL,y=19,dx=6)}, legs=d(LEG_M,y=30), tail=d(TAIL,y=25,dx=8), mane=True, teeth=True, muscles=2, seed=11,
      flavor='Fellkragen, Zähne, größere Hörner. Stark und treu an deiner Seite.'),
 dict(lvl=40, name='Mächtig',     cell=5, W=31,H=37,cx=15, body_top=7, body_h=25, rx=8.2, horns=d(HORN_L,y=2,dx=3), eyes_y=14, eye=EYE4, arms={'m':d(ARM_ML,y=19,dx=9),'f':d(ARM_FL,y=20,dx=6)}, legs=d(LEG_M,y=32), tail=d(TAIL,y=26,dx=8), wings=d(WING_M,y=13,dx=10), mane=True, teeth=True, muscles=2, seed=13,
      flavor='Flügel im Fell – mächtig und kaum wiederzuerkennen.'),
 dict(lvl=50, name='Kampfbestie', cell=5, W=33,H=39,cx=16, body_top=8, body_h=26, rx=8.4, horns=d(HORN_XL,y=2,dx=3), eyes_y=15, eye=EYE4W, arms={'m':d(ARM_ML,y=20,dx=10),'f':d(ARM_FL,y=21,dx=7)}, legs=d(LEG_M,y=34), tail=d(TAIL,y=27,dx=8), wings=d(WING_L,y=12,dx=10), mane=True, teeth=True, armor=True, muscles=2, seed=17,
      flavor='Die Kampfbestie ist erwacht – gepanzert, geflügelt, flauschig. Genau wie du.'),
]

def main():
    out=[]
    for s in STAGES:
        k={x:s[x] for x in s if x not in ('lvl','name','cell','flavor')}
        out.append({'lvl':s['lvl'],'name':s['name'],'cell':s['cell'],'flavor':s['flavor'],'body':build('m',**k),'femBody':build('f',**k)})
    js=json.dumps(out,ensure_ascii=False)
    print('  var COMPANION='+js.replace('},{','},\n   {').replace('"body":','\n    "body":').replace('"femBody":','\n    "femBody":')+';')
if __name__=='__main__': main()
