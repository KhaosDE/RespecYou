#!/usr/bin/env python3
"""Baut aus dem iOS/Web-Build eine in sich geschlossene Fassung zum Verschicken oder Veröffentlichen.

Die Schriften werden als data:-URI eingebettet und die Dokumenthülle entfernt, damit die Datei
auch dort läuft, wo keine Nachbardateien geladen werden können.
Aufruf: python3 tools/preview.py [zieldatei]
"""
import base64, os, re, sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,'dist','preview.html')

def font_uri(name):
    with open(os.path.join(ROOT,'docs','assets','fonts',name),'rb') as f:
        return 'data:font/ttf;base64,'+base64.b64encode(f.read()).decode('ascii')

def main():
    with open(os.path.join(ROOT,'docs','index.html'),encoding='utf-8') as f: h=f.read()
    for name in ('PressStart2P-Regular.ttf','VT323-Regular.ttf'):
        h=h.replace("url('assets/fonts/%s')"%name, "url('%s')"%font_uri(name))
    # Dokumenthülle und Verweise auf Nachbardateien entfernen
    h=re.sub(r'(?is)<!doctype[^>]*>','',h)
    h=re.sub(r'(?is)</?(html|head|body)[^>]*>','',h)
    # charset und viewport bleiben, sonst brechen die Umlaute beim direkten Öffnen
    h=re.sub(r'(?is)<link[^>]*rel="(manifest|apple-touch-icon|icon)"[^>]*>','',h)
    if '<title>' not in h: h='<title>RespecYou Testvariante</title>\n'+h
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,'w',encoding='utf-8') as f: f.write(h.strip()+'\n')
    print('%s  %.0f KB'%(OUT, os.path.getsize(OUT)/1024))

if __name__=='__main__': main()
