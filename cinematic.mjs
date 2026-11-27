import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
import {clone} from 'three/addons/utils/SkeletonUtils.js';

const base='https://models.vinish.dev/dinosaurs/';
const models=[
 ['raptor','velociraptor.glb',base+'velociraptor.glb'],
 ['trex','tyrannosaurus-rex.glb','https://media.animalanimator.com/free-3d-animated-t-rex-reference/model/tyrannosaurus-rex-rigged-animated.glb',base+'tyrannosaurus-rex.glb'],
 ['pteranodon','pteranodon.glb',base+'pteranodon.glb'],
 ['triceratops','triceratops.glb',base+'triceratops.glb']
];
const photos=['forest_floor','rock_wall_08','nature_reserve_forest'];
const local=(name)=>new URL('./assets/'+name,import.meta.url).href;
async function get(url,timeout=16000){const c=new AbortController(),timer=setTimeout(()=>c.abort(),timeout);try{let r=await fetch(url,{signal:c.signal});if(!r.ok)throw Error('HTTP '+r.status);return await r.arrayBuffer()}finally{clearTimeout(timer)}}
function glbOK(b){return b.byteLength>20&&new DataView(b).getUint32(0,true)===0x46546c67}
async function file(name,urls,check=()=>true){for(let u of [local(name),...urls])try{let b=await get(u);if(check(b))return b}catch(e){}throw Error(name+' unavailable')}
async function poly(name,channel,ext){const r=await fetch('https://api.polyhaven.com/files/'+name,{signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('Poly Haven unavailable');const a=await r.json();const v=a[channel]?.['1k']?.[ext]?.url;if(!v||!v.startsWith('https://'))throw Error('Asset resolution unavailable');return v}
async function texture(name,asset,channel){let urls=[];try{urls.push(await poly(asset,channel,'jpg'))}catch(e){}let bytes=await file(name,urls,b=>{let a=new Uint8Array(b);return a.length>3&&a[0]===255&&a[1]===216});let bitmap=await createImageBitmap(new Blob([bytes],{type:'image/jpeg'}));let t=new THREE.CanvasTexture(bitmap);t.flipY=false;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.colorSpace=channel==='diff'?THREE.SRGBColorSpace:THREE.NoColorSpace;t.anisotropy=2;t.needsUpdate=true;return t}
function fitTemplate(gltf,kind){
 const root=gltf.scene;root.updateMatrixWorld(true);
 let box=new THREE.Box3().setFromObject(root),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
 if(!Number.isFinite(size.length())||size.length()<.001)throw Error('Invalid model dimensions');
 let head=null;root.traverse(o=>{if(!head&&/(^|[._ -])head($|[._ -])|^head/i.test(o.name))head=o});
 let forward=new THREE.Vector3(0,0,1);
 if(head){forward=head.getWorldPosition(new THREE.Vector3()).sub(center);forward.y=0;if(forward.length()<size.length()*.04)forward.set(0,0,1)}
 else if(size.x>size.z*1.4&&kind!==2)forward.set(1,0,0);
 let yaw=Math.atan2(forward.x,forward.z);
 // Normalize the imported asset to the original game hitbox scale, not absolute museum scale.
 let factor=(kind===2?5.9/Math.max(size.x,size.z):[2.1,3.4,1,2.15][kind]/Math.max(size.y,.001));
 const wrapper=new THREE.Group(),orientation=new THREE.Group(),shift=new THREE.Group();
 shift.position.set(-center.x,kind===2?-center.y:-box.min.y,-center.z);
 shift.add(root);orientation.add(shift);orientation.rotation.y=-yaw;wrapper.add(orientation);wrapper.scale.setScalar(factor);
 let clips=gltf.animations||[],clip=clips.find(c=>kind===2?/flap|fly/i.test(c.name):/run/i.test(c.name))||clips.find(c=>/walk|glide/i.test(c.name))||clips[0];
 root.traverse(o=>{if(o.isMesh){o.frustumCulled=false;if(o.material)for(let m of Array.isArray(o.material)?o.material:[o.material]){if(m.isMeshStandardMaterial){m.roughness=Math.max(.42,m.roughness);m.envMapIntensity=.65;}}}});
 return {wrapper,clip,triangles:countTriangles(root),textured:hasTexture(root)};
}
function countTriangles(root){let n=0;root.traverse(o=>{if(o.isMesh){let g=o.geometry;n+=(g.index?.count||g.attributes.position.count)/3}});return Math.round(n)}
function hasTexture(root){let n=false;root.traverse(o=>{if(o.isMesh)for(let m of Array.isArray(o.material)?o.material:[o.material])if(m?.map)n=true});return n}
export async function createCinema({canvas,updateStatus}){
 let renderer=new THREE.WebGLRenderer({canvas,antialias:false,alpha:false,powerPreference:'high-performance'});
 renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
 renderer.autoClear=false;renderer.setScissorTest(true);
 const scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(65,1,.06,130),sun=new THREE.DirectionalLight(0xffe0b4,2.4),ambient=new THREE.HemisphereLight(0xb5d5e5,0x5d6046,1.55);
 sun.position.set(-25,40,-20);scene.add(sun,ambient);scene.fog=new THREE.FogExp2(0x8dada0,.016);
 const pool=new THREE.Group(),enemyGroup=new THREE.Group();scene.add(pool,enemyGroup);
 const geometries=new WeakMap(),materials=new Map(),slots=[],actors=new Map(),templates=new Map(),loader=new GLTFLoader();
 let tex={},loaded=0,failed=0,done=false,highRes=false,lastTime=null,lastWidth=0,lastHeight=0;
 function status(){updateStatus({loaded,failed,done,texturedTrex:templates.get(1)?.textured||false,photos:Object.keys(tex).filter(k=>tex[k]&&k!=='panorama').length})}
 async function loadModel(kind){let [label,name,...urls]=models[kind];try{let buffer=await file(name,urls,glbOK);let gltf=await loader.parseAsync(buffer,'');let t=fitTemplate(gltf,kind);templates.set(kind,t);loaded++}catch(e){failed++;console.warn('Model fallback',label,e.message)}status()}
 // Sequential model parsing prevents four high-memory uploads from landing in one frame.
 const ready=(async()=>{for(let kind of [1,0,3,2])await loadModel(kind);done=true;status()})();
 const photoReady=(async()=>{
  for(let [key,asset,channel] of [['ground','forest_floor','diff'],['stone','rock_wall_08','diff'],['normal','forest_floor','nor_gl']])try{tex[key]=await texture(key+'.jpg',asset,channel);status()}catch(e){console.warn('Photo fallback',key)}
  try{let urls=[];try{urls.push(await poly(photos[2],'hdr','hdr'))}catch(e){}let bytes=await file('forest.hdr',urls,b=>new Uint8Array(b)[0]===35),hdr=new RGBELoader().parse(bytes),t=new THREE.DataTexture(hdr.data,hdr.width,hdr.height,THREE.RGBAFormat,hdr.type||THREE.HalfFloatType);t.mapping=THREE.EquirectangularReflectionMapping;t.minFilter=t.magFilter=THREE.LinearFilter;t.needsUpdate=true;let pmrem=new THREE.PMREMGenerator(renderer),env=pmrem.fromEquirectangular(t);scene.environment=env.texture;tex.hdr=env;tex.panorama=t;pmrem.dispose();status()}catch(e){console.warn('HDR fallback',e.message)}
 })();
 function geometry(raw){if(geometries.has(raw))return geometries.get(raw);let a=raw.verts,p=[],n=[],uv=[];for(let i=0;i<a.length;i+=6){let x=a[i],y=a[i+1],z=a[i+2],nx=a[i+3],ny=a[i+4],nz=a[i+5];p.push(x,y,z);n.push(nx,ny,nz);if(Math.abs(ny)>=Math.max(Math.abs(nx),Math.abs(nz)))uv.push(x*.35,z*.35);else if(Math.abs(nx)>Math.abs(nz))uv.push(z*.35,y*.35);else uv.push(x*.35,y*.35)}let g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(n,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeBoundingSphere();geometries.set(raw,g);return g}
 function mat(o){let key=o.c.join(',')+':'+(o.mat||0),m=materials.get(key);if(!m){let color=new THREE.Color().setRGB(...o.c,THREE.SRGBColorSpace);m=o.mat===5?new THREE.MeshBasicMaterial({color}):new THREE.MeshStandardMaterial({color,roughness:o.mat===6?.45:.86,metalness:o.mat===6?.55:0,side:THREE.DoubleSide});materials.set(key,m)}if(o.mat===2){let map=o.s[0]===1&&o.s[1]===1&&o.s[2]===1?tex.stone:null;if(o.c[1]>o.c[0]*.85&&o.c[1]>o.c[2])map=tex.ground||map;if(map&&m.map!==map){m.map=map;m.needsUpdate=true}if(map===tex.ground&&tex.normal&&m.normalMap!==tex.normal){m.normalMap=tex.normal;m.normalScale.set(.5,.5);m.needsUpdate=true}}return m}
 function actor(e,elapsed){let t=templates.get(e.kind);if(!t)return false;let a=actors.get(e.id);if(!a){let root=clone(t.wrapper),mixer=new THREE.AnimationMixer(root);if(t.clip)mixer.clipAction(t.clip).play();a={root,mixer};actors.set(e.id,a);enemyGroup.add(root)}a.root.position.set(e.x,e.y,e.z);a.root.rotation.y=Math.atan2(-e.x,Math.max(4,-e.z))*.8; a.mixer.setTime(elapsed+e.id*.37);return true}
 function render({items,meshes,enemies,elapsed,zone,at,q,right,vr,width,height,preview}){
  let now=performance.now();if(lastTime!==null&&!preview&&now-lastTime>2500)lastTime=null;lastTime=now;
  let w=Math.max(2,Math.round(width*.83)),h=Math.max(2,Math.round(height*.83));if(w!==lastWidth||h!==lastHeight){renderer.setSize(w,h,false);lastWidth=w;lastHeight=h}
  let ids=new Set(enemies.map(e=>e.id));for(let [id,a] of actors)if(!ids.has(id)){a.mixer.stopAllAction();enemyGroup.remove(a.root);actors.delete(id)}
  let replaced=new Set();for(let e of enemies)if(actor(e,elapsed))replaced.add(e.id);
  let j=0;
  for(let o of items){if(o.enemyId&&replaced.has(o.enemyId))continue;let raw=o.mesh||meshes[o.type];if(!raw)continue;let g=geometry(raw),m=mat(o),obj=slots[j];if(!obj){obj=new THREE.Mesh(g,m);slots.push(obj);pool.add(obj)}else{obj.geometry=g;obj.material=m}obj.visible=true;obj.position.fromArray(o.p);obj.quaternion.fromArray(o.q);obj.scale.fromArray(o.s);j++}
  for(;j<slots.length;j++)slots[j].visible=false;
  let sky=new THREE.Color().setRGB(...at.h,THREE.SRGBColorSpace);scene.background=zone===0&&tex.panorama?tex.panorama:sky;scene.backgroundIntensity=.85;scene.fog.color.copy(sky);sun.color.setRGB(...at.sun,THREE.SRGBColorSpace);
  let count=vr?2:1;cam.quaternion.fromArray(q);
  for(let i=0;i<count;i++){let x=Math.floor(w*i/count),ww=Math.floor(w*(i+1)/count)-x;cam.aspect=ww/h;cam.updateProjectionMatrix();cam.position.set(right[0]*(vr?(i?1:-1)*.032:0),1.7+right[1]*(vr?(i?1:-1)*.032:0),right[2]*(vr?(i?1:-1)*.032:0));renderer.setViewport(x,0,ww,h);renderer.setScissor(x,0,ww,h);renderer.clear(true,true,true);renderer.render(scene,cam)}
 }
 function reset(){for(let a of actors.values()){a.mixer.stopAllAction();enemyGroup.remove(a.root)}actors.clear();lastTime=null}
 status();return {render,reset,ready,photoReady,get available(){return loaded},get done(){return done},get summary(){return {loaded,failed,done,texturedTrex:templates.get(1)?.textured||false,models:[...templates].map(([kind,t])=>({kind,triangles:t.triangles,textured:t.textured})),photos:Object.keys(tex).filter(k=>k!=='panorama').length}}}
}
