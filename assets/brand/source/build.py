#!/usr/bin/env python3
"""Build Crawlie assets from editable polygons. Requires Python 3, Pillow and rsvg-convert."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, io, json, shutil, struct, subprocess, hashlib, zipfile, math

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source'

def load(name):return json.loads((SRC/name).read_text())
mascot=load('mascot-polygons.json')
wordmark=load('wordmark-polygons.json')
small=load('favicon-small-polygons.json')
micro=load('favicon-16-polygons.json')

def path(poly):return 'M'+' '.join(f'{x:g},{y:g}' for x,y in poly)+'Z'
def shapes(polys,color):return ''.join(f'<path fill="{color}" d="{path(p)}"/>' for p in polys)
def letters(color):return ''.join(f'<path fill="{color}" fill-rule="evenodd" d="'+ ' '.join(path(p) for p in glyph)+'"/>' for glyph in wordmark)
def group(content,x=0,y=0,scale=1):return f'<g transform="translate({x} {y}) scale({scale})">{content}</g>'
def svg(w,h,content,title,bg=None):
 back=f'<path fill="{bg}" d="M0 0H{w}V{h}H0Z"/>' if bg else ''
 return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">
<title id="title">{title}</title>
{back}{content}
</svg>
'''
def save(rel,data):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data);return p

def render(src,dest,width,height=None):
 dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
 cmd=['rsvg-convert','--width',str(width)]
 if height:cmd+=['--height',str(height)]
 subprocess.run(cmd+[str(src),'-o',str(dest)],check=True,capture_output=True)

def layout(kind,color):
 m=shapes(mascot,color);w=letters(color)
 if kind=='mascot':return 680,460,m
 if kind=='wordmark':return 741,199,group(w,20,20)
 if kind=='primary':return 800,675,group(m,26,0,1.1)+group(w,49.5,490)
 if kind=='horizontal':return 1220,380,group(m,0,28,.7)+group(w,479,85)
 if kind=='vertical':return 800,760,group(m,26,28,1.1)+group(w,49.5,565)
 raise ValueError(kind)

variants={'black':('#000000',None),'white':('#FFFFFF',None),'black-on-white':('#000000','#FFFFFF'),'white-on-black':('#FFFFFF','#000000')}
for kind in ['mascot','wordmark','primary','horizontal','vertical']:
 for variant,(color,bg) in variants.items():
  w,h,content=layout(kind,color)
  p=save(f'svg/crawlie-{kind}-{variant}.svg',svg(w,h,content,f'Crawlie {kind} — {variant}',bg))
  render(p,ROOT/f'png/logos/crawlie-{kind}-{variant}.png',2048 if kind!='mascot' else 1600)

sizes=[1024,512,256,192,180,128,64]
# Platform icons have opaque square backgrounds. The OS supplies its own mask.
for variant,(color,bg) in {k:v for k,v in variants.items() if v[1]}.items():
 angle=18; c=math.cos(math.radians(angle)); s=math.sin(math.radians(angle))
 points=[(x*c-y*s,x*s+y*c) for poly in mascot for x,y in poly]
 x0=min(x for x,y in points);x1=max(x for x,y in points)
 y0=min(y for x,y in points);y1=max(y for x,y in points)
 scale=820/max(x1-x0,y1-y0)
 tx=512-scale*(x0+x1)/2;ty=512-scale*(y0+y1)/2
 content=f'<g transform="translate({tx:.4f} {ty:.4f}) scale({scale:.6f}) rotate(18)">{shapes(mascot,color)}</g>'
 p=save(f'svg/crawlie-app-{variant}.svg',svg(1024,1024,content,f'Crawlie app icon — {variant}',bg))
 for size in sizes:render(p,ROOT/f'png/app-icons/crawlie-app-{variant}-{size}.png',size,size)
 badge=save(f'svg/crawlie-badge-{variant}.svg',svg(1024,1024,f'<rect width="1024" height="1024" rx="176" fill="{bg}"/>'+content,f'Crawlie rounded badge — {variant}'))
 for size in sizes:render(badge,ROOT/f'png/badges/crawlie-badge-{variant}-{size}.png',size,size)
 # Small optical favicon masters: no hairlines, fewer spines, broader gaps.
 for name,polys,dim in [('small',small,64),('16',micro,16)]:
  p=save(f'svg/crawlie-favicon-{name}-{variant}.svg',svg(dim,dim,shapes(polys,color),f'Crawlie optical favicon {name} — {variant}',bg))
  for size in ([32,48] if name=='small' else [16]):render(p,ROOT/f'png/favicons/crawlie-favicon-{variant}-{size}.png',size,size)

# Default web assets, ready to copy to /brand/.
web=ROOT/'web';web.mkdir(exist_ok=True)
for size in [192,512]:shutil.copyfile(ROOT/f'png/app-icons/crawlie-app-white-on-black-{size}.png',web/f'icon-{size}.png')
shutil.copyfile(ROOT/'png/app-icons/crawlie-app-white-on-black-180.png',web/'apple-touch-icon.png')
for size in [16,32,48]:shutil.copyfile(ROOT/f'png/favicons/crawlie-favicon-white-on-black-{size}.png',web/f'favicon-{size}.png')
# SVG uses the optical 16px drawing because browser tabs can render it at 16 CSS px.
shutil.copyfile(ROOT/'svg/crawlie-favicon-16-white-on-black.svg',web/'favicon.svg')

def make_ico(paths,dest):
 entries=[];payloads=[];offset=6+16*len(paths)
 for p in paths:
  im=Image.open(p).convert('RGBA');w,h=im.size
  # Windows ICO DIB: 32-bit BGRA, bottom-up bitmap; doubled height includes AND mask.
  rgba=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  pixels=rgba.tobytes('raw','BGRA')
  and_mask=b'\0'*(((w+31)//32)*4*h)
  dib=struct.pack('<IIIHHIIIIII',40,w,h*2,1,32,0,len(pixels)+len(and_mask),0,0,0,0)+pixels+and_mask
  entries.append(struct.pack('<BBBBHHII',w if w<256 else 0,h if h<256 else 0,0,0,1,32,len(dib),offset))
  payloads.append(dib);offset+=len(dib)
 Path(dest).write_bytes(struct.pack('<HHH',0,1,len(paths))+b''.join(entries)+b''.join(payloads))
for variant in ['white-on-black','black-on-white']:
 make_ico([ROOT/f'png/favicons/crawlie-favicon-{variant}-{s}.png' for s in [16,32,48]],ROOT/f'png/favicons/crawlie-favicon-{variant}.ico')
shutil.copyfile(ROOT/'png/favicons/crawlie-favicon-white-on-black.ico',web/'favicon.ico')
save('web/site.webmanifest',json.dumps({'name':'Crawlie','short_name':'Crawlie','icons':[{'src':f'icon-{s}.png','sizes':f'{s}x{s}','type':'image/png','purpose':'any'} for s in [192,512]],'theme_color':'#000000','background_color':'#000000','display':'standalone'},indent=2)+'\n')

# A plain local usage gallery doubles as an inspection surface.
sections=[]
for kind in ['primary','horizontal','vertical','wordmark','mascot']:
 sections.append(f'<section><h2>{kind}</h2><div class="pair"><figure><img src="svg/crawlie-{kind}-black.svg" alt="Crawlie {kind}"></figure><figure class="dark"><img src="svg/crawlie-{kind}-white.svg" alt="Crawlie {kind} inverted"></figure></div></section>')
fav=''.join(f'<div><img width="{s}" height="{s}" src="web/favicon-{s}.png" alt="{s} pixel favicon"><p>{s} × {s} native size</p><img class="pixel" width="192" src="web/favicon-{s}.png" alt="Enlarged {s} pixel favicon"></div>' for s in [16,32,48])
save('preview.html','''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crawlie · brand assets</title><style>*{box-sizing:border-box}body{margin:0;background:#eee;color:#000;font:15px Arial,sans-serif}main{max-width:1280px;margin:auto;padding:40px}h1{font-size:40px;letter-spacing:-2px}h2{text-transform:uppercase;font:12px monospace;letter-spacing:3px;margin:40px 0 12px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#ccc}figure{margin:0;padding:40px;height:330px;background:white;display:grid;place-items:center}figure img{max-width:100%;max-height:100%}.dark{background:black}.fav{display:flex;gap:60px;align-items:start;flex-wrap:wrap}.pixel{image-rendering:pixelated}a{color:inherit}@media(max-width:650px){main{padding:20px}.pair{grid-template-columns:1fr}figure{height:260px}}</style><main><h1>Crawlie / asset system</h1><p>Geometric mascot. Outlined lettering. Black and white.</p>'''+''.join(sections)+f'<section><h2>Optical favicons</h2><div class="fav">{fav}</div></section><p><a href="README.md">Usage & file guide</a></p></main></html>')

# Editorial contact sheet, composed only from the exported files.
W,H=1800,1940
sheet=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(sheet)
fontroot=Path('/Users/laponfire/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/reportlab/fonts')
regular=fontroot/'Vera.ttf';bold=fontroot/'VeraBd.ttf'
def font(sz,b=False):
 try:return ImageFont.truetype(str(bold if b else regular),sz)
 except OSError:return ImageFont.load_default(size=sz)
def text(x,y,s,size=18,color='black',b=False):d.text((x,y),s,font=font(size,b),fill=color)
def line(y):d.line((48,y,W-48,y),fill='#bbb',width=1)
def place(rel,box,bg=None):
 im=Image.open(ROOT/rel).convert('RGBA');im.thumbnail((box[2],box[3]),Image.Resampling.LANCZOS)
 x=round(box[0]+(box[2]-im.width)/2);y=round(box[1]+(box[3]-im.height)/2)
 sheet.paste(im,(x,y),im)
text(48,30,'CRAWLIE / BRAND ASSET SYSTEM',28,b=True)
text(48,76,'01  /  GEOMETRIC LARVA     •     BLACK + WHITE     •     VECTOR MASTERS',15)
line(116)
text(48,140,'PRIMARY LOGO',14)
place('png/logos/crawlie-primary-black.png',(50,176,995,650))
d.rounded_rectangle((1100,162,1752,814),radius=112,fill='black')
place('png/badges/crawlie-badge-white-on-black-1024.png',(1100,162,652,652))
text(1100,832,'ROUNDED BADGE / INVERTED',14)
line(880)
text(48,906,'HORIZONTAL LOCKUP',14)
place('png/logos/crawlie-horizontal-black.png',(48,944,1050,280))
d.rectangle((1140,902,1752,1225),fill='black')
place('png/logos/crawlie-wordmark-white.png',(1180,955,532,190))
text(1180,1180,'OUTLINED WORDMARK',14,'white')
line(1250)
text(48,1274,'APP ICONS / OPAQUE SQUARE MASTERS',14)
thumbs=[(1024,220),(512,190),(256,160),(192,140),(180,125),(128,105),(64,64)]
x=48
for size,display in thumbs:
 im=Image.open(ROOT/f'png/app-icons/crawlie-app-white-on-black-{size}.png').convert('RGB').resize((display,display),Image.Resampling.LANCZOS)
 sheet.paste(im,(x,1330+(220-display)//2));text(x,1574,str(size)+' × '+str(size),14);x+=display+64
line(1620)
text(48,1644,'OPTICAL FAVICONS / NATIVE SIZE + PIXEL INSPECTION',14)
x=48
for size in [16,32,48]:
 im=Image.open(ROOT/f'web/favicon-{size}.png').convert('RGB')
 sheet.paste(im,(x,1690));sheet.paste(im.resize((144,144),Image.Resampling.NEAREST),(x+80,1688))
 text(x,1850,f'{size} × {size}',14);x+=330
text(1110,1694,'16 px is separately drawn.',21,b=True)
text(1110,1735,'Wider gaps. Fewer spikes.',18)
text(1110,1770,'All icon sizes exported individually.',18)
text(48,1900,'SVG / PNG / ICO     •     NO FONT DEPENDENCIES     •     README + WEB TAGS INCLUDED',14)
(ROOT/'preview').mkdir(exist_ok=True)
sheet.save(ROOT/'preview/contact-sheet.png',optimize=True)
print('Built SVG, PNG, ICO, web assets and preview.')
