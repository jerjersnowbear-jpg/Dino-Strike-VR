from pathlib import Path
import shutil,json
ROOT=Path('.');OUT=ROOT/'site'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir()
for n in ['index.html','play-1.3.2.html','cinematic.mjs','sw.js','manifest.webmanifest','icon.svg','ASSET-CREDITS.md']:
    shutil.copy2(ROOT/n,OUT/n)
(OUT/'.nojekyll').touch()
shutil.copytree('assets',OUT/'assets')
pkg=ROOT/'node_modules'/'three'
(OUT/'vendor'/'three').mkdir(parents=True)
for n in ['build','examples/jsm']:
    shutil.copytree(pkg/n,OUT/'vendor'/'three'/n)
shutil.copy2(pkg/'LICENSE',OUT/'vendor'/'three'/'LICENSE')
index=OUT/'index.html'
s=index.read_text().replace('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js','./vendor/three/build/three.module.js').replace('https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/','./vendor/three/examples/jsm/')
index.write_text(s)
(OUT/'play-1.3.2.html').write_text(s)
print('Same-origin site:',sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file()),'bytes')
