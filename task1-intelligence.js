/* IELTS Boost Stage 47 — Task 1 Visual Intelligence Engine
 * Deterministic inspection and teaching guidance for original IELTS Boost datasets.
 * It does not assign an IELTS band or claim semantic marking of learner writing.
 */
export const TASK1_ENGINE_VERSION = '47.0.0';

export const TASK1_GUIDES = {
  line_graph: {
    name: 'Line graph',
    purpose: 'Compare change over time. The overview should describe the broad direction and the most important contrast, not list every point.',
    structure: ['Introduction: paraphrase what changed, for whom and over which period.', 'Overview: summarise the main direction, peak/trough or contrast between series.', 'Body 1: group the first meaningful movement or one series.', 'Body 2: explain the remaining movement and compare the end points.'],
    focus: ['Start and end values', 'Overall direction and fluctuations', 'Highest and lowest points', 'Largest rise/fall and turning points', 'Whether the two series move together or diverge'],
    language: ['rose / increased / climbed', 'fell / declined / dropped', 'fluctuated / remained stable', 'peaked at / reached a low of', 'ended at / stood at / compared with'],
    traps: ['Do not describe every data point in sequence.', 'Do not call a fluctuating line a steady rise.', 'Do not confuse the absolute difference with a percentage change.', 'Keep past-tense reporting consistent when the time period is historical.']
  },
  bar_chart: {
    name: 'Bar chart',
    purpose: 'Compare quantities across categories, groups or time points. Select the most informative comparisons rather than describing each bar separately.',
    structure: ['Introduction: identify the categories and what is measured.', 'Overview: state the largest/smallest group and one broad contrast.', 'Body 1: compare the leading or similar categories.', 'Body 2: compare the remaining categories and notable gaps.'],
    focus: ['Highest and lowest bars across all series', 'Largest gap within a category', 'Categories where the ranking changes', 'Similar values that can be grouped', 'Units and whether the scale starts at zero'],
    language: ['recorded / accounted for', 'was higher/lower than', 'exceeded / was below', 'by a margin of', 'roughly twice as high as'],
    traps: ['Do not compare values with different units as if they were identical.', 'Do not use “twice” unless the ratio supports it.', 'Do not turn fictional practice data into real-world claims.', 'Do not confuse a category label with a time period.']
  },
  pie_chart: {
    name: 'Pie chart',
    purpose: 'Describe how a whole is divided. Focus on the largest and smallest shares and meaningful groupings.',
    structure: ['Introduction: paraphrase the subject and identify the whole.', 'Overview: identify the dominant and smallest shares or the broad distribution.', 'Body 1: report the largest shares and compare them.', 'Body 2: describe the smaller shares and key percentage-point gaps.'],
    focus: ['Largest and smallest proportions', 'Whether one category dominates', 'Combined shares of meaningful groups', 'Percentage-point differences', 'Whether totals form 100%'],
    language: ['accounted for / represented', 'made up / comprised', 'just over / just under', 'approximately one third', 'the share was higher/lower by … percentage points'],
    traps: ['Do not confuse percent with percentage points.', 'Do not claim a category increased if only one pie is shown.', 'Do not assume the total is 100 if the displayed values do not sum to 100.', 'Avoid reporting all slices mechanically.']
  },
  table: {
    name: 'Table',
    purpose: 'Find patterns in structured figures. Group rows or columns by meaningful similarities and differences.',
    structure: ['Introduction: explain what the table compares.', 'Overview: state the clearest high/low pattern or broad contrast.', 'Body 1: group the strongest or similar figures.', 'Body 2: report the remaining comparison and useful exceptions.'],
    focus: ['Highest and lowest cells', 'Row/column patterns', 'Largest within-row or within-column gap', 'Similar values worth grouping', 'Units, headings and footnotes'],
    language: ['the highest figure was recorded for', 'stood at / amounted to', 'was marginally / substantially higher', 'the corresponding figure', 'in contrast / respectively'],
    traps: ['Do not read the table cell by cell.', 'Do not forget to identify what each row and column represents.', 'Do not compare mismatched units.', 'Use “respectively” only when the order is unambiguous.']
  },
  process: {
    name: 'Process diagram',
    purpose: 'Explain how something is produced or how a system works. The sequence and stages matter more than comparisons.',
    structure: ['Introduction: paraphrase what the process illustrates.', 'Overview: state the number of broad stages and the starting and ending points.', 'Body 1: describe the opening stages in order.', 'Body 2: describe the later stages and final output.'],
    focus: ['Starting input and final output', 'Number and order of stages', 'Actions versus materials', 'Human involvement, if shown', 'Whether the process is linear or cyclical'],
    language: ['initially / first / subsequently', 'is collected / is transferred', 'is then processed', 'following this stage', 'finally / the finished product'],
    traps: ['Do not invent a reason or purpose not shown.', 'Use passive voice where the actor is unknown or irrelevant.', 'Do not omit a stage.', 'Do not describe a linear process as cyclical.']
  },
  map: {
    name: 'Maps / plans',
    purpose: 'Compare a place at two times or in two plans. Describe the main changes and retained features with spatial accuracy.',
    structure: ['Introduction: identify the place and the two time points/plans.', 'Overview: summarise the scale and nature of the main redevelopment.', 'Body 1: describe major additions, removals or relocations.', 'Body 2: describe retained, expanded or reorganised features.'],
    focus: ['North arrow and orientation', 'Added and removed features', 'Relocation and expansion', 'Features that remained unchanged', 'Relative position (north/south/near/between)'],
    language: ['was replaced by', 'was converted into', 'was relocated to', 'was extended / expanded', 'remained unchanged / was retained'],
    traps: ['Do not invent compass direction or distance.', 'Do not say “north” unless the map has a north arrow.', 'Do not claim a feature was removed if it was only renamed.', 'Do not infer scale from a schematic illustration.']
  }
};

const n = v => Number(v);
const fmt = v => Number.isInteger(v) ? String(v) : String(Math.round(v * 10) / 10);
const direction = d => d > 0 ? 'increased overall' : d < 0 ? 'decreased overall' : 'was unchanged overall';

export function analyseTask1Spec(spec = {}) {
  const type = spec.type || 'line_graph';
  const labels = Array.isArray(spec.labels) ? spec.labels : [];
  const series = Array.isArray(spec.series) && spec.series.length
    ? spec.series.map(s => ({ name: s.name || 'Series', values: (s.values || []).map(n) }))
    : (Array.isArray(spec.values) ? [{ name: spec.series_label || 'Main group', values: spec.values.map(n) }] : []);
  const all = series.flatMap(s => s.values).filter(Number.isFinite);
  const guide = TASK1_GUIDES[type] || TASK1_GUIDES.line_graph;
  let facts = [], overview = '', quality = { valid: true, issues: [] };

  if (['line_graph', 'bar_chart', 'table'].includes(type)) {
    if (labels.length < 2) quality.issues.push('At least two categories or time points are required.');
    if (!series.length) quality.issues.push('No numerical series was found.');
    for (const s of series) if (s.values.length !== labels.length || s.values.some(v => !Number.isFinite(v))) quality.issues.push(`Series “${s.name}” does not align with all labels.`);
    if (all.length) {
      const entries = [];
      for (const s of series) s.values.forEach((v, i) => entries.push({ value: v, label: labels[i] || `Item ${i + 1}`, series: s.name }));
      const hi = entries.reduce((a, b) => !a || b.value > a.value ? b : a, null);
      const lo = entries.reduce((a, b) => !a || b.value < a.value ? b : a, null);
      facts.push(`Highest figure: ${hi.value} (${hi.series}, ${hi.label}).`, `Lowest figure: ${lo.value} (${lo.series}, ${lo.label}).`, `Overall range: ${fmt(hi.value - lo.value)} ${spec.unit || 'units'}.`);
      if (type === 'line_graph') {
        const changes = series.map(s => ({ name: s.name, start: s.values[0], end: s.values.at(-1), delta: s.values.at(-1) - s.values[0], peak: Math.max(...s.values), peakAt: labels[s.values.indexOf(Math.max(...s.values))], low: Math.min(...s.values), lowAt: labels[s.values.indexOf(Math.min(...s.values))] }));
        changes.forEach(c => facts.push(`${c.name}: ${direction(c.delta)} (${fmt(c.start)} → ${fmt(c.end)}); peak ${fmt(c.peak)} at ${c.peakAt}; low ${fmt(c.low)} at ${c.lowAt}.`));
        overview = changes.length > 1
          ? `Overall, ${changes.map(c => `${c.name} ${direction(c.delta)}`).join(', whereas ')}. ${changes.map(c => `${c.name} peaked at ${fmt(c.peak)} in ${c.peakAt}`).join('; ')}.`
          : `Overall, the figure ${direction(changes[0].delta)} from ${fmt(changes[0].start)} to ${fmt(changes[0].end)}, with a peak of ${fmt(changes[0].peak)} in ${changes[0].peakAt}.`;
      } else if (type === 'bar_chart' || type === 'table') {
        const categoryStats = labels.map((label, i) => {
          const cells = series.map(s => ({ name: s.name, value: s.values[i] })).filter(x => Number.isFinite(x.value));
          const total = cells.reduce((sum, x) => sum + x.value, 0);
          const mean = cells.length ? total / cells.length : NaN;
          const top = cells.reduce((a, b) => !a || b.value > a.value ? b : a, null);
          const bottom = cells.reduce((a, b) => !a || b.value < a.value ? b : a, null);
          return { label, cells, mean, top, bottom, gap: top && bottom ? top.value - bottom.value : 0 };
        }).filter(x => Number.isFinite(x.mean));
        if (categoryStats.length) {
          const highestCategory = categoryStats.reduce((a, b) => !a || b.mean > a.mean ? b : a, null);
          const lowestCategory = categoryStats.reduce((a, b) => !a || b.mean < a.mean ? b : a, null);
          facts.push(`Highest average across the displayed series: ${highestCategory.label} (${fmt(highestCategory.mean)} ${spec.unit || 'units'}).`);
          facts.push(`Lowest average across the displayed series: ${lowestCategory.label} (${fmt(lowestCategory.mean)} ${spec.unit || 'units'}).`);
          categoryStats.forEach(c => facts.push(`${c.label}: ${c.cells.map(x => `${x.name} ${fmt(x.value)}`).join(' vs ')}; gap ${fmt(c.gap)} ${spec.unit || 'units'}.`));
          overview = `Overall, ${highestCategory.label} recorded the highest average across the displayed series, whereas ${lowestCategory.label} had the lowest. The size of the gaps between the comparison groups also varied by category.`;
        }
      }
    }
  } else if (type === 'pie_chart') {
    const vals = (spec.values || []).map(n);
    if (labels.length !== vals.length || vals.length < 2 || vals.some(v => !Number.isFinite(v) || v < 0)) quality.issues.push('Pie categories and non-negative values must align.');
    const total = vals.reduce((a, b) => a + b, 0);
    if (!total) quality.issues.push('Pie chart total cannot be zero.');
    if (vals.length && total) {
      const hi = Math.max(...vals), lo = Math.min(...vals), hiAt = vals.indexOf(hi), loAt = vals.indexOf(lo);
      facts.push(`Largest share: ${labels[hiAt]} (${fmt(hi)}).`, `Smallest share: ${labels[loAt]} (${fmt(lo)}).`, `Total: ${fmt(total)} ${spec.unit || 'units'}.`, `Difference between largest and smallest: ${fmt(hi - lo)} ${Math.abs(total - 100) < 0.01 ? 'percentage points' : 'units'}.`);
      overview = `Overall, ${labels[hiAt]} accounted for the largest share (${fmt(hi)}), whereas ${labels[loAt]} represented the smallest (${fmt(lo)}).`;
      if (Math.abs(total - 100) > 0.01) quality.issues.push(`The values sum to ${fmt(total)}, not 100; describe them as ${spec.unit || 'units'}, not percentages.`);
    }
  } else if (type === 'process') {
    const steps = spec.steps || [];
    if (steps.length < 3) quality.issues.push('A process should contain at least three ordered stages.');
    facts.push(`Number of displayed stages: ${steps.length}.`, `Starting stage: ${steps[0] || 'Not supplied'}.`, `Final stage: ${steps.at(-1) || 'Not supplied'}.`);
    overview = `Overall, the process consists of ${steps.length} main stages, beginning with ${steps[0] || 'the initial step'} and ending with ${steps.at(-1) || 'the final step'}.`;
  } else if (type === 'map') {
    const before = spec.before || [], after = spec.after || [];
    if (!before.length || before.length !== after.length) quality.issues.push('Before/after map features must be paired consistently.');
    const changed = before.map((v, i) => ({ before: v, after: after[i] || '' })).filter(x => x.before !== x.after);
    const lower = x => String(x || '').toLowerCase();
    const retainedOrExtended = changed.filter(x => lower(x.after).includes(lower(x.before)));
    const replacedOrRenamed = changed.filter(x => !lower(x.after).includes(lower(x.before)));
    facts.push(`Mapped feature pairs: ${before.length}.`, `Pairs with changed descriptions: ${changed.length}.`, `Descriptions that retain the original feature name: ${retainedOrExtended.length}.`, `Descriptions that appear replaced or renamed: ${replacedOrRenamed.length}.`);
    overview = `Overall, the later plan shows substantial redevelopment: ${changed.length} of ${before.length} paired feature descriptions changed, while the comparison should focus on additions, extensions, replacements and retained features shown on the maps.`;
    changed.forEach(x => facts.push(`${x.before} → ${x.after}.`));
  }
  quality.valid = quality.issues.length === 0;
  return { type, guide, facts, overview, quality, labels, series, unit: spec.unit || 'units' };
}

export function validateTask1Days(days = []) {
  const issues = [];
  const counts = {};
  const allowed = new Set(Object.keys(TASK1_GUIDES));
  days.forEach((day, i) => {
    const spec = day?.resources?.writing?.task1 || day?.writing?.task1 || {};
    const type = spec.type || 'missing';
    counts[type] = (counts[type] || 0) + 1;
    const add = message => issues.push({ day: i + 1, type, issue: message });
    if (!allowed.has(type)) add('Unsupported or missing Task 1 visual type.');
    if (!spec.prompt || !spec.title) add('Missing Task 1 title or prompt.');
    if (!/fictional|illustrative|original/i.test(spec.data_note || '')) add('Dataset provenance note must clearly state that data is original/fictional.');
    if (spec.source_type !== 'original_practice_dataset') add('Dataset source_type must be original_practice_dataset.');
    if (!spec.unit && !spec.display_units) add('Measurement unit or display unit is missing.');

    if (['line_graph', 'bar_chart', 'table'].includes(type)) {
      const labels = spec.labels || [];
      const series = spec.series || [];
      if (labels.length < 3) add('At least three labels are required for a meaningful chart/table practice set.');
      if (new Set(labels.map(x => String(x).trim())).size !== labels.length) add('Category/time labels must be unique.');
      if (!series.length) add('At least one numerical series is required.');
      series.forEach((row, j) => {
        if (!Array.isArray(row.values) || row.values.length !== labels.length) add(`Series ${j + 1} does not align with all labels.`);
        if ((row.values || []).some(v => !Number.isFinite(Number(v)) || Number(v) < 0)) add(`Series ${j + 1} contains a negative or non-numeric value.`);
      });
    } else if (type === 'pie_chart') {
      const labels = spec.labels || [], values = spec.values || [];
      if (labels.length < 3 || values.length !== labels.length) add('Pie chart requires at least three categories with one value each.');
      if (values.some(v => !Number.isFinite(Number(v)) || Number(v) < 0)) add('Pie chart contains a negative or non-numeric value.');
      const total = values.reduce((sum, v) => sum + Number(v), 0);
      if (Math.abs(total - 100) > 0.01) add(`Pie chart percentage shares must total 100; current total is ${fmt(total)}.`);
    } else if (type === 'process') {
      const steps = spec.steps || [];
      if (steps.length < 3 || steps.some(x => !String(x).trim())) add('Process diagram requires at least three named, ordered stages.');
    } else if (type === 'map') {
      const before = spec.before || [], after = spec.after || [];
      if (before.length < 3 || before.length !== after.length) add('Map needs at least three consistently paired before/after features.');
      if ([...before, ...after].some(x => !String(x).trim())) add('Map features must not be blank.');
    }
  });
  return { valid: issues.length === 0, days: days.length, counts, issues };
}
