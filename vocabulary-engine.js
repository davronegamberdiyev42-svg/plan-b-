export const VOCAB_ENGINE_VERSION = '48.0.0';

const CORE_FIELDS = ['meaning_en', 'uzbek', 'example', 'part_of_speech'];
const clean = value => String(value ?? '').trim();
const normal = value => clean(value).toLocaleLowerCase().normalize('NFKC')
  .replace(/[’‘`]/g, "'").replace(/[^a-z0-9' -]/g, ' ').replace(/\s+/g, ' ').trim();

export function auditVocabulary(words = [], dailySets = []) {
  const list = Array.isArray(words) ? words : [];
  const byId = new Map(list.map(word => [Number(word.id), word]));
  const ids = dailySets.flatMap(set => Array.isArray(set.word_ids) ? set.word_ids.map(Number) : []);
  const coreIds = [...new Set(ids)];
  const coreWords = coreIds.map(id => byId.get(id)).filter(Boolean);
  const complete = word => CORE_FIELDS.every(field => clean(word?.[field]));
  const dualIpa = word => !!(clean(word?.ipa_us) && clean(word?.ipa_uk));
  const normalisedWords = list.map(word => normal(word.word)).filter(Boolean);
  const duplicateCount = normalisedWords.length - new Set(normalisedWords).size;
  const count = fn => list.filter(fn).length;
  const sourceCounts = {};
  for (const word of list) {
    const source = clean(word.source) || 'Not recorded';
    sourceCounts[source] = (sourceCounts[source] || 0) + 1;
  }
  return {
    engineVersion: VOCAB_ENGINE_VERSION,
    indexed: list.length,
    uniqueNormalisedTerms: new Set(normalisedWords).size,
    duplicateNormalisedTerms: duplicateCount,
    dailySetCount: dailySets.length,
    dailyItemsDeclared: ids.length,
    dailyUniqueItems: coreIds.length,
    dailyMissingIds: ids.filter(id => !byId.has(id)),
    dailyDuplicateIds: ids.length - coreIds.length,
    dailyItemsPerSet: dailySets.map(set => (set.word_ids || []).length),
    dailyCoreComplete: coreWords.filter(complete).length,
    dailyCoreWithUsIpa: coreWords.filter(word => !!clean(word.ipa_us)).length,
    dailyCoreWithUkIpa: coreWords.filter(word => !!clean(word.ipa_uk)).length,
    dailyCoreWithBothIpa: coreWords.filter(dualIpa).length,
    dailyCoreMissingIpaIds: coreWords.filter(word => !dualIpa(word)).map(word => Number(word.id)),
    completeBilingualGlosses: count(complete),
    completeBilingualWithBothIpa: count(word => complete(word) && dualIpa(word)),
    usIpaFields: count(word => !!clean(word.ipa_us)),
    ukIpaFields: count(word => !!clean(word.ipa_uk)),
    dualIpaFields: count(dualIpa),
    partOfSpeechFields: count(word => !!clean(word.part_of_speech)),
    pronunciationOnlyEntries: count(word => word.translation_mode === 'pronunciation_index_only'),
    cefrNotAssessed: count(word => word.cefr_confidence === 'not_assessed' || word.cefr_level === 'Not assessed'),
    estimatedCefrEntries: count(word => word.cefr_confidence === 'estimated'),
    sourceCounts,
    coreFields: [...CORE_FIELDS]
  };
}

export function containsLexicalItem(sentence, term) {
  const haystack = normal(sentence);
  const needle = normal(term);
  if (!haystack || !needle) return false;
  const pattern = needle.split(/\s+/).map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('[\\s-]+');
  return new RegExp(`(^|[^a-z0-9])${pattern}(?=$|[^a-z0-9])`, 'i').test(haystack);
}

function dateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// SM-2-inspired local scheduler. Ratings are learner recall judgements, not objective language scores.
export function scheduleVocabularyReview(previous = {}, rating = 'good', now = new Date()) {
  const allowed = new Set(['again', 'hard', 'good', 'easy']);
  if (!allowed.has(rating)) throw new Error(`Unsupported SRS rating: ${rating}`);
  const item = { ...previous };
  const oldCount = Math.max(0, Number(item.count ?? item.repetitions) || 0);
  const oldInterval = Math.max(0, Number(item.intervalDays ?? item.interval) || 0);
  const ease = Math.max(1.3, Math.min(3.0, Number(item.ease) || 2.3));
  const quality = { again: 1, hard: 3, good: 4, easy: 5 }[rating];
  const delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02);
  item.ease = Math.max(1.3, Math.min(3.0, Math.round((ease + delta) * 100) / 100));
  item.lapses = Math.max(0, Number(item.lapses) || 0);

  let intervalDays;
  if (rating === 'again') {
    item.count = 0;
    item.lapses += 1;
    intervalDays = 0;
  } else if (rating === 'hard') {
    item.count = oldCount + 1;
    intervalDays = oldCount === 0 ? 1 : oldCount === 1 ? 4 : Math.max(1, Math.ceil(oldInterval * Math.max(1.3, item.ease * 0.8)));
  } else if (rating === 'easy') {
    item.count = oldCount + 1;
    intervalDays = oldCount === 0 ? 4 : oldCount === 1 ? 8 : Math.max(4, Math.ceil(oldInterval * item.ease * 1.3));
  } else {
    item.count = oldCount + 1;
    intervalDays = oldCount === 0 ? 1 : oldCount === 1 ? 6 : Math.max(1, Math.round(oldInterval * item.ease));
  }

  const reviewedAt = new Date(now);
  const dueDate = new Date(reviewedAt);
  dueDate.setDate(dueDate.getDate() + intervalDays);
  item.intervalDays = intervalDays;
  item.due = dateKey(dueDate);
  item.last = rating;
  item.lastReviewedAt = reviewedAt.toISOString();
  item.history = Array.isArray(item.history) ? item.history.slice(-19) : [];
  item.history.push({ rating, intervalDays, ease: item.ease, reviewedAt: reviewedAt.toISOString(), due: item.due });
  item.repetitions = item.count;
  return item;
}

export function validateDailyVocabularyCompletion(recallScore, transferHits, wordCount) {
  return Number(recallScore) >= 6 && Number(transferHits) >= 2 && Number(wordCount) >= 12;
}
