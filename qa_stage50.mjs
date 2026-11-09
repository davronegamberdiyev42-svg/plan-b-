import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { objectiveAccuracy, calculateWeightedObjectiveSkill, calculateEqualCriteria, calculateWritingOverall, calculateWritingDailyScore, buildAssessmentRecord } from '../assets/js/core/scoring-engine.js';
import { containsLexicalItem, scheduleVocabularyReview, validateDailyVocabularyCompletion } from '../assets/js/core/vocabulary-engine.js';
import { mergeBackupState, inspectBackupEnvelope } from '../assets/js/core/backup-engine.js';
import { inspectPwaManifest } from '../assets/js/core/pwa-validation.js';
import { buildAdaptiveProfile, buildAdaptivePlan } from '../assets/js/core/adaptive-engine.js';
import { LAB_IDS, validateTransfer } from '../assets/js/core/lab-quality-engine.js';

let passed = 0;
const test = (name, value) => { const ok = typeof value === 'function' ? value() : value; assert.ok(ok, name); passed++; console.log(`PASS | ${name}`); };
const app = readFileSync(new URL('../assets/js/app.js', import.meta.url), 'utf8');
const sw = readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const manifest = JSON.parse(readFileSync(new URL('../manifest.webmanifest', import.meta.url), 'utf8'));

// Final release identity and shell wiring.
test('Final release title and version exposed', html.includes('IELTS Boost · Final Release 50') && app.includes("DATA.meta.release='50.0.0'") && app.includes("window.__IELTS_BOOST_STAGE50__={version:'50.0.0'"));
test('Final acceptance summary is visible in Settings', app.includes('stage50-release-panel') && app.includes('Samsung A14 acceptance still needs to be completed'));
test('Stage 50 stylesheet is linked and precached', html.includes('./assets/css/stage50.css') && sw.includes('./assets/css/stage50.css'));
test('PWA relative manifest resolves correctly on GitHub Pages repository subpath', inspectPwaManifest(manifest,'https://example.github.io/ielts/manifest.webmanifest','https://example.github.io/ielts/').valid);
test('PWA diagnostic accepts nested in-scope page paths', inspectPwaManifest(manifest,'https://example.github.io/ielts/manifest.webmanifest','https://example.github.io/ielts/?day=12').currentWithinScope);
test('PWA diagnostic rejects a start URL outside scope', inspectPwaManifest({...manifest,start_url:'/other/'},'https://example.github.io/ielts/manifest.webmanifest','https://example.github.io/ielts/').valid === false);
test('Service worker uses new final shell cache', sw.includes("const PREFIX='ielts-boost-stage50'") && sw.includes("const SHELL_CACHE=PREFIX+'-shell-v12'"));
test('Stage 42 audio cache remains preserved', sw.includes("const AUDIO_CACHE='ielts-boost-stage42-audio-v3'"));
test('Deployment-relative PWA validator is imported and precached', app.includes('inspectPwaManifest') && sw.includes('pwa-validation.js'));
test('PWA manifest is relative to project scope', manifest.id === './' && manifest.scope === './' && manifest.start_url === './' && manifest.version === '50.0.0');
test('App remains local-first without false cloud/AI claims', app.includes('cloudSync:false') && app.includes('liveAIAssessment:false') && app.includes('encryptionAtRest:false'));
test('Backup clearly discloses IndexedDB audio separation', app.includes('audioIncluded:false') && app.includes('Audio blobs stay in IndexedDB'));

// Scoring invariants.
test('Objective accuracy returns internal 0–10 metric', objectiveAccuracy(8, 10) === 8 && objectiveAccuracy(1, 0) === null);
test('Reading accuracy is weighted 50 percent', calculateWeightedObjectiveSkill('reading', 8, 10, [0, 8, 8, 8]).score === 8);
test('Writing combines Task 1 and Task 2 at 1:2 weighting', calculateWritingOverall(6, 9).score === 8);
test('Task 1-only daily writing needs only Task 1 score', calculateWritingDailyScore('task1', 7, null).valid === true && calculateWritingDailyScore('task1', 7, null).score === 7);
test('Task 2-only daily writing needs only Task 2 score', calculateWritingDailyScore('task2', null, 8).valid === true && calculateWritingDailyScore('task2', null, 8).score === 8);
test('Both-task writing rejects missing companion task score', calculateWritingDailyScore('both', 7, null).valid === false);
test('Equal-criteria writing/speaking keeps four equal criteria', calculateEqualCriteria([6, 8, 7, 9]).score === 7.5);
test('Assessment source and internal scale remain explicit', buildAssessmentRecord({skill:'writing',task:'task2',result:calculateEqualCriteria([6,6,6,6]),source:'learner_self_review'}).scale.includes('not an IELTS band'));

// Adaptive logic and evidence gates.
const empty = buildAdaptiveProfile({currentDay:1});
test('Adaptive baseline never claims mastery', empty.skills.every(x => x.canClaimMastery === false));
test('Adaptive profile preserves four mandatory skills', empty.skills.map(x => x.skill).sort().join(',') === 'listening,reading,speaking,writing');
test('Adaptive plan does not impose a time quota', !JSON.stringify(buildAdaptivePlan(empty,{mode:'balanced',currentDay:1})).match(/mandatory.{0,20}\d+\s*minutes/i));
test('All ten primary labs remain registered', LAB_IDS.length === 10 && new Set(LAB_IDS).size === 10);
test('Lab transfer validates a new objective item only with evidence', validateTransfer({labId:'reading',kind:'objective',correct:true,text:'new answer',evidence:'paragraph evidence present',reason:'because the matching phrase appears clearly in this paragraph',checks:{freshItem:true,answerKey:true}}).valid === true);

// Vocabulary / SRS invariants.
test('Vocabulary exact-token matching avoids substring false positives', containsLexicalItem('The party was excellent.', 'art') === false && containsLexicalItem('This is an art project.', 'art') === true);
test('Daily vocabulary gate needs 6/8 + 2 terms + 12 words', validateDailyVocabularyCompletion(6,2,12) && !validateDailyVocabularyCompletion(5,2,12) && !validateDailyVocabularyCompletion(8,1,12));
test('Again returns SRS card for same-day retry', scheduleVocabularyReview({},'again',new Date('2026-11-09T12:00:00')).intervalDays === 0);
test('SRS rejects unsupported rating', (() => { try { scheduleVocabularyReview({},'unknown'); return false; } catch { return true; } })());

// Backup / migration invariants.
test('Backup merge keeps new default keys while importing old settings', JSON.stringify(mergeBackupState({settings:{theme:'dark',lang:'uz'},newFlag:true},{settings:{theme:'light'}})) === JSON.stringify({settings:{theme:'light',lang:'uz'},newFlag:true}));
test('Backup validator rejects unsafe prototype key', inspectBackupEnvelope({app:'IELTS Boost',formatVersion:2,state:JSON.parse('{"completed":{},"scores":{},"drafts":{},"__proto__":{"x":1}}')}).valid === false);
test('Backup validator rejects missing required state maps', inspectBackupEnvelope({app:'IELTS Boost',formatVersion:2,state:{completed:{},scores:{}}}).valid === false);

// Transcript, Task 1, 4-skill and shell integration.
test('Transcript segment-aware lifecycle and manual fallback remain in runtime', ['SpeechRecognition','MediaRecorder','manual / keyboard dictation'].every(x => app.includes(x)));
test('Task 1 visual inspector remains connected', app.includes('task1-intelligence.js') && app.includes('s47Task1Masterclass') && app.includes('s47-data-inspector'));
test('Four daily skills remain mandatory in final curriculum', app.includes("['reading','writing','speaking','listening']") && app.includes('84-day IELTS Academic core'));
test('No official IELTS band conversion or live AI claim', !app.includes('officialBandScore=') && app.includes('liveAIAssessment:false'));

console.log(`STAGE 50 ENGINE QA: ${passed}/36 PASS`);
