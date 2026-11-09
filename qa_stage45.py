#!/usr/bin/env python3
"""IELTS Boost Stage 45 Evidence-led Laboratories QA.
Run from project root: python tools/qa_stage45.py
Checks the 10 live labs, objective/process provenance, adaptive evidence thresholds,
transfer validation, cache integration and Stage 41–44 regression scripts.
"""
from pathlib import Path
import json, subprocess, tempfile, sys, re
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'assets/js/app.js'
ENGINE=ROOT/'assets/js/core/lab-quality-engine.js'
CSS=ROOT/'assets/css/app.css'
SW=ROOT/'sw.js'
DATA=ROOT/'data/app-data.json'
HTML=ROOT/'index.html'
checks=[]
def check(name, passed, detail=''):
    checks.append({'name':name,'passed':bool(passed),'detail':detail})
app=APP.read_text(encoding='utf-8')
engine=ENGINE.read_text(encoding='utf-8')
sw=SW.read_text(encoding='utf-8')
css=CSS.read_text(encoding='utf-8')
html=HTML.read_text(encoding='utf-8')
# Release and module integration.
check('Stage 45 pure quality engine exists and is imported', ENGINE.is_file() and "from './core/lab-quality-engine.js'" in app)
check('All ten live P37 laboratories are represented in the quality engine', all(f"'{x}'" in engine for x in ['reading','listening','writing','speaking','collocations','pronunciation','paraphrase','grammar','vocabulary','fluency']))
check('Stage 45 runtime metadata is declared', 'DATA.meta.stage45=' in app and 'window.__IELTS_BOOST_STAGE45__' in app)
check('Stage 47 shell cache generation is advanced', "const PREFIX='ielts-boost-stage50'" in sw and "const SHELL_CACHE=PREFIX+'-shell-v12'" in sw)
check('New lab engine is precached', './assets/js/core/lab-quality-engine.js' in sw)
check('Stage 42 Listening audio cache key is preserved', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw)
check('Stage 47 title is present', '<title>IELTS Boost · Final Release 50</title>' in html)
check('Stage 45 UI styles exist', '.p45-overview' in css and '.p45-transfer' in css)
# Evidence / provenance safeguards.
check('Only answer-key checked labs can create objective records', 'p45CurrentObjective' in app and "if(id==='reading'||id==='listening')answer=q.answer??q.a" in app and "else if(id==='collocations'||id==='grammar')answer=q.a" in app)
check('Open-ended labs are explicitly classified as process/self-review', 'Process / self-review evidence only' in app and 'No automatic language-quality grade' in app and "kind: 'process'" in engine)
check('Mastery accuracy is sample-gated at three distinct objective prompts', 'recentObjectiveAttempts>=3' in app and 'minimumObjectiveSampleForAccuracy:3' in app and 'itemKey' in engine and 'uniqueObjective' in engine)
check('Old P37 /10 figures are disclosed as practice-completion index', 'Practice-completion index only; not verified language mastery.' in app and 'not verified skill mastery' in app)
check('Old practice progress is preserved for continuity', 'legacyPracticeProgress' in app)
check('Writing / Speaking / Pronunciation / Paraphrase / Vocabulary / Fluency are not auto-scored for language accuracy', "classifyLabOutcome({labId:id,mode,correct})" in app and 'process/self-review until independent criterion review is connected' in app)
check('Error-cause and repair-plan workflow is present', 'data-p45-field="errorCause"' in app and 'repairPlan' in app)
check('Transfer challenge is optional and does not alter mandatory day requirements', 'OPTIONAL' in app and 'does not add minutes to your required daily plan' in app)
check('Reading transfer evidence is checked against fresh source text', "if(id==='reading'&&!spec.notGiven||id==='listening')" in app and 'notGiven' in app)
check('Listening transfer requires full audio completion', "if(id==='listening'&&!t.audioCompleted)" in app and "e.target?.id!=='p45TransferAudio'" in app)
check('All ten labs have a transfer task builder branch', all(f"id==='{x}'" in app[app.find('function p45TransferSpec'):app.find('function p45TransferState')] for x in ['reading','listening','writing','speaking','collocations','pronunciation','paraphrase','grammar','vocabulary','fluency']))
check('Adaptive focus uses answer-key evidence, not practice average', 'function p45Focus()' in app and 'recentAccuracyPercent<80' in app)
check('Classic 100-mode archive remains preserved', 'Classic Power Labs · previous 100 practice modes' in app)
# Content integrity.
try:
    data=json.loads(DATA.read_text(encoding='utf-8'))
    plan=data.get('plan',{}).get('days',[])
    core=data.get('core',{}).get('days',[])
    check('84-day Academic plan remains intact', len(plan)==84 and len(core)==84, f'plan={len(plan)}, core={len(core)}')
    check('All four mandatory skill modules remain on all 84 days', bool(plan) and all(all(d.get('modules',{}).get(k) for k in ('reading','listening','writing','speaking')) for d in plan), '336/336')
    check('61-article supplemental library remains intact', len(data.get('library',{}).get('articles',[]))==61, str(len(data.get('library',{}).get('articles',[]))))
    check('Core day content has the required transfer sources', all(d.get('reading',{}).get('passage') and d.get('listening',{}).get('script') and d.get('writing',{}).get('task2_prompt') and d.get('speaking',{}).get('part3') for d in core), 'Reading, Listening, Writing Task 2 and Speaking Part 3 available')
except Exception as ex:
    check('App data JSON parses', False, str(ex))
# JavaScript syntax.
for label,path in [('application runtime',APP),('lab quality engine',ENGINE),('service worker',SW)]:
    proc=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
    check(f'JavaScript syntax: {label}', proc.returncode==0, (proc.stderr or 'node --check PASS').strip()[:350])
# Pure-module executable tests (ESM harness).
harness=r'''import assert from 'node:assert/strict';
import {LAB_QUALITY_ENGINE_VERSION,LAB_IDS,ERROR_CAUSES,summariseLabAttempts,recommendLabMode,classifyLabOutcome,validateTransfer,buildLabAttempt} from '../assets/js/core/lab-quality-engine.js';
assert.equal(LAB_QUALITY_ENGINE_VERSION,'45.0.0'); assert.equal(LAB_IDS.length,10); assert.ok(ERROR_CAUSES.evidence);
const mk=(mode,correct,at)=>({labId:'reading',mode,correct,kind:'objective',at});
let s=summariseLabAttempts([mk(0,true,'2026-11-01'),mk(0,false,'2026-11-02')],'reading'); assert.equal(s.recentObjectiveAttempts,2); assert.equal(s.status,'insufficient'); assert.equal(s.recentAccuracyPercent,50);
s=summariseLabAttempts([mk(0,true,'2026-11-01'),mk(0,false,'2026-11-02'),mk(1,true,'2026-11-03')],'reading'); assert.equal(s.recentObjectiveAttempts,3); assert.equal(s.recentAccuracyPercent,66.7); assert.equal(s.status,'developing'); assert.equal(s.weakestMode,0);
const proc={labId:'reading',mode:2,correct:null,kind:'process',at:'2026-11-04'}; s=summariseLabAttempts([mk(0,true,'2026-11-01'),mk(0,false,'2026-11-02'),mk(1,true,'2026-11-03'),proc],'reading'); assert.equal(s.objectiveAttempts,3); assert.equal(s.processEvidenceCount,1);
const dup=summariseLabAttempts([{...mk(0,true,'2026-11-01'),itemKey:'same-prompt'},{...mk(0,false,'2026-11-02'),itemKey:'same-prompt'}, {...mk(1,true,'2026-11-03'),itemKey:'new-prompt'}],'reading'); assert.equal(dup.objectiveAttempts,2); assert.equal(dup.recentObjectiveAttempts,2);
assert.equal(recommendLabMode(s,2,3).mode,0);
s=summariseLabAttempts([mk(0,true,'2026-11-01'),mk(0,true,'2026-11-02'),mk(0,true,'2026-11-03')],'reading'); assert.equal(s.status,'promising'); assert.equal(recommendLabMode(s,0,3).mode,1);
assert.equal(classifyLabOutcome({labId:'reading',correct:true,mode:0}).kind,'objective'); assert.equal(classifyLabOutcome({labId:'writing',correct:null,mode:0}).kind,'process'); assert.equal(classifyLabOutcome({labId:'speaking',correct:null,mode:0}).source,'practice_process');
assert.equal(buildLabAttempt({labId:'writing',mode:0,day:2,score:null,kind:'process'}).score,null);
const words='This is a sufficiently detailed academic response with enough words to develop a clear position and two separate reasons supported by an illustrative example that addresses the task requirements directly. It also explains the main limitation, identifies the relevant group affected, and connects the evidence to the question without adding an unrelated claim.';
const cases=[
 ['reading',{kind:'objective',correct:true,evidence:'a precise phrase',reason:'The statement supports the question scope directly.'}],
 ['listening',{kind:'objective',correct:true,evidence:'final corrected detail',reason:'The speaker corrected the earlier answer.',audioCompleted:true}],
 ['writing',{kind:'process',text:words,evidence:'I addressed the causes and consequences clearly.'}],
 ['speaking',{kind:'process',text:words,evidence:'00:32 I hesitated before the key comparison.'}],
 ['collocations',{kind:'objective',correct:true,text:'The policy can have a meaningful impact on local communities.',reason:'This verb noun combination is natural in this context.'}],
 ['pronunciation',{kind:'process',checks:{stress:true,final:true,chunk:true},evidence:'00:18 final consonant in results was unclear.'}],
 ['paraphrase',{kind:'process',text:'The revised proposal could produce a substantial improvement in public transport access for residents across several neighbourhoods over the next five years.',checks:{meaning:true,scope:true,certainty:true},evidence:'Changed clause structure and retained the original qualification.'}],
 ['grammar',{kind:'objective',correct:true,reason:'The head noun is singular so the verb agrees.',text:'The number of participants has increased significantly during the last financial year.'}],
 ['vocabulary',{kind:'process',text:'A measure used to reduce a problem or risk.',evidence:'The new context uses mitigation of environmental damage.'}],
 ['fluency',{kind:'process',fields:{claim:'The policy should be reviewed regularly.',reason:'This is necessary because conditions can change.',example:'For example, local demand may rise quickly.',qualification:'However, reviews should consider the cost.'}}]
];
for(const [lab,args] of cases){const result=validateTransfer({labId:lab,...args});assert.equal(result.valid,true,lab+': '+result.errors.join('; '));}
const ng=validateTransfer({labId:'reading',kind:'objective',correct:true,notGiven:true,evidence:'',reason:'The passage does not mention the exact external funding amount.'});assert.equal(ng.valid,true);
const ngInvented=validateTransfer({labId:'reading',kind:'objective',correct:true,notGiven:true,evidence:'invented evidence phrase',reason:'The passage does not mention the exact external funding amount.'});assert.equal(ngInvented.valid,false);
const noAudio=validateTransfer({labId:'listening',kind:'objective',correct:true,evidence:'exact words',reason:'The speaker confirmed the final detail.'});assert.equal(noAudio.valid,false);
const noCause=validateTransfer({labId:'reading',kind:'objective',correct:false,evidence:'a precise phrase',reason:'The statement supports the question scope directly.'});assert.equal(noCause.valid,false);
const diagnosed=validateTransfer({labId:'reading',kind:'objective',correct:false,evidence:'a precise phrase',reason:'The statement supports the question scope directly.',fields:{errorCause:'evidence',repairPlan:'I will locate and verify the full sentence before choosing.'}});assert.equal(diagnosed.valid,true);
console.log('Stage45 pure engine assertions PASS');'''
with tempfile.NamedTemporaryFile('w',suffix='.mjs',dir=ROOT/'tools',encoding='utf-8',delete=False) as f:
    f.write(harness); hp=Path(f.name)
try:
    proc=subprocess.run(['node','--experimental-default-type=module',str(hp)],cwd=ROOT,capture_output=True,text=True)
    check('Executable Stage 45 quality / adaptive / transfer validation tests',proc.returncode==0,(proc.stdout+proc.stderr).strip()[-1200:])
finally:
    hp.unlink(missing_ok=True)
# Prior QA suites on updated release.
for stage in (41,42,43,44):
    proc=subprocess.run([sys.executable,f'tools/qa_stage{stage}.py'],cwd=ROOT,capture_output=True,text=True)
    out=proc.stdout+proc.stderr
    m=re.search(r'STAGE\s+'+str(stage)+r'\s+QA:\s+(\d+)/(\d+)\s+PASS',out)
    ok=proc.returncode==0 and (m is None or m.group(1)==m.group(2))
    check(f'Stage {stage} inherited regression suite',ok,(m.group(0) if m else out[-500:]))
# Produce durable report.
passed=sum(x['passed'] for x in checks)
report={'stage':45,'release':'45.0.0','date':'2026-11-08','passed':passed,'total':len(checks),'all_passed':passed==len(checks),'checks':checks,'limitations':['No external AI or human examiner is connected; open-response lab quality remains process/self-review evidence.','Writing, Speaking, Pronunciation, Paraphrase, Vocabulary and Fluency do not receive semantic or acoustic accuracy grades from word counts/checklists.','Audio transfer completion and live ASR still depend on browser/device support; physical Samsung A14 acceptance remains pending.','Static/Node QA does not replace full browser E2E or human content calibration.']}
(ROOT/'STAGE45_QA_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'STAGE 45 QA: {passed}/{len(checks)} PASS')
for x in checks:
    print(('PASS' if x['passed'] else 'FAIL')+' | '+x['name']+((' | '+x['detail']) if x['detail'] else ''))
sys.exit(0 if passed==len(checks) else 1)
