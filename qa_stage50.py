#!/usr/bin/env python3
"""Final Stage 50 release validation. Runs direct product/data/media checks and non-recursive engine suites."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
import json, csv, re, subprocess, threading, os, hashlib, time, sys

ROOT = Path(__file__).resolve().parents[1]
checks=[]
regressions=[]

def check(name, ok, detail=''):
    checks.append({'name':name,'passed':bool(ok),'detail':str(detail)[:1800]})

def run(cmd, timeout=240):
    try:
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
        return p.returncode, (p.stdout or '')+(p.stderr or '')
    except subprocess.TimeoutExpired as e:
        return 124, (e.stdout or b'').decode(errors='replace')+'\nTIMEOUT'

# Release identity, shell, PWA and deploy target.
html=(ROOT/'index.html').read_text(encoding='utf-8')
app=(ROOT/'assets/js/app.js').read_text(encoding='utf-8')
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
css=(ROOT/'assets/css/stage50.css').read_text(encoding='utf-8')
manifest=json.loads((ROOT/'manifest.webmanifest').read_text(encoding='utf-8'))
target=(ROOT/'DEPLOY_TARGET.txt').read_text(encoding='utf-8')
check('Final HTML release title is Stage 50', '<title>IELTS Boost · Final Release 50</title>' in html)
check('Stage 50 app metadata and acceptance object exist', "DATA.meta.release='50.0.0'" in app and "window.__IELTS_BOOST_STAGE50__={version:'50.0.0'" in app)
check('Settings has final acceptance transparency panel', 'stage50-release-panel' in app and 'browser end-to-end testing was blocked' in app.lower())
check('Stage 50 stylesheet linked and exists', './assets/css/stage50.css' in html and (ROOT/'assets/css/stage50.css').exists())
check('Project-relative PWA validator is imported and precached', "from './core/pwa-validation.js'" in app and (ROOT/'assets/js/core/pwa-validation.js').exists() and 'pwa-validation.js' in sw)
check('Legacy hard-coded PWA readiness check is overridden by final relative-scope validator', 'p37CheckPwa=p50CheckPwa' in app and 'inspectPwaManifest(manifest,link.href,location.href)' in app)
check('Responsive final release CSS covers mobile and reduced motion', '@media(max-width:760px)' in css and '@media(max-width:360px)' in css)
check('Manifest uses deployment-relative PWA scope', manifest.get('id')=='./' and manifest.get('scope')=='./' and manifest.get('start_url')=='./')
check('Manifest final version and standalone display', manifest.get('version')=='50.0.0' and manifest.get('display')=='standalone')
check('Manifest icons have valid local relative paths', all(x.get('src','').startswith('./') and (ROOT/x['src'][2:]).exists() for x in manifest.get('icons',[])))
check('Service worker uses Stage 50 shell generation', "const PREFIX='ielts-boost-stage50'" in sw and "const SHELL_CACHE=PREFIX+'-shell-v12'" in sw)
check('Startup watchdog is linked, precached and present', './assets/js/boot-watchdog.js' in html and (ROOT/'assets/js/boot-watchdog.js').exists() and './assets/js/boot-watchdog.js' in sw)
check('Old Stage 42 listening audio cache is retained', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw)
check('Service worker includes new Stage 50 CSS and prior core modules', all(x in sw for x in ['stage50.css','app.js','data-loader.js','scoring-engine.js','adaptive-engine.js','task1-intelligence.js','vocabulary-engine.js','backup-engine.js','pwa-validation.js']))
check('CSP restricts scripts to same origin and blocks objects', "script-src 'self'" in html and "object-src 'none'" in html)
check('External scripts are not injected into HTML', not re.search(r'<script[^>]+src=["\']https?://',html,re.I))
check('Skip link and main landmark retained', 'class="skip-link"' in html and '<main id="app" tabindex="-1">' in html)
check('Deployment target file is explicit and matches relative PWA strategy', 'GitHub Pages URL:' in target and manifest['scope']=='./')

# Ensure all shell precache assets exist.
m=re.search(r'const CORE=\[(.*?)\]\.map',sw,re.S)
core_paths=re.findall(r"['\"](\./[^'\"]+)['\"]",m.group(1)) if m else []
missing_core=[x for x in core_paths if not (ROOT/x[2:]).exists()]
check('All Service Worker CORE precache paths exist', bool(core_paths) and not missing_core, f'{len(core_paths)} core paths; missing={missing_core}')

# Content integrity, curriculum and resources.
data=json.loads((ROOT/'data/app-data.json').read_text(encoding='utf-8'))
res=json.loads((ROOT/'data/stage47-resource-catalog.json').read_text(encoding='utf-8'))
plan=data['plan']['days']; core=data['core']['days']; resources=data['resources']['days']
check('84-day IELTS Academic plan remains intact', len(plan)==84 and data['plan'].get('assumed_test_type','').lower().find('academic')>=0)
check('All four mandatory skills exist on all 84 days', len(core)==84 and all(all(k in d for k in ['reading','listening','writing','speaking']) for d in core))
check('All 336 resource cards are mapped', len(resources)==84 and all(all(k in d.get('resources',{}) for k in ['reading','listening','writing','speaking']) for d in resources))
check('Reading question bank contains 840 questions', sum(len(d['reading'].get('questions',[])) for d in core)==840)
check('Listening question bank contains 420 questions', sum(len(d['listening'].get('questions',[])) for d in core)==420)
check('84 original Writing Task 2 prompts are present', len({d['writing'].get('task2_prompt','').strip() for d in core})==84)
check('Speaking prompt pack has 252 Part 1, 84 Part 2 and 252 Part 3 items', sum(len(d['speaking'].get('part1',[])) for d in core)==252 and sum(len(d['speaking'].get('part3',[])) for d in core)==252 and sum(bool(d['speaking'].get('part2')) for d in core)==84)
check('61-article supplemental library preserved', len(data.get('library',{}).get('articles',[]))==61)
check('864 Sentence Patterns preserved', len(data.get('patterns',[]))==864)
check('Vocabulary index has 19,000 unique records', len(data.get('words',[]))==19000 and len({w.get('id') for w in data['words']})==19000)
sets=data.get('vocabularyExpert',{}).get('daily_sets',[])
word_ids=[i for x in sets for i in x.get('word_ids',[])]
check('84 vocabulary packs contain 672 distinct core items', len(sets)==84 and len(word_ids)==672 and len(set(word_ids))==672)
check('Daily vocabulary core remains 672 complete bilingual glosses', sum(1 for w in data['words'] if w.get('id') in set(word_ids) and all(str(w.get(k,'')).strip() for k in ['meaning_en','uzbek','example','part_of_speech']))==672)
check('61 articles and 864 patterns are supplemental, not mandatory replacements', len(data.get('library',{}).get('articles',[]))==61 and len(data.get('patterns',[]))==864)

# Ten labs and all 84 Task 1 original visuals.
lab=(ROOT/'assets/js/core/lab-quality-engine.js').read_text(encoding='utf-8')
ids=re.search(r'LAB_IDS\s*=\s*Object\.freeze\(\[(.*?)\]\)',lab,re.S)
lab_ids=re.findall(r"['\"]([a-z_]+)['\"]",ids.group(1)) if ids else []
check('Ten primary learning laboratories are uniquely registered', len(lab_ids)==10 and len(set(lab_ids))==10, ', '.join(lab_ids))
with (ROOT/'STAGE47_TASK1_84_VISUAL_AUDIT_UZ.csv').open(encoding='utf-8-sig',newline='') as f: visual_rows=list(csv.DictReader(f))
types={}
for r in visual_rows: types[r['visual_type']]=types.get(r['visual_type'],0)+1
check('84 Task 1 visuals cover six families with 14 each', len(visual_rows)==84 and sorted(types.values())==[14]*6, str(types))
check('Task 1 visual families are original fictional datasets', all('original' in r.get('provenance','').lower() or 'fictional' in r.get('provenance','').lower() for r in visual_rows))
check('Task 1 inspector and 4-part planner remain wired', 's47Task1Masterclass' in app and 's47-data-inspector' in app and all(x in app for x in ['overview','bodyOne','bodyTwo','accuracyNotes']))

# 84 day external listening mapping and provider boundaries.
assignments=res.get('assignments',[]); catalog=res.get('catalog',[])
check('84 day Listening companion mapping exists', len(assignments)==84 and all(x.get('url','').startswith('https://') and x.get('title') and x.get('provider') for x in assignments))
check('Listening companion mapping has individual task/focus per day', all(x.get('listening_focus') and x.get('study_task') and x.get('repeat_design') for x in assignments))
check('External podcast/video assets are not rehosted in the project', all('official' in str(x.get('embed_mode','')).lower() or 'link' in str(x.get('embed_mode','')).lower() for x in assignments))
check('Rights policy explicitly rejects copyrighted Barron copying and source rehosting', (ROOT/'STAGE47_RESOURCE_RIGHTS_POLICY_UZ.md').exists() and 'Do not reproduce Barron' in (ROOT/'STAGE47_RESOURCE_RIGHTS_POLICY_UZ.md').read_text(encoding='utf-8'))
check('Joe Rogan is excluded from compulsory 84-day schedule', all('Joe Rogan' not in x.get('provider','') for x in assignments))
check('Listening catalog is distinct from daily reuse count', len(catalog)>=25 and len({x.get('resource_id') for x in assignments})<84)

# All bundled MP3 tracks exist, have content and can be parsed by ffprobe.
audios=sorted((ROOT/'audio').glob('listening-day-*.mp3'))
check('84 bundled Listening MP3 files are present and non-empty', len(audios)==84 and all(x.stat().st_size>10000 for x in audios), f'{len(audios)} files; {sum(x.stat().st_size for x in audios):,} bytes')
def probe(p):
    cp=subprocess.run(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels','-show_entries','format=duration','-of','json',str(p)],capture_output=True,text=True,timeout=30)
    if cp.returncode: return p.name,False,cp.stderr[-400:]
    try:
        meta=json.loads(cp.stdout); st=meta['streams'][0]; dur=float(meta['format']['duration'])
        return p.name,st.get('codec_name')=='mp3' and dur>0, f"{st.get('codec_name')} · {dur:.2f}s"
    except Exception as e: return p.name,False,str(e)
probe_results=[]
with ThreadPoolExecutor(max_workers=6) as ex:
    futures=[ex.submit(probe,p) for p in audios]
    for future in as_completed(futures): probe_results.append(future.result())
probe_results.sort()
check('All 84 bundled MP3 files pass ffprobe stream/container validation', len(probe_results)==84 and all(x[1] for x in probe_results), f"{sum(1 for x in probe_results if x[1])}/84 valid")

# JavaScript syntax and direct engine suites.
modules=sorted((ROOT/'assets/js').rglob('*.js'))+[ROOT/'sw.js']
syntax=[]
for p in modules:
    cp=subprocess.run(['node','--experimental-default-type=module','--check',str(p)],capture_output=True,text=True,timeout=30)
    syntax.append({'file':str(p.relative_to(ROOT)),'passed':cp.returncode==0,'detail':cp.stderr[-500:]})
check('All application/core/service-worker JavaScript modules parse', all(x['passed'] for x in syntax), f'{sum(x["passed"] for x in syntax)}/{len(syntax)} modules')

engine_cmds=[
    ('Stage 50 cross-engine final invariants',['node','--experimental-default-type=module','tools/qa_stage50.mjs'],'STAGE 50 ENGINE QA: 36/36 PASS'),
    ('Stage 48 vocabulary engine',['node','--experimental-default-type=module','tools/qa_stage48.mjs'],'STAGE 48 ENGINE QA: 34/34 PASS'),
    ('Stage 49 backup integrity engine',['node','--experimental-default-type=module','tools/qa_stage49.mjs'],'STAGE 49 BACKUP ENGINE TESTS: 10/10 PASS'),
    ('Stage 46 adaptive engine',['node','tools/qa_stage46.mjs'],'"passed": 47'),
    ('Stage 47 Task 1 engine',['node','tools/qa_stage47.mjs'],'"passed": 19'),
]
engine_results=[]
for label,cmd,needle in engine_cmds:
    rc,out=run(cmd,timeout=120)
    ok=rc==0 and needle in out
    engine_results.append({'label':label,'returncode':rc,'passed':ok,'summary':out[-3000:]})
    check(label,ok,out[-700:])

# Historical regression suites without recursively invoking the entire Stage 49 aggregate.
regression_cmds=[
 ('Stage 41 curriculum/transcript static regression',['python','tools/qa_stage41.py'],'STAGE 41 STATIC QA: 21/21 PASS'),
 ('Stage 42 transcript lifecycle regression',['python','tools/qa_stage42.py'],'STAGE 42 STATIC QA: 23/23 PASS'),
 ('Stage 43 modular architecture regression',['python','tools/qa_stage43.py'],'STAGE 43 QA: 39/39 PASS'),
 ('Stage 44 scoring regression',['python','tools/qa_stage44.py'],'STAGE 44 QA: 30/30 PASS'),
 ('Stage 45 laboratory regression',['python','tools/qa_stage45.py'],'STAGE 45 QA: 33/33 PASS'),
 ('Stage 47 resource integration regression',['python','tools/qa_stage47.py'],'STAGE 47 QA: 40/40 PASS'),
]
for label,cmd,needle in regression_cmds:
    rc,out=run(cmd,timeout=240)
    ok=rc==0 and needle in out
    regression_results={'label':label,'returncode':rc,'passed':ok,'summary':out[-3000:]}
    regressions.append(regression_results)
    check(label,ok,out[-800:])

# HTTP smoke for all local shell, data and media paths using HEAD.
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
old=os.getcwd(); os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet); th=threading.Thread(target=server.serve_forever,daemon=True); th.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
paths=['/','/index.html','/manifest.webmanifest','/sw.js','/assets/css/app.css','/assets/css/stage47.css','/assets/css/stage48.css','/assets/css/stage49.css','/assets/css/stage50.css','/assets/js/app.js','/assets/js/core/data-loader.js','/assets/js/core/backup-engine.js','/assets/js/core/vocabulary-engine.js','/assets/js/core/task1-intelligence.js','/assets/js/core/adaptive-engine.js','/assets/js/core/scoring-engine.js','/assets/js/core/lab-quality-engine.js','/data/app-data.json','/data/stage47-resource-catalog.json','/audio/listening-day-01.mp3','/audio/listening-day-84.mp3']
http=[]
try:
    for path in paths:
        try:
            with urlopen(Request(base+path,method='HEAD'),timeout=20) as resp: http.append({'path':path,'status':resp.status})
        except Exception as e: http.append({'path':path,'status':0,'error':str(e)})
finally:
    server.shutdown(); server.server_close(); os.chdir(old)
check('HTTP smoke: all 21 local routes return 200',len(http)==21 and all(x['status']==200 for x in http),'; '.join(f"{x['path']}={x['status']}" for x in http))

# Payload/performance disclosure and safe external links.
payload=(ROOT/'data/app-data.json').stat().st_size
check('Large initial payload is disclosed rather than called fully lazy-loaded', payload>10*1024*1024 and 'Initial content payload remains a large JSON resource' in app)
check('No app-generated official IELTS band guarantee', 'does not guarantee a band score' in app or 'not an IELTS band' in app)
check('Backup/restore limitations are disclosed to learners', 'Audio blobs stay in IndexedDB' in app and 'not encrypted by the app' in app)

passed=sum(x['passed'] for x in checks); total=len(checks)
report={
 'stage':50,'release':'50.0.0','date':'2026-11-09','passed':passed,'total':total,'failed':total-passed,
 'checks':checks,'engine_suites':engine_results,'regression_suites':regressions,
 'audio_probe':probe_results,'js_syntax':syntax,'http':http,
 'browser_acceptance':{'status':'BLOCKED_BY_ENVIRONMENT','passed':0,'executed':1,'detail':'Chromium/Playwright was attempted; environment returned ERR_BLOCKED_BY_ADMINISTRATOR before app navigation. No page-render assertions ran.'},
 'physical_device_acceptance':{'status':'PENDING','device':'Samsung Galaxy A14','required':['GitHub Pages project-scope load','Chrome install/Add to Home Screen','offline shell and requested MP3 playback','microphone + MediaRecorder','SpeechRecognition or keyboard fallback','backup export/import','320–430px layout review']},
 'limitations':['The 15 MB app-data JSON is loaded as one content payload; no final Lighthouse score or real-device performance benchmark is claimed.','Local-first progress is not encrypted at rest and no cloud sync exists.','JSON backup excludes IndexedDB audio blobs; recordings must be exported separately.','Live SpeechRecognition depends on browser/device/network support; manual transcript remains available.','External video/caption/embed availability is controlled by providers.','IELTS Boost is independent practice, not an official IELTS product or examiner; internal 0–10 scores are not IELTS bands.'],
 'deployment_target':target.strip()
}
(ROOT/'STAGE50_QA_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'STAGE50_QA_RESULTS.txt').write_text('\n'.join([f'STAGE 50 FINAL QA: {passed}/{total} PASS']+[('PASS' if x['passed'] else 'FAIL')+' | '+x['name']+' | '+x['detail'] for x in checks]),encoding='utf-8')
print(f'STAGE 50 FINAL QA: {passed}/{total} PASS')
for x in checks: print(('PASS' if x['passed'] else 'FAIL')+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
if passed!=total: sys.exit(1)
