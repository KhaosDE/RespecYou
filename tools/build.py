#!/usr/bin/env python3
"""Baut aus der gemeinsamen Quelle src/index.html die beiden Plattform-Fassungen.

  docs/index.html            iOS/Web (PWA, GitHub Pages, kein Store, keine geplanten Erinnerungen)
  dist/android/www/index.html  Android (Capacitor) - in das lokale Capacitor-Projekt nach www/ kopieren

Die Versionsnummern stehen in der Datei VERSION und laufen getrennt.
Aufruf: python3 tools/build.py
"""
import os, re, shutil, sys

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def versions():
    v={}
    with open(os.path.join(ROOT,'VERSION'),encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if line and '=' in line:
                k,_,val=line.partition('='); v[k.strip()]=val.strip()
    return v

def render(src, platform, version):
    out=src.replace('__PLATFORM__',platform).replace('__VERSION__',version)
    left=[m for m in ('__PLATFORM__','__VERSION__') if m in out]
    if left: sys.exit('Platzhalter nicht ersetzt: '+', '.join(left))
    return out

def bump_sw(path, version):
    """Cache-Name an die Version binden, damit ein Update sicher ankommt."""
    with open(path,encoding='utf-8') as f: sw=f.read()
    sw=re.sub(r"const CACHE = '[^']*';", "const CACHE = 'respecyou-ios-%s';"%version, sw, count=1)
    with open(path,'w',encoding='utf-8') as f: f.write(sw)

def main():
    v=versions()
    with open(os.path.join(ROOT,'src','index.html'),encoding='utf-8') as f: src=f.read()

    ios=os.path.join(ROOT,'docs','index.html')
    with open(ios,'w',encoding='utf-8') as f: f.write(render(src,'ios',v['ios']))
    bump_sw(os.path.join(ROOT,'docs','sw.js'), v['ios'])

    andir=os.path.join(ROOT,'dist','android','www')
    os.makedirs(andir,exist_ok=True)
    with open(os.path.join(andir,'index.html'),'w',encoding='utf-8') as f: f.write(render(src,'android',v['android']))
    fonts_src=os.path.join(ROOT,'docs','assets')
    fonts_dst=os.path.join(andir,'assets')
    if os.path.isdir(fonts_src):
        shutil.rmtree(fonts_dst,ignore_errors=True); shutil.copytree(fonts_src,fonts_dst)

    print('docs/index.html            iOS  %s'%v['ios'])
    print('dist/android/www/index.html Android %s'%v['android'])

if __name__=='__main__': main()
