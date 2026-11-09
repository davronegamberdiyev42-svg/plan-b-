#!/usr/bin/env python3
"""Stage 49 vocabulary data, integration, legacy regression and HTTP checks."""
from pathlib import Path
import json, csv, re, subprocess, sys, threading, os
from collections import Counter
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail=''):
    checks.append({'name':name,'passed':bool(ok),'detail':detail})

data=json.loads((ROOT/'data/app-data.json').read_text(encoding='utf-8'))
words=data['words']; daily=data['vocabularyExpert']['daily_sets']
idx={int(w['id']):w for w in words}
core_ids=[int(i) for p in daily for i in p.get('word_ids',[])]
core=set(core_ids)
complete=lambda w: all(str(w.get(k,'')).strip() for k in ('meaning_en','uzbek','example','part_of_speech'))
norm=lambda s: re.sub(r'\s+',' ',re.sub(r"[^a-z0-9' -]",' ',str(s).lower())).strip()
keys=[norm(w['word']) for w in words]
core_words=[idx[i] for i in core if i in idx]

check('19,000 indexed word/phrase records',len(words)==19000)
check('All word record IDs are unique',len(idx)==19000)
check('All normalised headwords are unique',len(keys)==len(set(keys)))
check('84 daily vocabulary packs exist',len(daily)==84)
check('Every daily pack contains exactly 8 items',all(len(x.get('word_ids',[]))==8 for x in daily))
check('84-day core has 672 distinct items',len(core)==672 and len(core_ids)==672)
check('All 672 daily-core items have complete bilingual gloss + example + POS',len(core_words)==672 and all(complete(w) for w in core_words))
check('All 672 daily-core items have US and UK IPA fields',all(w.get('ipa_us') and w.get('ipa_uk') for w in core_words))
check('Total complete offline bilingual glossary coverage is 677',sum(complete(w) for w in words)==677)
check('4,000 pronunciation-only entries are explicitly classified',sum(w.get('translation_mode')=='pronunciation_index_only' for w in words)==4000)
check('No pronunciation-only entry is misreported as full gloss',all(not complete(w) for w in words if w.get('translation_mode')=='pronunciation_index_only'))
check('15,678 US IPA fields are present',sum(bool(w.get('ipa_us')) for w in words)==15678)
check('11,678 UK IPA fields are present',sum(bool(w.get('ipa_uk')) for w in words)==11678)
check('11,678 records have both IPA fields',sum(bool(w.get('ipa_us') and w.get('ipa_uk')) for w in words)==11678)
check('4,541 part-of-speech fields are present',sum(bool(w.get('part_of_speech')) for w in words)==4541)
check('15,000 CEFR labels are estimates and 4,000 are not assessed',sum(w.get('cefr_confidence')=='estimated' for w in words)==15000 and sum(w.get('cefr_confidence')=='not_assessed' for w in words)==4000)
check('Missing-field count is openly measurable',sum(not complete(w) for w in words)==18323)
check('The daily-core discrepancy IPA has its Cambridge source recorded',idx[13277].get('ipa_source_url')=='https://dictionary.cambridge.org/pronunciation/english/discrepancy' and idx[13277].get('ipa_us') and idx[13277].get('ipa_uk'))
check('Vocabulary audit metadata matches actual bundled coverage',data['vocabularyExpert']['stage48']['index']['total']==19000 and data['vocabularyExpert']['stage48']['index']['complete_offline_glosses']==677 and data['vocabularyExpert']['stage48']['daily_core']['items']==672)
check('61-article supplementary library remains intact',len(data.get('library',{}).get('articles',[]))==61)
check('864 sentence patterns remain intact',len(data.get('patterns',[]))==864)

app=(ROOT/'assets/js/app.js').read_text(encoding='utf-8')
html=(ROOT/'index.html').read_text(encoding='utf-8')
sw=(ROOT/'sw.js').read_text(encoding='utf-8')
css=(ROOT/'assets/css/stage48.css').read_text(encoding='utf-8')
css49=(ROOT/'assets/css/stage49.css').read_text(encoding='utf-8')
engine=(ROOT/'assets/js/core/vocabulary-engine.js').read_text(encoding='utf-8')
backup_engine=(ROOT/'assets/js/core/backup-engine.js').read_text(encoding='utf-8')
check('Stage 49 CSS remains wired in final shell', 'assets/css/stage49.css' in html and (ROOT/'assets/css/stage49.css').exists())
check('Vocabulary pure engine is imported', "from './core/vocabulary-engine.js'" in app and "export function auditVocabulary" in engine)
check('Stage 49 search cache is constructed once', 'const WORD_SEARCH_CACHE=WORDS.map' in app)
check('Search merges legacy Stage 36, Stage 37 and current cache', all(x in app for x in ['p36Ensure().vocabularyCache','p37Ensure().vocabulary.cache','state.vocabCache']))
check('Search persists query and resets pagination', "if(t.id==='vocabSearch'){state.vocabSearch=t.value;state.vocabOffset=0" in app)
check('Daily pack maps IDs through stable Map rather than repeated linear scan', 'WORD_BY_ID.get(Number(id))' in app)
check('Transfer uses exact lexical token/phrase matching, not substring', 'containsLexicalItem(sentence,w.word)' in app and 'q.includes(vxNormal(w.word))' not in app)
check('Daily vocabulary completion requires ≥6/8 recall + 2 target terms + 12 words', 'validateDailyVocabularyCompletion(st.quizResult?.score||0,hits.length,wc)' in app and 'Number(recallScore) >= 6 && Number(transferHits) >= 2 && Number(wordCount) >= 12' in engine)
check('Changing answers or transfer text invalidates stale completion result', 'st.quizResult=null;st.complete=false' in app and 'st.sentenceResult=null;st.complete=false' in app)
check('Review scheduler is SM-2-inspired and retains bounded history', 'scheduleVocabularyReview' in app and 'reviewHistoryLimit:20' in app and 'item.history.slice(-19)' in engine)
check('Again returns the word to same-day review', "if (rating === 'again')" in engine and 'intervalDays = 0' in engine)
check('SRS ratings require the meaning to be revealed first', 'details[data-p48-srs-detail]' in app and 'button.disabled=!details.open' in app)
check('Online cache drafts are blocked from SRS until user-verified', 'hasDraft&&!note.verifiedByUser' in app)
check('SRS uses local calendar date keys', 'function p48TodayKey' in app and 'due:p48TodayKey()' in app)
check('Legacy Stage 37 SRS entries and favourites are surfaced and safely migrated', 'function p48SrsRecord(word)' in app and 'function p48SrsWords()' in app and 'p48SrsRecord(word)' in app)
check('CEFR estimates and IPA field provenance are clearly qualified', 'CEFR darajalari rasmiy sertifikat emas' in app and 'IPA field presence does not mean' in app)
check('Stage 49 vocabulary coverage panel discloses real counts', all(s in app for s in ['19,000','677','672','4,000','a.usIpaFields','a.ukIpaFields']))
check('Stage 48 CSS contains mobile responsive styles', '@media' in css and '.p48-hero' in css and '.p48-srs-row' in css)
check('Stage 49 responsive/a11y CSS provides mobile, touch, focus and reduced motion', all(x in css49 for x in ['@media (max-width: 760px)','44px','focus-visible','prefers-reduced-motion','safe-area-inset-bottom']))
check('Stage 49 modules remain precached in current Stage 50 shell', "const PREFIX='ielts-boost-stage50'" in sw and "const SHELL_CACHE=PREFIX+'-shell-v12'" in sw and all(x in sw for x in ['stage49.css','stage50.css','backup-engine.js','vocabulary-engine.js']))
check('Stage 42 offline audio cache continuity is preserved', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw)
check('All 84 listening MP3 files remain present',len(list((ROOT/'audio').glob('listening-day-*.mp3')))==84 and all(p.stat().st_size>10000 for p in (ROOT/'audio').glob('listening-day-*.mp3')))
check('4-skill 84-day programme and Stage 47 resource map are intact',len(data['plan']['days'])==84 and len(data['resources']['days'])==84 and all(all(k in x['resources'] for k in ['reading','listening','writing','speaking']) for x in data['resources']['days']))

# Stage 49 security, backup, deployment and accessibility checks
manifest=json.loads((ROOT/'manifest.webmanifest').read_text(encoding='utf-8'))
html_text=html
check('PWA manifest uses deployment-relative id/scope/start URL',manifest.get('id')=='./' and manifest.get('scope')=='./' and manifest.get('start_url')=='./')
check('Manifest icons are relative and all resolve inside project',all(str(x.get('src','')).startswith('./') and (ROOT/x['src'][2:]).exists() for x in manifest.get('icons',[])))
check('HTML has CSP restricting scripts to same-origin',"script-src 'self'" in html_text and "object-src 'none'" in html_text)
check('HTML includes strict-origin referrer policy', 'strict-origin-when-cross-origin' in html_text)
check('Accessible skip link and focusable main landmark exist', 'class="skip-link"' in html_text and '<main id="app" tabindex="-1">' in html_text)
check('Backup engine rejects unsafe keys and validates state schema', all(x in backup_engine for x in ['__proto__','completed','scores','drafts','BACKUP_MAX_BYTES','mergeBackupState']))
check('Backup engine adds SHA-256 and supports legacy backup import', 'SHA-256' in backup_engine and 'legacy-unchecksummed' in backup_engine)
check('Import takes a pre-import snapshot and caps file size', 'pre-import-safety' in app and 'BACKUP_MAX_BYTES' in app and 'mergeBackupState(defaultState(),checked.state)' in app)
check('Audio exclusion from JSON backup is disclosed', 'audioIncluded: false' in backup_engine and 'Audio blobs stay in IndexedDB' in app)
check('Persistent storage request is user initiated', 'navigator.storage.persist()' in app and 'data-action="protect-storage"' in app)
check('Offline status banner and online/offline listeners exist', 'p49NetworkBanner' in html_text and "addEventListener('offline',p49RefreshNetworkStatus)" in app)
check('Device diagnostics include quota, mic, ASR, SW and viewport', all(x in app for x in ['Storage estimate','Microphone API','Live speech recognition','Service Worker active','Viewport','Page performance','JavaScript heap estimate']))
check('Stage 49 metadata records honest local-first limitations', 'encryptionAtRest:false' in app and 'audioIncluded:false' in app)
check('Old audio cache name is preserved across release', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw)
check('Stage 49 CSS is included in current shell precache', 'stage49.css' in sw and 'stage50.css' in sw)

# Syntax checks
for rel in ['assets/js/app.js','assets/js/core/backup-engine.js','assets/js/core/vocabulary-engine.js','assets/js/core/task1-intelligence.js','assets/js/core/adaptive-engine.js','sw.js']:
    cp=subprocess.run(['node','--experimental-default-type=module','--check',str(ROOT/rel)],capture_output=True,text=True)
    check(f'JavaScript syntax: {rel}',cp.returncode==0,cp.stderr[-600:] if cp.returncode else 'PASS')

# Pure engine behaviour tests
cp=subprocess.run(['node','--experimental-default-type=module','tools/qa_stage48.mjs'],cwd=ROOT,capture_output=True,text=True)
check('Vocabulary engine unit suite',cp.returncode==0,cp.stdout.strip() if cp.returncode else cp.stderr[-1000:])
cp_backup=subprocess.run(['node','--experimental-default-type=module','tools/qa_stage49.mjs'],cwd=ROOT,capture_output=True,text=True)
check('Backup integrity and import validation suite',cp_backup.returncode==0,cp_backup.stdout.strip() if cp_backup.returncode==0 else cp_backup.stderr[-1200:])

# Inherited regression suites (QA expectations updated to new shell version).
regressions=[('Stage 41', ['python','tools/qa_stage41.py']),('Stage 42', ['python','tools/qa_stage42.py']),('Stage 43', ['python','tools/qa_stage43.py']),('Stage 44', ['python','tools/qa_stage44.py']),('Stage 45', ['python','tools/qa_stage45.py']),('Stage 46', ['node','tools/qa_stage46.mjs']),('Stage 47 Task 1', ['node','tools/qa_stage47.mjs']),('Stage 47 integration', ['python','tools/qa_stage47.py'])]
reg_results=[]
for label,cmd in regressions:
    cp=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=180)
    out=(cp.stdout or '')+(cp.stderr or '')
    match=re.search(r'(?:QA|TESTS?):\s*(\d+)/(\d+)\s*PASS',out)
    result={'label':label,'returncode':cp.returncode,'summary':match.group(0) if match else ('PASS' if cp.returncode==0 else 'FAIL'),'tail':out[-1800:]}
    reg_results.append(result)
    check(f'Inherited regression: {label}',cp.returncode==0,result['summary'])

# Local HTTP smoke: HEAD only so the 15 MB JSON is not transferred.
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
old=os.getcwd();os.chdir(ROOT)
server=ThreadingHTTPServer(('127.0.0.1',0),Quiet);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_address[1]}'
paths=['/','/index.html','/manifest.webmanifest','/assets/css/stage47.css','/assets/css/stage48.css','/assets/css/stage49.css','/assets/js/app.js','/assets/js/core/backup-engine.js','/assets/js/core/vocabulary-engine.js','/data/app-data.json','/sw.js','/audio/listening-day-01.mp3','/audio/listening-day-84.mp3']
http=[]
try:
    for path in paths:
        try:
            with urlopen(Request(base+path,method='HEAD'),timeout=20) as resp: http.append((path,resp.status))
        except Exception as ex: http.append((path,0,str(ex)))
finally:
    server.shutdown();server.server_close();os.chdir(old)
check('HTTP smoke: all 13 app/data/audio resources return 200',len(http)==13 and all(x[1]==200 for x in http),'; '.join(f'{x[0]}={x[1]}' for x in http))

passed=sum(x['passed'] for x in checks);total=len(checks)
print(f'STAGE 49 QA: {passed}/{total} PASS')
for x in checks: print(('PASS' if x['passed'] else 'FAIL')+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
report={'stage':49,'passed':passed,'total':total,'failed':total-passed,'checks':checks,'regressions':reg_results,'http':http,'limitations':['Static, data, module and HTTP checks do not replace full browser end-to-end tests.','Samsung A14 physical microphone, PWA installation and offline acceptance still require testing on the user device.','IPA field presence is not proof of expert/audio verification; CEFR values are estimates unless independently sense-verified.','Online lookup results remain drafts until the exact sense, source and Uzbek gloss are manually reviewed.']}
(ROOT/'STAGE49_QA_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
sys.exit(0 if passed==total else 1)
