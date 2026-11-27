from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from functools import partial
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=b.new_page(viewport={'width':1100,'height':650},service_workers='block')
        page.goto(f'http://127.0.0.1:{server.server_port}/?test=1')
        page.evaluate('()=>{__ride.prepareCinema()}')
        page.wait_for_function('__ride.cinema?.done===true',timeout=120000)
        data=page.evaluate('__ride.cinema');assert data['loaded']==4,data
        page.locator('#graphics').select_option('cinema')
        page.locator('#vrStart').click();page.locator('#adult').check();page.locator('#preview').click()
        assert page.locator('#cinemaCanvas').is_visible()
        colors=page.evaluate("""()=>{__ride.render(__ride.camera());let canvas=document.getElementById('cinemaCanvas'),gl=canvas.getContext('webgl2'),out=[];if(!gl)return [];for(let e=0;e<2;e++){let set=new Set();for(let x=1;x<9;x++)for(let y=1;y<7;y++){let p=new Uint8Array(4);gl.readPixels(Math.floor(canvas.width*(e+x/9)/2),Math.floor(canvas.height*y/7),1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);set.add([...p].join(','));}out.push(set.size)}return out}""")
        assert len(colors)==2 and min(colors)>5,colors
        page.screenshot(path=str(ROOT/'assets'/'cinematic-preview.png'))
        print('PASS: imported animated models and stereo pixels',data,colors)
        b.close()
finally:
    server.shutdown();server.server_close()
