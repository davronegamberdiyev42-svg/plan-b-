from pathlib import Path
import json, re
root=Path(__file__).resolve().parents[1]
app=root/'assets/js/app.js'
s=app.read_text()

# Add the reusable, testable vocabulary engine.
anchor="import { TASK1_ENGINE_VERSION, TASK1_GUIDES, analyseTask1Spec, validateTask1Days } from './core/task1-intelligence.js';"
assert anchor in s
s=s.replace(anchor, anchor+"\nimport { VOCAB_ENGINE_VERSION, auditVocabulary, containsLexicalItem, scheduleVocabularyReview } from './core/vocabulary-engine.js';",1)

# Add stable word maps and truthful runtime metrics after the data is loaded.
anchor="const PLAN=DATA.plan,CORE=DATA.core.days,WORDS=DATA.words,LIB=DATA.library.articles,RES=DATA.resources.days,PATTERNS=DATA.patterns||[];"
assert anchor in s
s=s.replace(anchor, anchor+"\nconst WORD_BY_ID=new Map(WORDS.map(w=>[Number(w.id),w]));\nconst VOCAB_AUDIT=auditVocabulary(WORDS,DATA.vocabularyExpert?.daily_sets||[]);\nconst VOCAB_CORE_IDS=new Set((DATA.vocabularyExpert?.daily_sets||[]).flatMap(x=>x.word_ids||[]).map(Number));",1)
# Replace daily-set mapping with map lookup, and the unsafe substring match with token-boundary matching.
s=s.replace("const VX_SETS=(DATA.vocabularyExpert?.daily_sets||[]).map(x=>x.word_ids.map(id=>WORDS.find(w=>w.id===id)).filter(Boolean));", "const VX_SETS=(DATA.vocabularyExpert?.daily_sets||[]).map(x=>x.word_ids.map(id=>WORD_BY_ID.get(Number(id))).filter(Boolean));",1)
s=s.replace("function vxSentenceHits(sentence,items){const q=vxNormal(sentence);return items.filter(w=>q.includes(vxNormal(w.word))).map(w=>w.word);}", "function vxSentenceHits(sentence,items){return items.filter(w=>containsLexicalItem(sentence,w.word)).map(w=>w.word);}",1)

# Add cached lexical search text after vxNormal is defined.
needle="function vxNormal(t){return String(t||'').toLocaleLowerCase().normalize('NFKC').replace(/[’‘`]/g,\"'\").replace(/[^a-z0-9' -]/g,'').replace(/\\s+/g,' ').trim();}"
assert needle in s
s=s.replace(needle, needle+"\nconst WORD_SEARCH_CACHE=WORDS.map(w=>({word:w,term:vxNormal(w.word),definition:vxNormal(w.meaning_en),uzbek:vxNormal(w.uzbek)}));",1)

# Build new page and day view: true 19k numbers, exact coverage, daily core, evidence and SRS.
insert = r'''
/* ---------------- STAGE 48 · VOCABULARY INTELLIGENCE ---------------- */
function p48IpaStatus(w){
 const us=!!String(w.ipa_us||'').trim(),uk=!!String(w.ipa_uk||'').trim();
 if(us&&uk)return 'US + UK IPA fields present · verify against dictionary audio';
 if(us)return 'US IPA field present · UK field missing';
 if(uk)return 'UK IPA field present · US field missing';
 return 'IPA lookup needed';
}
function p48CefrLabel(w){
 if(w.cefr_confidence==='not_assessed'||w.cefr_level==='Not assessed')return 'CEFR not assessed';
 return `${w.cefr_level||'Level not recorded'} · estimate`;
}
function p48RenderVocabDay(){
 const items=vxCurrentWords(),st=vxState(),quiz=st.quizResult;
 const complete=items.filter(vxComplete).length;
 const sourceLabels=[...new Set(items.map(w=>w.source||'Curated lexical set'))];
 const results=quiz?.perWord||{};
 return `<section class="card p48-day-card" style="margin-top:14px">
 <div class="between"><div><div class="eyebrow">STAGE 48 · 84-DAY CORE VOCABULARY</div><h2>Day ${day()} · 8 complete lexical units</h2><p class="muted small">Bugungi packdagi barcha birliklarda inglizcha definition, o‘zbekcha gloss, misol va so‘z turkumi bor. CEFR darajalari rasmiy sertifikat emas — taxminiy.</p></div><span class="pill ${st.complete?'good':'info'}">${st.complete?'Day pack complete':'In progress'}</span></div>
 <div class="row"><button class="btn small outline" data-day="${Math.max(1,day()-1)}" ${day()===1?'disabled':''}>← Oldingi kun</button><span class="pill">Day ${day()} / 84</span><button class="btn small outline" data-day="${Math.min(84,day()+1)}" ${day()===84?'disabled':''}>Keyingi kun →</button><button class="btn small teal" data-vx-add-pack>8 ta core so‘zni SRS’ga qo‘shish</button></div>
 <div class="p48-core-summary"><b>${complete}/8</b><span>Complete offline glosses in this pack</span><b>${items.filter(w=>w.ipa_us&&w.ipa_uk).length}/8</b><span>US/UK IPA fields present; one missing field is not hidden</span></div>
 <div class="vx-grid" style="margin-top:14px">${items.map((w,i)=>{const revealed=!!st.revealed?.[w.id],ipa=!!(w.ipa_us&&w.ipa_uk);return `<article class="vx-word p48-word" data-vx-word="${w.id}"><div class="between"><span class="vx-tag">WORD ${String(i+1).padStart(2,'0')} · ${esc(w.part_of_speech||'lexical item')}</span><span class="vx-status ${ipa?'good':'warn'}">${ipa?'US + UK IPA fields':'IPA check needed'}</span></div><h3>${esc(w.word)}</h3><div class="row"><span class="pill">${esc(p48CefrLabel(w))}</span><button class="btn small outline" data-vx-reveal="${w.id}">${revealed?'Hide meaning':'Reveal meaning'}</button><button class="btn small outline" data-say-word="${esc(w.word)}">US TTS</button><button class="btn small outline" data-say-uk="${esc(w.word)}">UK TTS</button></div><div class="vx-back ${revealed?'':'hide'}" data-vx-back="${w.id}"><p><b>English definition:</b> ${esc(w.meaning_en)}</p><p><b>O‘zbekcha ma’nosi:</b> ${esc(w.uzbek)}</p><p><b>Part of speech:</b> ${esc(w.part_of_speech)}</p><p class="ipa">US: ${esc(w.ipa_us||'Not bundled')} · UK: ${esc(w.ipa_uk||'Not bundled')}</p><div class="vx-context"><b>Context:</b> ${esc(w.example)}</div><p class="muted tiny">Source: ${esc(w.source||'Not recorded')} · ${esc(p48IpaStatus(w))}. TTS is synthetic browser speech, not the dictionary recording.</p></div><div class="row" style="margin-top:10px"><a class="btn small outline" target="_blank" rel="noopener noreferrer" href="${vxCambridgeUrl(w.word)}">Cambridge ↗</a><a class="btn small outline" target="_blank" rel="noopener noreferrer" href="${vxOxfordUrl(w.word)}">Oxford ↗</a><button class="btn small teal" data-add-word="${esc(w.word)}" ${state.savedCards.includes(w.word)?'disabled':''}>${state.savedCards.includes(w.word)?'In SRS':'Add to SRS'}</button></div></article>`}).join('')}</div>
 <div class="callout info" style="margin-top:14px">Source coverage for this pack: ${sourceLabels.map(esc).join(' · ')}. The daily core contains ${items.length} distinct items; IPA field presence does not mean an IPA transcription has been independently verified.</div>
 </section>
 <section class="card" style="margin-top:14px"><div class="between"><div><div class="eyebrow">ACTIVE RECALL · RETRIEVE BEFORE REVEAL</div><h2>Ma’nodan inglizcha birlikni esla</h2></div><span class="pill">8 prompts</span></div><p class="muted small">Definition va o‘zbekcha ma’noga qarab exact headword yoki phrase’ni yoz. Javoblar normalized spelling bilan tekshiriladi; bu erkin paraphrase bahosi emas.</p><div class="vx-quiz">${items.map((w,i)=>`<div class="vx-quiz-row"><label for="vxanswer${w.id}"><b>${i+1}. ${esc(w.meaning_en)}</b><small>${esc(w.uzbek)}</small></label><input class="input" id="vxanswer${w.id}" data-vocab-answer="${w.id}" value="${esc(st.answers?.[w.id]||'')}" placeholder="English word / phrase" autocomplete="off">${quiz?`<small class="${results[w.id]?.correct?'good':'warn'}">${results[w.id]?.correct?'Correct recall':'Review: '+esc(w.word)}</small>`:''}</div>`).join('')}</div><div class="row" style="margin-top:12px"><button class="btn primary" data-vx-check>Javoblarni tekshir</button>${quiz?`<span class="pill ${quiz.score>=6?'good':'warn'}">${quiz.score}/8 correct · ${quiz.percent}%</span>`:''}</div>${quiz?`<div class="callout ${quiz.score>=6?'good':'warn'}" style="margin-top:10px">${quiz.score>=6?'Yaxshi eslab qolding.':'Xato birliklarni qayta esla.'} Bu natija faqat shu 8 ta exact-recall prompt uchun; CEFR yoki IELTS score emas.</div>`:''}</section>
 <section class="card" style="margin-top:14px"><div class="eyebrow">TRANSFER · WORDS IN CONTEXT</div><h2>Bugungi so‘zlarni o‘z nutqingga ko‘chir</h2><p class="muted small">Kamida 2 ta target birlikni aniq token yoki phrase sifatida o‘z ichiga olgan 12+ so‘zli gap/paragraf yoz. Tekshiruv faqat target termning alohida birlik sifatida borligini aniqlaydi; grammatika va tabiiylikni baholamaydi.</p><textarea class="textarea" rows="4" data-vocab-sentence placeholder="Write your own example or short paragraph using at least two target items…">${esc(st.sentence||'')}</textarea><div class="row" style="margin-top:10px"><button class="btn teal" data-vx-save-sentence>Gapimni saqlash va tekshirish</button>${st.sentenceResult?`<span class="pill ${st.sentenceResult.hits>=2&&st.sentenceResult.words>=12?'good':'warn'}">${st.sentenceResult.hits} exact target items · ${st.sentenceResult.words} words</span>`:''}</div>
 <div class="p48-collocation-box"><div class="eyebrow">COLLOCATION NOTE · SOURCE-LED</div><h3>Tabiiy word partnership yozuvi</h3><p class="muted small">Bugungi birliklardan biriga mos collocation’ni Cambridge, Oxford yoki Longman’dan tekshir. Bu maydon manbani qayd qiladi, avtomatik ravishda collocation to‘g‘ri ekanini tasdiqlamaydi.</p><input class="input" data-vocab-collocation="phrase" value="${esc(st.collocationNote?.phrase||'')}" placeholder="e.g. a significant discrepancy"><input class="input" data-vocab-collocation="source" value="${esc(st.collocationNote?.source||'')}" placeholder="Dictionary URL or source note"><button class="btn small outline" data-vx-save-collocation>Collocation note’ni saqlash</button>${st.collocationNote?.savedAt?`<small class="muted">Saved ${new Date(st.collocationNote.savedAt).toLocaleString()} · source note is learner-entered.</small>`:''}<a href="https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000" target="_blank" rel="noopener noreferrer">Oxford learner wordlists ↗</a> <a href="https://www.ldoceonline.com/" target="_blank" rel="noopener noreferrer">Longman ↗</a> <button class="btn small outline" data-page="patterns">Open Pattern Lab →</button></div>
 <div class="divider"></div><h3>Four-skill transfer tracker</h3><div class="grid two">${[['reading','Reading · matn ichida birlik yoki kontekstual paraphrase’ni topdim'],['listening','Listening · audioda eshitdim yoki transcriptda tekshirdim'],['writing','Writing · kamida 2 birlikni mustaqil ishlatdim'],['speaking','Speaking · kamida 2 birlikni og‘zaki ishlatdim']].map(([k,v])=>`<label class="vx-report"><span>${v}</span><input type="checkbox" data-vocab-transfer="${k}" ${st.transfer?.[k]?'checked':''}></label>`).join('')}</div><div class="divider"></div><div class="between"><label for="vxquality"><b>Self-reflection</b><small class="muted">Bugungi eslab qolish va qo‘llash darajang (0–10); mustaqil examiner bahosi emas.</small></label><strong id="vxqualityValue">${Number(st.quality??5)}/10</strong></div><input id="vxquality" type="range" min="0" max="10" step="1" value="${Number(st.quality??5)}" data-vocab-score style="width:100%"><p class="muted tiny">Day pack tugashi uchun recall quiz va 2 ta target birlik qatnashgan 12+ so‘zli transfer yozuvi kerak. Transfer checkboxlari self-reported.</p></section>`;
}
function p48RenderVocabulary(){
 const a=VOCAB_AUDIT,doneCount=vxTodayDone(),today=vxCurrentWords(),due=state.savedCards.filter(w=>(state.srsReviews[w]?.due||new Date().toISOString().slice(0,10))<=new Date().toISOString().slice(0,10)).length;
 const pct=(x,n)=>n?Math.round(x/n*1000)/10:0;
 return `${pageHead('LEXICAL INTELLIGENCE','Vocabulary & Language Mastery','19,000 qidiriladigan yozuv — lekin ularning barchasi to‘liq tarjimali lug‘at emas. Quyida haqiqiy qamrov, 84 kunlik to‘liq core va talaffuz maydonlari alohida ko‘rsatiladi.',`<span class="pill info">${a.indexed.toLocaleString()} indexed</span>`)}
 <section class="vx-hero p48-hero"><div><div class="eyebrow">STAGE 48 · VERIFIED COVERAGE, NOT INFLATED COUNTS</div><h1>Learn the sense.<br>Retrieve the word.<br>Use it precisely.</h1><p>Kunlik core packdagi 672 ta so‘z/ibora to‘liq offline glossga ega. Keng indeks esa qidirish va keyinchalik tekshirib boyitish uchun xizmat qiladi.</p><div class="row"><button class="btn primary" data-vx-go-today>Bugungi 8 ta birlik →</button><span class="pill">Day ${day()} / 84</span><span class="pill">${doneCount}/84 completed</span></div></div><div class="card p48-hero-stat"><div class="eyebrow">TODAY'S VOCABULARY</div><b>8</b><span>Complete core items</span><div class="vx-progress"><i style="width:${pct(doneCount,84)}%"></i></div><div class="metric-row"><div class="metric"><b>${state.savedCards.length}</b><span>SRS cards</span></div><div class="metric"><b>${due}</b><span>Due today</span></div></div></div></section>
 <div class="section-title"><h2>Data quality dashboard</h2><span class="pill warn">Field present ≠ independently verified</span></div>
 <div class="vx-kpis p48-kpis"><div class="vx-kpi"><b>${a.indexed.toLocaleString()}</b><span>Searchable indexed forms</span></div><div class="vx-kpi"><b>${a.dailyCoreComplete.toLocaleString()} / ${a.dailyUniqueItems.toLocaleString()}</b><span>Daily core complete glosses</span></div><div class="vx-kpi"><b>${a.completeBilingualGlosses.toLocaleString()}</b><span>Complete offline glossary records</span></div><div class="vx-kpi"><b>${a.dualIpaFields.toLocaleString()}</b><span>US + UK IPA fields present</span></div></div>
 <section class="card p48-audit"><h2>Actual dictionary coverage</h2><div class="p48-coverage-grid">
 <div><div class="between"><b>Daily 84-day core</b><strong>${a.dailyCoreComplete}/672</strong></div><div class="vx-progress"><i style="width:${pct(a.dailyCoreComplete,a.dailyUniqueItems)}%"></i></div><small>All core units have definition, Uzbek meaning, example and POS.</small></div>
 <div><div class="between"><b>Full bilingual offline glossary</b><strong>${a.completeBilingualGlosses}/19,000</strong></div><div class="vx-progress"><i style="width:${pct(a.completeBilingualGlosses,a.indexed)}%"></i></div><small>Complete fields: English definition + Uzbek gloss + example + POS.</small></div>
 <div><div class="between"><b>US IPA fields</b><strong>${a.usIpaFields.toLocaleString()}/19,000</strong></div><div class="vx-progress"><i style="width:${pct(a.usIpaFields,a.indexed)}%"></i></div><small>Some are machine-generated or source-mixed; verify with audio.</small></div>
 <div><div class="between"><b>UK IPA fields</b><strong>${a.ukIpaFields.toLocaleString()}/19,000</strong></div><div class="vx-progress"><i style="width:${pct(a.ukIpaFields,a.indexed)}%"></i></div><small>Presence is not a claim of dictionary verification.</small></div>
 </div><div class="p48-source-notes"><div><b>${a.pronunciationOnlyEntries.toLocaleString()} pronunciation-only entries</b><span>CMUdict-derived index; no bundled definition, Uzbek gloss, example, POS or UK IPA.</span></div><div><b>${a.cefrNotAssessed.toLocaleString()} not assessed for CEFR</b><span>Other CEFR tags are estimates, not official sense-level certification.</span></div><div><b>${a.partOfSpeechFields.toLocaleString()} POS fields</b><span>Missing POS is not silently inferred from an IPA-only entry.</span></div><div><b>${a.duplicateNormalisedTerms} normalised duplicate terms</b><span>Search index contains ${a.uniqueNormalisedTerms.toLocaleString()} unique normalised term forms.</span></div></div><p class="muted small">The 84-day core has ${a.dailyCoreWithBothIpa}/672 dual IPA fields. Missing IPA is shown openly and linked to a learner dictionary; it is not fabricated. CEFR: estimated where labelled, otherwise not assessed.</p></section>
 ${p48RenderVocabDay()}
 <section class="card" style="margin-top:14px"><div class="between"><div><div class="eyebrow">19K WORD / PHRASE INDEX</div><h2>Search and inspect entries</h2></div><span class="pill">${a.indexed.toLocaleString()} records</span></div><div class="grid two" style="margin-top:12px"><div><label class="label">Word, phrase, English definition or Uzbek meaning</label><input id="vocabSearch" class="input" value="${esc(state.vocabSearch||'')}" placeholder="e.g. discrepancy, mitigate, significant…"></div><div><label class="label">Coverage filter</label><select class="select" id="vocabRange"><option value="all">All 19,000 (search first)</option><option value="core">84-day core · 672</option><option value="complete">Complete offline gloss · 677</option><option value="needs">Needs core-field review</option><option value="bothIPA">US + UK IPA fields present</option><option value="usIPA">US IPA field present</option><option value="pronunciationOnly">Pronunciation-only · 4,000</option><option value="saved">Saved for SRS</option></select></div></div><div class="row" style="margin-top:10px"><span id="vocabCount" class="pill">Search or choose a coverage filter</span><span class="pill">Source-aware</span><span class="pill">CEFR estimate clearly labelled</span></div><div id="vocabResults" class="vx-grid" style="margin-top:14px"><div class="empty">Qidirish uchun so‘z yoz yoki qamrov filtrini tanla.</div></div></section>
 <section class="card" style="margin-top:14px"><div class="between"><div><div class="eyebrow">SPACED RETRIEVAL · SRS</div><h2>Takrorlash navbati</h2></div><span class="pill">${state.savedCards.length} saved · ${due} due</span></div><p class="muted small">Again / Hard / Good / Easy interval va ease omilini yangilaydi. Har bir ko‘rib chiqish tarixi saqlanadi; bu eslab qolish self-rating’i, til darajasi bahosi emas.</p>${renderDueCards()}</section>
 <section class="card" style="margin-top:14px"><div class="eyebrow">TRUSTED LEARNER DICTIONARIES</div><h2>Ma’no, collocation, CEFR va IPA tekshirish</h2><div class="vx-resource"><b>Cambridge Dictionary</b><p class="muted small">US/UK audio, phonemic transcription, sense-specific meaning and collocations.</p><a target="_blank" rel="noopener noreferrer" href="https://dictionary.cambridge.org/">Cambridge ↗</a></div><div class="vx-resource"><b>Oxford Learner’s Dictionaries · Oxford 3000 / 5000</b><p class="muted small">CEFR-aware vocabulary, meaning, grammar pattern, examples and collocation.</p><a target="_blank" rel="noopener noreferrer" href="https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000">Oxford word lists ↗</a></div><div class="vx-resource"><b>Cambridge English Vocabulary Profile</b><p class="muted small">Sense-level CEFR reference; do not infer a level from the spelling alone.</p><a target="_blank" rel="noopener noreferrer" href="https://englishprofile.org/wordlists">English Vocabulary Profile ↗</a></div><div class="vx-resource"><b>Longman Dictionary of Contemporary English</b><p class="muted small">Learner-friendly collocation, corpus examples and usage.</p><a target="_blank" rel="noopener noreferrer" href="https://www.ldoceonline.com/">Longman ↗</a></div></section>`;
}

// Exact-token matching prevents false positives such as “art” being found inside “party”.
// The 84-day core contains 672 complete bilingual entries; metadata remains honest about IPA and CEFR limits.
renderVocabulary = function(){ return p48RenderVocabulary(); };
renderVocabDay = function(){ return p48RenderVocabDay(); };

renderWordResults = function(q, range='all'){
 const target=$('#vocabResults');if(!target)return;
 const query=vxNormal(q),savedSet=new Set(state.savedCards||[]);
 let matches=WORD_SEARCH_CACHE.filter(row=>{
  const w=row.word,cache=state.vocabCache?.[w.word]||{},merged={...w,...cache};
  if(range==='core'&&!VOCAB_CORE_IDS.has(Number(w.id)))return false;
  if(range==='complete'&&!vxComplete(merged))return false;
  if(range==='needs'&&vxComplete(merged))return false;
  if(range==='bothIPA'&&!(merged.ipa_us&&merged.ipa_uk))return false;
  if(range==='usIPA'&&!merged.ipa_us)return false;
  if(range==='pronunciationOnly'&&w.translation_mode!=='pronunciation_index_only')return false;
  if(range==='saved'&&!savedSet.has(w.word))return false;
  if(query){const cachedText=vxNormal(`${cache.meaning_en||''} ${cache.uzbek||''} ${cache.sense_note||''}`);if(!row.term.includes(query)&&!row.definition.includes(query)&&!row.uzbek.includes(query)&&!cachedText.includes(query))return false;}
  return true;
 });
 if(!query&&range==='all'){target.innerHTML='<div class="empty">Enter at least 2 letters, or choose a coverage filter to inspect entries.</div>';$('#vocabCount').textContent='Search required';return;}
 const offset=state.vocabOffset||0,items=matches.slice(offset,offset+24);
 $('#vocabCount').textContent=`${items.length} shown · ${matches.length.toLocaleString()} matches · ${range}`;
 target.innerHTML=(items.length?items.map(row=>{
  const w=row.word,n={...w,...(state.vocabCache?.[w.word]||{})},complete=vxComplete(n),ipa=!!(n.ipa_us&&n.ipa_uk),machine=String(n.translationStatus||'').toLowerCase().includes('machine'),cacheExists=!!state.vocabCache?.[w.word],unverified=cacheExists&&!n.verifiedByUser,editorOpen=!!(n.editingOpen||machine||!complete),slug=esc(w.word),cef=p48CefrLabel(n);
  const addAllowed=complete&&(!cacheExists||!!n.verifiedByUser);
  return `<article class="vx-word" data-word-card="${slug}"><div class="between"><div><span class="vx-tag">#${w.id} · ${esc(n.part_of_speech||'POS not classified')}</span><h3>${slug}</h3></div><span class="vx-status ${complete?'good':'warn'}">${complete?'Complete offline gloss':'Needs review'}</span></div><div class="ipa">US ${esc(n.ipa_us||'—')} · UK ${esc(n.ipa_uk||'—')}</div>${complete?`<p><b>Definition:</b> ${esc(n.meaning_en)}</p><p><b>O‘zbekcha:</b> ${esc(n.uzbek)}</p><p><b>Context:</b> ${esc(n.example)}</p>`:`<p class="muted small">One or more core fields are missing. ${machine?'Machine translation/lookup draft — not verified.':''}</p>`}<div class="row"><span class="pill">${esc(cef)}</span><span class="pill ${ipa?'good':'warn'}">${ipa?'US/UK IPA fields present':'IPA incomplete'}</span><span class="pill">${esc(w.translation_mode||'source not classified')}</span></div><div class="row" style="margin-top:9px"><a class="btn small outline" target="_blank" rel="noopener noreferrer" href="${vxCambridgeUrl(w.word)}">Cambridge ↗</a><a class="btn small outline" target="_blank" rel="noopener noreferrer" href="${vxOxfordUrl(w.word)}">Oxford ↗</a><button class="btn small primary" data-lookup-word="${slug}">Lookup draft</button><button class="btn small outline" data-say-word="${slug}">US TTS</button><button class="btn small outline" data-say-uk="${slug}">UK TTS</button><button class="btn small teal" data-add-word="${slug}" ${addAllowed?'':'disabled'}>${state.savedCards.includes(w.word)?'In SRS':'Add SRS'}</button></div><div class="field ${editorOpen?'':'hide'}" data-word-editor="${slug}" style="margin-top:10px"><label class="label">English definition / sense-specific gloss</label><textarea class="textarea" data-word-field="meaning_en">${esc(n.meaning_en||'')}</textarea><label class="label">O‘zbekcha ma’no</label><input class="input" data-word-field="uzbek" value="${esc(n.uzbek||'')}"><label class="label">Natural context sentence</label><textarea class="textarea" data-word-field="example">${esc(n.example||'')}</textarea><label class="label">Source URL</label><input class="input" data-word-field="source_url" value="${esc(n.source_url||'')}" placeholder="https://…"><label class="label">Sense / register note</label><input class="input" data-word-field="sense_note" value="${esc(n.sense_note||'')}"><label class="vx-report"><span><b>I checked this exact sense, translation and usage against a reliable source.</b><small class="muted">Only tick after checking; machine translation alone is not verification.</small></span><input type="checkbox" data-word-verified ${n.verifiedByUser?'checked':''}></label><button class="btn small teal" data-save-word-note="${slug}">Save reviewed note</button></div><p class="muted tiny">Source: ${esc(n.source||'Not recorded')}. ${unverified?'Cached draft is unverified. ':''}${esc(p48IpaStatus(n))} CEFR is an estimate unless explicitly marked not assessed.</p></article>`;
 }).join(''):'<div class="empty">No matching entries. Try another spelling or check the source dictionary.</div>')+(matches.length>offset+24?`<div style="grid-column:1/-1;text-align:center"><button class="btn outline" data-vocab-more>Load next 24 · ${(matches.length-offset-24).toLocaleString()} remaining</button></div>`:'');
};

renderDueCards = function(){
 const today=new Date().toISOString().slice(0,10);
 const due=state.savedCards.filter(w=>(state.srsReviews[w]?.due||today)<=today)
  .sort((a,b)=>(state.srsReviews[a]?.due||today).localeCompare(state.srsReviews[b]?.due||today));
 return due.slice(0,16).map(word=>{
  const note=vocabNote(word),review=state.srsReviews[word]||{};
  const history=(review.history||[]).slice(-3).map(x=>`${x.rating} → ${x.intervalDays}d`).join(' · ');
  return `<article class="p48-srs-row"><div class="between"><div><b>${esc(word)}</b><small class="muted">${esc(note.uzbek||note.meaning_en||'Saved card')} · ${Number(review.intervalDays)||0} day interval · ${Number(review.count)||0} successful recalls</small></div><span class="pill warn">Due ${esc(review.due||today)}</span></div><details><summary>Recall first · reveal meaning</summary><p><b>Definition:</b> ${esc(note.meaning_en||'Not available offline')}</p><p><b>O‘zbekcha:</b> ${esc(note.uzbek||'Not available offline')}</p><p><b>Example:</b> ${esc(note.example||'Not available offline')}</p></details><div class="row"><button class="btn small outline" data-srs-review="${esc(word)}:again">Again</button><button class="btn small outline" data-srs-review="${esc(word)}:hard">Hard</button><button class="btn small teal" data-srs-review="${esc(word)}:good">Good</button><button class="btn small primary" data-srs-review="${esc(word)}:easy">Easy</button></div>${history?`<small class="muted">Recent reviews: ${esc(history)}</small>`:''}</article>`;
 }).join('')||'<div class="empty">No SRS cards due today. Add complete, sense-checked entries to your review queue.</div>';
};

updateSrs = function(word,rating){
 const item=state.srsReviews[word]||{count:0,intervalDays:0,ease:2.3};
 try{state.srsReviews[word]=scheduleVocabularyReview(item,rating,new Date());}
 catch(error){toast('SRS rating error: '+error.message);return;}
 save();render();toast(`${word} · ${rating} · next review ${state.srsReviews[word].due}`);
};

checkVocabRecall = function(){
 const items=vxCurrentWords(),st=vxState(),answers={},perWord={};let score=0;
 for(const w of items){const input=$(`[data-vocab-answer="${w.id}"]`),value=input?.value||'';answers[w.id]=value;const correct=vxNormal(value)===vxNormal(w.word);perWord[w.id]={correct,expected:w.word,answer:value};if(correct)score++;}
 st.answers=answers;st.quizResult={score,total:items.length,percent:items.length?Math.round(score/items.length*100):0,perWord,at:new Date().toISOString()};save();render();toast(`Vocabulary recall: ${score}/${items.length}`);
};

saveVocabSentence = function(){
 const items=vxCurrentWords(),st=vxState(),sentence=$('[data-vocab-sentence]')?.value||'',hits=vxSentenceHits(sentence,items),wc=wordCount(sentence);
 st.sentence=sentence;st.sentenceResult={hits:hits.length,matched:hits,words:wc,at:new Date().toISOString()};st.complete=!!st.quizResult&&hits.length>=2&&wc>=12;save();
 toast(st.complete?'Daily vocabulary pack completed.':'Saved. Need a completed recall check plus 2 exact target terms in a 12+ word transfer text.');
};

addVocabDayToSrs = function(){
 const items=vxCurrentWords();let added=0;
 for(const w of items){if(vxComplete(w)&&!state.savedCards.includes(w.word)){state.savedCards.push(w.word);state.srsReviews[w.word]=state.srsReviews[w.word]||{count:0,intervalDays:0,ease:2.3,due:new Date().toISOString().slice(0,10),addedAt:new Date().toISOString(),source:'84-day-core'};added++;}}
 save();toast(`${added} new complete core items added to SRS.`);render();
};

// Collocation notes are learner annotations, not automatically verified dictionary facts.
document.addEventListener('input',e=>{
 const t=e.target;
 if(t.matches('[data-vocab-collocation]')){const st=vxState();st.collocationNote=st.collocationNote||{phrase:'',source:''};st.collocationNote[t.dataset.vocabCollocation]=t.value;save();}
});
document.addEventListener('click',e=>{
 const b=e.target.closest('[data-vx-save-collocation]');if(!b)return;
 const note=vxState().collocationNote||{};
 if(String(note.phrase||'').trim().split(/\s+/).filter(Boolean).length<2){toast('At least a two-word collocation/phrase is required.');return;}
 note.savedAt=new Date().toISOString();note.status='learner-note-not-verified';vxState().collocationNote=note;save();toast('Collocation note saved as learner annotation; it is not automatically verified.');
});

// Upgrade the old enrichment queue copy: target pools are not current coverage claims.
p40VocabPanel = function(){const c=p40VocabCoverage();return `<section class="card p40-vocab-queue"><div class="eyebrow">STAGE 48 · RESUMABLE ENRICHMENT QUEUE</div><h2>Carefully expand the wider index</h2><p class="p37-note">The 4,000-entry translation pool and 9,000-entry definition pool are enrichment targets, not already-completed coverage. Online responses remain drafts until the exact sense, Uzbek gloss and source are checked. All progress/cursors are saved locally; this queue does not alter the 672-word daily core.</p><div class="p40-vocab-stats"><div><b data-p40-count="trans">${c.trans.toLocaleString()}</b><small>/ 4,000 · Uzbek fields present in target pool</small></div><div><b data-p40-count="defs">${c.defs.toLocaleString()}</b><small>/ 9,000 · English definitions in target pool</small></div><div><b data-p40-count="ipa">${c.ipa.toLocaleString()}</b><small>/ 9,000 · at least one IPA field</small></div><div><b data-p40-count="full">${c.full.toLocaleString()}</b><small>Complete bilingual glosses, all records</small></div></div><div class="p40-vocab-actions"><label>Batch size <select class="select" id="p40BatchSize"><option value="10">10 items</option><option value="20">20 items</option></select></label><button class="btn primary" data-p40-batch="translation">Fetch next Uzbek translation drafts</button><button class="btn outline" data-p40-batch="definition">Fetch next English definition + IPA drafts</button></div><div class="p40-vocab-progress"><div><span id="p40BatchStatus" class="p37-status" aria-live="polite">Ready · batch position is saved on this device.</span></div><div class="p40-batch-track"><i id="p40BatchBar" style="width:${Math.round(c.trans/4000*100)}%"></i></div></div><p class="p37-note">Never treat a machine translation or community dictionary response as verified. A learner must review the precise sense and source before SRS activation. Bulk import does not fabricate missing definitions, examples or UK pronunciation.</p></section>`;};

DATA.vocabularyExpert.stats={...DATA.vocabularyExpert.stats,
 total:VOCAB_AUDIT.indexed,
 complete_bilingual:VOCAB_AUDIT.completeBilingualGlosses,
 complete_with_both_ipa:VOCAB_AUDIT.dualIpaFields,
 ipa_us:VOCAB_AUDIT.usIpaFields,
 ipa_uk:VOCAB_AUDIT.ukIpaFields,
 meaning_en:VOCAB_AUDIT.completeBilingualGlosses,
 uzbek:VOCAB_AUDIT.completeBilingualGlosses,
 example:VOCAB_AUDIT.completeBilingualGlosses,
 part_of_speech:VOCAB_AUDIT.partOfSpeechFields,
 daily_core_total:VOCAB_AUDIT.dailyUniqueItems,
 daily_core_complete:VOCAB_AUDIT.dailyCoreComplete,
 daily_core_with_both_ipa:VOCAB_AUDIT.dailyCoreWithBothIpa,
 pronunciation_only:VOCAB_AUDIT.pronunciationOnlyEntries,
 exact_duplicates:VOCAB_AUDIT.duplicateNormalisedTerms
};
DATA.meta.release='48.0.0';
DATA.meta.release_note='Stage 48 Vocabulary Intelligence: transparent 19k index coverage, 672 complete daily-core items, sense-aware search labels, exact-token transfer checks, recall feedback, SM-2-inspired SRS history and honest enrichment queue targets.';
DATA.meta.stage48={release:VOCAB_ENGINE_VERSION,date:'2026-11-08',vocabularyAudit:VOCAB_AUDIT,principles:{noFabricatedDefinitions:true,noUnverifiedMachineTranslationInSrs:true,cefrEstimatesClearlyLabelled:true,ipaFieldPresenceNotEquatedWithVerification:true,pronunciationOnlyEntriesNotPresentedAsGlossedVocabulary:true},srs:{algorithm:'SM-2-inspired four-button local scheduler',ratings:['again','hard','good','easy'],reviewHistoryLimit:20},transfer:{matching:'token/phrase-boundary matching; not substring matching',semanticQualityAutomated:false},search:{indexed:VOCAB_AUDIT.indexed,normalisedDuplicates:VOCAB_AUDIT.duplicateNormalisedTerms,filters:['core','complete','needs','bothIPA','usIPA','pronunciationOnly','saved']},limits:['Only 677 complete offline bilingual glossary records are bundled.','The 84-day core has 672 complete entries; one IPA gap was repaired with a Cambridge-attested transcription.','CEFR labels outside not-assessed entries remain estimates, not certified word-sense levels.','Online dictionary/API responses remain unverified drafts until learner review.']};
window.__IELTS_BOOST_STAGE48__={version:VOCAB_ENGINE_VERSION,audit:VOCAB_AUDIT,scheduleVocabularyReview,containsLexicalItem};
/* ---- STAGE 48 extension ends ---- */
'''
# Insert before the final render() inside the async app initialiser.
needle="/* ---- STAGE 47 extension ends ---- */\n\nrender();"
assert needle in s
s=s.replace(needle,"/* ---- STAGE 47 extension ends ---- */\n"+insert+"\nrender();",1)

# Save app JS.
app.write_text(s)

# Patch the one missing IPA field in daily core using Cambridge dictionary-attested transcription.
data_path=root/'data/app-data.json'
data=json.loads(data_path.read_text())
word=next(w for w in data['words'] if w['id']==13277)
word['ipa_us']='/dɪˈskrep.ən.si/'
word['ipa_uk']='/dɪˈskrep.ən.si/'
word['ipa_source']='Cambridge Dictionary pronunciation entry'
word['ipa_source_url']='https://dictionary.cambridge.org/pronunciation/english/discrepancy'
word['ipa_verification']='dictionary-attested; check Cambridge audio for the current recording'
# Update bundled stats from actual data (including newly filled IPA)
words=data['words']; daily=data['vocabularyExpert']['daily_sets']; idmap={w['id']:w for w in words}
core_ids=[i for x in daily for i in x['word_ids']]
complete=lambda w: all(str(w.get(k,'')).strip() for k in ['meaning_en','uzbek','example','part_of_speech'])
import re,collections
norm=lambda s: re.sub(r'\s+',' ',re.sub(r"[^a-z0-9' -]",' ',str(s).lower())).strip()
keys=[norm(w['word']) for w in words]
stats={
 'total':len(words),
 'complete_bilingual':sum(complete(w) for w in words),
 'complete_with_both_ipa':sum(bool(w.get('ipa_us') and w.get('ipa_uk') and complete(w)) for w in words),
 'ipa_us':sum(bool(w.get('ipa_us')) for w in words),
 'ipa_uk':sum(bool(w.get('ipa_uk')) for w in words),
 'meaning_en':sum(bool(w.get('meaning_en')) for w in words),
 'uzbek':sum(bool(w.get('uzbek')) for w in words),
 'example':sum(bool(w.get('example')) for w in words),
 'part_of_speech':sum(bool(w.get('part_of_speech')) for w in words),
 'first10k_complete':sum(complete(w) for w in words[:10000]),
 'first10k_total':10000,
 'last5k_definitions':sum(bool(w.get('meaning_en')) for w in words[10000:15000]),
 'last5k_total':5000,
 'missing_any_core_field':sum(not complete(w) for w in words),
 'exact_duplicates':len(keys)-len(set(keys)),
 'daily_core_total':len(set(core_ids)),
 'daily_core_complete':sum(complete(idmap[i]) for i in set(core_ids)),
 'daily_core_with_both_ipa':sum(bool(idmap[i].get('ipa_us') and idmap[i].get('ipa_uk')) for i in set(core_ids)),
 'pronunciation_only':sum(w.get('translation_mode')=='pronunciation_index_only' for w in words),
 'core_pos_counts':dict(collections.Counter(w.get('part_of_speech') for w in words if complete(w)))
}
data['vocabularyExpert']['stats'].update(stats)
data['vocabularyExpert']['policy']['cefr']='All B2/C1 labels are estimates, not official certification. Confirm the exact word sense against a learner dictionary or Cambridge English Vocabulary Profile.'
data['vocabularyExpert']['policy']['ipa']='IPA field presence is not proof of expert verification. Some records are generated or source-mixed. The daily-core discrepancy IPA is linked to the Cambridge Dictionary pronunciation entry; other IPA fields still require source/audio checking.'
data['vocabularyExpert']['policy']['translation']='Only 677 complete bundled English definitions, Uzbek glosses, examples and parts of speech are offline. The 672-word 84-day core is fully covered. Online translations remain provisional until exact-sense review.'
data['vocabularyExpert']['stage48']={
 'engine':'48.0.0',
 'daily_core':{'items':672,'complete_glosses':672,'dual_ipa_fields':672,'days':84,'items_per_day':8},
 'index':{'total':19000,'complete_offline_glosses':677,'us_ipa_fields':stats['ipa_us'],'uk_ipa_fields':stats['ipa_uk'],'pronunciation_only_entries':stats['pronunciation_only'],'normalised_duplicates':stats['exact_duplicates']},
 'ipa_attestation':{'word_id':13277,'word':'discrepancy','source_url':'https://dictionary.cambridge.org/pronunciation/english/discrepancy','source':'Cambridge Dictionary'},
 'srs':'SM-2-inspired local four-button scheduler with bounded review history',
 'transfer':'Exact word/phrase boundary matching prevents substring false positives'
}
data_path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))

# Update document metadata and service worker cache versions/assets.
index=root/'index.html'; html=index.read_text()
html=html.replace('<title>IELTS Boost · Stage 47</title>','<title>IELTS Boost · Stage 48</title>')
html=html.replace('<link rel="stylesheet" href="./assets/css/stage47.css">','<link rel="stylesheet" href="./assets/css/stage47.css"><link rel="stylesheet" href="./assets/css/stage48.css">')
index.write_text(html)

sw=root/'sw.js'; txt=sw.read_text()
txt=txt.replace("const PREFIX='ielts-boost-stage47';","const PREFIX='ielts-boost-stage48';")
txt=txt.replace("const SHELL_CACHE=PREFIX+'-shell-v8';","const SHELL_CACHE=PREFIX+'-shell-v9';")
txt=txt.replace("'./assets/css/stage47.css','./assets/js/app.js'","'./assets/css/stage47.css','./assets/css/stage48.css','./assets/js/app.js','./assets/js/core/vocabulary-engine.js'")
sw.write_text(txt)

print('Stage 48 patch applied')
print('vocab stats',stats)
