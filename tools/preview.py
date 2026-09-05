#!/usr/bin/env python3
"""Baut aus dem iOS/Web-Build eine in sich geschlossene Fassung zum Verschicken oder Veröffentlichen.

Die Schriften werden als data:-URI eingebettet und die Dokumenthülle entfernt, damit die Datei
auch dort läuft, wo keine Nachbardateien geladen werden können. Mit --test kommt unten ein
Knopf dazu, der den gespeicherten Stand löscht und den Einstieg neu startet.
Aufruf: python3 tools/preview.py [zieldatei] [--test]
"""
import base64, os, re, sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS=[a for a in sys.argv[1:] if not a.startswith('--')]
TEST='--test' in sys.argv
OUT=ARGS[0] if ARGS else os.path.join(ROOT,'dist','preview.html')

TEST_UI = """
<div style="position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;justify-content:center;
     padding:6px;background:rgba(0,0,0,.75);font-family:'Courier New',monospace">
  <button onclick="if(confirm('Test zurücksetzen? Der gespeicherte Fortschritt in dieser Vorschau wird gelöscht.')){try{localStorage.clear()}catch(e){};location.reload()}"
     style="font-family:inherit;font-size:11px;letter-spacing:1px;padding:7px 14px;background:#ffd93b;
     color:#111;border:3px solid #000;cursor:pointer">TEST ZURÜCKSETZEN</button>
</div>
"""

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
    if TEST: h=h.rstrip()+'\n'+TEST_UI
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    with open(OUT,'w',encoding='utf-8') as f: f.write(h.strip()+'\n')
    print('%s  %.0f KB'%(OUT, os.path.getsize(OUT)/1024))

if __name__=='__main__': main()
