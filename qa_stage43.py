#!/usr/bin/env python3
"""Stage 43 modular architecture + Stage 44 scoring integration regression QA.

Run from project root: python tools/qa_stage43.py
This is static/structural QA; it does not claim physical-device acceptance.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
checks: list[dict] = []

def check(name: str, ok: bool, detail: str = '') -> None:
    checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

def file(path: str) -> Path:
    return ROOT / path

index = file('index.html')
data_file = file('data/app-data.json')
app_js = file('assets/js/app.js')
css = file('assets/css/app.css')
loader = file('assets/js/core/data-loader.js')
boot_error = file('assets/js/core/boot-error.js')
sw_file = file('sw.js')

# Structural separation
check('HTML shell exists and is lightweight', index.is_file() and index.stat().st_size < 10_000, f'{index.stat().st_size:,} bytes')
html = index.read_text(encoding='utf-8') if index.exists() else ''
check('HTML loads one external stylesheet', 'href="./assets/css/app.css"' in html and '<style' not in html.lower(), 'external CSS reference found')
check('HTML loads app as an ES module', '<script type="module" src="./assets/js/app.js"></script>' in html, 'module entry found')
check('Large JSON payload is no longer embedded in HTML', 'id="appData"' not in html and 'application/json' not in html, 'no embedded appData script')
check('Application runtime is external', app_js.is_file() and app_js.stat().st_size > 500_000, f'{app_js.stat().st_size:,} bytes')
check('Stylesheet is external and complete', css.is_file() and css.stat().st_size > 50_000, f'{css.stat().st_size:,} bytes')
check('Core data loader module exists', loader.is_file() and 'loadAppData' in loader.read_text(encoding='utf-8'), 'loader module found')
check('Boot error/retry module exists', boot_error.is_file() and 'showBootError' in boot_error.read_text(encoding='utf-8'), 'accessible failure UI found')

# Content preservation
try:
    data = json.loads(data_file.read_text(encoding='utf-8'))
    data_valid = isinstance(data, dict)
except Exception as exc:
    data = {}
    data_valid = False
check('External content JSON parses', data_valid, f'{data_file.stat().st_size:,} bytes' if data_file.exists() else 'missing')
plan = data.get('plan', {})
plan_days = plan.get('days', [])
core_days = data.get('core', {}).get('days', [])
check('84-day curriculum preserved', len(plan_days) == 84 and len(core_days) == 84, f'plan={len(plan_days)}, content={len(core_days)}')
required = ('reading', 'writing', 'speaking', 'listening')
all_skill = bool(plan_days) and all(all(day.get('modules', {}).get(k) for k in required) for day in plan_days)
check('All four mandatory skills preserved every day', all_skill, '336/336 modules' if all_skill else 'missing skill module')
reading_q = sum(len(d.get('reading', {}).get('questions', [])) for d in core_days)
listening_q = sum(len(d.get('listening', {}).get('questions', [])) for d in core_days)
check('Reading question bank preserved', reading_q == 840, f'{reading_q} questions')
check('Listening question bank preserved', listening_q == 420, f'{listening_q} questions')
check('Vocabulary index preserved', len(data.get('words', [])) == 19_000, f'{len(data.get("words", [])):,} records')
check('61-article library preserved', len(data.get('library', {}).get('articles', [])) == 61, f'{len(data.get("library", {}).get("articles", []))} articles')
check('864 sentence patterns preserved', len(data.get('patterns', [])) == 864, f'{len(data.get("patterns", []))} patterns')

# App asset references resolve within the release folder.
for rel in ['./assets/css/app.css', './assets/js/app.js', './assets/js/core/data-loader.js', './assets/js/core/boot-error.js', './data/app-data.json']:
    check(f'Asset path resolves: {rel}', file(rel[2:]).is_file(), 'exists' if file(rel[2:]).is_file() else 'missing')
loader_text = loader.read_text(encoding='utf-8') if loader.exists() else ''
check('Data loader fetches content relative to deployment root', "new URL('./data/app-data.json', document.baseURI)" in loader_text, 'works with GitHub Pages project subpath')
check('Data loader validates schema and 84-day curriculum', all(x in loader_text for x in ['data.plan', 'data.core?.days', 'data.words', 'APP_DATA_CURRICULUM']), 'shape and curriculum guards found')
check('Startup failure includes retry path', 'appBootRetry' in (boot_error.read_text(encoding='utf-8') if boot_error.exists() else ''), 'retry control found')

# Existing learner state and Stage 42 speaking implementation remain unchanged.
runtime = app_js.read_text(encoding='utf-8') if app_js.exists() else ''
check('Existing localStorage namespace unchanged', "const STORAGE='ielts-boost-rebuilt-1.0'" in runtime, 'legacy storage namespace preserved')
check('Existing IndexedDB audio database unchanged', "indexedDB.open('IELTSBoostMedia',1)" in runtime, 'IELTSBoostMedia v1 preserved')
check('Stage 42 transcript module preserved in runtime', "const P42_VERSION='42.0.0'" in runtime and 'p37StartASR' in runtime, 'transcript runtime retained')
check('Ten primary learning laboratories preserved', 'const P37_MODULES' in runtime and len(re.findall(r"\bid\s*:\s*'[^']+'", runtime[runtime.find('const P37_MODULES'):runtime.find('const P37_MODULES')+10000])) >= 10, 'laboratory registry found')

# Service worker offline shell and old audio cache continuity.
sw = sw_file.read_text(encoding='utf-8') if sw_file.exists() else ''
check('Service worker cache namespace advanced to Stage 47', "const PREFIX='ielts-boost-stage50'" in sw and 'shell-v12' in sw, 'Stage 46 shell cache generation')
check('Previously cached Stage 42 audio cache retained', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw, 'offline listening cache continuity')
cache_assets = ['./assets/css/app.css','./assets/js/app.js','./assets/js/core/data-loader.js','./assets/js/core/boot-error.js','./assets/js/core/scoring-engine.js','./data/app-data.json']
check('Service worker precaches all separated modules and data', all(x in sw for x in cache_assets), 'Stage 43–45 app resources in CORE')
missing_cache = [p for p in cache_assets if not file(p[2:]).is_file()]
check('Every precached Stage 45 asset exists', not missing_cache, ', '.join(missing_cache) if missing_cache else 'all found')

# Syntax
for name, path in [('Application ES module', app_js), ('Data loader module', loader), ('Boot error module', boot_error), ('Scoring engine module', file('assets/js/core/scoring-engine.js')), ('Service worker', sw_file)]:
    if path.exists():
        proc = subprocess.run(['node', '--check', str(path)], text=True, capture_output=True)
        check(f'JavaScript syntax: {name}', proc.returncode == 0, 'node --check PASS' if proc.returncode == 0 else proc.stderr[-800:])
    else:
        check(f'JavaScript syntax: {name}', False, 'file missing')

# Confirm all 84 bundled audios remain present and non-empty.
audio = sorted((ROOT/'audio').glob('listening-day-*.mp3')) if (ROOT/'audio').exists() else []
check('84 listening audio files remain bundled', len(audio) == 84, f'{len(audio)} MP3 files')
check('All listening audio files are non-empty', len(audio) == 84 and all(p.stat().st_size > 10_000 for p in audio), 'all audio files exceed 10 KB')

passed = sum(x['passed'] for x in checks)
report = {
    'stage': 43, 'release': '43.0.0 + Stage 44 scoring-regression', 'date': '2026-11-08',
    'passed': passed, 'total': len(checks), 'all_passed': passed == len(checks),
    'checks': checks,
    'not_covered': [
        'Live Chromium end-to-end rendering was attempted but did not complete in the available runtime.',
        'Real Samsung A14 browser/PWA/microphone acceptance remains a physical-device test.',
        'Feature-level function extraction is intentionally deferred; Stage 42 runtime remains as a compatibility bundle in this safe first migration.'
    ]
}
file('STAGE43_QA_RESULTS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f"STAGE 43 QA: {passed}/{len(checks)} PASS")
for row in checks:
    print(('PASS' if row['passed'] else 'FAIL')+' | '+row['name']+(f" | {row['detail']}" if row['detail'] else ''))
print('LIMITATIONS: static/structural QA does not replace physical-device acceptance or full browser E2E validation.')
sys.exit(0 if passed == len(checks) else 1)
