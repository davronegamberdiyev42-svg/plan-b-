/* IELTS Boost Stage 45 — evidence-led laboratory quality engine.
 * Separates answer-key outcomes from completion/self-review evidence.
 * Never treats text length or checkbox completion as proof of language mastery.
 */
export const LAB_QUALITY_ENGINE_VERSION = '45.0.0';

export const LAB_IDS = Object.freeze([
  'reading', 'listening', 'writing', 'speaking',
  'collocations', 'pronunciation', 'paraphrase', 'grammar', 'vocabulary', 'fluency'
]);

export const LAB_LABELS = Object.freeze({
  reading: 'Reading Evidence Studio',
  listening: 'Listening Audio Mission',
  writing: 'Writing Visual Studio',
  speaking: 'Speaking Response Studio',
  collocations: 'Collocation Forge',
  pronunciation: 'Pronunciation Clinic',
  paraphrase: 'Paraphrase Arena',
  grammar: 'Grammar Architect',
  vocabulary: 'Vocabulary Recall',
  fluency: 'Academic Fluency Builder'
});

export const ERROR_CAUSES = Object.freeze({
  task_focus: 'Savol yoki topshiriq talabini noto‘g‘ri tushunish',
  evidence: 'Matndan / audiodan kerakli dalilni topmaslik',
  paraphrase: 'Paraphrase yoki sinonimni tanimaslik',
  distractor: 'Chalg‘ituvchi javobga ergashish',
  detail: 'Raqam, ism, sana yoki word form xatosi',
  grammar: 'Grammatik qoida yoki gap tuzilishi',
  collocation: 'Tabiiy so‘z birikmasini tanlamaslik',
  meaning: 'Ma’no, scope yoki certainty o‘zgarib ketishi',
  pronunciation: 'Tovush, urg‘u, linking yoki intonatsiya',
  vocabulary: 'So‘z ma’nosi yoki qo‘llanish konteksti',
  organisation: 'Fikrlar ketma-ketligi va bog‘lanishi',
  other: 'Boshqa / hali aniqlanmagan sabab'
});

const clampInt = (n, min, max) => Math.min(max, Math.max(min, Math.trunc(Number(n) || 0)));
const round1 = n => Math.round((Number(n) + Number.EPSILON) * 10) / 10;

export function summariseLabAttempts(attempts = [], labId = '') {
  const rows = (Array.isArray(attempts) ? attempts : [])
    .filter(x => x && x.labId === labId)
    .sort((a, b) => String(a.at || '').localeCompare(String(b.at || '')));
  const rawObjective = rows.filter(x => x.kind === 'objective' && typeof x.correct === 'boolean');
  // A repeated attempt on the exact same prompt is one evidence item, not a new independent sample.
  const uniqueObjective = new Map();
  rawObjective.forEach((row, index) => uniqueObjective.set(row.itemKey ? String(row.itemKey) : `legacy:${row.at || index}:${index}`, row));
  const objective = [...uniqueObjective.values()].sort((a, b) => String(a.at || '').localeCompare(String(b.at || '')));
  const recent = objective.slice(-5);
  const accuracy = recent.length ? round1(recent.filter(x => x.correct).length / recent.length * 100) : null;
  const modeMap = new Map();
  for (const row of objective) {
    const m = clampInt(row.mode, 0, 9);
    const prev = modeMap.get(m) || { mode: m, attempts: 0, correct: 0 };
    prev.attempts += 1;
    if (row.correct) prev.correct += 1;
    modeMap.set(m, prev);
  }
  const modeStats = [...modeMap.values()].map(x => ({ ...x, accuracy: round1(x.correct / x.attempts * 100) }));
  const weak = modeStats.filter(x => x.attempts >= 1).sort((a, b) => a.accuracy - b.accuracy || b.attempts - a.attempts)[0] || null;
  const processCount = rows.filter(x => x.kind !== 'objective').length;
  const transferRows = rows.filter(x => x.kind === 'transfer');
  const transferObjective = transferRows.filter(x => typeof x.correct === 'boolean');
  const transferAccuracy = transferObjective.length
    ? round1(transferObjective.filter(x => x.correct).length / transferObjective.length * 100)
    : null;

  let status = 'insufficient';
  let statusLabel = 'Dalil yetarli emas';
  let explanation = 'Kamida 3 ta javob kaliti bilan tekshirilgan urinish yig‘ilmaguncha mastery xulosasi chiqarilmaydi.';
  if (recent.length >= 3) {
    if (accuracy < 60) {
      status = 'priority'; statusLabel = 'Maqsadli tuzatish kerak';
      explanation = 'Oxirgi 5 tagacha obyektiv urinishda aniqlik 60% dan past. Avval xato sababini aniqlab, shu rejimni qayta mashq qil.';
    } else if (accuracy < 80) {
      status = 'developing'; statusLabel = 'Rivojlanmoqda';
      explanation = 'Natija yaxshilanmoqda, lekin barqarorlik uchun yangi savollarda qo‘shimcha transfer kerak.';
    } else {
      status = 'promising'; statusLabel = 'Barqaror signal';
      explanation = 'Oxirgi urinishlar yaxshi natija ko‘rsatmoqda. Bu laboratoriya namunasi, rasmiy IELTS darajasi yoki umumiy skill mastery emas.';
    }
  }
  return {
    labId,
    totalAttempts: rows.length,
    objectiveAttempts: objective.length,
    recentObjectiveAttempts: recent.length,
    recentAccuracyPercent: accuracy,
    processEvidenceCount: processCount,
    transferAttempts: transferRows.length,
    transferObjectiveAttempts: transferObjective.length,
    transferAccuracyPercent: transferAccuracy,
    status, statusLabel, explanation,
    weakestMode: weak?.mode ?? null,
    weakestModeAccuracy: weak?.accuracy ?? null,
    modeStats
  };
}

export function recommendLabMode(summary, currentMode = 0, modeCount = 10) {
  const current = clampInt(currentMode, 0, modeCount - 1);
  if (summary?.weakestMode !== null && summary?.weakestMode !== undefined && summary.weakestModeAccuracy < 80) {
    return { mode: clampInt(summary.weakestMode, 0, modeCount - 1), reason: 'weakest-evidence-mode', label: 'Zaifroq rejimni qayta mashq qil' };
  }
  if ((summary?.recentObjectiveAttempts || 0) >= 3 && (summary?.recentAccuracyPercent ?? 0) >= 80) {
    return { mode: (current + 1) % modeCount, reason: 'advance-after-stable-sample', label: 'Keyingi rejimga o‘t' };
  }
  return { mode: current, reason: 'collect-comparable-evidence', label: 'Joriy rejimda dalil yig‘' };
}

export function classifyLabOutcome({ correct, mode, labId }) {
  if (typeof correct === 'boolean') {
    return { kind: 'objective', source: 'answer_key', scoreMeaning: 'answer-key result plus required evidence' };
  }
  if ((labId === 'writing' || labId === 'speaking') && Number(mode) === 9) {
    return { kind: 'self_review', source: 'learner_self_review', scoreMeaning: 'criterion self-review; not independently verified' };
  }
  return { kind: 'process', source: 'practice_process', scoreMeaning: 'task completion / evidence completeness; not language accuracy' };
}

export function validateTransfer({ labId, kind, correct, text = '', evidence = '', reason = '', fields = {}, checks = {}, audioCompleted = false, notGiven = false }) {
  const words = value => String(value || '').trim().split(/\s+/).filter(Boolean).length;
  const errors = [];
  if (kind === 'objective') {
    if (correct !== true && correct !== false) errors.push('Javob variantini tanla.');
    if (labId === 'reading' && notGiven) {
      const absence = /not mentioned|not stated|no information|does not mention|doesn't mention|not reported|cannot be determined|not specified|no exact quote/i.test(String(reason));
      if (String(evidence).trim() && !/^(no exact quote|not stated|not given|no evidence)$/i.test(String(evidence).trim())) errors.push('NOT GIVEN javobida mavjud bo‘lmagan dalilni ixtiro qilma; evidence maydonini bo‘sh qoldir.');
      if (!absence || words(reason) < 5) errors.push('NOT GIVEN uchun ma’lumot passage’da yo‘qligini kamida 5 so‘z bilan asosla.');
    } else if (labId === 'reading' && (String(evidence).trim().length < 8 || words(reason) < 5)) errors.push('Matndan dalil va sabab izohini kiriting.');
    if (labId === 'listening' && !audioCompleted) errors.push('Yangi audio’ni oxirigacha tingla.');
    if (labId === 'listening' && String(evidence).trim().length < 5) errors.push('Eshitilgan ibora yoki detalni yoz.');
    if (labId === 'collocations' && words(text) < 10) errors.push('Target collocation bilan kamida 10 so‘zli yangi gap tuz.');
    if (labId === 'grammar' && (words(reason) < 6 || words(text) < 8)) errors.push('Grammatik qoida izohi va yangi misol gap yoz.');
  } else if (labId === 'writing') {
    if (words(text) < 35) errors.push('Yangi prompt uchun kamida 35 so‘zli thesis/reja yoz.');
    if (String(evidence).trim().length < 12) errors.push('Promptning qaysi qismini qamrab olganingni tushuntir.');
  } else if (labId === 'speaking') {
    if (words(text) < 35) errors.push('Yangi promptga kamida 35 so‘z bilan javob ber.');
    if (String(evidence).trim().length < 12) errors.push('Nutq bo‘yicha aniq self-review yoz.');
  } else if (labId === 'pronunciation') {
    if (Object.values(checks).filter(Boolean).length < 3) errors.push('Kamida 3 ta audio self-check belgila.');
    if (String(evidence).trim().length < 8) errors.push('Qaysi tovush yoki urg‘uni tuzatishingni yoz.');
  } else if (labId === 'paraphrase') {
    if (words(text) < 15) errors.push('Kamida 15 so‘zli paraphrase yoz.');
    if (Object.values(checks).filter(Boolean).length < 3) errors.push('Meaning, scope va certainty bo‘yicha kamida 3 tekshiruvni tasdiqla.');
    if (String(evidence).trim().length < 10) errors.push('Qaysi grammatik/lexical o‘zgarish qilganingni izohla.');
  } else if (labId === 'vocabulary') {
    if (words(text) < 5) errors.push('So‘z ma’nosini xotiradan kamida 5 so‘z bilan yoz.');
    if (String(evidence).trim().length < 8) errors.push('Yangi kontekst yoki collocation misolini yoz.');
  } else if (labId === 'fluency') {
    for (const key of ['claim', 'reason', 'example', 'qualification']) {
      if (words(fields[key]) < 5) errors.push(`${key} bo‘limini kamida 5 so‘z bilan to‘ldir.`);
    }
  }
  if (kind === 'objective' && correct === false) {
    if (!fields.errorCause) errors.push('Xato sababini tanla.');
    if (String(fields.repairPlan || '').trim().length < 10) errors.push('Xatoni tuzatish bo‘yicha aniq reja yoz.');
  }
  return { valid: errors.length === 0, errors, wordCounts: { text: words(text), reason: words(reason) } };
}

export function buildLabAttempt({ labId, mode, day, correct = null, score = null, at = new Date().toISOString(), kind = 'process', source = 'practice_process', transfer = false, errorCause = '', itemKey = '' }) {
  return {
    labId, mode: clampInt(mode, 0, 9), day: clampInt(day, 1, 84),
    correct: typeof correct === 'boolean' ? correct : null,
    score: score !== null && score !== undefined && Number.isFinite(Number(score)) ? round1(score) : null,
    at, kind: transfer ? 'transfer' : kind, source,
    errorCause: String(errorCause || ''),
    itemKey: String(itemKey || ''),
    scale: 'practice evidence only; not an IELTS band'
  };
}
