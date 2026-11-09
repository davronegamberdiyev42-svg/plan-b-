#!/usr/bin/env python3
"""Stage 42 static + pure-logic QA for IELTS Boost transcript reliability.

This does not claim real microphone or live browser speech-service testing.
Run from the project root: python tools/qa_stage42.py
"""
from __future__ import annotations
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'
APP_JS = ROOT / 'assets/js/app.js'
DATA_JSON = ROOT / 'data/app-data.json'
SW = ROOT / 'sw.js'
results: list[tuple[str, bool, str]] = []

def check(name: str, ok: bool, detail: str = '') -> None:
    results.append((name, bool(ok), detail))

html = HTML.read_text(encoding='utf-8')
runtime = APP_JS.read_text(encoding='utf-8') if APP_JS.exists() else ''
sw = SW.read_text(encoding='utf-8')
try:
    app_data = json.loads(DATA_JSON.read_text(encoding='utf-8')) if DATA_JSON.exists() else None
    data_ok = isinstance(app_data, dict) and len(app_data.get('core', {}).get('days', [])) == 84
except Exception:
    app_data, data_ok = None, False
check('External app-data JSON remains valid and contains 84 days', data_ok, 'parsed' if data_ok else 'parse failed')
loader_text = (ROOT / 'assets/js/core/data-loader.js').read_text(encoding='utf-8') if (ROOT / 'assets/js/core/data-loader.js').exists() else ''
check('External module references are present', './assets/css/app.css' in html and './assets/js/app.js' in html and './data/app-data.json' in loader_text)
check('Stage 42 release marker present', "const P42_VERSION='42.0.0'" in runtime)
check('Four transcript targets are explicitly scoped', "const P42_TARGETS=['part1Transcript','part2Transcript','part3Transcript','challengeResponse']" in runtime)
check('Final recognition results are committed', 'result?.isFinal' in runtime and 'meta.lastFinalAt' in runtime)
check('Interim text is displayed but not saved as final', 'session.interimByIndex' in runtime and 'p42UpdateField(target,s,interim)' in runtime)
check('Restart deduplication uses stable session base', 'session.baseText=String(s[target]||\'\').trim()' in runtime and 'session.finalByIndex' in runtime)
check('Recognition restart loop is bounded', 'session.restartCount>=12' in runtime and 'max:12' in runtime)
check('No-speech loop is bounded', 'session.noSpeechCount>=2' in runtime and 'noSpeechLimit:2' in runtime)
check('Manual and keyboard fallback controls exist', 'data-p42-manual' in runtime and 'Samsung Keyboard/Gboard' in runtime)
check('Permission/network/unsupported errors are mapped', all(x in runtime for x in ["'not-allowed'", "'network'", "'audio-capture'", "'language-not-supported'", "'no-speech'"]))
check('Final transcripts autosave through app state', 's[target]=committed' in runtime and 'save();' in runtime)
check('Manual edits stop conflicting live ASR', 'ignoreLateResults=true' in runtime and 'Matn maydoni qo‘lda tahrirlandi' in runtime)
check('Speaking audio recording function is preserved', 'async function startSpeakingClip(slot)' in runtime and 'storeBlob(\'speaking-\'+current,day(),blob,name)' in runtime)
check('Existing general Speaking recording remains intact', 'async function startRecording()' in runtime and "storeBlob('speaking',day(),blob,name)" in runtime)
check('Server STT limitation is disclosed in metadata', "backendStt:'not connected" in runtime and 'backendSTT:false' in runtime)
check('Stage 42 UI status panel is present', 'TRANSCRIPT RELIABILITY' in runtime and 'Browser speech recognition' in runtime)
check('Service worker Stage 47 shell version, adaptive module and Stage 42 audio cache are preserved', "const PREFIX='ielts-boost-stage50'" in sw and 'shell-v12' in sw and "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw and 'scoring-engine.js' in sw and 'lab-quality-engine.js' in sw and 'adaptive-engine.js' in sw)
check('Existing app storage namespace is preserved', "indexedDB.open('IELTSBoostMedia',1)" in runtime and "localStorage" in runtime)

# Validate external ES module runtime with Node.js.
node = subprocess.run(['node', '--version'], text=True, capture_output=True)
if node.returncode == 0 and APP_JS.exists():
    syntax = subprocess.run(['node', '--check', str(APP_JS)], text=True, capture_output=True)
    check('External application ES module syntax', syntax.returncode == 0, 'node --check passed' if syntax.returncode == 0 else syntax.stderr[-1000:])
else:
    check('External application ES module syntax', False, 'Node.js or app.js unavailable')

sw_check = subprocess.run(['node', '--check', str(SW)], text=True, capture_output=True)
check('Service worker JavaScript syntax', sw_check.returncode == 0, 'node --check passed' if sw_check.returncode == 0 else sw_check.stderr[-1000:])

# Test pure helper functions from the actual app source, not reimplemented copies.
def extract_function(name: str) -> str | None:
    # These three pure helpers are adjacent in the source; stop at the next named function.
    start = runtime.find(f'function {name}(')
    if start < 0: return None
    following = re.search(r"\nfunction [A-Za-z0-9_]+\(", runtime[start + 10:])
    if not following: return None
    return runtime[start:start + 10 + following.start()]

helpers = [extract_function(x) for x in ['p42JoinTranscript', 'p42CountWords', 'p42SpeechErrorMessage']]
if all(helpers):
    test_code = '\n'.join(helpers) + r'''
const assert=require('node:assert/strict');
assert.equal(p42JoinTranscript('', 'First sentence.'),'First sentence.');
assert.equal(p42JoinTranscript('First', 'sentence.'),'First sentence.');
assert.equal(p42JoinTranscript('First sentence', ', however, second.'),'First sentence, however, second.');
assert.equal(p42JoinTranscript('  First  ', '  second  '),'First second');
assert.equal(p42CountWords("I've learned 4 useful phrases today."),6);
assert.ok(p42SpeechErrorMessage('not-allowed').includes('Mikrofon'));
assert.ok(p42SpeechErrorMessage('network').includes('internet'));
assert.ok(p42SpeechErrorMessage('unknown').length>20);
process.stdout.write('8 pure helper assertions PASS');
'''
    with tempfile.NamedTemporaryFile('w', suffix='.cjs', encoding='utf-8', delete=False) as f:
        f.write(test_code); test_path = Path(f.name)
    unit = subprocess.run(['node', str(test_path)], text=True, capture_output=True)
    test_path.unlink(missing_ok=True)
    check('Transcript helper unit tests', unit.returncode == 0, unit.stdout.strip() if unit.returncode == 0 else unit.stderr[-1000:])
else:
    check('Transcript helper unit tests', False, 'Could not extract pure helpers from app.js')

# Simulate the actual Stage 42 recognition session with a mocked browser SpeechRecognition API.
start_engine = runtime.find("const P42_VERSION='42.0.0';")
end_engine = runtime.find('// Existing controls are retained.', start_engine)
if start_engine >= 0 and end_engine > start_engine:
    engine = runtime[start_engine:end_engine]
    harness = r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
const engine=__ENGINE_SOURCE__;
const timers=[];
class FakeRecognition{
 static instances=[];
 constructor(){FakeRecognition.instances.push(this);this.lang='';}
 start(){this.started=true;this.onstart&&this.onstart();}
 stop(){this.stopped=true;this.onend&&this.onend();}
 abort(){this.aborted=true;this.onend&&this.onend();}
}
const ctx=vm.createContext({
 state:{speaking:{}},save:()=>{},day:()=>1,toast:()=>{},assert,FakeSpeech:FakeRecognition,timers,
 window:{isSecureContext:true,SpeechRecognition:FakeRecognition},navigator:{onLine:true},
 document:{querySelector:()=>null,querySelectorAll:()=>[],getElementById:()=>null},
 p37SpeakingFullText:s=>['part1Transcript','part2Transcript','part3Transcript','challengeResponse'].map(k=>String(s[k]||'').trim()).filter(Boolean).join('\n\n'),
 p37Recognition:null,p37RecognitionTarget:'part1Transcript',p37RecognitionRunning:false,p37RecognitionRestarts:0,p37RestartTimer:null,
 setTimeout:(fn)=>{timers.push(fn);return timers.length;},clearTimeout:()=>{}
});
vm.runInContext(engine,ctx);
vm.runInContext(`
const part='part1Transcript';
assert.equal(p37StartASR(part),true);
const first=FakeSpeech.instances[0];
const item=t=>Object.assign([{transcript:t,confidence:0.92}],{isFinal:true});
first.onresult({resultIndex:0,results:[item('I enjoy reading')]});
first.onresult({resultIndex:1,results:[item('I enjoy reading'),item('because it relaxes me')]});
assert.equal(state.speaking[1][part],'I enjoy reading because it relaxes me');
// A natural end triggers one bounded restart. The next recognizer must continue from saved final text.
first.onend();
assert.equal(timers.length,1);
timers.shift()();
const second=FakeSpeech.instances[1];
second.onresult({resultIndex:0,results:[item('It also teaches me new ideas')]});
assert.equal(state.speaking[1][part],'I enjoy reading because it relaxes me It also teaches me new ideas');
// Stop must commit the session and release the active recognizer.
p37StopASR();
assert.equal(p42ActiveSession,null);
assert.equal(state.speaking[1][part],'I enjoy reading because it relaxes me It also teaches me new ideas');
// A late event after a manual edit must not overwrite the learner's text.
assert.equal(p37StartASR(part),true);
const third=FakeSpeech.instances[2];
p42ActiveSession.ignoreLateResults=true;
third.onresult({resultIndex:0,results:[item('overwritten text')]});
assert.equal(state.speaking[1][part],'I enjoy reading because it relaxes me It also teaches me new ideas');
p37StopASR();
`,ctx);
process.stdout.write('Recognition lifecycle simulation PASS');
"""
    import json as _json
    harness = harness.replace('__ENGINE_SOURCE__', _json.dumps(engine))
    with tempfile.NamedTemporaryFile('w', suffix='.cjs', encoding='utf-8', delete=False) as f:
        f.write(harness); sim_path = Path(f.name)
    sim = subprocess.run(['node', str(sim_path)], text=True, capture_output=True)
    sim_path.unlink(missing_ok=True)
    check('Mocked recognition lifecycle (final commit, reconnect, stop, manual protection)', sim.returncode == 0,
          sim.stdout.strip() if sim.returncode == 0 else sim.stderr[-1400:])
else:
    check('Mocked recognition lifecycle (final commit, reconnect, stop, manual protection)', False,
          'Could not isolate Stage 42 engine code')

passed = sum(ok for _, ok, _ in results)
report = {
    'stage': 42,
    'release': '42.0.0',
    'date': '2026-11-08',
    'passed': passed,
    'total': len(results),
    'all_passed': passed == len(results),
    'checks': [{'name': name, 'passed': ok, 'detail': detail} for name, ok, detail in results],
    'not_covered': [
        'Real microphone permission and live speech-service availability',
        'Physical Samsung Galaxy A14 Chrome / Samsung Internet acceptance',
        'Server-side transcription of previously saved audio blobs'
    ],
    'note': 'Mocked SpeechRecognition lifecycle tests are not evidence of real device speech-service support.'
}
(ROOT / 'STAGE42_QA_RESULTS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'STAGE 42 STATIC QA: {passed}/{len(results)} PASS')
for name, ok, detail in results:
    print(('PASS' if ok else 'FAIL') + ' | ' + name + (f' | {detail}' if detail else ''))
print('\nLIMITATION: This script does not grant microphone permission and does not verify real device/browser speech recognition. Complete the Samsung A14 acceptance checklist in STAGE42_TRANSCRIPT_ACCEPTANCE_UZ.md.')
sys.exit(0 if passed == len(results) else 1)
