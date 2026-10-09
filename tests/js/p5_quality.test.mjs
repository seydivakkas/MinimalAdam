import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initialProject,snapMinimalAdam} from '../../editor/core.mjs';
import {auditProject,QA_LIMITS,QA_VERSION} from '../../editor/quality.mjs';
const source=n=>JSON.parse(readFileSync(new URL(`../../examples/technical/specs/${n}.json`,import.meta.url),'utf8'));
const SAMPLE=['01-yazilim-mimarisi','02-veri-akisi','03-ml-pipeline','04-muhendislik-sistemi'];
const run=(s)=>auditProject(initialProject(s));
for(const name of SAMPLE)test(`P5 ${name}: basic automated QA and unverified aesthetic checklist`,()=>{
 const r=run(source(name));assert.equal(r.summary.automatedStatus,'PASS');assert.equal(r.summary.errors,0);
 assert.equal(r.manualChecks.length,4);assert.ok(r.manualChecks.every(c=>c.status==='NOT_VERIFIED'));
 assert.equal(r.version,QA_VERSION);assert.equal(r.metrics.canvas.aspect,'16:9');
});
test('P5: structurally invalid input is FAIL without attempting route calculations',()=>{
 const s=source(SAMPLE[0]);s.edges[0].from='unknown';const r=run(s);
 assert.equal(r.summary.automatedStatus,'FAIL');assert.ok(r.issues.some(x=>x.severity==='error'));
});
test('P5: node label overflow is REVIEW with focused node',()=>{
 const s=source(SAMPLE[0]);s.nodes[0].label='Türkçe metin çok uzun';s.nodes[0].w=.115;
 const r=run(s);assert.ok(r.issues.some(x=>x.id.startsWith('TEXT_NODE_')&&x.subject.type==='node'));
 assert.equal(r.summary.automatedStatus,'REVIEW');
});
test('P5: character detached from its connection triggers REVIEW',()=>{
 const s=source(SAMPLE[2]);s.minimaladam.x=.15;s.minimaladam.y=.85;
 const r=run(s);assert.ok(r.issues.some(x=>x.id==='MINIMALADAM_CONTACT'));
 snapMinimalAdam(s);assert.ok(run(s).metrics.maxContactDistancePx <= QA_LIMITS.contactWarningPx);
});
test('P5: a graph orphan is detected and exported for remediation',()=>{
 const s=source(SAMPLE[2]);s.edges=s.edges.filter(e=>e.from!=='new_data'&&e.to!=='new_data');s.minimaladam.edge=0;
 const r=run(s);assert.ok(r.issues.some(x=>x.id==='GRAPH_ORPHAN_new_data'));
 assert.ok(r.metrics.disconnectedNodes>=1);
});
test('P5: edge passing through unrelated node is flagged',()=>{
 const s=source(SAMPLE[0]);const n=s.nodes.find(n=>!['client','api'].includes(n.id))??s.nodes.at(-1);
 const e=s.edges[0];const a=s.nodes.find(n=>n.id===e.from),b=s.nodes.find(n=>n.id===e.to);
 const outsider=s.nodes.find(x=>x.id!==e.from&&x.id!==e.to);
 outsider.x=(a.x+b.x)/2;outsider.y=(a.y+b.y)/2;
 const r=run(s);assert.ok(r.issues.some(x=>x.id.startsWith('EDGE_NODE_')));
});
test('P5: severity and metrics remain deterministic for repeated reports',()=>{
 const s=source(SAMPLE[1]);assert.deepEqual(run(s),run(s));
});

test('P5: out-of-range MinimalAdam scale is a blocking error',()=>{
 const s=source(SAMPLE[0]);s.minimaladam.scale=900;const r=run(s);
 assert.equal(r.summary.automatedStatus,'FAIL');assert.ok(r.issues.some(x=>x.id==='MINIMALADAM_SCALE'));
});
