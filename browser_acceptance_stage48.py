from pathlib import Path
import threading, os, json, traceback, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
results=[];console_errors=[];page_errors=[];failed_requests=[]
def ck(name,ok,detail=''):
    results.append({'name':name,'passed':bool(ok),'detail':str(detail)[:8000]})
try:
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    ctx=browser.new_context(viewport={'width':1365,'height':900},service_workers='block')
    page=ctx.new_page()
    page.on('console',lambda m: console_errors.append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e: page_errors.append(str(e)))
    page.on('requestfailed',lambda r: failed_requests.append({'url':r.url,'failure':r.failure}))
    try:
      resp=page.goto(base+'/',wait_until='domcontentloaded',timeout=90000)
      page.wait_for_selector('#nav button[data-page="vocabulary"]',timeout=90000)
      page.wait_for_selector('#app',timeout=90000)
      page.wait_for_timeout(2000)
      ck('App loads in Chromium',resp is not None and resp.status==200, f'HTTP {resp.status if resp else "none"}')
      ck('Global Academic navigation renders',page.locator('#topbar').inner_text().find('ACADEMIC')>=0)
      page.locator('#nav button[data-page="vocabulary"]').click()
      page.wait_for_selector('.p48-hero',timeout=20000)
      page.wait_for_timeout(500)
      ck('Stage 48 Vocabulary dashboard renders',page.locator('.p48-hero').count()==1)
      ck('Honest daily core count is shown',page.locator('.p48-hero').inner_text().find('672')>=0)
      ck('Daily core shows 8 vocabulary cards',page.locator('.p48-word').count()==8,str(page.locator('.p48-word').count()))
      # Reveal a card, then navigate previous/next days and see the pack update.
      firstid=page.locator('.p48-word').first.get_attribute('data-vx-word')
      page.locator(f'[data-vx-reveal="{firstid}"]').click()
      ck('Daily card reveals the full lexical note',page.locator(f'[data-vx-back="{firstid}"]').is_visible())
      page.locator('button[data-day="2"]').click()
      page.wait_for_timeout(250)
      ck('Day navigation changes current daily pack', 'Day 2' in page.locator('.p48-day-card').inner_text())
      # Search a bundled word and verify a card appears.
      search=page.locator('#vocabSearch')
      search.fill('discrepancy')
      page.wait_for_timeout(400)
      ck('19k index search returns the Cambridge-attested core word',page.locator('[data-word-card="discrepancy"]').count()==1)
      # SRS card reveal gate: add core pack to SRS then check review buttons are disabled before reveal.
      page.locator('button[data-vx-add-pack]').click()
      page.wait_for_timeout(250)
      # The render returns to day page and SRS due items; find first row.
      row=page.locator('.p48-srs-row').first
      ck('SRS adds complete daily core items',row.count()==1)
      again=row.locator('[data-srs-review$=":again"]')
      ck('SRS rating is disabled until meaning is revealed',again.is_disabled())
      row.locator('details[data-p48-srs-detail] summary').click()
      page.wait_for_timeout(200)
      ck('SRS rating unlocks only after reveal',not again.is_disabled())
      # Mobile width sanity check.
      page.set_viewport_size({'width':390,'height':844})
      page.wait_for_timeout(200)
      overflow=page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth')
      ck('Vocabulary dashboard has no horizontal page overflow at 390px',not overflow,f'scrollWidth={page.evaluate("document.documentElement.scrollWidth")}; clientWidth={page.evaluate("document.documentElement.clientWidth")}')
      ck('No uncaught browser errors',not page_errors,'; '.join(page_errors))
      # ignore browser extension/noncritical resource errors? collect console errors explicitly.
      ck('No console error messages during tested flow',not console_errors,'; '.join(console_errors[:10]))
    except Exception as exc:
      ck('Chromium browser flow completed',False,traceback.format_exc())
    browser.close()
finally:
  server.shutdown();server.server_close()
ok=sum(x['passed'] for x in results)
report={'passed':ok,'total':len(results),'checks':results,'consoleErrors':console_errors,'pageErrors':page_errors,'failedRequests':failed_requests}
(ROOT/'STAGE48_CHROMIUM_ACCEPTANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'STAGE 48 CHROMIUM ACCEPTANCE: {ok}/{len(results)} PASS')
for x in results: print(('PASS' if x['passed'] else 'FAIL')+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
