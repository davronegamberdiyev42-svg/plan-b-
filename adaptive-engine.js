/* IELTS Boost Stage 46 — evidence-led adaptive learning engine.
 * Deterministic local decision support. This is not a generative AI or an IELTS examiner.
 * Completion, self-review, objective answers, rubric records and error history are kept distinct.
 */
export const ADAPTIVE_ENGINE_VERSION = '46.0.0';
export const ADAPTIVE_SKILLS = Object.freeze(['reading', 'writing', 'speaking', 'listening']);

const clamp = (n, lo = 0, hi = 10) => Math.max(lo, Math.min(hi, Number.isFinite(Number(n)) ? Number(n) : lo));
const round1 = n => Math.round((Number(n) + Number.EPSILON) * 10) / 10;
const finite = n => n !== null && n !== undefined && n !== '' && Number.isFinite(Number(n));
const normSkill = value => {
  const s = String(value || '').toLowerCase();
  return ADAPTIVE_SKILLS.find(k => s.includes(k)) || 'other';
};

function criterionSignals(criteria = []) {
  const rows = (Array.isArray(criteria) ? criteria : [])
    .filter(x => x && finite(x.mean) && Number(x.n) >= 2)
    .map(x => ({ name: String(x.name || 'Criterion'), mean: clamp(x.mean, 0, 9), n: Math.max(0, Math.trunc(Number(x.n) || 0)) }));
  rows.sort((a, b) => a.mean - b.mean || b.n - a.n);
  return rows;
}

function makeDiagnostic(skill, metric = {}, errors = [], lab = null) {
  const rawCount = Math.max(0, Math.trunc(Number(metric.rawSampleCount ?? metric.raw?.length ?? 0) || 0));
  const rawPct = finite(metric.rawAccuracyPercent ?? metric.rawPct) ? clamp(metric.rawAccuracyPercent ?? metric.rawPct, 0, 100) : null;
  const qualityCount = Math.max(0, Math.trunc(Number(metric.qualitySampleCount ?? metric.rows?.length ?? 0) || 0));
  const qualityAvg = finite(metric.qualityAverage ?? metric.avg) ? clamp(metric.qualityAverage ?? metric.avg, 0, 10) : null;
  const trendCount = Math.max(0, Math.trunc(Number(metric.trendSampleCount ?? metric.rows?.length ?? 0) || 0));
  const trendDelta = finite(metric.trendDelta ?? metric.trend?.delta) ? Number(metric.trendDelta ?? metric.trend?.delta) : null;
  const evidencePct = finite(metric.evidencePercent ?? metric.evidencePct) ? clamp(metric.evidencePercent ?? metric.evidencePct, 0, 100) : null;
  const criterionRows = criterionSignals(metric.criteria || []);
  const criterionMinN = criterionRows.length ? Math.min(...criterionRows.map(x => x.n)) : 0;
  const criterionAvg = criterionRows.length ? criterionRows.reduce((s, x) => s + x.mean, 0) / criterionRows.length : null;
  const weakestCriterion = criterionRows[0] || null;
  const openErrorCount = Math.max(0, Math.trunc(Number(metric.openErrorCount ?? metric.openErrors ?? errors.reduce((n, e) => n + (normSkill(e.skill) === skill ? Number(e.count) || 1 : 0), 0)) || 0));
  const matchingErrors = errors.filter(e => normSkill(e.skill) === skill);
  const repeatError = matchingErrors.slice().sort((a, b) => Number(b.count || 0) - Number(a.count || 0))[0] || null;
  const labSamples = Math.max(0, Math.trunc(Number(lab?.objectiveAttempts || 0)));
  const labAccuracy = finite(lab?.recentAccuracyPercent) ? clamp(lab.recentAccuracyPercent, 0, 100) : null;
  const objectiveSamples = Math.max(rawCount, labSamples);
  const objectiveAccuracy = rawCount >= labSamples ? rawPct : labAccuracy;
  const objectiveSource = rawCount >= labSamples ? 'daily_answer_key' : (labSamples ? 'laboratory_answer_key' : null);

  // A strong primary signal requires multiple independent attempts. Self-review is never promoted to objective evidence.
  let primarySource = null;
  let primarySamples = 0;
  let primaryMean = null;
  let primaryKind = 'none';
  if ((skill === 'reading' || skill === 'listening') && objectiveSamples >= 3 && objectiveAccuracy !== null) {
    primarySource = objectiveSource || 'answer_key';
    primarySamples = objectiveSamples;
    primaryMean = objectiveAccuracy / 10; // convert percentage to 0–10
    primaryKind = 'objective_accuracy';
  } else if ((skill === 'writing' || skill === 'speaking') && criterionMinN >= 2 && criterionRows.length >= 3) {
    primarySource = 'saved_rubric_records';
    primarySamples = criterionMinN;
    primaryMean = criterionAvg * (10 / 9); // rubric records use 0–9; convert only for internal risk ordering
    primaryKind = 'criterion_review';
  }

  const signals = [];
  if (primaryMean !== null) {
    signals.push({ id: primaryKind, label: primaryKind === 'objective_accuracy' ? 'Javob kaliti bilan tekshirilgan natija' : 'Saqlangan mezonli baholash yozuvlari', severity: 1 - clamp(primaryMean, 0, 10) / 10, weight: 0.58, samples: primarySamples, source: primarySource });
  } else if (qualityAvg !== null && qualityCount >= 3) {
    // Self-score is a low-weight review hint only.
    signals.push({ id: 'self_review_hint', label: 'O‘quvchining ichki 0–10 self-review bahosi', severity: (1 - qualityAvg / 10) * 0.45, weight: 0.18, samples: qualityCount, source: 'learner_self_review' });
  }
  if (trendDelta !== null && trendCount >= 4 && trendDelta <= -0.5) {
    signals.push({ id: 'declining_trend', label: 'Oxirgi baholarda pasayish tendensiyasi', severity: clamp(Math.abs(trendDelta) / 2.5, 0, 1), weight: 0.18, samples: trendCount, source: 'saved_skill_scores' });
  }
  if (openErrorCount > 0) {
    signals.push({ id: 'open_errors', label: 'Hal qilinmagan xato qaydlari', severity: clamp(openErrorCount / 4, 0, 1), weight: 0.18, samples: openErrorCount, source: 'error_log' });
  }
  if (evidencePct !== null && qualityCount >= 3 && evidencePct < 60) {
    signals.push({ id: 'evidence_gap', label: 'Baholangan sessiyalarda dalil qamrovi past', severity: clamp((60 - evidencePct) / 60, 0, 1), weight: 0.08, samples: qualityCount, source: 'task_evidence_records' });
  }
  if (labSamples >= 3 && labAccuracy !== null && primaryKind !== 'objective_accuracy') {
    signals.push({ id: 'lab_accuracy', label: 'Laboratoriya javob kaliti natijasi', severity: 1 - labAccuracy / 100, weight: 0.32, samples: labSamples, source: 'answer_key' });
  }

  const weightTotal = signals.reduce((s, x) => s + x.weight, 0);
  const priority = weightTotal ? round1(10 * signals.reduce((s, x) => s + x.severity * x.weight, 0) / weightTotal) : (qualityCount || openErrorCount ? 3.2 : 2.5);
  const confidenceSamples = primarySamples || (labSamples >= 3 ? labSamples : 0);
  let confidence = 'Dalil yetarli emas';
  let confidenceLevel = 'insufficient';
  if (confidenceSamples >= 5) { confidence = 'Yaxshi namuna'; confidenceLevel = 'high'; }
  else if (confidenceSamples >= 3) { confidence = 'O‘rtacha namuna'; confidenceLevel = 'moderate'; }
  else if (confidenceSamples >= 1 || qualityCount >= 2 || openErrorCount > 0) { confidence = 'Cheklangan signal'; confidenceLevel = 'limited'; }

  let actionType = 'baseline';
  let phase = 'Baseline / diagnostika';
  let task = 'Birinchi taqqoslanadigan diagnostik urinish';
  let action = 'Bugungi majburiy skill vazifasini bajar, javob yoki draftni saqla va mos dalilni biriktir. Vaqt limiti yo‘q.';
  let why = 'Hozircha bu skill bo‘yicha ishonchli xulosa chiqarish uchun yetarli mustaqil dalil yo‘q.';
  if (primaryKind === 'objective_accuracy' && primaryMean !== null && primaryMean < 6.5) {
    actionType = 'objective_repair'; phase = 'Maqsadli aniqlikni tuzatish'; task = skill === 'reading' ? 'Reading: savol turi + evidence repair' : 'Listening: signal, distractor va detail repair';
    action = 'Eng ko‘p xato bo‘lgan savol turini ajrat, javobni kalit va matn/audio dalili bilan qayta tahlil qil, so‘ng yangi materialda tekshir.';
    why = `Javob kaliti bilan tekshirilgan ${primarySamples} ta mustaqil namuna bo‘yicha aniqlik ${round1(primaryMean)}/10 ekvivalentida.`;
  } else if ((skill === 'writing' || skill === 'speaking') && weakestCriterion && weakestCriterion.mean < 5.5) {
    actionType = 'criterion_repair'; phase = 'Mezon bo‘yicha tuzatish'; task = `${weakestCriterion.name}: maqsadli revision`;
    action = skill === 'writing' ? 'Zaif mezon bo‘yicha bitta draft qismini qayta yoz, o‘zgarishni sabab bilan izohla va yangi promptda transfer qil.' : 'Zaif mezon uchun yangi javob yozib/yozib ol, dalilni audio yoki matn bo‘yicha tekshir va yangi savolda qayta sinab ko‘r.';
    why = `${weakestCriterion.name} mezonida ${weakestCriterion.n} ta saqlangan baholash yozuvi o‘rtachasi ${weakestCriterion.mean.toFixed(1)}/9. Bu mustaqil examiner bahosi ekanini anglatmaydi.`;
  } else if (trendDelta !== null && trendCount >= 4 && trendDelta <= -0.5) {
    actionType = 'trend_recovery'; phase = 'Trendni tiklash'; task = `${skill} · pasayish sababini tekshirish`;
    action = 'Oxirgi va oldingi ishlarni taqqosla, farqni keltirgan bitta sababni yoz, keyin yangi promptda qayta tekshir.';
    why = `Saqlangan baholar tendensiyasi ${Math.abs(trendDelta).toFixed(1)} ballga pasaygan; kamida 4 ta baholangan sessiya bor.`;
  } else if (repeatError && (Number(repeatError.count) || 0) >= 2) {
    actionType = 'error_repair'; phase = 'Takrorlangan xatoni tuzatish'; task = `Error Lab · ${repeatError.type}`;
    action = 'Shu xatoning sababini va oldini olish qoidalarini yoz, so‘ng boshqa savol yoki mavzuda transfer sinovi bajar.';
    why = `${repeatError.type} xatosi ${repeatError.count} marta qayd etilgan.`;
  } else if (primaryKind === 'objective_accuracy' && primaryMean !== null && primaryMean >= 8) {
    actionType = 'stretch'; phase = 'Murakkabroq transfer'; task = `${skill} · unseen stretch challenge`;
    action = 'Yangi mavzu yoki murakkabroq savol turida natija barqarorligini tekshir; eski item’ni takrorlashni yangi namuna deb hisoblama.';
    why = `${primarySamples} ta mustaqil javob-kalitli namunada natija yaxshi; keyingi sinovda yangi material ishlatiladi.`;
  } else if (primaryKind === 'criterion_review' && primaryMean !== null && primaryMean >= 8) {
    actionType = 'transfer'; phase = 'Yangi promptga ko‘chirish'; task = `${skill} · fresh prompt + revision`;
    action = 'Yaxshi ko‘ringan mezonlarni yangi, ko‘rilmagan promptda qo‘llab ko‘r; self-review va mustaqil reviewni alohida saqla.';
    why = 'Saqlangan mezonli yozuvlar yaxshi ko‘rsatmoqda; natija hali mustaqil examiner yoki AI tekshiruvi bilan tasdiqlanmagan.';
  } else if (primaryKind !== 'none') {
    actionType = 'transfer'; phase = 'Transfer va barqarorlik'; task = `${skill} · yangi materialda qo‘llash`;
    action = 'Yangi savol, mavzu yoki recording tanla; avvalgi xatoni qaytarmasdan qo‘llashni dalil bilan tekshir.';
    why = 'Mavjud dalillar qo‘shimcha transfer mashqini tanlashga yetadi, lekin barcha mezonlar to‘liq tasdiqlanmagan.';
  } else if (qualityCount >= 3) {
    actionType = 'verify_self_review'; phase = 'Self-reviewni tekshirish'; task = `${skill} · mustaqil dalil yig‘ish`;
    action = 'O‘zing bergan bahoni yangi task, raw answer key yoki to‘liq mezonli review bilan tekshir. Hozirgi self-score yakka holda mastery hisoblanmaydi.';
    why = `Ichki baho ${qualityAvg?.toFixed(1)}/10, ammo yetarli mustaqil natija signali yo‘q.`;
  } else if (openErrorCount > 0) {
    actionType = 'error_capture'; phase = 'Xato tarixini to‘ldirish'; task = 'Error Lab · sabab va tuzatish';
    action = 'Ochiq xatolarni ko‘rib chiq, sababini aniqla va yangi topshiriqda qayta tekshir.';
    why = `${openErrorCount} ta ochiq xato qaydi bor, ammo skill bo‘yicha mastery xulosasi uchun namuna yetarli emas.`;
  }

  const basedOn = signals.map(x => `${x.label} (${x.samples})`);
  const unknowns = [];
  if (confidenceLevel === 'insufficient' || confidenceLevel === 'limited') unknowns.push('Mustaqil namuna soni hali kam.');
  if (skill === 'writing' || skill === 'speaking') unknowns.push('Mezonli yozuvlar self-review bo‘lishi mumkin; examiner tasdig‘i avtomatik taxmin qilinmaydi.');
  if (skill === 'speaking') unknowns.push('Transcript so‘z tanlash/grammatikani ko‘rsatishi mumkin, ammo talaffuzni audio tekshiruvisiz baholamaydi.');
  if (skill === 'listening' && objectiveKindUnavailable(metric)) unknowns.push('Tashqi audio uchun javob kaliti bo‘lmasa raw accuracy hisoblanmaydi.');
  if (qualityCount && primaryKind === 'none') unknowns.push('0–10 ichki sifat bahosi mustaqil mastery dalili emas.');

  return {
    skill, phase, actionType, task, action, why,
    priority: clamp(priority, 0, 10), confidence, confidenceLevel,
    primaryKind, primarySamples, primaryMean: primaryMean === null ? null : round1(primaryMean),
    rawSampleCount: rawCount, rawAccuracyPercent: rawPct,
    qualitySampleCount: qualityCount, qualityAverage: qualityAvg,
    trendDelta: trendCount >= 4 ? trendDelta : null,
    openErrorCount, repeatedError: repeatError ? { type: repeatError.type, count: Number(repeatError.count) || 1 } : null,
    weakestCriterion: weakestCriterion ? { ...weakestCriterion } : null,
    lab: lab ? { attempts: labSamples, accuracyPercent: labAccuracy, weakestMode: lab.weakestMode ?? null } : null,
    signals, basedOn, unknowns,
    canClaimMastery: false,
    note: 'Bu tavsiya mahalliy, tushuntiriladigan qoidalarga asoslangan. Generativ AI emas va rasmiy IELTS bandi emas.'
  };
}
function objectiveKindUnavailable(metric) {
  return !(Number(metric?.raw?.length || metric?.rawSampleCount || 0) >= 3);
}

export function buildAdaptiveProfile({ skills = {}, errors = [], labs = {}, currentDay = 1, completedCount = 0, now = new Date().toISOString() } = {}) {
  const diagnostics = ADAPTIVE_SKILLS.map(skill => makeDiagnostic(skill, skills[skill] || {}, Array.isArray(errors) ? errors : [], labs[skill] || null));
  diagnostics.sort((a, b) => b.priority - a.priority || (ADAPTIVE_SKILLS.indexOf(a.skill) - ADAPTIVE_SKILLS.indexOf(b.skill)));
  const sufficientlyMeasured = diagnostics.filter(x => x.confidenceLevel === 'high' || x.confidenceLevel === 'moderate').length;
  const top = diagnostics[0] || null;
  const measuredSkills = diagnostics.filter(x => x.primarySamples >= 3).length;
  return {
    version: ADAPTIVE_ENGINE_VERSION,
    computedAt: now,
    currentDay: clamp(currentDay, 1, 84),
    completedSkillSessions: Math.max(0, Math.trunc(Number(completedCount) || 0)),
    skills: diagnostics,
    recommendedFocus: top?.skill || null,
    nextAction: top ? { skill: top.skill, actionType: top.actionType, phase: top.phase, task: top.task, action: top.action, priority: top.priority, confidence: top.confidence } : null,
    evidenceCoverage: { measuredSkills, sufficientlyMeasured, totalSkills: 4, label: `${measuredSkills}/4 skillda kamida 3 mustaqil yoki mezonli namuna mavjud` },
    limitations: ['Kunlik majburiy 4-skill rejasi o‘zgartirilmaydi.', 'Tavsiyalar qo‘shimcha fokus; vaqt limiti yaratmaydi.', 'Bu lokal qoidaviy engine; Live AI yoki IELTS examiner emas.', 'Completion foizi mastery deb talqin qilinmaydi.']
  };
}

export function buildAdaptivePlan(profile, { mode = 'balanced', pendingSession = null, openError = null, currentDay = 1 } = {}) {
  const maxSteps = mode === 'gentle' ? 1 : mode === 'full' ? 3 : 2;
  const steps = [];
  if (pendingSession && steps.length < maxSteps) {
    steps.push({ id: `resume-${currentDay}`, type: 'resume', skill: pendingSession.skill, day: pendingSession.day, title: `Day ${pendingSession.day} · ${pendingSession.skill} majburiy sessiyasini davom ettir`, description: 'Bu 84 kunlik asosiy rejadagi sessiya. Boshqa kunlar yoki skilllar o‘chirilmaydi.', route: pendingSession.skill });
  }
  const top = profile?.skills?.slice().sort((a, b) => b.priority - a.priority)[0];
  if (top && steps.length < maxSteps) {
    steps.push({ id: `focus-${top.skill}-${currentDay}`, type: 'focus', skill: top.skill, day: currentDay, title: `${top.skill.toUpperCase()} · ${top.task}`, description: `${top.why} ${top.action}`, confidence: top.confidence, route: top.skill });
  }
  if (openError && steps.length < maxSteps) {
    steps.push({ id: `error-${currentDay}`, type: 'error_repair', skill: normSkill(openError.skill), day: currentDay, title: `Error Lab · ${openError.type || 'takrorlangan xato'}`, description: 'Xato sababini yoz, tuzatish qoidasini belgila va boshqa savolda tekshir.', route: 'errors' });
  }
  return { version: ADAPTIVE_ENGINE_VERSION, mode, createdAt: new Date().toISOString(), steps: steps.slice(0, maxSteps), timeLimit: null, preservesMandatoryPlan: true, source: 'local_evidence_based_rules' };
}
