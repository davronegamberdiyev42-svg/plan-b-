from pathlib import Path
import threading, os, json, traceback, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet); t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
results=[]; console_errors=[]; page_errors=[]; failed_requests=[]; environment_blocked=False
def ck(name,ok,detail=''): results.append({'name':name,'passed':None if ok is None else bool(ok),'detail':str(detail)[:5000]})
try:
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    ctx=browser.new_context(viewport={'width':1365,'height':900},service_workers='block',accept_downloads=True)
    page=ctx.new_page()
    page.on('console',lambda m: console_errors.append(m.text) if m.type=='error' else None)
    page.on('pageerror',lambda e: page_errors.append(str(e)))
    page.on('requestfailed',lambda r: failed_requests.append({'url':r.url,'failure':r.failure}))
    try:
      resp=page.goto(base+'/',wait_until='domcontentloaded',timeout=90000)
      page.wait_for_selector('#nav button[data-page="vocabulary"]',timeout=90000)
      page.wait_for_timeout(1000)
      ck('Stage 49 app loads in Chromium',resp is not None and resp.status==200,f'HTTP {resp.status if resp else "none"}')
      ck('CSP meta is present',page.locator('meta[http-equiv="Content-Security-Policy"]').count()==1)
      ck('Stage 49 stylesheet loads',page.locator('link[href*="stage49.css"]').count()==1 and page.evaluate("[...document.styleSheets].some(s=>s.href&&s.href.includes('stage49.css'))"))
      ck('Skip link is keyboard accessible',page.locator('a.skip-link[href="#app"]').count()==1)
      ck('Network status chip renders',page.locator('#p49Connectivity').count()==1)
      page.locator('#nav button[data-page="settings"]').click()
      page.wait_for_timeout(250)
      ck('Settings and safety section renders',page.locator('h2').filter(has_text='Backup & restore').count()==1)
      ck('Persistent storage request control renders',page.locator('[data-action="protect-storage"]').count()==1)
      page.locator('[data-action="device-check"]').click()
      page.wait_for_timeout(1000)
      ck('Device diagnostics populate',page.locator('#deviceCheck .p49-diagnostic-row').count()>=8,str(page.locator('#deviceCheck .p49-diagnostic-row').count()))
      with page.expect_download(timeout=15000) as dl:
        page.locator('[data-action="backup"]').click()
      download=dl.value
      path=Path('/mnt/data/stage49_work/test-backup.json')
      download.save_as(path)
      env=json.loads(path.read_text())
      ck('Backup download includes SHA-256 envelope',env.get('integrity',{}).get('algorithm')=='SHA-256' and len(env.get('integrity',{}).get('sha256',''))==64)
      ck('Backup contains state payload',all(k in env.get('state',{}) for k in ['completed','scores','drafts']))
      # tamper file and verify the product rejects it without importing
      env['state']['day']=82
      tamper=Path('/mnt/data/stage49_work/test-backup-tampered.json');tamper.write_text(json.dumps(env))
      page.locator('input#backupFile').set_input_files(str(tamper))
      page.wait_for_timeout(700)
      ck('Tampered backup rejected with checksum message', 'checksum mismatch' in page.locator('#backupStatus').inner_text().lower())
      # Relative manifest scope should resolve to current deployment scope
      manifest=page.evaluate("fetch('./manifest.webmanifest').then(r=>r.json())")
      ck('Relative PWA manifest uses deployment-relative scope',manifest.get('scope')=='./' and manifest.get('start_url')=='./' and manifest.get('id')=='./')
      page.set_viewport_size({'width':390,'height':844})
      page.wait_for_timeout(250)
      overflow=page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth')
      ck('Settings has no horizontal page overflow at 390px',not overflow,f"scrollWidth={page.evaluate('document.documentElement.scrollWidth')}; clientWidth={page.evaluate('document.documentElement.clientWidth')}")
      ck('No uncaught browser exceptions',not page_errors,'; '.join(page_errors[:10]))
      ck('No console errors during tested flow',not console_errors,'; '.join(console_errors[:10]))
    except Exception as exc:
      trace=traceback.format_exc()
      if 'ERR_BLOCKED_BY_ADMINISTRATOR' in trace:
        environment_blocked=True
        ck('Browser acceptance flow',None,'Blocked by execution environment before page navigation; no browser assertions were run.')
      else:
        ck('Browser acceptance flow completed',False,trace)
    browser.close()
finally:
  server.shutdown();server.server_close()
passed=sum(x['passed'] is True for x in results)
status='BLOCKED_BY_ENVIRONMENT' if environment_blocked else ('PASS' if passed==len(results) else 'FAIL')
report={'stage':49,'status':status,'passed':passed,'total':len(results),'failed':len([x for x in results if x['passed'] is False]),'checks':results,'consoleErrors':console_errors,'pageErrors':page_errors,'failedRequests':failed_requests,'environment':'Chromium via Playwright; localhost HTTP; service workers blocked in test context','note':'BLOCKED means the browser was prevented from opening localhost before app navigation. It is not a product PASS or FAIL.' if environment_blocked else ''}
(ROOT/'STAGE49_CHROMIUM_ACCEPTANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(f'STAGE 49 CHROMIUM ACCEPTANCE: {status} ({passed}/{len(results)} checks executed)')
for x in results: print(('PASS' if x['passed'] else ('BLOCKED' if x['passed'] is None else 'FAIL'))+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
