import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { ADAPTIVE_ENGINE_VERSION, buildAdaptiveProfile, buildAdaptivePlan } from '../assets/js/core/adaptive-engine.js';

const empty = buildAdaptiveProfile({ currentDay: 1, completedCount: 0 });
assert.equal(ADAPTIVE_ENGINE_VERSION, '46.0.0');
assert.equal(empty.skills.length, 4);
assert.equal(empty.evidenceCoverage.measuredSkills, 0);
assert.equal(empty.skills[0].confidenceLevel, 'insufficient');
assert.equal(empty.skills[0].canClaimMastery, false);

const tinyReading = buildAdaptiveProfile({ skills: { reading: { rawSampleCount: 2, rawAccuracyPercent: 0 } } });
assert.notEqual(tinyReading.skills.find(x => x.skill === 'reading').primaryKind, 'objective_accuracy', '2 samples must not claim reliable objective weakness');
assert.equal(tinyReading.skills.find(x => x.skill === 'reading').confidenceLevel, 'insufficient');

const weakReading = buildAdaptiveProfile({ skills: { reading: { rawSampleCount: 4, rawAccuracyPercent: 50 } } });
const rd = weakReading.skills.find(x => x.skill === 'reading');
assert.equal(rd.actionType, 'objective_repair');
assert.equal(rd.primarySamples, 4);
assert.equal(rd.primaryMean, 5);
assert.match(rd.why, /5\/10/);
assert.equal(rd.confidenceLevel, 'moderate');

const strongReading = buildAdaptiveProfile({ skills: { reading: { rawSampleCount: 5, rawAccuracyPercent: 92 } } });
assert.equal(strongReading.skills.find(x => x.skill === 'reading').actionType, 'stretch');
assert.equal(strongReading.skills.find(x => x.skill === 'reading').confidenceLevel, 'high');

const weakWriting = buildAdaptiveProfile({ skills: { writing: { criteria: [
  { name: 'Task Achievement', mean: 4, n: 2 }, { name: 'Coherence', mean: 6, n: 2 },
  { name: 'Lexical', mean: 6, n: 2 }, { name: 'Grammar', mean: 6, n: 2 }
] } } });
const wr = weakWriting.skills.find(x => x.skill === 'writing');
assert.equal(wr.actionType, 'criterion_repair');
assert.equal(wr.weakestCriterion.name, 'Task Achievement');
assert.ok(wr.why.includes('mustaqil examiner bahosi'));
assert.equal(wr.canClaimMastery, false);

const selfOnly = buildAdaptiveProfile({ skills: { speaking: { qualitySampleCount: 5, qualityAverage: 3, rows: [{}, {}, {}, {}, {}] } } });
const sp = selfOnly.skills.find(x => x.skill === 'speaking');
assert.equal(sp.primaryKind, 'none');
assert.notEqual(sp.actionType, 'criterion_repair');
assert.ok(sp.unknowns.some(x => x.includes('self-review')));

const repeatedErrors = buildAdaptiveProfile({ errors: [{ skill: 'Listening', type: 'Spelling', count: 3 }] });
const li = repeatedErrors.skills.find(x => x.skill === 'listening');
assert.equal(li.actionType, 'error_repair');
assert.equal(li.openErrorCount, 3);
assert.equal(li.confidenceLevel, 'limited');

const declining = buildAdaptiveProfile({ skills: { writing: { qualitySampleCount: 5, qualityAverage: 7, trendSampleCount: 5, trendDelta: -1.2, rows: [{},{},{},{},{}] } } });
assert.equal(declining.skills.find(x => x.skill === 'writing').actionType, 'trend_recovery');

const listeningNoKey = buildAdaptiveProfile({ skills: { listening: { rawSampleCount: 1, rawAccuracyPercent: 10, raw: [{}] } } });
assert.ok(listeningNoKey.skills.find(x => x.skill === 'listening').unknowns.some(x => x.includes('javob kaliti')));

const labEvidence = buildAdaptiveProfile({ labs: { reading: { objectiveAttempts: 4, recentObjectiveAttempts: 4, recentAccuracyPercent: 55, weakestMode: 3 } } });
assert.equal(labEvidence.skills.find(x => x.skill === 'reading').actionType, 'objective_repair');

const mixed = buildAdaptiveProfile({
 skills: {
  reading: { rawSampleCount: 5, rawAccuracyPercent: 88 },
  writing: { criteria: [0,1,2,3].map(i => ({ name: `C${i}`, mean: 7, n: 4 })) },
  speaking: { criteria: [0,1,2,3].map(i => ({ name: `C${i}`, mean: 7.5, n: 4 })) },
  listening: { rawSampleCount: 4, rawAccuracyPercent: 72 }
 }, currentDay: 22, completedCount: 44
});
assert.equal(mixed.evidenceCoverage.measuredSkills, 4);
assert.equal(mixed.completedSkillSessions, 44);
assert.ok(mixed.skills.every(x => x.canClaimMastery === false));

const gentle = buildAdaptivePlan(weakReading, { mode: 'gentle', pendingSession: { day: 3, skill: 'reading' }, currentDay: 10 });
assert.equal(gentle.steps.length, 1);
assert.equal(gentle.timeLimit, null);
assert.equal(gentle.preservesMandatoryPlan, true);
const full = buildAdaptivePlan(weakReading, { mode: 'full', pendingSession: { day: 3, skill: 'reading' }, openError: { skill: 'reading', type: 'TFNG' }, currentDay: 10 });
assert.ok(full.steps.length <= 3);
assert.equal(full.timeLimit, null);
assert.equal(full.source, 'local_evidence_based_rules');

const appSource = readFileSync(new URL('../assets/js/app.js', import.meta.url), 'utf8');
const swSource = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
assert.match(appSource, /from '\.\/core\/adaptive-engine\.js'/);
assert.match(appSource, /\['adviser','Intelligence'\]/);
assert.match(appSource, /function s46AdvisorMarkup\(/);
assert.match(appSource, /buildAdaptivePlan\(profile/);
assert.match(appSource, /timeLimit:null/);
assert.match(appSource, /DATA\.meta\.stage46=/);
assert.match(appSource, /Yuqori ichki baho · mustaqil tasdiq yo‘q/);
assert.match(appSource, /Mezon xaritasi/);
assert.match(swSource, /assets\/js\/core\/adaptive-engine\.js/);
assert.match(swSource, /ielts-boost-stage42-audio-v3/);
assert.match(swSource, /shell-v12/);

console.log(JSON.stringify({ version: ADAPTIVE_ENGINE_VERSION, tests: 47, passed: 47, failed: 0, cases: [
 'empty baseline', 'minimum sample gate', 'objective repair', 'strong objective stretch', 'criterion repair',
 'self-review non-mastery', 'repeated error', 'trend recovery', 'listening key unavailable', 'lab objective evidence',
 'four-skill evidence coverage', 'gentle/full adaptive plan', 'no time limit', 'mandatory curriculum preserved', 'application import wiring', 'Intelligence tab wiring', 'advisor markup', 'adaptive plan wiring', 'time limit disabled', 'release metadata', 'no false independent mastery UI label', 'criterion-map UI label', 'service worker module precache', 'legacy audio cache preserved', 'shell cache version'
]}, null, 2));
