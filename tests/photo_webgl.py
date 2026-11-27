from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from functools import partial
from playwright.sync_api import sync_playwright
site=Path('site').resolve()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(site)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=b.new_page(viewport={'width':1100,'height':650},service_workers='block')
        origin=f'http://127.0.0.1:{server.server_port}'
        page.route('**/*',lambda r:r.continue_() if r.request.url.startswith(origin+'/') else r.abort())
        page.goto(origin+'/?test=1')
        page.evaluate('()=>{__ride.prepareCinema()}')
        page.wait_for_function('__ride.cinema?.done===true',timeout=120000)
        result=page.evaluate('__ride.cinema')
        assert result['loaded']==4,result
        page.wait_for_function('__ride.cinema?.photos>=3',timeout=90000)
        page.locator('#graphics').select_option('cinema')
        page.locator('#vrStart').click();page.locator('#adult').check();page.locator('#preview').click()
        assert page.locator('#cinemaCanvas').is_visible()
        result=page.evaluate("""()=>{let v=__ride;while(v.state.enemies.length<4)v.spawn();for(let [i,e] of v.state.enemies.entries()){e.x=(i-1.5)*2.4;e.z=-10-i*2}v.render(v.camera());let c=document.getElementById('cinemaCanvas'),gl=c.getContext('webgl2'),out=[];if(!gl)return [];for(let e=0;e<2;e++){let set=new Set();for(let x=1;x<10;x++)for(let y=1;y<8;y++){let p=new Uint8Array(4);gl.readPixels(Math.floor(c.width*(e+x/10)/2),Math.floor(c.height*y/8),1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);set.add([...p].join(','));}out.push(set.size)}return {colors:out,assets:v.cinema,error:gl.getError()}}""")
        assert min(result['colors'])>=8 and result['error']==0,result
        page.screenshot(path='photo-proof.png')
        print('Verified local assets and stereo rendering:',result)
        b.close()
finally:
    server.shutdown();server.server_close()
