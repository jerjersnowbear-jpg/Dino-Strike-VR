from pathlib import Path
import json,struct,urllib.request,urllib.parse,hashlib,shutil
from pathlib import PurePosixPath
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
for name,asset,channel,ext in [('ground.jpg','forest_floor','diff','jpg'),('stone.jpg','rock_wall_08','diff','jpg'),('normal.jpg','forest_floor','nor_gl','jpg'),('forest.hdr','nature_reserve_forest','hdr','hdr'),('rough.jpg','forest_floor','rough','jpg'),('rockNormal.jpg','rock_wall_08','nor_gl','jpg'),('rockRough.jpg','rock_wall_08','rough','jpg'),('bark.jpg','metasequoia_bark','diff','jpg'),('barkNormal.jpg','metasequoia_bark','nor_gl','jpg')]:
    try:
        url=json.loads(get('https://api.polyhaven.com/files/'+asset))[channel]['1k'][ext]['url'];b=get(url)
        assert b.startswith(b'\xff\xd8') if ext=='jpg' else b.startswith(b'#?')
        (OUT/name).write_bytes(b);report[name]={'source':url,'bytes':len(b)}
    except Exception as e: print('Photo candidate failed',name,str(e))
# Download actual glTF dependencies from the provider's published metadata.
def safe_rel(uri):
    p=PurePosixPath(urllib.parse.unquote(uri))
    if p.is_absolute() or '..' in p.parts or '\\' in str(p) or ':' in str(p): raise ValueError('Unsafe dependency path')
    return p
for name in ['fern_02','rock_moss_set_01']:
    try:
        data=json.loads(get('https://api.polyhaven.com/files/'+name))
        info=data['gltf']['1k']['gltf'];url=info['url'];b=get(url);g=json.loads(b)
        folder=OUT/name;folder.mkdir(exist_ok=True)
        if not g.get('meshes'): raise ValueError('Missing mesh')
        for item in g.get('buffers',[])+g.get('images',[]):
            uri=item.get('uri')
            if not uri or uri.startswith('data:'): continue
            rel=safe_rel(uri)
            listed=info.get('include',{}).get(uri,{})
            source=listed.get('url') if isinstance(listed,dict) else None
            blob=get(source or urllib.parse.urljoin(url,uri))
            path=folder/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
        (folder/(name+'_1k.gltf')).write_bytes(b)
        report[name]={'source':url,'bytes':len(b)}
    except Exception as e: print('Scanned asset unavailable',name,str(e));shutil.rmtree(OUT/name,ignore_errors=True)
try:
    url=BASE+'cycad.glb';b=get(url)
    assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b)
    (OUT/'cycad.glb').write_bytes(b);report['cycad']={'source':url,'bytes':len(b)}
except Exception as e: print('Cycad unavailable',str(e))
for name,data in report.items():
    path=OUT/name
    if path.is_file(): data['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if not all(n in report for n in MODELS): raise SystemExit('One or more animated models unavailable')
