#!/usr/bin/env python3
"""Regenerate the compact profile artwork from the saved portrait character grid.
Python 3.10+, no extra packages. Run: python scripts/generate_art.py
"""
import json
from pathlib import Path
import re
from html import escape
from make_portrait import render_svg as render_portrait

ROOT = Path(__file__).resolve().parents[1]

def information_card():
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="440" height="540" viewBox="0 0 440 540" role="img" aria-labelledby="info-title info-desc">',
       '<title id="info-title">Geetha Bonthu — Analytics Engineer</title>',
       '<desc id="info-desc">Four-plus years turning data into decisions. SQL, Python, dbt, Azure, Databricks and Power BI. Marketing and product analytics. Building toward AI engineering. MS Business Analytics, University of Cincinnati.</desc>',
       '<style>.info-text{font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace}.info-line{opacity:1;animation:info-print .4s ease-out both;animation-delay:var(--delay)}@keyframes info-print{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}@media(prefers-reduced-motion:reduce){.info-line{animation:none}}</style>',
       '<rect x=".5" y=".5" width="439" height="539" rx="7" fill="#0d1117" stroke="#21262d"/>',
       '<path d="M1 31H439M24 175H416M24 465H416" stroke="#21262d"/>',
       '<circle cx="13" cy="16" r="3" fill="#ef6a60"/><circle cx="25" cy="16" r="3" fill="#e5c052"/><circle cx="37" cy="16" r="3" fill="#53bd68"/>',
       '<text class="info-text" x="220" y="19" text-anchor="middle" font-size="8" fill="#84919f">geetha@github:~ $ whoami</text>']
    def line(y,value,size=13,color='#c9d1d9',weight=400,delay=.1):
        p.append(f'<text class="info-text info-line" x="26" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" style="--delay:{delay}s">{escape(value)}</text>')
    line(87,'Geetha Bonthu',28,'#f0f6fc',700)
    line(119,'Analytics Engineer',19,'#7ee787',500,.2)
    line(150,'Data noise → clear decisions.',13,'#c9d1d9',400,.3)
    rows=[(208,'BUILD','Models, pipelines & dashboards'),(276,'STACK','SQL · Python · dbt','Azure · Databricks · Power BI'),(364,'FOCUS','Marketing & product analytics','Building toward AI engineering')]
    for index,row in enumerate(rows):
        y,label,*values=row
        line(y,'$ '+label.lower(),11,'#7ee787',400,.4+index*.15)
        for j,value in enumerate(values): line(y+25+j*24,value,13,'#c9d1d9',400,.5+index*.15)
    line(491,'4+ years in analytics',12,'#e6edf3',500,.95)
    line(518,'MS Business Analytics · Cincinnati',11,'#8b949e',400,1.05)
    p.append('</svg>')
    return '\n'.join(p)+'\n'

def contents(svg):
    return re.sub(r'^<svg\b[^>]*>', '', svg.strip(), count=1).rsplit('</svg>',1)[0]

def compose(portrait,info,mobile=False):
    width,height=(440,1100) if mobile else (900,540)
    x,y=(0,560) if mobile else (460,0)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="profile-title profile-desc">\n'
            '<title id="profile-title">Geetha Bonthu — animated ASCII portrait</title>\n'
            '<desc id="profile-desc">Geetha’s photo converted to characters beside a short introduction as an Analytics Engineer. The portrait prints row by row, then stays visible.</desc>\n'
            + '<g>'+contents(portrait)+'</g>\n'
            +f'<g transform="translate({x} {y})">'+contents(info)+'</g>\n</svg>\n')

def main():
    assets=ROOT/'assets'
    portrait=render_portrait(json.loads((ROOT/'data/portrait.json').read_text()))
    info=information_card()
    for name,body in [('portrait.svg',portrait),('info-card.svg',info),('profile.svg',compose(portrait,info)),('profile-mobile.svg',compose(portrait,info,True))]:
        (assets/name).write_text(body,encoding='utf-8')
        print('Generated assets/'+name)

if __name__=='__main__': main()
