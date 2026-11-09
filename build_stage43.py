from pathlib import Path
from bs4 import BeautifulSoup
import re, json, hashlib, shutil, zipfile, os

ROOT=Path('/mnt/data/stage43_work')
html_path=ROOT/'index.html'
html=html_path.read_text(encoding='utf-8')
soup=BeautifulSoup(html,'html.parser')

# Locate source payloads without serializing the full HTML through BeautifulSoup.
app_data_tag=soup.find('script', id='appData')
if not app_data_tag:
    raise SystemExit('Missing appData script')
data_text=app_data_tag.string if app_data_tag.string is not None else app_data_tag.get_text()
data=json.loads(data_text)
if not isinstance(data,dict) or not isinstance(data.get('plan'),dict) or len(data.get('core',{}).get('days',[])) != 84:
    raise SystemExit('Unexpected app data schema or curriculum size')

runtime_tag=None
for tag in soup.find_all('script'):
    if tag.get('id') is None and tag.get('type') != 'application/json' and not tag.get('src'):
        runtime_tag=tag
if not runtime_tag:
    raise SystemExit('Missing inline runtime script')
runtime=runtime_tag.string if runtime_tag.string is not None else runtime_tag.get_text()

style_tags=soup.find_all('style')
if len(style_tags)!=6:
    raise SystemExit(f'Expected 6 style blocks, found {len(style_tags)}')
css='\n\n/* ---- Extracted from original inline style block {i} ---- */\n'.join(
    (tag.string if tag.string is not None else tag.get_text()) for i,tag in enumerate(style_tags,1)
)

# Prepare separated asset structure.
(ROOT/'data').mkdir(exist_ok=True)
(ROOT/'assets'/'css').mkdir(parents=True,exist_ok=True)
(ROOT/'assets'/'js'/'core').mkdir(parents=True,exist_ok=True)
(ROOT/'assets'/'js'/'runtime').mkdir(parents=True,exist_ok=True)
(ROOT/'data'/'app-data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'assets'/'css'/'app.css').write_text(css,encoding='utf-8')

# Core data loader with explicit validation and useful, non-sensitive boot errors.
loader=r'''/**
 * IELTS Boost data loader — Stage 43
 * Loads the content payload separately from the document shell.
 */
export async function loadAppData() {
  const url = new URL('./data/app-data.json', document.baseURI);
  let response;
  try {
    response = await fetch(url.href, { cache: 'default', credentials: 'same-origin' });
  } catch (cause) {
    const error = new Error('IELTS Boost kontent faylini yuklab bo‘lmadi. Internetni tekshir yoki offline cache mavjudligini tasdiqla.');
    error.code = 'APP_DATA_NETWORK';
    error.cause = cause;
    throw error;
  }
  if (!response.ok) {
    const error = new Error(`IELTS Boost kontent fayli yuklanmadi (HTTP ${response.status}).`);
    error.code = 'APP_DATA_HTTP';
    throw error;
  }
  let data;
  try {
    data = await response.json();
  } catch (cause) {
    const error = new Error('IELTS Boost kontent fayli JSON formatida o‘qilmadi.');
    error.code = 'APP_DATA_INVALID_JSON';
    error.cause = cause;
    throw error;
  }
  if (!data || typeof data !== 'object' || !data.plan || !Array.isArray(data.core?.days) || !Array.isArray(data.words)) {
    const error = new Error('IELTS Boost kontent faylining tuzilmasi kutilgan formatga mos emas.');
    error.code = 'APP_DATA_SCHEMA';
    throw error;
  }
  if (data.core.days.length !== 84) {
    const error = new Error(`84 kunlik dastur to‘liq yuklanmadi (${data.core.days.length}/84).`);
    error.code = 'APP_DATA_CURRICULUM';
    throw error;
  }
  return data;
}
'''
(ROOT/'assets'/'js'/'core'/'data-loader.js').write_text(loader,encoding='utf-8')

boot_error=r'''/** Accessible boot-failure UI. Never exposes secrets or raw stack traces. */
export function showBootError(error) {
  console.error('[IELTS Boost boot]', error?.code || 'UNKNOWN', error);
  const host = document.querySelector('#app') || document.body;
  host.innerHTML = `
    <section role="alert" aria-live="assertive" class="card" style="max-width:720px;margin:24px auto;padding:24px">
      <div class="eyebrow">IELTS BOOST · STARTUP CHECK</div>
      <h2>Platforma ma’lumotlarini yuklashda muammo yuz berdi</h2>
      <p>${String(error?.message || 'Noma’lum xatolik yuz berdi.').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]))}</p>
      <p class="muted small">Internetga ulanishni tekshir. Agar avval platformani ochgan bo‘lsang, sahifani qayta yukla. Offline fayllar cache’da bo‘lishi kerak.</p>
      <button type="button" class="btn primary" id="appBootRetry">Qayta yuklash</button>
    </section>`;
  document.querySelector('#appBootRetry')?.addEventListener('click', () => location.reload());
}
'''
(ROOT/'assets'/'js'/'core'/'boot-error.js').write_text(boot_error,encoding='utf-8')

# Turn the legacy app body into a module-backed asynchronous boot while preserving its internal runtime.
rt=runtime
prefix="(()=>{'use strict';\nconst DATA=JSON.parse(document.getElementById('appData').textContent),PLAN=DATA.plan,CORE=DATA.core.days,WORDS=DATA.words,LIB=DATA.library.articles,RES=DATA.resources.days,PATTERNS=DATA.patterns||[];"
if prefix not in rt:
    raise SystemExit('Runtime bootstrap marker not found; aborting safe migration')
new_prefix="""import { loadAppData } from './core/data-loader.js';
import { showBootError } from './core/boot-error.js';

(async () => {
'use strict';
const DATA = await loadAppData();
const PLAN=DATA.plan,CORE=DATA.core.days,WORDS=DATA.words,LIB=DATA.library.articles,RES=DATA.resources.days,PATTERNS=DATA.patterns||[];"""
rt=rt.replace(prefix,new_prefix,1)
# Original final closure is the app IIFE. Add an explicit boot rejection handler.
end="})();;\n\n"
if not rt.rstrip().endswith('})();;'):
    raise SystemExit('Unexpected runtime ending; aborting')
rt=rt.rstrip()
rt=rt[:-len('})();;')] + "})().catch(showBootError);\n"
(ROOT/'assets'/'js'/'app.js').write_text(rt,encoding='utf-8')

# Modify HTML conservatively via exact tags derived from BeautifulSoup contents.
# Replace six inline styles with a single external stylesheet at the original first style position.
style_patterns=list(re.finditer(r'<style\b[^>]*>.*?</style\s*>',html,flags=re.I|re.S))
if len(style_patterns)!=6:
    raise SystemExit(f'HTML regex style count mismatch: {len(style_patterns)}')
for i,m in reversed(list(enumerate(style_patterns))):
    replacement='<link rel="stylesheet" href="./assets/css/app.css">' if i==0 else ''
    html=html[:m.start()]+replacement+html[m.end():]
# Remove embedded content JSON.
html, n=re.subn(r'<script\b(?=[^>]*\bid=["\']appData["\'])(?=[^>]*\btype=["\']application/json["\'])[^>]*>.*?</script\s*>','',html,count=1,flags=re.I|re.S)
if n!=1:
    raise SystemExit('Could not remove embedded appData safely')
# Replace remaining inline runtime script with external module loader.
# Stage 42 runtime has exactly one remaining inline script block.
runtime_repl='<script type="module" src="./assets/js/app.js"></script>'
html,n=re.subn(r'<script\b(?![^>]*\bsrc=)[^>]*>.*?</script\s*>',runtime_repl,html,count=1,flags=re.I|re.S)
if n!=1:
    raise SystemExit(f'Could not externalize runtime script, replacements={n}')
(ROOT/'index.html').write_text(html,encoding='utf-8')

# Service worker: bump cache generation and precache separated app modules/data for offline cold start.
sw_path=ROOT/'sw.js'
sw=sw_path.read_text(encoding='utf-8')
sw=sw.replace("const PREFIX='ielts-boost-stage42';", "const PREFIX='ielts-boost-stage43';")
sw=sw.replace("const SHELL_CACHE=PREFIX+'-shell-v3';", "const SHELL_CACHE=PREFIX+'-shell-v4';")
sw=sw.replace("const AUDIO_CACHE=PREFIX+'-audio-v3';", "const AUDIO_CACHE=PREFIX+'-audio-v4';")
sw=sw.replace("'./app-icon-96-maskable.png'].map", "'./app-icon-96-maskable.png','./assets/css/app.css','./assets/js/app.js','./assets/js/core/data-loader.js','./assets/js/core/boot-error.js','./data/app-data.json'].map")
sw_path.write_text(sw,encoding='utf-8')

# Update metadata/docs without changing learner data or old storage key.
meta={
 'stage':'43','release':'43.0.0','date':'2026-11-08',
 'architecture':'phase-1 safe extraction',
 'document_shell':'index.html',
 'styles':'assets/css/app.css',
 'runtime':'assets/js/app.js (Stage 42 compatibility runtime, now loaded as an ES module)',
 'core_modules':['assets/js/core/data-loader.js','assets/js/core/boot-error.js'],
 'content_data':'data/app-data.json',
 'offline':'Service Worker precaches shell, runtime modules, stylesheet and content JSON',
 'storage_compatibility':'Existing localStorage namespace and IndexedDB audio keys are unchanged',
 'curriculum':'84 days / 336 core skill sessions',
 'limits':'Feature-level runtime decomposition remains a later safe migration; no unverified function-level extraction was attempted.'
}
(ROOT/'STAGE43_ARCHITECTURE_MANIFEST.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')

print('Built Stage 43')
print('HTML bytes', (ROOT/'index.html').stat().st_size)
print('Data bytes', (ROOT/'data/app-data.json').stat().st_size)
print('JS bytes', (ROOT/'assets/js/app.js').stat().st_size)
print('CSS bytes', (ROOT/'assets/css/app.css').stat().st_size)
