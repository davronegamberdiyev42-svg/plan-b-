import assert from 'node:assert/strict';
import fs from 'node:fs';
import { TASK1_ENGINE_VERSION, TASK1_GUIDES, analyseTask1Spec, validateTask1Days } from '../assets/js/core/task1-intelligence.js';

const data = JSON.parse(fs.readFileSync(new URL('../data/app-data.json', import.meta.url), 'utf8'));
const report = validateTask1Days(data.resources.days);
assert.equal(TASK1_ENGINE_VERSION, '47.0.0');
assert.equal(report.valid, true, JSON.stringify(report.issues));
assert.equal(report.days, 84);
for (const type of ['line_graph','bar_chart','pie_chart','table','process','map']) assert.equal(report.counts[type], 14);

const fixtures = {
  line_graph: { type:'line_graph', title:'Line', prompt:'Summarise the graph.', labels:['2010','2015','2020','2025'], unit:'index points', series:[{name:'A',values:[20,30,18,45]},{name:'B',values:[10,12,15,16]}], data_note:'Original fictional practice data', source_type:'original_practice_dataset' },
  bar_chart: { type:'bar_chart', title:'Bars', prompt:'Summarise the chart.', labels:['A','B','C','D'], unit:'cases', series:[{name:'Group 1',values:[10,25,20,15]},{name:'Group 2',values:[8,22,28,16]}], data_note:'Original fictional practice data', source_type:'original_practice_dataset' },
  pie_chart: { type:'pie_chart', title:'Pie', prompt:'Summarise the chart.', labels:['A','B','C','D'], values:[40,30,20,10], unit:'percentage', data_note:'Original fictional practice data', source_type:'original_practice_dataset' },
  table: { type:'table', title:'Table', prompt:'Summarise the table.', labels:['A','B','C','D'], unit:'units', series:[{name:'2024',values:[10,20,15,25]},{name:'2025',values:[12,18,22,24]}], data_note:'Original fictional practice data', source_type:'original_practice_dataset' },
  process: { type:'process', title:'Process', prompt:'Summarise the process.', steps:['Input is collected','The material is sorted','The product is checked','The product is stored'], unit:'stages', data_note:'Original fictional practice data', source_type:'original_practice_dataset' },
  map: { type:'map', title:'Map', prompt:'Summarise the maps.', before:['Gate','Hall','Garden'], after:['Gate with ramp','Expanded hall','New library'], unit:'features', data_note:'Original fictional practice data', source_type:'original_practice_dataset' }
};
for (const [type, spec] of Object.entries(fixtures)) {
  const result = analyseTask1Spec(spec);
  assert.equal(result.type, type);
  assert.ok(result.quality.valid, `${type}: ${result.quality.issues.join('; ')}`);
  assert.ok(result.guide.structure.length >= 4);
  assert.ok(result.facts.length >= 2);
  assert.ok(result.overview.length > 15);
}
assert.equal(Object.keys(TASK1_GUIDES).length, 6);
assert.equal(analyseTask1Spec({ type:'pie_chart', labels:['A','B','C'], values:[50,30,10], unit:'percent' }).quality.valid, false, 'bad pie total must fail');
assert.equal(analyseTask1Spec({ type:'process', steps:['Start','Finish'] }).quality.valid, false, 'short process must fail');
assert.equal(analyseTask1Spec({ type:'map', before:['A','B','C'], after:['A'] }).quality.valid, false, 'unpaired map must fail');
assert.equal(analyseTask1Spec({ type:'line_graph', labels:['A','B','C'], series:[{values:[1,2]}] }).quality.valid, false, 'mismatched series must fail');
console.log(JSON.stringify({ version:TASK1_ENGINE_VERSION, tests:19, passed:19, failed:0, chartDays:report.days, typeCounts:report.counts, cases:['84-day dataset validation','6 visual guides','6 valid visual fixture analysis','pie total integrity','process minimum stages','map pair integrity','series/label alignment'] },null,2));
