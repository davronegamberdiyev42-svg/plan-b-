#!/usr/bin/env python3
"""Stage 47 static/data/HTTP acceptance checks. Not a substitute for device E2E."""
from pathlib import Path
import csv, json, subprocess, sys, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
checks = []
def check(name, condition, detail=''):
    checks.append((name, bool(condition), detail))

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

app = (ROOT/'assets/js/app.js').read_text(encoding='utf-8')
index = (ROOT/'index.html').read_text(encoding='utf-8')
sw = (ROOT/'sw.js').read_text(encoding='utf-8')
css = (ROOT/'assets/css/stage47.css').read_text(encoding='utf-8')
data = load_json('data/app-data.json')
resources = data['resources']
stage = resources['stage47']
assignments = stage['daily_assignments']
resource_days = resources['days']
core_days = data['core']['days']

check('Stage 47 title and stylesheet are wired', 'Final Release 50' in index and 'assets/css/stage47.css' in index and 'assets/css/stage48.css' in index, 'HTML title + CSS link')
check('Task 1 intelligence module is imported and used', "./core/task1-intelligence.js" in app and 'analyseTask1Spec(' in app and 'validateTask1Days(' in app)
check('Stage 47 companion, four-skill and Task 1 UI are present', all(x in app for x in ['s47ResourceCard','s47AllFourPack','s47Task1Masterclass','s47-data-inspector','150 so‘z']))
check('Stage 47 responsive visual styles exist', all(x in css for x in ['s47-companion','s47-task1-master','s47-data-table','@media']))
check('Service worker precaches Stage 47 assets and preserves audio cache', ('ielts-boost-stage50' in sw and 'shell-v12' in sw) and 'assets/css/stage47.css' in sw and 'assets/css/stage48.css' in sw and 'vocabulary-engine.js' in sw and 'task1-intelligence.js' in sw and 'ielts-boost-stage42-audio-v3' in sw)

check('84-day curriculum intact', data['plan']['duration_days'] == 84 and len(data['plan']['days']) == 84 and len(core_days) == 84)
check('Four compulsory skill modules exist for all 84 days', all(all(k in d.get('modules',{}) for k in ['reading','writing','speaking','listening']) for d in data['plan']['days']), '84 × 4 = 336 plan modules')
check('84 daily in-app resource maps exist', len(resource_days) == 84)
check('Four daily in-app resource packs exist on every day', all(all(k in d.get('resources',{}) for k in ['reading','listening','writing','speaking']) for d in resource_days), '84 × 4 = 336 in-app skill resource slots')
check('61-article supplementary library remains', len(data.get('library',{}).get('articles',[])) == 61 if isinstance(data.get('library'),dict) else len(data.get('library',[])) == 61)

check('84 individual listening companion assignments exist', len(assignments) == 84 and [x.get('day') for x in assignments] == list(range(1,85)))
check('All 84 assignments have exact official HTTPS URLs and item metadata', all(x.get('title') and x.get('url','').startswith('https://') and x.get('provider') and x.get('level_estimate') and x.get('listening_focus') and x.get('transcript_caption_status') and x.get('age_suitability') for x in assignments))
check('Each daily resource map carries the identical selected companion', all(resource_days[i]['resources']['listening'].get('stage47_companion',{}).get('url') == assignments[i]['url'] and resource_days[i]['resources']['listening']['stage47_companion'].get('resource_id') == assignments[i]['resource_id'] for i in range(84)))
check('Daily companion rotation uses 28 unique selected items', len({x['resource_id'] for x in assignments}) == 28, '84 day slots; repeats use a distinct listening focus')
check('Curated catalogue contains 36 individually named official resources', len(stage['catalog']) == 36 and len({x['id'] for x in stage['catalog']}) == 36)
provider_daily = Counter(x['provider'] for x in assignments)
check('Daily provider mix includes TED-Ed, TED, Huberman Lab and DOAC', all(provider_daily[x] > 0 for x in ['TED-Ed','TED','Huberman Lab','The Diary of a CEO']), str(dict(provider_daily)))
provider_names = {x['provider'] for x in stage['provider_directory']}
check('All five requested provider families are documented', {'TED-Ed','TED Talks','Huberman Lab','The Diary of a CEO','Joe Rogan Experience'} <= provider_names)
jre = stage.get('optional_discovery',[])
check('Joe Rogan is optional preview-only, never compulsory', len(jre) >= 1 and all(x.get('eligible_for_daily') is False and 'PREVIEW_REQUIRED' in x.get('safe','') for x in jre))
check('External media is not downloaded or rehosted', all(x.get('embed') in ['official-link-only','official-youtube-link-only','TED official page/link only'] for x in stage['catalog']) and all(term in ' '.join(stage.get('source_rights',{}).values()).lower() for term in ['no rehosting','do not download']), 'Official provider URLs only; no third-party media copies')

chart_days = [x for x in resource_days if x.get('resources',{}).get('writing',{}).get('task1')]
types = Counter(x['resources']['writing']['task1']['type'] for x in chart_days)
check('All 84 Task 1 visuals are present', len(chart_days) == 84)
check('Six Task 1 visual families have exactly 14 datasets each', types == Counter({'line_graph':14,'bar_chart':14,'pie_chart':14,'table':14,'process':14,'map':14}), str(dict(types)))
check('All Task 1 sets are labelled original fictional practice data', all(x['resources']['writing']['task1'].get('source_type') == 'original_practice_dataset' and 'fictional' in x['resources']['writing']['task1'].get('data_note','').lower() and 'original' in x['resources']['writing']['task1'].get('dataset_status','').lower() for x in chart_days))
check('All 84 Task 2 prompts remain present', all(bool(x['resources']['writing'].get('task2_prompt')) for x in resource_days))
check('All four skill content records exist in 84 core days', all(all(k in d for k in ['reading','listening','writing','speaking']) for d in core_days))
check('84 MP3 tracks remain present and non-empty', len(list((ROOT/'audio').glob('listening-day-*.mp3'))) == 84 and all(p.stat().st_size > 10_000 for p in (ROOT/'audio').glob('listening-day-*.mp3')))

# Run full data validation and visual-specific logic harness.
res = subprocess.run(['node','tools/qa_stage47.mjs'], cwd=ROOT, text=True, capture_output=True)
check('Task 1 visual engine: 84-day data + six chart fixtures + edge cases', res.returncode == 0, res.stdout.strip() if res.returncode == 0 else res.stderr.strip())

# Parse resource mapping: one exact row per day.
with (ROOT/'STAGE47_RESOURCE_MAPPING_UZ.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
check('84-row resource mapping CSV is complete', len(rows) == 84 and [int(x['day']) for x in rows] == list(range(1,85)))
check('84-row mapping agrees with app-data assignments', all(rows[i]['official_url'] == assignments[i]['url'] and rows[i]['resource_id'] == assignments[i]['resource_id'] for i in range(84)))
with (ROOT/'STAGE47_336_SKILL_RESOURCE_AUDIT_UZ.csv').open(encoding='utf-8-sig', newline='') as f:
    skill_rows = list(csv.DictReader(f))
check('336-row mandatory skill resource audit is complete', len(skill_rows) == 336)
check('Each of 84 days has exactly 4 skill audit rows', all(sum(1 for x in skill_rows if int(x['day'])==d)==4 for d in range(1,85)))
check('Every daily resource-audit row has a primary in-app material and source/rights note', all(x.get('primary_in_app_material') and x.get('source_and_rights') and x.get('verification_status') for x in skill_rows))
with (ROOT/'STAGE47_TASK1_84_VISUAL_AUDIT_UZ.csv').open(encoding='utf-8-sig', newline='') as f:
    task1_rows = list(csv.DictReader(f))
check('84-row Task 1 visual audit is complete', len(task1_rows) == 84 and [int(x['day']) for x in task1_rows] == list(range(1,85)))
check('Task 2 prompts are 84 distinct originals', len({x['resources']['writing']['task2_prompt'] for x in resource_days}) == 84)
check('Speaking daily pack has 252 Part 1, 84 Part 2 and 252 Part 3 prompts', all(len(x['speaking']['part1'])==3 and bool(x['speaking']['part2']) and len(x['speaking']['part3'])==3 for x in core_days))

# Syntax-check core app modules.
for rel in ['assets/js/app.js','assets/js/core/task1-intelligence.js','assets/js/core/adaptive-engine.js','assets/js/core/lab-quality-engine.js','sw.js']:
    cp = subprocess.run(['node','--check',str(ROOT/rel)], cwd=ROOT, text=True, capture_output=True)
    check(f'JavaScript syntax · {rel}', cp.returncode == 0, 'node --check PASS' if cp.returncode == 0 else cp.stderr.strip())

# Local HTTP resource smoke check.
class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def http_smoke():
    import os
    old=os.getcwd(); os.chdir(ROOT)
    server=ThreadingHTTPServer(('127.0.0.1',0), QuietHandler)
    th=threading.Thread(target=server.serve_forever,daemon=True); th.start()
    base=f'http://127.0.0.1:{server.server_address[1]}'
    paths=['/','/index.html','/assets/css/stage47.css','/assets/css/stage48.css','/assets/js/app.js','/assets/js/core/task1-intelligence.js','/assets/js/core/vocabulary-engine.js','/data/app-data.json','/sw.js','/audio/listening-day-01.mp3','/audio/listening-day-84.mp3']
    out=[]
    try:
        for path in paths:
            try:
                with urlopen(Request(base+path,method='HEAD'),timeout=15) as r:
                    out.append((path,r.status,r.headers.get('Content-Type','')))
                    # HEAD checks status and headers without transferring the large asset.
            except Exception as e: out.append((path,0,str(e)))
    finally:
        server.shutdown();server.server_close();os.chdir(old)
    return out
http = http_smoke()
check('HTTP local-server smoke test: 11 core resources return 200', len(http)==11 and all(x[1]==200 for x in http), '; '.join(f'{p}={s}' for p,s,_ in http))

ok=sum(1 for _,passed,_ in checks if passed)
print(f'STAGE 47 QA: {ok}/{len(checks)} PASS')
for name,passed,detail in checks:
    print(('PASS' if passed else 'FAIL')+' | '+name+(f' | {detail}' if detail else ''))
if res.returncode != 0:
    print('TASK1 NODE TEST STDERR:',res.stderr)
report={'stage':47,'passed':ok,'total':len(checks),'failed':len(checks)-ok,'checks':[{'name':n,'passed':p,'detail':d} for n,p,d in checks], 'limitations':['Static/data and local HTTP QA do not replace browser E2E or physical Android acceptance.','External video playback and caption availability can change and must be checked in provider players.','JRE remains optional preview-only; it is not part of compulsory daily listening.']}
(ROOT/'STAGE47_QA_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
sys.exit(0 if ok==len(checks) else 1)
