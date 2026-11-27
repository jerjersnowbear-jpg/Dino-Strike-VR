from pathlib import Path
from playwright.sync_api import sync_playwright
import os
root=Path(__file__).resolve().parents[1]
MOCK='''<script>let id=0;const real=HTMLCanvasElement.prototype.getContext;const mock=new Proxy({getShaderParameter:()=>true,getProgramParameter:()=>true,getAttribLocation:()=>0,getUniformLocation:()=>({}),createBuffer:()=>({}),createShader:()=>({}),createProgram:()=>({}),createTexture:()=>({})},{get(t,k){if(k in t)return t[k];if(/^[A-Z0-9_]+$/.test(k))return ++id;return ()=>{}}});HTMLCanvasElement.prototype.getContext=function(k,...a){return k==='webgl'?mock:real.call(this,k,...a)};Object.defineProperty(window,'localStorage',{value:{getItem:()=>null,setItem:()=>{}}});</script>'''
with sync_playwright() as p:
    opts={'headless':True,'args':['--no-sandbox']}
    if os.environ.get('CHROMIUM_BIN'):opts['executable_path']=os.environ['CHROMIUM_BIN']
    b=p.chromium.launch(**opts);page=b.new_page(viewport={'width':1100,'height':650});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    html=(root/'index.html').read_text().replace('<script>\n','<script>\n',1).replace('<script>\n\'use strict\';',MOCK+"<script>\n'use strict';",1).replace("if(new URLSearchParams(location.search).has('test'))window.__ride=","window.__ride=")
    page.set_content(html);assert page.evaluate('!!window.__ride'),errors
    if os.environ.get('MENU_PREVIEW'):page.screenshot(path=os.environ['MENU_PREVIEW'])
    print('PASS: application initialized with mock WebGL')
    stats=page.evaluate('__ride.visualStats()');assert stats['variants']==[2,2,2] and len(stats['dino'])==4 and min(stats['dino'])>15,stats
    print('PASS: six scenery variants and four enhanced dinosaur meshes')
    page.evaluate('''()=>{let f=__ride.gazeStep,g={id:null,seconds:0};for(let i=0;i<19;i++)g=f(g,1,.1);if(g.fire||g.seconds<1.89)throw Error('premature fire');g=f(g,null,.1);if(g.seconds!==0||g.fire)throw Error('loss not reset');g=f({id:1,seconds:1.9},2,.1);if(g.seconds!==.1||g.fire)throw Error('switch not reset');g={id:null,seconds:0};for(let i=0;i<20;i++)g=f(g,1,.1);if(!g.fire)throw Error('no shot at 2 seconds')}''')
    print('PASS: two-second continuous lock, interruption reset, target switch reset')
    result=page.evaluate('''()=>{let v=__ride;v.start(false);v.setMode('comfort');v.spawn();let id=v.state.enemies[0].id;for(let i=0;i<21&&v.state.enemies.some(e=>e.id===id);i++){v.aim(id);v.advance(.1)}let s=v.state;if(s.hits!==1||s.score!==100||s.dist<7.9)throw Error(JSON.stringify(s));v.menu();return {score:s.score,dist:s.dist}}''');print('PASS: moving ride, charging raptor, laser hit, points:',result)
    page.evaluate('''()=>{let v=__ride;v.start(false);v.setMode('arcade');v.spawn();let e=v.state.enemies[0];if(-e.z/8.6<8)throw Error('insufficient attack time');for(let i=0;i<150;i++)v.advance(.1);if(v.state.shield>=5)throw Error('no shield hit');v.menu()}''');print('PASS: attack travel time and shield collision')
    page.evaluate('''()=>{let v=__ride;v.start(false);v.setMode('gentle');for(let i=0;i<3;i++)v.spawn();let e=v.state.enemies[2],id=e.id;if(!e.spec.fly||e.y<4)throw Error('no flying target');for(let i=0;i<21&&v.state.enemies.some(e=>e.id===id);i++){v.aim(id);v.advance(.1)}if(v.state.hits!==1||v.state.score!==150)throw Error('flying target scoring');v.menu()}''');print('PASS: flying dinosaur tracking and bonus score')
    page.locator('#vrStart').click();assert page.locator('#preview').is_disabled();page.locator('#adult').check();page.locator('#preview').click();assert page.locator('#hud .eye').count()==2;assert page.evaluate('__ride.state.preview');assert not page.evaluate('!!document.fullscreenElement');page.locator('#exit').click();assert page.locator('#pause').is_visible();page.locator('#pauseMenu').click();print('PASS: stereo preview, safety gate, pause and return')
    page.set_viewport_size({'width':650,'height':1100});page.locator('#vrStart').click();page.locator('#adult').check();page.locator('#preview').click();assert page.locator('#setup').is_visible();assert 'landscape' in page.locator('#sensorStatus').inner_text();print('PASS: portrait rejected')
    assert not errors,errors;b.close()
