#!/usr/bin/env python3
"""Erzeugt die Pixel-Raster für Khaos: runder Fellklumpen mit großen Augen, Wangenröte,
Fangzähnen, Ohren und stämmigen Füßen. Sechs Stufen in drei Entwicklungsformen (die Silhouette
springt, statt nur zu wachsen), jede männlich und weiblich.

  Form 1 (Stufe 1-2): Fellknäuel, Ohren, winkender Arm, keine Hörner
  Form 2 (Stufe 3-4): aufrecht, Hörner brechen durch, Schwanz, dichter Fellkragen
  Form 3 (Stufe 5-6): Flügel, große Hörner, Brustpanzer

Ohren, Arme, Füße und Schwanz gehören zur SILHOUETTE: erst wird eine gemeinsame Maske gebaut,
dann laufen Fellkante und Umriss einmal außen herum. Nur Flügel liegen als eigene Ebene dahinter.

Zeichen: . leer | o Umriss | b Fell | d Fellschatten | l helles Fell/Bauch | h Horn
         e Lichtpunkt im Auge | p Auge/Mundinnenraum | t Fangzahn | a Rüstung | r Wangenröte
Aufruf: python3 tools/khaos_gen.py > /tmp/khaos.js   (Ausgabe in docs/index.html einsetzen)
"""
import math, json

def grid(W,H): return [['.']*W for _ in range(H)]
def newmask(W,H): return [[False]*W for _ in range(H)]

def half_width(y,cy,rx,ry,sex,squish=2.5):
    """Halbe Körperbreite in Zeile y. Männlich: breitere Schultern. Weiblich: Taille + Hüfte."""
    t=(y+0.5-cy)/ry
    if abs(t)>1: return 0.0
    w=rx*(1-abs(t)**squish)**(1.0/squish)
    if sex=='f':
        w*=1-0.16*math.exp(-((t-0.05)/0.30)**2)
        w*=1+0.13*math.exp(-((t-0.60)/0.28)**2)
    else:
        w*=1+0.17*math.exp(-((t+0.35)/0.32)**2)
        w*=1-0.04*math.exp(-((t-0.30)/0.30)**2)
    return w

def add_body(m,W,H,cx,cy,rx,ry,sex):
    for y in range(H):
        w=half_width(y,cy,rx,ry,sex)
        if w<=0: continue
        for x in range(W):
            if abs(x+0.5-cx)<=w: m[y][x]=True

def add_ellipse(m,W,H,cx,cy,rx,ry):
    for y in range(H):
        for x in range(W):
            dx=(x+0.5-cx)/rx; dy=(y+0.5-cy)/ry
            if dx*dx+dy*dy<=1.0: m[y][x]=True

def add_ear(m,W,H,x0,base_y,h,dirn):
    """Ohr als sich verjüngendes Dreieck, das vom Kopf aus nach oben-außen zeigt."""
    cxf=float(x0)
    for i in range(h):
        y=base_y-i
        w=(h-i)*0.52
        for x in range(int(round(cxf-w)), int(round(cxf+w))+1):
            if 0<=x<W and 0<=y<H: m[y][x]=True
        cxf+=dirn*0.62

def add_arm(m,W,H,x0,y0,length,thick,dirn,raised=False):
    """Arm am Körper: raised = schräg nach oben-außen (winken), sonst gerade nach unten-außen."""
    xf=float(x0); yf=float(y0)
    for i in range(length):
        for t in range(thick):
            for u in range(thick):
                x=int(round(xf))+dirn*t; y=int(round(yf))+u
                if 0<=x<W and 0<=y<H: m[y][x]=True
        xf+=dirn*1.0
        yf+= -1.0 if raised else 1.0

def add_foot(m,W,H,cx,cy,rx,ry): add_ellipse(m,W,H,cx,cy,rx,ry)

def add_tail(m,W,H,x0,y0,n,dirn):
    xf=float(x0); yf=float(y0)
    for i in range(n):
        r=1.6-0.08*i
        add_ellipse(m,W,H,xf,yf,r,r)
        xf+=dirn*1.15; yf-=0.55

def fur_edge(m,W,H,seed=3,dense=False):
    out=[row[:] for row in m]
    for y in range(H):
        for x in range(W):
            if not m[y][x]: continue
            for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H and not m[ny][nx]:
                    k=(x*7+y*3+seed)%(3 if dense else 5)
                    if (dy!=0 and k in (0,2)) or (dy==0 and k==1): out[ny][nx]=True
    return out

def outline(m,W,H):
    o=newmask(W,H)
    for y in range(H):
        for x in range(W):
            if m[y][x]: continue
            for dx,dy in ((0,-1),(0,1),(-1,0),(1,0)):
                nx,ny=x+dx,y+dy
                if 0<=nx<W and 0<=ny<H and m[ny][nx]: o[y][x]=True
    return o

def stamp(g,rows,x0,y0,mirror=False):
    for j,row in enumerate(rows):
        r=row[::-1] if mirror else row
        for i,ch in enumerate(r):
            if ch=='.': continue
            x,y=x0+i,y0+j
            if 0<=y<len(g) and 0<=x<len(g[0]): g[y][x]=ch

def paint(g,m,ch):
    for y,row in enumerate(m):
        for x,v in enumerate(row):
            if v: g[y][x]=ch

def put(g,x,y,ch,only=None):
    if 0<=y<len(g) and 0<=x<len(g[0]) and (only is None or g[y][x] in only): g[y][x]=ch

# Augen: dunkle Iris mit weißem Lichtpunkt oben links. Beide Augen gleich (Licht kommt von links),
# darum werden sie NICHT gespiegelt.
EYE_S=[".pp.","pepp","pppp",".pp."]
EYE_M=[".ppp.","peppp","peppp","ppppp",".ppp."]
EYE_L=[".pppp.","peepppp"[:6],"peeppp","pppppp","pppppp",".pppp."]
EYE_GAP={4:2,5:2,6:3}
HORN_M=["h...",".h..","hh..",".hh."]
HORN_L=["hh...",".hh..","..hh.","..hhh",".hhh."]
HORN_XL=["hhh....",".hhh...","..hhh..","...hhh.","...hhhh","..hhhh."]

def build(sex, W,H,cx, body_top, body_h, rx, eyes_y, eye, ear_h, arm, foot,
          horns=None, tail=None, wing=None, mane=False, armor=False, fangs=1, muscles=0, seed=3):
    ry=body_h/2.0; cy=body_top+ry
    rxs = rx*0.93 if sex=='f' else rx*1.05
    g=grid(W,H)

    # ---- Flügel als eigene Ebene hinter dem Körper ----
    if wing:
        wm=newmask(W,H)
        for dirn in (-1,1):
            xf=cx+dirn*int(round(rxs*0.75)); yf=wing['y']
            for i in range(wing['len']):
                h=wing['h']-i*0.55
                for u in range(max(1,int(round(h)))):
                    x=int(round(xf)); y=int(round(yf))+u
                    if 0<=x<W and 0<=y<H: wm[y][x]=True
                xf+=dirn*1.0; yf-=0.35
        paint(g,outline(wm,W,H),'o'); paint(g,wm,'d')

    # ---- Gemeinsame Silhouette: Körper + Ohren + Arme + Füße + Schwanz ----
    sil=newmask(W,H)
    add_body(sil,W,H,cx+0.5,cy,rxs,ry,sex)
    ear_base=body_top+max(1,ear_h//3)
    ex=int(round(rxs*0.58))
    add_ear(sil,W,H,cx-ex,ear_base,ear_h,-1)
    add_ear(sil,W,H,cx+ex,ear_base,ear_h,+1)
    thick=arm.get('thick',2) if sex=='m' else max(1,arm.get('thick',2)-1)
    ay=arm['y']; hw=int(round(half_width(ay,cy,rxs,ry,sex)))-1
    add_arm(sil,W,H,cx-hw,ay,arm['len'],thick,-1,arm.get('raised',False))  # winkt nur in Form 1
    ay2=int(round(cy+ry*0.34)); hw2=int(round(half_width(ay2,cy,rxs,ry,sex)))-1
    add_arm(sil,W,H,cx+hw2,ay2,max(2,arm['len']-1),thick,+1,False)
    fy=int(round(cy+ry))
    fhw=half_width(fy-2,cy,rxs,ry,sex)
    for dirn in (-1,1):
        add_foot(sil,W,H,cx+0.5+dirn*fhw*0.52,fy,foot['rx'],foot['ry'])
    if tail: add_tail(sil,W,H,cx+rxs*0.85,cy+ry*0.72,tail,+1)

    fur=fur_edge(sil,W,H,seed)
    if mane:
        fur2=fur_edge(fur,W,H,seed+2,dense=True)
        for y in range(H):
            if y<cy-ry*0.20: fur[y]=fur2[y]
    ol=outline(fur,W,H)
    paint(g,fur,'b')

    # ---- Bauch, Schatten, Glanz ----
    belly=newmask(W,H); add_ellipse(belly,W,H,cx+0.5,cy+ry*0.40,rxs*(0.40 if sex=='f' else 0.46),ry*0.38)
    for y in range(H):
        for x in range(W):
            if belly[y][x] and sil[y][x]: g[y][x]='l'
    for y in range(H):
        for x in range(W):
            if not sil[y][x] or g[y][x]!='b': continue
            dx=(x+0.5-cx-0.5)/rxs; dy=(y+0.5-cy)/ry; r=dx*dx+dy*dy
            if r>0.70 and dx>0.32 and dy>-0.20: g[y][x]='d'
            elif r>0.52 and (x*5+y*11+seed)%13==0: g[y][x]='d'
            elif r<0.40 and dx<-0.12 and dy<-0.22 and (x+y)%4==0: g[y][x]='l'
    # Innenohr hell
    for dirn,exx in ((-1,cx-ex),(1,cx+ex)):
        inner=newmask(W,H); add_ear(inner,W,H,exx+dirn,ear_base-1,max(1,ear_h-2),dirn)
        for y in range(H):
            for x in range(W):
                if inner[y][x] and sil[y][x]: g[y][x]='l'
    if armor:
        ar=newmask(W,H); add_ellipse(ar,W,H,cx+0.5,cy+ry*0.26,rxs*0.46,ry*0.26)
        for y in range(H):
            for x in range(W):
                if ar[y][x] and sil[y][x]: g[y][x]='a'
        for y,row in enumerate(outline(ar,W,H)):
            for x,v in enumerate(row):
                if v and sil[y][x]: g[y][x]='o'
    paint(g,ol,'o')

    # ---- Gesicht ----
    ew=len(eye[0]); gap=EYE_GAP[ew]
    lx=cx-gap-ew+1; rx0=cx+gap
    stamp(g,eye,lx,eyes_y); stamp(g,eye,rx0,eyes_y)
    if sex=='f':
        for xx in (lx-1,lx,rx0+ew-1,rx0+ew): put(g,xx,eyes_y-1,'o','bdl')
    by=eyes_y+len(eye)
    for i in range(2):
        for yy in (by,by+1):
            put(g,lx-1+i,yy,'r','bdl'); put(g,rx0+ew-2+i,yy,'r','bdl')
    my=eyes_y+len(eye)+1
    for i in (-1,0,1): put(g,cx+i,my,'o')
    put(g,cx-1,my+1,'t'); put(g,cx,my+1,'p'); put(g,cx+1,my+1,'t')
    if fangs>=2:
        put(g,cx-2,my,'o'); put(g,cx+2,my,'o')
        put(g,cx-2,my+1,'t'); put(g,cx+2,my+1,'t'); put(g,cx,my+2,'o')
    if sex=='m' and muscles>=1:
        py=my+3
        for i in range(2,5): put(g,cx-i,py,'d','bl'); put(g,cx+i,py,'d','bl')
        put(g,cx-1,py+1,'d','bl'); put(g,cx+1,py+1,'d','bl')
        if muscles>=2:
            for j in range(2,7): put(g,cx,py+j,'d','bl')
            for j in (3,5): put(g,cx-2,py+j,'d','bl'); put(g,cx+2,py+j,'d','bl')
    if horns:
        stamp(g,horns['rows'],cx-horns['dx']-len(horns['rows'][0])+1,horns['y'])
        stamp(g,horns['rows'],cx+horns['dx'],horns['y'],mirror=True)
    return [''.join(r) for r in g]

def d(base,**k):
    x=dict(base) if isinstance(base,dict) else {'rows':base}
    x.update(k); return x

STAGES=[
 dict(lvl=1,  name='Fellknäuel', cell=6, W=23,H=25,cx=11, body_top=6, body_h=14, rx=6.6, eyes_y=10, eye=EYE_S,
      ear_h=4, arm=dict(y=12,len=2,thick=2,raised=True), foot=dict(rx=2.2,ry=1.6), fangs=1, seed=3,
      flavor='Frisch geschlüpft: ein Fellknäuel mit großen Augen, das dir zuwinkt.'),
 dict(lvl=10, name='Struppel',   cell=6, W=25,H=29,cx=12, body_top=7, body_h=17, rx=7.0, eyes_y=12, eye=EYE_M,
      ear_h=5, arm=dict(y=15,len=3,thick=2,raised=True), foot=dict(rx=2.4,ry=1.8), fangs=1, muscles=1, seed=5,
      flavor='Die Ohren werden lang, die Arme kräftiger. Struppel legt los.'),
 dict(lvl=20, name='Hornfell',   cell=5, W=29,H=34,cx=14, body_top=8, body_h=20, rx=7.8, eyes_y=14, eye=EYE_M,
      ear_h=6, arm=dict(y=17,len=2,thick=3), foot=dict(rx=2.6,ry=1.9), horns=d(HORN_M,y=4,dx=2), tail=5, fangs=1, muscles=2, seed=7,
      flavor='Erste Entwicklung: die Hörner brechen durch, ein Schwanz kommt dazu.'),
 dict(lvl=30, name='Wildkhaos',  cell=5, W=31,H=36,cx=15, body_top=9, body_h=21, rx=8.2, eyes_y=15, eye=EYE_M,
      ear_h=6, arm=dict(y=18,len=2,thick=3), foot=dict(rx=2.8,ry=2.0), horns=d(HORN_L,y=4,dx=2), tail=5, mane=True, fangs=2, muscles=2, seed=11,
      flavor='Dichter Fellkragen, längere Hörner, echte Fangzähne. Wild und treu.'),
 dict(lvl=40, name='Sturmkhaos', cell=5, W=37,H=39,cx=18, body_top=10, body_h=22, rx=8.4, eyes_y=17, eye=EYE_L,
      ear_h=7, arm=dict(y=20,len=3,thick=3), foot=dict(rx=2.8,ry=2.0), horns=d(HORN_L,y=5,dx=2), tail=6,
      wing=dict(y=14,len=6,h=9), mane=True, fangs=2, muscles=2, seed=13,
      flavor='Zweite Entwicklung: Flügel entfalten sich aus dem Fell.'),
 dict(lvl=50, name='Kampfbestie',cell=5, W=39,H=42,cx=19, body_top=11, body_h=23, rx=8.6, eyes_y=19, eye=EYE_L,
      ear_h=7, arm=dict(y=22,len=3,thick=3), foot=dict(rx=3.0,ry=2.1), horns=d(HORN_XL,y=5,dx=2), tail=6,
      wing=dict(y=15,len=8,h=11), mane=True, armor=True, fangs=2, muscles=2, seed=17,
      flavor='Endform: gepanzert, geflügelt, flauschig. Genau wie du.'),
]

def main():
    out=[]
    for s in STAGES:
        k={x:s[x] for x in s if x not in ('lvl','name','cell','flavor')}
        out.append({'lvl':s['lvl'],'name':s['name'],'cell':s['cell'],'flavor':s['flavor'],
                    'body':build('m',**k),'femBody':build('f',**k)})
    js=json.dumps(out,ensure_ascii=False)
    print('  var COMPANION='+js.replace('},{','},\n   {').replace('"body":','\n    "body":').replace('"femBody":','\n    "femBody":')+';')
if __name__=='__main__': main()
