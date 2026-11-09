from pathlib import Path
import threading, os, json, traceback
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet)
t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
results=[]; console_errors=[]; page_errors=[]; failed_requests=[]; environment_blocked=False

def ck(name,ok,detail=''):
    results.append({'name':name,'passed':None if ok is None else bool(ok),'detail':str(detail)[:3000]})
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
      page.wait_for_timeout(1500)
      ck('Final Release 50 app loads in Chromium',resp is not None and resp.status==200,f'HTTP {resp.status if resp else "none"}; title={page.title()}')
      ck('Final Release title is visible',page.title().startswith('IELTS Boost · Final Release 50'),page.title())
      ck('Stage 50 CSS loads',page.evaluate("[...document.styleSheets].some(s=>s.href&&s.href.includes('stage50.css'))"))
      ck('Skip link and main landmark render',page.locator('a.skip-link[href="#app"]').count()==1 and page.locator('main#app').count()==1)
      # Navigate all principal routes once to catch render-time errors.
      for route in ['plan','reading','writing','listening','speaking','games','vocabulary','errors','mock','progress','articles','resources','settings']:
        btn=page.locator(f'#nav button[data-page="{route}"]')
        if btn.count():
          btn.click(); page.wait_for_timeout(100)
          ck(f'Route renders: {route}',page.locator('#app').count()==1 and page.locator('#app').inner_text().strip()!='')
      page.locator('#nav button[data-page="settings"]').click();page.wait_for_timeout(250)
      ck('Settings backup panel renders',page.locator('h2').filter(has_text='Backup & restore').count()==1)
      ck('Final acceptance summary renders',page.locator('#stage50-release-title').count()==1)
      ck('PWA panel renders',page.locator('#p37PwaDiagnostics').count()==1)
      page.locator('[data-action="device-check"]').click();page.wait_for_timeout(300)
      ck('Device diagnostics populate',page.locator('#deviceCheck .p49-diagnostic-row').count()>=8,str(page.locator('#deviceCheck .p49-diagnostic-row').count()))
      with page.expect_download(timeout=15000) as dl:
        page.locator('[data-action="backup"]').click()
      download=dl.value
      path=ROOT/'STAGE50_BROWSER_TEST_BACKUP.json';download.save_as(path)
      env=json.loads(path.read_text())
      ck('Backup exports SHA-256 envelope',env.get('integrity',{}).get('algorithm')=='SHA-256' and len(env.get('integrity',{}).get('sha256',''))==64)
      ck('Backup contains core progress maps',all(k in env.get('state',{}) for k in ['completed','scores','drafts']))
      # The PWA diagnostic should run against its project-relative manifest.
      page.locator('[data-p37-pwa-check]').click();page.wait_for_timeout(800)
      ck('PWA diagnostic resolves relative manifest',page.locator('#p37PwaDiagnostics').inner_text().lower().find('manifest')>=0)
      for width in [430,390,360,320]:
        page.set_viewport_size({'width':width,'height':844});page.wait_for_timeout(100)
        dims=page.evaluate('({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})')
        ck(f'No horizontal overflow at {width}px',dims['sw']<=dims['cw'],str(dims))
      ck('No uncaught browser exceptions',not page_errors,'; '.join(page_errors[:8]))
      ck('No console errors during acceptance flow',not console_errors,'; '.join(console_errors[:8]))
      page.screenshot(path=str(ROOT/'STAGE50_CHROMIUM_ACCEPTANCE.png'),full_page=True)
    except Exception:
      trace=traceback.format_exc()
      if 'ERR_BLOCKED_BY_ADMINISTRATOR' in trace:
        environment_blocked=True
        ck('Browser acceptance flow',None,'Execution environment blocked localhost navigation before app load; no browser assertions were run.')
      else:
        ck('Browser acceptance flow completed',False,trace)
    browser.close()
finally:
  server.shutdown();server.server_close()
passed=sum(x['passed'] is True for x in results)
status='BLOCKED_BY_ENVIRONMENT' if environment_blocked else ('PASS' if passed==len(results) else 'FAIL')
report={'stage':50,'release':'50.0.0','status':status,'passed':passed,'total':len(results),'failed':sum(x['passed'] is False for x in results),'checks':results,'consoleErrors':console_errors,'pageErrors':page_errors,'failedRequests':failed_requests,'environment':'Chromium via Playwright; localhost HTTP; service workers disabled in test context','note':'A blocked result means Chromium could not navigate to localhost before application code ran; it is not a product pass or fail.' if environment_blocked else ''}
(ROOT/'STAGE50_CHROMIUM_ACCEPTANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(f'STAGE 50 CHROMIUM ACCEPTANCE: {status} ({passed}/{len(results)} checks executed; {report["failed"]} failed)')
for x in results:
  label='PASS' if x['passed'] is True else ('BLOCKED' if x['passed'] is None else 'FAIL')
  print(label+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
