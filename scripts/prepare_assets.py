from pathlib import Path
import json,struct,urllib.request
OUT=Path('assets');OUT.mkdir(exist_ok=True)
BASE='https://models.vinish.dev/dinosaurs/'
MODELS={'tyrannosaurus-rex.glb':['https://media.animalanimator.com/free-3d-animated-t-rex-reference/model/tyrannosaurus-rex-rigged-animated.glb',BASE+'tyrannosaurus-rex.glb'],**{n+'.glb':[BASE+n+'.glb'] for n in ['velociraptor','triceratops','pteranodon']}}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'DinoStrikeVR/1.2'}),timeout=45) as r:
        b=r.read(30*1024*1024+1)
    if len(b)>30*1024*1024: raise ValueError('Asset exceeds budget')
    return b
report={}
for name,urls in MODELS.items():
    for url in urls:
        try:
            b=get(url);magic,version,length=struct.unpack_from('<4sII',b);n,typ=struct.unpack_from('<II',b,12)
            assert magic==b'glTF' and version==2 and length==len(b) and typ==0x4e4f534a and n<=len(b)-20
            data=json.loads(b[20:20+n].decode());assert data.get('meshes') and data.get('animations')
            (OUT/name).write_bytes(b);report[name]={'source':url,'bytes':len(b),'animations':[a.get('name','') for a in data['animations']],'images':len(data.get('images',[]))};break
        except Exception as e: print('Candidate failed',url,str(e))
for name,asset,channel,ext in [('ground.jpg','forest_floor','diff','jpg'),('stone.jpg','rock_wall_08','diff','jpg'),('normal.jpg','forest_floor','nor_gl','jpg'),('forest.hdr','nature_reserve_forest','hdr','hdr')]:
    try:
        url=json.loads(get('https://api.polyhaven.com/files/'+asset))[channel]['1k'][ext]['url'];b=get(url)
        assert b.startswith(b'\xff\xd8') if ext=='jpg' else b.startswith(b'#?')
        (OUT/name).write_bytes(b);report[name]={'source':url,'bytes':len(b)}
    except Exception as e: print('Photo candidate failed',name,str(e))
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if not all(n in report for n in MODELS): raise SystemExit('One or more animated models unavailable')
