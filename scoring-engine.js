/* IELTS Boost Stage 44 — provenance-aware formative scoring engine.
 * All scores are internal learning indices (0–10), never official IELTS bands.
 */
export const SCORING_ENGINE_VERSION = '44.0.0';

export const SCORING_CONFIG = Object.freeze({
  reading: Object.freeze({
    kind: 'objective_plus_evidence',
    criteria: ['Accuracy', 'Evidence', 'Strategy', 'Transfer'],
    weights: [0.50, 0.20, 0.15, 0.15]
  }),
  listening: Object.freeze({
    kind: 'equal_criteria',
    criteria: ['Comprehension & detail', 'Detail & word form', 'Paraphrase / distractor', 'Evidence & retest'],
    weights: [0.25, 0.25, 0.25, 0.25],
    note: 'Authentic provider recordings have no imported answer key in this release; criterion ratings remain learner self-review. The optional offline quiz is reported separately.'
  }),
  writing: Object.freeze({
    kind: 'equal_criteria',
    criteria: ['Task Achievement / Task Response', 'Coherence & Cohesion', 'Lexical Resource', 'Grammatical Range & Accuracy'],
    weights: [0.25, 0.25, 0.25, 0.25]
  }),
  speaking: Object.freeze({
    kind: 'equal_criteria',
    criteria: ['Fluency & Coherence', 'Lexical Resource', 'Grammatical Range & Accuracy', 'Pronunciation'],
    weights: [0.25, 0.25, 0.25, 0.25]
  })
});

export const ASSESSMENT_SOURCE_LABELS = Object.freeze({
  learner_self_review: 'O‘quvchining o‘zini baholashi',
  answer_key: 'Javob kaliti asosidagi avtomatik natija',
  deterministic_rule: 'Qoidalarga asoslangan avtomatik tahlil',
  ai_assisted: 'AI yordamidagi tahlil',
  teacher_review: 'Ustoz / examiner tekshiruvi',
  imported_legacy: 'Oldingi versiyadan import qilingan natija'
});

const isFiniteNumber = value => value !== null && value !== undefined && String(value).trim() !== '' && Number.isFinite(Number(value));
const clamp = value => Math.max(0, Math.min(10, Number(value)));
const round1 = value => Math.round((Number(value) + Number.EPSILON) * 10) / 10;

export function validateCriteria(values, expected = 4) {
  const errors = [];
  if (!Array.isArray(values) || values.length !== expected) {
    return { valid: false, errors: [`${expected} ta mezon balli talab qilinadi.`], values: [] };
  }
  const clean = values.map((value, index) => {
    if (!isFiniteNumber(value) || Number(value) < 0 || Number(value) > 10) {
      errors.push(`${index + 1}-mezon 0–10 oralig‘ida bo‘lishi kerak.`);
      return null;
    }
    return Number(value);
  });
  return { valid: errors.length === 0, errors, values: clean };
}

export function objectiveAccuracy(correct, total) {
  if (!isFiniteNumber(correct) || !isFiniteNumber(total) || Number(total) <= 0) return null;
  const c = Number(correct), t = Number(total);
  if (!Number.isInteger(c) || !Number.isInteger(t) || c < 0 || c > t) return null;
  return round1((c / t) * 10);
}

export function calculateWeightedObjectiveSkill(skill, correct, total, criterionValues) {
  const config = SCORING_CONFIG[skill];
  if (!config || config.kind !== 'objective_plus_evidence') throw new Error(`Unsupported objective skill: ${skill}`);
  const checked = validateCriteria(criterionValues, 4);
  if (!checked.valid) return { valid: false, errors: checked.errors, score: null };
  const objective = objectiveAccuracy(correct, total);
  if (objective === null) return { valid: false, errors: ['To‘g‘ri javoblar soni va jami savollar soni kerak.'], score: null };
  const criteria = [...checked.values];
  criteria[0] = objective;
  const score = round1(criteria.reduce((sum, value, index) => sum + value * config.weights[index], 0));
  return {
    valid: true,
    skill,
    score,
    criteria,
    objective: { correct: Number(correct), total: Number(total), accuracyPercent: round1(Number(correct) / Number(total) * 100), score10: objective },
    weights: [...config.weights],
    source: 'answer_key_plus_learner_self_review',
    scoreType: 'internal_practice_quality_0_to_10'
  };
}

export function calculateEqualCriteria(values, weights = [0.25, 0.25, 0.25, 0.25]) {
  const checked = validateCriteria(values, 4);
  if (!checked.valid) return { valid: false, errors: checked.errors, score: null };
  if (!Array.isArray(weights) || weights.length !== 4 || weights.some(x => !Number.isFinite(Number(x)) || Number(x) < 0) || Math.abs(weights.reduce((a,b)=>a+Number(b),0)-1) > 1e-8) {
    return { valid: false, errors: ['Mezon vaznlari yig‘indisi 1 bo‘lishi kerak.'], score: null };
  }
  return {
    valid: true,
    score: round1(checked.values.reduce((sum, value, index) => sum + value * Number(weights[index]), 0)),
    criteria: checked.values,
    weights: weights.map(Number),
    scoreType: 'internal_practice_quality_0_to_10'
  };
}

export function calculateWritingOverall(task1Score, task2Score) {
  if (!isFiniteNumber(task1Score) || !isFiniteNumber(task2Score)) return { valid: false, score: null, message: 'Task 1 va Task 2 baholari ikkalasi ham kerak.' };
  if ([task1Score, task2Score].some(value => Number(value) < 0 || Number(value) > 10)) return { valid: false, score: null, message: 'Task baholari 0–10 oralig‘ida bo‘lishi kerak.' };
  return { valid: true, task1: Number(task1Score), task2: Number(task2Score), weights: [1/3, 2/3], score: round1((Number(task1Score) + 2 * Number(task2Score)) / 3), scoreType: 'internal_practice_quality_0_to_10' };
}

export function calculateWritingDailyScore(primaryTask, task1Score, task2Score) {
  if (primaryTask === 'both') {
    const combined = calculateWritingOverall(task1Score, task2Score);
    return combined.valid ? { ...combined, basis: 'both_tasks_task2_double_weight', requiredTasks: ['task1', 'task2'] } : { ...combined, basis: 'both_tasks_task2_double_weight', requiredTasks: ['task1', 'task2'] };
  }
  if (!['task1', 'task2'].includes(primaryTask)) return { valid: false, score: null, message: 'Kunlik Writing vazifasi task1, task2 yoki both bo‘lishi kerak.' };
  const value = primaryTask === 'task1' ? task1Score : task2Score;
  if (!isFiniteNumber(value) || Number(value) < 0 || Number(value) > 10) return { valid: false, score: null, message: `${primaryTask.toUpperCase()} uchun baho hali saqlanmagan.` };
  return { valid: true, score: round1(value), basis: `${primaryTask}_only_daily_task`, requiredTasks: [primaryTask], task1: primaryTask === 'task1' ? Number(value) : null, task2: primaryTask === 'task2' ? Number(value) : null, scoreType: 'internal_practice_quality_0_to_10' };
}

export function assessEvidenceStrength(evidenceItems = [], objectivePresent = false, source = 'learner_self_review') {
  const items = Array.isArray(evidenceItems) ? evidenceItems : [];
  const anchored = items.filter(item => String(item || '').trim().length >= 10).length;
  const total = items.length;
  const coverage = total ? round1((anchored / total) * 100) : 0;
  let label = 'Cheklangan';
  if (coverage >= 90 && (objectivePresent || ['teacher_review', 'ai_assisted'].includes(source))) label = 'Kuchli';
  else if (coverage >= 65) label = 'O‘rtacha';
  return {
    evidenceItems: anchored,
    totalItems: total,
    coveragePercent: coverage,
    label,
    objectiveEvidencePresent: !!objectivePresent,
    note: 'Bu dalil qamrovi ko‘rsatkichi; statistik ishonch oralig‘i yoki examiner ishonchliligi emas.'
  };
}

export function buildAssessmentRecord({ skill, task = null, result, source = 'learner_self_review', evidence = [], objectivePresent = false, reviewer = '', audioVerified = false, notes = '' }) {
  if (!result || result.valid !== true || !isFiniteNumber(result.score)) throw new Error('Valid scoring result is required.');
  const config = SCORING_CONFIG[skill];
  const criteria = (result.criteria || []).map((score, index) => ({
    id: `${skill}_${index + 1}`,
    name: config?.criteria?.[index] || `Criterion ${index + 1}`,
    score: Number(score),
    weight: Number(result.weights?.[index] ?? 0),
    source: index === 0 && result.objective ? 'answer_key' : source,
    evidence: String(evidence[index] || '').trim()
  }));
  const evidenceStrength = assessEvidenceStrength(evidence, objectivePresent || !!result.objective, source);
  return {
    version: SCORING_ENGINE_VERSION,
    skill,
    task,
    score: round1(result.score),
    scale: '0–10 internal practice quality; not an IELTS band',
    source,
    sourceLabel: ASSESSMENT_SOURCE_LABELS[source] || 'Manba ko‘rsatilmagan',
    criteria,
    objective: result.objective || null,
    evidenceStrength,
    reviewer: String(reviewer || '').trim(),
    audioVerified: !!audioVerified,
    notes: String(notes || '').trim(),
    calculatedAt: new Date().toISOString()
  };
}

export function roundScore(value) { return round1(clamp(value)); }
