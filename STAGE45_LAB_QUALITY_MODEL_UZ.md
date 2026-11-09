# Stage 45 — Laboratory Quality Model

## 1. Why the scoring labels changed

The previous P37 laboratory engine awards an internal `/10` score for several combinations of word count, checkboxes, answer selection and reflection fields. Those signals can help confirm that a learner completed a practice workflow, but they do not establish whether a free-response essay is coherent, a paraphrase preserves its meaning, speech is fluent, or pronunciation is intelligible.

Stage 45 keeps the previous practice index and XP history. It no longer treats those values as verified skill mastery.

## 2. Outcome types

| Type | Source | Eligible for objective accuracy? |
|---|---|---|
| `objective` | Known item answer key | Yes |
| `process` | Completion / required evidence | No |
| `self_review` | Learner criterion reflection | No |
| `transfer` | Fresh follow-up challenge | Reported separately from core objective samples |

### Current lab classification

- Answer-key objective: Reading, Listening, Collocations, Grammar.
- Process/self-review: Writing, Speaking, Pronunciation, Paraphrase, Vocabulary, Fluency.

## 3. Objective sample rules

1. Only rows with `kind === 'objective'` and boolean `correct` are included.
2. Each prompt has an `itemKey`. Duplicate attempts on the same key are collapsed to the latest recorded outcome.
3. Accuracy is calculated over the latest five distinct objective prompts.
4. Fewer than three distinct prompts means `Dalil yetarli emas` and no accuracy percentage is promoted as mastery.
5. At 3+ distinct prompts: below 60% suggests priority repair; 60–79.9% suggests developing; 80%+ is a promising sample signal, not a global IELTS proficiency claim.
6. A weakest mode can only be selected from answer-key-backed attempts.

## 4. Transfer rules

Each lab's optional transfer uses a fresh source/question from the next study day. Day 84 uses a different cumulative item from Day 84 rather than wrapping the core plan back to Day 1.

| Lab | Required evidence | Guardrail |
|---|---|---|
| Reading | Answer, exact quote, reasoning; wrong answer includes cause + repair | Quote must occur in fresh passage |
| Listening | Full audio playback, answer, heard phrase; wrong answer includes cause + repair | Audio ended event required and phrase checked against script |
| Writing | 35+ word thesis/plan and prompt coverage note | No automatic essay quality score |
| Speaking | 35+ word response/transcript and timestamp/quote reflection | Transcript count is not fluency or pronunciation |
| Collocations | Answer key, 10+ word new sentence, wrong-answer repair | Free sentence naturalness not auto-certified |
| Pronunciation | 3+ self-checks and timestamped target | IPA/TTS is a practice prompt, not an acoustic score |
| Paraphrase | 15+ word rewrite, meaning/scope/certainty checks, explanation | Checkboxes do not prove equivalence |
| Grammar | Answer key, rule explanation, 8+ word new sentence | Correct selection does not certify general accuracy |
| Vocabulary | 5+ word recall and new-context use | No token-overlap score used as exact sense proof |
| Fluency | Claim, reason, example and qualification | Written structure is not spoken fluency |

Wrong objective answers require an error cause and a repair plan. Current cause labels include task focus, evidence, paraphrase, distractor, detail, grammar, collocation, meaning, pronunciation, vocabulary and organisation.

## 5. Adaptive guidance

The current adaptive element recommends a lab/mode only when sufficient distinct answer-key results exist. It does not use word count, XP, checklist completion or self-rating to declare objective accuracy. Open-response labs remain eligible for future criterion review, but not for a fabricated automatic grade.

## 6. Internal scale vs IELTS band

The internal `/10` practice index is a learning-workflow metric. It is not an official IELTS band, CEFR certification or examiner score. Future AI assistance must store the model/source, criterion-by-criterion evidence and confidence, and it must be clearly labelled as AI-assisted rather than examiner verified.
