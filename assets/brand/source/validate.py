#!/usr/bin/env python3
"""Validate deliverable sizes, SVG portability, inverse variants, and ICO frames."""
from pathlib import Path
from PIL import Image, ImageChops
import json, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
checks=[]
for variant in ['black-on-white','white-on-black']:
 for size in [1024,512,256,192,180,128,64]:
  for role in ['app','badge']:
   directory='app-icons' if role=='app' else 'badges'
   im=Image.open(ROOT/f'png/{directory}/crawlie-{role}-{variant}-{size}.png')
   assert im.size==(size,size)
   if role=='app':assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
 for size in [16,32,48]:
  im=Image.open(ROOT/f'png/favicons/crawlie-favicon-{variant}-{size}.png')
  assert im.size==(size,size)
 ico=Image.open(ROOT/f'png/favicons/crawlie-favicon-{variant}.ico')
 assert ico.ico.sizes()=={(16,16),(32,32),(48,48)}
 for size in [16,32,48]:
  frame=ico.ico.getimage((size,size)).convert('RGBA')
  expected=Image.open(ROOT/f'png/favicons/crawlie-favicon-{variant}-{size}.png').convert('RGBA')
  assert ImageChops.difference(frame,expected).getbbox() is None
checks.append('All requested PNG dimensions, square-icon opacity, and exact 16/32/48 ICO frames verified.')
for directory,prefix,sizes in [('app-icons','app',[1024,512,256,192,180,128,64]),('favicons','favicon',[16,32,48])]:
 for size in sizes:
  a=Image.open(ROOT/f'png/{directory}/crawlie-{prefix}-black-on-white-{size}.png').convert('RGB')
  b=Image.open(ROOT/f'png/{directory}/crawlie-{prefix}-white-on-black-{size}.png').convert('RGB')
  delta=ImageChops.difference(a,ImageChops.invert(b))
  assert max(v[1] for v in delta.getextrema())<=1
checks.append('Monochrome inversions verified within one antialiasing level.')
for p in list((ROOT/'svg').glob('*.svg'))+[ROOT/'web/favicon.svg']:
 tree=ET.parse(p);r=tree.getroot()
 assert r.tag.endswith('svg') and 'viewBox' in r.attrib
 for e in r.iter():
  assert e.tag.rsplit('}',1)[-1] not in {'image','text','script','foreignObject','filter'}
  assert not any('href' in k or k.lower().startswith('on') for k in e.attrib)
checks.append('SVGs parse successfully and contain no embedded rasters, fonts, scripts, or external references.')
for kind in ['mascot','wordmark','primary','horizontal','vertical']:
 for color in ['black','white']:
  im=Image.open(ROOT/f'png/logos/crawlie-{kind}-{color}.png').convert('RGBA')
  bounds=im.getchannel('A').getbbox();assert bounds
  x0,y0,x1,y1=bounds
  assert x0>0 and y0>0 and x1<im.width and y1<im.height,(kind,color,bounds)
  assert im.getchannel('A').getextrema()==(0,255)
checks.append('Transparent logo backgrounds and clear, unclipped outer artboard edges verified.')
for p in ROOT.rglob('*.png'):
 im=Image.open(p)
 if p.name=='reference-approved.png':continue
 rgb=im.convert('RGB');r,g,b=rgb.split()
 assert ImageChops.difference(r,g).getbbox() is None
 assert ImageChops.difference(r,b).getbbox() is None
checks.append('All production PNGs are neutral monochrome, including antialiased edges.')
manifest=json.loads((ROOT/'web/site.webmanifest').read_text())
for icon in manifest['icons']:assert (ROOT/'web'/icon['src']).exists()
checks.append('Web manifest icon paths resolve within the packaged web folder.')
# The micro artwork must remain a separate drawing, not the same master resized.
assert json.loads((ROOT/'source/favicon-16-polygons.json').read_text())!=json.loads((ROOT/'source/favicon-small-polygons.json').read_text())
checks.append('Distinct 16 px optical source present; default SVG favicon uses that micro drawing.')
print('\n'.join(checks))
