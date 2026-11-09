#!/usr/bin/env python3
"""Stage 41 static acceptance checks for IELTS Boost. Uses Python stdlib + Node.js."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'
APP_JS = ROOT / 'assets/js/app.js'
DATA_JSON = ROOT / 'data/app-data.json'
results: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = '') -> None:
    results.append((name, bool(ok), detail))

def read_app_data():
    return json.loads(DATA_JSON.read_text(encoding='utf-8'))

source = APP_JS.read_text(encoding='utf-8') if APP_JS.exists() else ''
html_source = HTML.read_text(encoding='utf-8')
check('Main HTML shell exists and references extracted modules', HTML.is_file() and './assets/js/app.js' in html_source and './assets/css/app.css' in html_source, f'{HTML.stat().st_size:,} bytes')
try:
    data = read_app_data()
    check('External app-data JSON parses', True)
except Exception as exc:
    data = {}
    check('External app-data JSON parses', False, str(exc))

plan = data.get('plan', {})
days = plan.get('days', [])
check('84-day curriculum', len(days) == 84, f'{len(days)} days')
required = ('reading', 'listening', 'writing', 'speaking')
missing = [(d.get('day'), k) for d in days for k in required if not d.get('modules', {}).get(k)]
check('All four skills present on every day', not missing, f'{336-len(missing)}/336 skill modules present' if days else 'no day data')
check('Academic plan', 'Academic' in str(plan.get('assumed_test_type', '')), str(plan.get('assumed_test_type', 'not set')))
notes = ' '.join(map(str, plan.get('design_notes', []))).lower()
check('No mandatory daily minute quota in curriculum notes', 'no daily minute quota' in notes, 'plan notes inspected')

content_days = data.get('core', {}).get('days', [])
reading_q = sum(len(d.get('reading', {}).get('questions', [])) for d in content_days)
listening_q = sum(len(d.get('listening', {}).get('questions', [])) for d in content_days)
check('Reading question bank count', reading_q == 840, f'{reading_q} questions')
check('Listening question bank count', listening_q == 420, f'{listening_q} questions')

words = data.get('words', [])
complete_fields = ('meaning_en', 'uzbek', 'example', 'part_of_speech')
complete = sum(all(str(w.get(k, '')).strip() for k in complete_fields) for w in words)
check('Searchable vocabulary index count', len(words) == 19000, f'{len(words):,} entries')
check('Complete offline bilingual entries measured from fields', complete == 677, f'{complete:,} complete entries')

library_count = len(data.get('library', {}).get('articles', []))
check('Article library count', library_count == 61, f'{library_count} articles')
patterns_count = len(data.get('patterns', []))
check('Sentence pattern count', patterns_count == 864, f'{patterns_count} patterns')
source_pack_count = len(data.get('readingSourcePacks', []))
check('Reading source pack count', source_pack_count == 12, f'{source_pack_count} packs')

matches = list(re.finditer(r'const\s+P37_MODULES\s*=\s*(\[.*?\]);', source, re.S))
lab_ids = re.findall(r"\bid\s*:\s*'([^']+)'", matches[0].group(1)) if matches else []
check('Ten primary Stage 40 laboratories', len(lab_ids) == 10 and len(set(lab_ids)) == 10, ', '.join(lab_ids))

mp3s = sorted((ROOT / 'audio').glob('listening-day-*.mp3')) if (ROOT / 'audio').exists() else []
check('84 bundled listening audio files', len(mp3s) == 84, f'{len(mp3s)} MP3 files')
check('All audio files non-empty', bool(mp3s) and all(p.stat().st_size > 10_000 for p in mp3s), f'{sum(p.stat().st_size for p in mp3s):,} bytes total')

# Validate the external application ES module.
try:
    proc = subprocess.run(['node', '--check', str(APP_JS)], capture_output=True, text=True, timeout=90)
    check('External application ES module syntax', proc.returncode == 0, (proc.stderr or 'node --check passed').strip()[:400])
except FileNotFoundError:
    check('External application ES module syntax', False, 'Node.js not installed')

sw = ROOT / 'sw.js'
if sw.exists():
    proc = subprocess.run(['node', '--check', str(sw)], capture_output=True, text=True, timeout=30)
    check('Service worker JavaScript syntax', proc.returncode == 0, (proc.stderr or 'node --check passed').strip()[:400])
else:
    check('Service worker file present', False, 'sw.js missing')

# Transcript capability boundary checks: API is optional and no server transcription endpoint is bundled.
check('Browser speech-recognition adapter exists', 'function p37StartASR' in source and 'window.SpeechRecognition' in source and 'window.webkitSpeechRecognition' in source, 'Web Speech API path found')
check('Microphone recording is separate from ASR', 'MediaRecorder' in source and 'p37StartASR' in source, 'MediaRecorder and SpeechRecognition are separate browser APIs')
check('Server-side transcription endpoint absent', not bool(re.search(r'fetch\([^)]*(?:/transcrib|speech-to-text|audio/transcription)', source, re.I)), 'No bundled STT backend/API call detected')

ok = sum(1 for _, passed, _ in results if passed)
print(f'STAGE 41 STATIC QA: {ok}/{len(results)} PASS')
for name, passed, detail in results:
    print(f"{'PASS' if passed else 'FAIL'} | {name}" + (f' | {detail}' if detail else ''))

# Always write a compact machine-readable result next to this script.
report = {
    'stage': 41,
    'release': '41.0.0-audit-baseline',
    'passed': ok,
    'total': len(results),
    'checks': [{'name': n, 'passed': p, 'detail': d} for n, p, d in results],
    'main_html_sha256': hashlib.sha256(HTML.read_bytes()).hexdigest(),
}
(ROOT / 'STAGE41_QA_RESULTS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.exit(0 if ok == len(results) else 1)
