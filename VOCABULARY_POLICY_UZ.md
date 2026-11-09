# Vocabulary data coverage and policy — Stage 40

- Searchable index: 19,000 word records.
- IPA: first 4,000 cohort fields; further API lookups may add `ipa_api` for words in the 9,000 definition pool. Some phonetic values are derived or machine-generated and must be checked.
- Uzbek translations: first 4,000 cohort can be enriched by the resumable on-demand MyMemory batch queue. Coverage counter is computed from actual bundled/cache values.
- English definitions: first 9,000 can be enriched through Free Dictionary API, with phonetics and examples where available. Coverage counter is computed from actual bundled/cache values.
- Batch sizes: 10 or 20 successful results per user-triggered run, cursor saved locally. Rate limits, missing entries and network failures are surfaced and do not count as success.
- Translation is machine-generated and sense-sensitive. It is not labelled human-verified; users should review the source sense in a learner dictionary before SRS.
- Bundled complete offline glosses: computed from records containing English definition + Uzbek meaning + example + POS. This is the only count described as complete offline gloss.
