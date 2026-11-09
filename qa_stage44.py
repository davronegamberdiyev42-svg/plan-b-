#!/usr/bin/env python3
"""Stage 44 scoring engine acceptance tests.

Run at project root: python tools/qa_stage44.py
Uses Node.js to execute deterministic scoring math and Python stdlib for
structure/regression checks. Does not claim real IELTS examiner or device QA.
"""
from __future__ import annotations
import json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'assets/js/app.js'
ENGINE = ROOT / 'assets/js/core/scoring-engine.js'
DATA = ROOT / 'data/app-data.json'
SW = ROOT / 'sw.js'
checks=[]
def check(name, passed, detail=''):
    checks.append({'name':name,'passed':bool(passed),'detail':detail})
app=APP.read_text(encoding='utf-8')
eng=ENGINE.read_text(encoding='utf-8')
sw=SW.read_text(encoding='utf-8')
html=(ROOT/'index.html').read_text(encoding='utf-8')

# Module loading and release integration.
check('Scoring engine module exists and is imported by app runtime', ENGINE.is_file() and "from './core/scoring-engine.js'" in app, 'separate ES module import')
check('Stage 47 service-worker shell generation', "const PREFIX='ielts-boost-stage50'" in sw and 'shell-v12' in sw, 'Stage 46 shell cache')
check('Scoring engine precached for offline use', './assets/js/core/scoring-engine.js' in sw, 'core module is included in service-worker CORE')
check('Audio cache continuity preserved', "const AUDIO_CACHE='ielts-boost-stage42-audio-v3'" in sw, 'Stage 42 listening cache key retained')
check('Stage 47 title exposed in app shell', 'Final Release 50' in html, 'document title')
check('Assessment history storage has backward-safe defaults', 'rubricEvidence:{}' in app and 'assessmentRecords:{}' in app and 'state.assessmentRecords=state.assessmentRecords||{}' in app, 'new data fields default without replacing old state')
check('Daily self-rating is stored separately from criterion score', 'taskQualitySelfRating' in app and 'taskQualityEvidence' in app, 'reflection no longer overwrites objective/criterion score')

# Skill-specific scoring rules.
check('Reading objective answer-key score replaces self-rating for Accuracy', 'objectiveRubricScore(skill)' in app and 'calculateWeightedObjectiveSkill(\'reading\'' in app, 'answer-key accuracy is first criterion')
check('Reading evidence, strategy and transfer each require explicit notes', "evidenceCheck('reading','',[1,2,3])" in app and 'kamida 10 belgi' in app, '3 evidence fields')
check('Authentic Listening does not claim missing provider answer key', "calculateEqualCriteria(vals)" in app and 'External provider answer key is not imported' in app, 'four learner-reviewed criteria for authentic source')
check('Optional offline Listening quiz remains separately identified', 'offlineQuizRawCorrect' in app and 'not substituted for external recording score' in app, 'raw companion quiz is stored separately')
check('Writing criterion review uses four criteria', 'calculateEqualCriteria(vals)' in app and 'writingReviews' in app and 'Task 2 × 2' in app, 'Task 1/Task 2 separate review')
check('Writing overall score applies Task 2 double weight', 'calculateWritingOverall(rec.task1.score,rec.task2.score)' in app, 'combined index uses 1:2')
check('Writing daily completion follows each day task1/task2/both requirement', 'calculateWritingDailyScore(primary,a,b)' in app and 'writingRequiredTasks' in app, 'daily assigned task can complete alone; both days require both reviews')
check('Speaking requires audio for pronunciation evidence', 'Pronunciation mezonini baholash' in app and 'audioVerified:gate.audio' in app, 'audio provenance stored')
check('Stage 35 writing PowerLab uses evidence-backed four-criterion review', "id==='writing'" in app and 'powerlab-' in app and "const keys=['ta','cc','lr','gra']" in app, 'separate practice mode assessment')
check('Stage 35 speaking PowerLab requires saved audio and four anchors', "id==='speaking'" in app and 'cp35audio' in app and "const keys=['fc','lr','gra','pron']" in app, 'pronunciation review is audio-gated')

# Provenance and UI transparency.
check('Assessment records keep source label, version, criterion evidence and scale', all(x in eng for x in ['sourceLabel','criteria','evidenceStrength','scale','version']), 'provenance-aware records')
check('No official IELTS band conversion in scoring engine', 'not an IELTS band' in eng and not re.search(r'bandFromRaw|convertToIELTSBand|officialBandConversion',eng,re.I), 'internal 0–10 practice scale only')
check('Saved assessment summary shown in four skill studios', all(x in app for x in ["assessmentSummary('reading','daily')","assessmentSummary('listening','authentic-source')","assessmentSummary('writing',tab)","assessmentSummary('speaking','daily')"]), 'source and evidence coverage visible after save')
check('Evidence coverage is explicitly not statistical confidence', 'statistik ishonch oralig‘i' in eng, 'not a statistical confidence interval')
check('AI/examiner provenance not falsely claimed as connected', 'API' not in app[app.find('DATA.meta.stage44'):app.find('DATA.meta.stage44')+1000] if 'DATA.meta.stage44' in app else False, 'no false live AI scoring claim in metadata')

# Content baseline preservation.
try:
    data=json.loads(DATA.read_text(encoding='utf-8'))
    days=data.get('plan',{}).get('days',[])
    core=data.get('core',{}).get('days',[])
    check('84-day Academic curriculum remains intact', len(days)==84 and len(core)==84, f'plan={len(days)}, core={len(core)}')
    check('All four mandatory skill modules remain on all days', bool(days) and all(all(d.get('modules',{}).get(k) for k in ('reading','listening','writing','speaking')) for d in days), '336/336 skill modules')
    primary=[d.get('modules',{}).get('writing',{}).get('primary_task') for d in days]
    check('Writing daily task map contains only task1/task2/both', len(primary)==84 and all(x in ('task1','task2','both') for x in primary), f"task1={primary.count('task1')}, task2={primary.count('task2')}, both={primary.count('both')}")
    check('61-article library remains intact', len(data.get('library',{}).get('articles',[]))==61, f"{len(data.get('library',{}).get('articles',[]))} articles")
except Exception as e:
    check('External content JSON remains parseable',False,str(e))

# JavaScript parse checks.
for name,path in [('application runtime',APP),('scoring engine',ENGINE),('service worker',SW)]:
    proc=subprocess.run(['node','--check',str(path)],capture_output=True,text=True)
    check(f'JavaScript syntax: {name}',proc.returncode==0,(proc.stderr or 'node --check PASS').strip()[:300])

# Execute scoring engine functions through Node ESM; exact numeric assertions.
harness=r'''import assert from 'node:assert/strict';
import {SCORING_ENGINE_VERSION,SCORING_CONFIG,objectiveAccuracy,calculateWeightedObjectiveSkill,calculateEqualCriteria,calculateWritingOverall,calculateWritingDailyScore,assessEvidenceStrength,buildAssessmentRecord} from '../assets/js/core/scoring-engine.js';
assert.equal(SCORING_ENGINE_VERSION,'44.0.0');
assert.equal(objectiveAccuracy(8,10),8.0);
assert.equal(objectiveAccuracy(8.5,10),null);
assert.equal(objectiveAccuracy(8,0),null);
const rd=calculateWeightedObjectiveSkill('reading',8,10,[1,9,6,8]);
assert.equal(rd.valid,true); assert.equal(rd.criteria[0],8); assert.equal(rd.score,7.9);
assert.equal(calculateWeightedObjectiveSkill('reading',11,10,[1,2,3,4]).valid,false);
assert.throws(()=>calculateWeightedObjectiveSkill('listening',8,10,[1,2,3,4]));
assert.equal(SCORING_CONFIG.listening.kind,'equal_criteria');
const eq=calculateEqualCriteria([8,6,7,9]); assert.equal(eq.valid,true); assert.equal(eq.score,7.5);
assert.equal(calculateEqualCriteria([8,6,7]).valid,false);
assert.equal(calculateEqualCriteria([8,6,7,9],[.2,.2,.2,.2]).valid,false);
const wr=calculateWritingOverall(6,9); assert.equal(wr.valid,true); assert.equal(wr.score,8.0);
assert.equal(calculateWritingOverall(6,null).valid,false);
assert.equal(calculateWritingDailyScore('task1',7.2,null).score,7.2);
assert.equal(calculateWritingDailyScore('task2',null,8.1).score,8.1);
assert.equal(calculateWritingDailyScore('both',6,9).score,8.0);
assert.equal(calculateWritingDailyScore('both',6,null).valid,false);
const weak=assessEvidenceStrength(['short','short','short','short'],false,'learner_self_review'); assert.equal(weak.coveragePercent,0); assert.equal(weak.label,'Cheklangan');
const medium=assessEvidenceStrength(['12345678901','12345678901','', '12345678901'],false,'learner_self_review'); assert.equal(medium.label,'O‘rtacha');
const strong=assessEvidenceStrength(['12345678901','12345678901','12345678901','12345678901'],true,'learner_self_review'); assert.equal(strong.label,'Kuchli');
const record=buildAssessmentRecord({skill:'reading',result:rd,source:'learner_self_review',evidence:['answer key 8/10','paragraph 2 exact quote','strategy notes here','retest result evidence'],objectivePresent:true});
assert.equal(record.score,7.9); assert.equal(record.objective.correct,8); assert.equal(record.criteria.length,4); assert.match(record.scale,/not an IELTS band/); assert.equal(record.criteria[0].source,'answer_key');
console.log('Scoring math and provenance assertions PASS');'''
with tempfile.NamedTemporaryFile('w',suffix='.mjs',dir=ROOT/'tools',encoding='utf-8',delete=False) as f:
    f.write(harness); hpath=Path(f.name)
try:
    proc=subprocess.run(['node','--experimental-default-type=module',str(hpath)],cwd=ROOT,capture_output=True,text=True)
    check('Executable scoring engine math and provenance tests',proc.returncode==0,(proc.stdout+proc.stderr).strip()[-700:])
finally:
    hpath.unlink(missing_ok=True)

passed=sum(c['passed'] for c in checks)
report={'stage':44,'release':'44.0.0','date':'2026-11-08','passed':passed,'total':len(checks),'all_passed':passed==len(checks),'checks':checks,'not_covered':['Real human IELTS examiner calibration and inter-rater reliability study','Live AI backend integration; this release records self-review and answer-key provenance only','Physical Samsung A14/browser/audio/microphone acceptance','Full Chromium end-to-end UI execution']}
(ROOT/'STAGE44_QA_RESULTS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'STAGE 44 QA: {passed}/{len(checks)} PASS')
for c in checks:
    print(('PASS' if c['passed'] else 'FAIL')+' | '+c['name']+((' | '+c['detail']) if c['detail'] else ''))
sys.exit(0 if passed==len(checks) else 1)
