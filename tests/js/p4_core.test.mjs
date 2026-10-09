import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {initialProject,unboxProject,exportSVG,validateSpec,route,ARM,snapMinimalAdam} from '../../editor/core.mjs';
const sample=(name)=>JSON.parse(readFileSync(new URL(`../../examples/technical/specs/${name}.json`,import.meta.url),'utf8'));
const files=['01-yazilim-mimarisi','02-veri-akisi','03-ml-pipeline','04-muhendislik-sistemi'];
for(const file of files){
 test(`P3 sample ${file} is valid and exported without altering graph`,()=>{
  const spec=sample(file),p=initialProject(spec);
  assert.equal(validateSpec(spec).filter(x=>x.level==='error').length,0);
  for(const style of ['sketch','technical','contrast']){
    p.style=style;const svg=exportSVG(p);assert.match(svg,/<svg /);assert.equal((svg.match(/data-node-id=/g)||[]).length,spec.nodes.length);assert.equal((svg.match(/data-edge-index=/g)||[]).length,spec.edges.length);
    assert.match(svg,/<metadata id="minimaladam-editable-spec">/);
  }
  assert.deepEqual(spec,sample(file));
 });
}
test('Input escaping protects SVG structure and retains Turkish characters',()=>{
 const p=initialProject(sample(files[0]));p.spec.concept='Çizim & güven <taslak>';p.spec.nodes[0].label='Gözlem & ölçüm';
 const svg=exportSVG(p);assert.match(svg,/Çizim &amp; güven &lt;taslak&gt;/);assert.match(svg,/Gözlem &amp; ölçüm/);
});
test('Missing node and duplicate ID produce errors',()=>{
 let s=sample(files[0]);s.nodes[1].id=s.nodes[0].id;
 assert.ok(validateSpec(s).some(v=>v.level==='error'));
 s=sample(files[0]);s.edges[0].to='not-found';assert.ok(validateSpec(s).some(v=>v.level==='error'));
});
test('overlaps and P3 bounds are warned and do not fail silently',()=>{
 const s=sample(files[0]);s.nodes[1].x=s.nodes[0].x;s.nodes[1].y=s.nodes[0].y;
 assert.ok(validateSpec(s).some(v=>v.level==='warning'));
});
test('round-trip project JSON preserves technical spec and style',()=>{
 const s=sample(files[2]),p=initialProject(s,'contrast');assert.deepEqual(unboxProject(JSON.parse(JSON.stringify(p))),p);
 assert.deepEqual(unboxProject(JSON.parse(JSON.stringify(s))).spec,s);
});
test('minimaladam snaps its hand onto connected edge',()=>{
 const s=sample(files[2]);s.minimaladam.x=.25;s.minimaladam.y=.45;
 snapMinimalAdam(s);const c=s.minimaladam,arm=ARM[c.action];
 assert.ok(c.x>=0&&c.x<=1);assert.ok(c.y>=0&&c.y<=1);
 const coords=route(s.edges[c.edge],s.nodes);assert.ok(coords.length>=2);
});
test('Invalid JSON cannot be imported',()=>{
 assert.throws(()=>unboxProject({format:'minimaladam-editor-v1',style:'alien',spec:sample(files[0])}));
 assert.throws(()=>unboxProject({format:'minimaladam-editor-v1',style:'sketch',spec:{version:99}}));
});

test('legacy v0.5 character key and project format migrate without mutating input',()=>{
 const original=sample(files[0]);original.xiaohei=original.minimaladam;delete original.minimaladam;
 const old={format:'xiaohei-editor-v1',style:'technical',spec:original};
 const migrated=unboxProject(old);
 assert.equal(migrated.format,'minimaladam-editor-v1');
 assert.ok(migrated.spec.minimaladam && !('xiaohei' in migrated.spec));
 assert.ok(original.xiaohei && !('minimaladam' in original));
 assert.match(exportSVG(migrated),/id="minimaladam-editable-spec"/);
 const invalid=sample(files[0]);invalid.xiaohei=invalid.minimaladam;
 assert.throws(()=>unboxProject(invalid),/iki kez/);
});
