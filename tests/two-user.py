"""Two simulated users chat through a fake Supabase. Run: python3 tests/two-user.py
Needs: pip install playwright && playwright install chromium. Exits non-zero on the first failure."""
import asyncio, contextlib, pathlib, subprocess, sys, time
from playwright.async_api import async_playwright

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
FAKE = (HERE / 'fake-supabase.js').read_text()
PORT = 8877
URL = f'http://localhost:{PORT}/index.html'

async def login(p, name, pin):
    await p.goto(URL)
    await p.wait_for_selector('#f-url, .key', state='attached')
    await asyncio.sleep(.8)
    if await p.locator('#st-con.on').count():
        await p.fill('#f-url', 'https://test.supabase.co'); await p.fill('#f-anon', 'anon'); await p.fill('#f-vk', 'test vault phrase')
        await p.click('#con-btn')
    elif await p.locator('#st-pin.on').count():
        await p.click('#pin-back')
    await p.wait_for_selector('.pick', state='visible')
    await p.click(f'.pick:has-text("{name}")'); await p.click('#pick-go'); await p.wait_for_selector('.key')
    for d in pin: await p.click(f'.key:text-is("{d}")')
    await p.wait_for_selector('#s-app.on', timeout=8000)

async def main():
    errors = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800})
        async def route(r):
            u = r.request.url
            if 'jsdelivr' in u and 'supabase' in u: await r.fulfill(body=FAKE, content_type='application/javascript')
            elif 'fonts.g' in u: await r.fulfill(body='', content_type='text/css')
            else: await r.continue_()
        await ctx.route('**/*', route)
        A, B = await ctx.new_page(), await ctx.new_page()
        for p in (A, B):
            p.on('pageerror', lambda e: errors.append(str(e)))
        await login(A, 'Alice', '1111'); await login(B, 'Bob', '2222')
        await A.click('.conv[data-th="alice__bob"]'); await B.click('.conv[data-th="alice__bob"]')

        await A.fill('#msg-ta', 'Hello Bob'); await A.keyboard.press('Enter')
        await B.wait_for_selector('.msg:not(.mine) .txt:has-text("Hello Bob")', timeout=5000)           # delivery
        await A.wait_for_selector('.msg.mine .tick.read', timeout=5000)                                  # read receipt

        await B.click('.msg:not(.mine) .txt'); await B.click('#menu [data-emo="❤️"]')
        await A.wait_for_selector('.react', timeout=5000)                                                # reaction syncs

        await A.click('.msg.mine .txt'); await A.click('#menu [data-act="edit"]')
        await A.fill('#msg-ta', 'Hello Bob (edited)'); await A.keyboard.press('Enter')
        await B.wait_for_selector('.foot span:text-is("edited")', timeout=5000)                          # edit syncs

        # Bob must not be able to edit or delete Alice's message by forging events
        await B.evaluate("""async()=>{const m=[...S.msgs[S.thread].values()].find(x=>x.sender==='alice');
            await sendRaw(S.thread,{k:'del',m:m.cid});await sendRaw(S.thread,{k:'edit',m:m.cid,t:'forged'})}""")
        await asyncio.sleep(.8)
        assert await A.locator('.bubble.gone').count() == 0, 'a non-sender deleted a message'
        assert 'forged' not in await A.inner_text('#msgs'), 'a non-sender edited a message'

        # A "photo" that is really a javascript: link must be dropped
        await B.evaluate("sendRaw(S.thread,{k:'m',id:'evil1',t:'look',i:'javascript:alert(1)'})")
        await A.wait_for_selector('.txt:has-text("look")', timeout=5000)
        assert await A.locator('.photo img').count() == 0, 'unsafe photo URL was rendered'

        # Stickers: pick one in a pack, it arrives as a big sticker
        await A.click('#btn-emoji'); await A.click('#emoji-pop [data-tab="Romance"]'); await A.click('#emoji-pop .st >> nth=0')
        await B.wait_for_selector('.msg:not(.mine) .bubble.sticker', timeout=5000)
        await A.screenshot(path='/tmp/sticker.png')

        await A.click('.msg.mine >> nth=0 >> .txt'); await A.click('#menu [data-act="del"]')
        await B.wait_for_selector('.bubble.gone', timeout=5000)                                          # delete for everyone
        await b.close()
    assert not errors, errors
    print('all checks passed')

srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    time.sleep(1); asyncio.run(main())
finally:
    srv.terminate()
