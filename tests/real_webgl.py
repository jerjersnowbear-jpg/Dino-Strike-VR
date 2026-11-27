"""Exercise the real WebGL shader and pixel pipeline in desktop Chromium.
This does not validate a physical Cardboard viewer or phone frame rate.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from functools import partial
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=browser.new_page(viewport={'width':1100,'height':650},service_workers='block')
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/?test=1')
        assert page.evaluate('!!window.__ride'),errors
        page.locator('#vrStart').click()
        page.locator('#adult').check()
        page.locator('#preview').click()
        result=page.evaluate("""()=>{const v=__ride;v.render(v.camera());const canvas=document.getElementById('world'),gl=canvas.getContext('webgl');const colors=[new Set(),new Set()];for(let eye=0;eye<2;eye++)for(let x=1;x<10;x++)for(let y=1;y<8;y++){const pixel=new Uint8Array(4);gl.readPixels(Math.floor(canvas.width*(eye+x/10)/2),Math.floor(canvas.height*y/8),1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixel);colors[eye].add([...pixel].join(','));}return {vr:v.state.vr,preview:v.state.preview,frames:v.state.frameCount,colors:colors.map(c=>c.size),error:gl.getError()}}""")
        assert result['vr'] and result['preview'] and result['frames']>0 and min(result['colors'])>=8 and result['error']==0,result
        assert not errors,errors
        assert page.locator('#hud .eye').count()==2
        print('PASS: real WebGL shader compilation, stereo scene and varied pixels',result)
        browser.close()
finally:
    server.shutdown()
    server.server_close()
