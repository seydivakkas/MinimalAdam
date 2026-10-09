/* P4: Dependency-free, editable SVG technical diagrams. Source of truth is P3 JSON. */
export const W=1600, H=900;
export const MODES=['architecture','data-flow','ml-pipeline','engineering-system'];
export const KINDS=['client','process','service','data','model','sensor','actuator','system','result'];
export const EDGES=['data','control','feedback','physical'];
export const ACCENTS=['black','orange','red','blue'];
export const STYLES=['sketch','technical','contrast'];
export const COLORS={black:'#1d2126',orange:'#ee8733',red:'#c84e3c',blue:'#3f7eaf'};
export const ARM={connect:[43,-15],inspect:[38,-27],carry:[45,-5],guard:[28,-35]};
export const clone=value=>JSON.parse(JSON.stringify(value));
export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const norm=(x)=>Math.round(x*10000)/10000;
export const esc=(s)=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');
export const isNum=x=>typeof x==='number'&&Number.isFinite(x);
export const validID=s=>typeof s==='string'&&/^[a-zA-Z0-9_]{1,32}$/.test(s);
// Convert pre-v0.6 projects without mutating their input object.
export function normalizeLegacySpec(raw) {
 const spec=clone(raw);
 if(spec && Object.prototype.hasOwnProperty.call(spec,'xiaohei')) {
  if(Object.prototype.hasOwnProperty.call(spec,'minimaladam'))throw Error('Karakter alanı iki kez verilmiş: xiaohei ve minimaladam');
  spec.minimaladam=spec.xiaohei;
  delete spec.xiaohei;
 }
 return spec;
}
export function initialProject(spec,style='sketch') {return {format:'minimaladam-editor-v1',style:STYLES.includes(style)?style:'sketch',spec:normalizeLegacySpec(spec)}}
export function unboxProject(raw) {
 const pr=['minimaladam-editor-v1','xiaohei-editor-v1'].includes(raw?.format)?raw:{format:'minimaladam-editor-v1',style:'sketch',spec:raw};
 const normalized=normalizeLegacySpec(pr.spec);
 if(!STYLES.includes(pr.style))throw Error('Bilinmeyen çizim stili');
 const errors=validateSpec(normalized).filter(v=>v.level==='error');
 if(errors.length)throw Error('Geçersiz P3 JSON: '+errors.map(x=>x.message).join(' · '));
 return initialProject(normalized,pr.style);
}
export function box(n) {return [(n.x-n.w/2)*W,(n.y-n.h/2)*H,(n.x+n.w/2)*W,(n.y+n.h/2)*H]}
export function boundsOverlap(a,b,pad=0) {return !(a[2]+pad<=b[0]||b[2]+pad<=a[0]||a[3]+pad<=b[1]||b[3]+pad<=a[1])}
export function validateSpec(s) {
 const out=[],err=m=>out.push({level:'error',message:m}),warn=m=>out.push({level:'warning',message:m});
 if(!s||typeof s!=='object'||Array.isArray(s))return [{level:'error',message:'Şema JSON nesnesi olmalı'}];
 if(s.version!==1)err('P3 version=1 olmalı');
 if(!MODES.includes(s.mode))err('Geçersiz teknik mod');
 if(typeof s.concept!=='string'||!s.concept.trim())err('Kısa bir concept gerekli');
 if(!Array.isArray(s.nodes)||s.nodes.length<2||s.nodes.length>8)err('P3: 2–8 düğüm gerekli');
 if(!Array.isArray(s.edges)||s.edges.length<1||s.edges.length>12)err('P3: 1–12 bağlantı gerekli');
 if(!Array.isArray(s.nodes)||!Array.isArray(s.edges))return out;
 const ids=new Set();
 s.nodes.forEach((n,i)=>{
  if(!n||typeof n!=='object'){err(`Düğüm ${i} geçersiz`);return}
  if(!validID(n.id)||ids.has(n.id))err(`Geçersiz/tekrarlı düğüm ID: ${n.id}`);ids.add(n.id);
  if(!KINDS.includes(n.kind))err(`${n.id}: geçersiz tür`);
  if(!ACCENTS.includes(n.accent??'black'))err(`${n.id}: geçersiz vurgu rengi`);
  if(typeof n.label!=='string'||!n.label.trim()||n.label.length>32||/[<>\r\n\t]/.test(n.label)||n.label!==n.label.normalize('NFC'))err(`${n.id}: geçersiz Türkçe etiket`);
  if(![n.x,n.y,n.w,n.h].every(isNum))err(`${n.id}: koordinatlar sayısal olmalı`);
  else if(n.w<.115||n.w>.285||n.h<.13||n.h>.235||box(n)[0]<64||box(n)[2]>W-64||box(n)[1]<70||box(n)[3]>H-70)warn(`${n.id}: P3 sınırları dışında`);
 });
 s.nodes.forEach((n,i)=>s.nodes.slice(i+1).forEach(k=>{if([n.x,n.y,n.w,n.h,k.x,k.y,k.w,k.h].every(isNum)&&boundsOverlap(box(n),box(k),26))warn(`${n.id} ile ${k.id} çakışıyor`)}));
 const pairs=new Set();
 s.edges.forEach((e,i)=>{
  if(!e||typeof e!=='object'){err(`Bağlantı ${i} geçersiz`);return}
  if(!ids.has(e.from)||!ids.has(e.to)||e.from===e.to)err(`Bağlantı ${i}: geçersiz kaynak veya hedef`);
  if(!EDGES.includes(e.kind??'data'))err(`Bağlantı ${i}: tür geçersiz`);
  if(e.label!==undefined&&(typeof e.label!=='string'||e.label.length>22||/[<>\r\n\t]/.test(e.label)||e.label!==e.label.normalize('NFC')))err(`Bağlantı ${i}: hatalı etiket`);
  const key=`${e.from}:${e.to}:${e.kind??'data'}`;if(pairs.has(key))err(`Tekrarlı bağlantı: ${key}`);pairs.add(key);
  if(e.from_port&&!['left','right','top','bottom'].includes(e.from_port))err(`Bağlantı ${i}: kaynak port`);
  if(e.to_port&&!['left','right','top','bottom'].includes(e.to_port))err(`Bağlantı ${i}: hedef port`);
  if(e.via!==undefined&&(!Array.isArray(e.via)||e.via.length>6||e.via.some(p=>!Array.isArray(p)||p.length!==2||p.some(v=>!isNum(v)||v<=.0175||v>=.9825))))err(`Bağlantı ${i}: ara noktalar geçersiz`);
 });
 const c=s.minimaladam;
 if(!c||!isNum(c.x)||!isNum(c.y)||!Number.isInteger(c.edge)||c.edge<0||c.edge>=s.edges.length||!Object.keys(ARM).includes(c.action??'connect'))err('MinimalAdam geçerli bir bağlantı ve eylem içermeli');
 return out;
}
export function port(n,p) {const [a,b,c,d]=box(n);return {left:[a,(b+d)/2],right:[c,(b+d)/2],top:[(a+c)/2,b],bottom:[(a+c)/2,d]}[p]}
export function defaultPorts(a,b) {const dx=(b.x-a.x)*W,dy=(b.y-a.y)*H;return Math.abs(dx)>=Math.abs(dy)?dx>0?['right','left']:['left','right']:dy>0?['bottom','top']:['top','bottom']}
export function route(e,nodes) {
 const a=nodes.find(n=>n.id===e.from), b=nodes.find(n=>n.id===e.to);
 if(!a||!b)return [];
 const [pa,pb]=defaultPorts(a,b),pf=e.from_port||pa,pt=e.to_port||pb;
 const start=port(a,pf),end=port(b,pt);
 if(e.via?.length)return [start,...e.via.map(p=>[p[0]*W,p[1]*H]),end];
 if(Math.abs(start[0]-end[0])<.01||Math.abs(start[1]-end[1])<.01)return [start,end];
 if(['left','right'].includes(pf)&&['left','right'].includes(pt)) {const mid=(start[0]+end[0])/2;return [start,[mid,start[1]],[mid,end[1]],end]}
 if(['top','bottom'].includes(pf)&&['top','bottom'].includes(pt)) {const mid=(start[1]+end[1])/2;return [start,[start[0],mid],[end[0],mid],end]}
 return [start,[end[0],start[1]],end];
}
export function pointToSegment(p,a,b) {const vx=b[0]-a[0],vy=b[1]-a[1],m=vx*vx+vy*vy,t=m?clamp(((p[0]-a[0])*vx+(p[1]-a[1])*vy)/m,0,1):0;return {point:[a[0]+vx*t,a[1]+vy*t],distance:Math.hypot(p[0]-a[0]-vx*t,p[1]-a[1]-vy*t)}}
export function nearestOnRoute(p,pts) {const opts=pts.slice(1).map((x,i)=>pointToSegment(p,pts[i],x));return opts.sort((a,b)=>a.distance-b.distance)[0]||null}
export function snapMinimalAdam(spec) {
 const c=spec.minimaladam;if(!c||!spec.edges[c.edge])return;
 const points=route(spec.edges[c.edge],spec.nodes);const arm=ARM[c.action]||ARM.connect,scale=c.scale||1;
 const hand=[c.x*W+arm[0]*scale,c.y*H+arm[1]*scale],p=nearestOnRoute(hand,points);
 if(p){c.x=norm(clamp((p.point[0]-arm[0]*scale)/W,.065,.935));c.y=norm(clamp((p.point[1]-arm[1]*scale)/H,.12,.9))}
}
function styleFor(style) {return {sketch:{line:2.6,round:20,font:'"Segoe UI", Arial, sans-serif',bg:'#ffffff',node:'#ffffff',text:'#1d2126',dash:'5 9'},technical:{line:2,round:6,font:'"Segoe UI", Arial, sans-serif',bg:'#ffffff',node:'#ffffff',text:'#1d2126',dash:'7 5'},contrast:{line:3.6,round:18,font:'"Segoe UI", Arial, sans-serif',bg:'#ffffff',node:'#f8fbff',text:'#111827',dash:'9 7'}}[style]||null}
function nodeGlyph(n,x,y) {const color=COLORS[n.accent||'black']||COLORS.black;
 switch(n.kind){case 'data':return `<ellipse cx="${x}" cy="${y-6}" rx="13" ry="5" fill="none" stroke="${color}" stroke-width="3"/><path d="M ${x-13} ${y-6} v16 q13 10 26 0 v-16" fill="none" stroke="${color}" stroke-width="3"/>`;
 case 'model':return `<path d="M ${x-13} ${y} l13 -13 13 13 -13 13 Z" fill="none" stroke="${color}" stroke-width="3"/><circle cx="${x}" cy="${y}" r="3.4" fill="${color}"/>`;
 case 'sensor':case 'client':return `<path d="M ${x-13} ${y+7} Q ${x} ${y-18} ${x+13} ${y+7}" fill="none" stroke="${color}" stroke-width="3"/><circle cx="${x}" cy="${y+7}" r="4" fill="${color}"/>`;
 case 'actuator':case 'system':return `<circle cx="${x}" cy="${y}" r="12" fill="none" stroke="${color}" stroke-width="3"/><path d="M ${x-5} ${y+4} l6 -13 6 13" fill="none" stroke="${color}" stroke-width="3"/>`;
 case 'result':return `<path d="M ${x-12} ${y} l8 8 18 -20" fill="none" stroke="${color}" stroke-width="4"/>`;
 default:return `<rect x="${x-12}" y="${y-12}" width="24" height="24" rx="5" fill="none" stroke="${color}" stroke-width="3"/><circle cx="${x}" cy="${y}" r="3" fill="${color}"/>`}}
export function nodeMarkup(n,style) {const opts=styleFor(style),[a,b,c,d]=box(n),w=c-a,h=d-b;
 return `<g class="diagram-node" id="node-${esc(n.id)}" data-node-id="${esc(n.id)}" style="cursor:grab"><rect x="${a}" y="${b}" width="${w}" height="${h}" rx="${opts.round}" fill="${opts.node}" stroke="${opts.text}" stroke-width="${opts.line}"/>${style==='sketch'?`<path d="M ${a+15} ${b+12} Q ${a+w/2} ${b+7} ${c-15} ${b+11}" stroke="${opts.text}" stroke-width="1.3" opacity=".24" fill="none"/>`:''}${nodeGlyph(n,a+28,b+30)}<text x="${n.x*W}" y="${n.y*H+12}" fill="${opts.text}" font-family='${opts.font}' font-size="24" font-weight="550" text-anchor="middle" dominant-baseline="middle">${esc(n.label)}</text></g>`}
export function edgeMarkup(e,i,spec,style) {const pts=route(e,spec.nodes);if(!pts.length)return '';
 const color={data:COLORS.orange,control:COLORS.black,feedback:COLORS.blue,physical:COLORS.red}[e.kind]||COLORS.orange;
 const path=pts.map((p,j)=>`${j?'L':'M'} ${p[0].toFixed(2)} ${p[1].toFixed(2)}`).join(' ');
 const dash=e.kind==='feedback'?(styleFor(style).dash):e.kind==='physical'?'2 7':'';
 const segments=pts.slice(1).map((p,j)=>[pts[j],p]);const [a,b]=segments.sort((a,b)=>Math.hypot(b[0][0]-b[1][0],b[0][1]-b[1][1])-Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]))[0];
 let lx=(a[0]+b[0])/2,ly=(a[1]+b[1])/2;if(Math.abs(a[0]-b[0])>=Math.abs(a[1]-b[1]))ly-=23;else lx+=22;
 return `<g class="diagram-edge" id="edge-${i}" data-edge-index="${i}" style="cursor:pointer"><path d="${path}" fill="none" stroke="${color}" stroke-width="${style==='contrast'?4.5:3.2}" stroke-dasharray="${dash}" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrow-${e.kind||'data'})"/><path d="${path}" fill="none" stroke="transparent" stroke-width="25"/>${e.label?`<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" font-size="19" font-family="Segoe UI,Arial,sans-serif" fill="${color}" stroke="white" stroke-width="7" paint-order="stroke" dominant-baseline="middle">${esc(e.label)}</text>`:''}</g>`}
export function creatureMarkup(c) {if(!c)return '';const arm=ARM[c.action]||ARM.connect,s=c.scale||1,x=c.x*W,y=c.y*H;return `<g id="minimaladam" data-creature="1" transform="translate(${x} ${y}) scale(${s})" style="cursor:pointer"><path d="M -17 21 l-8 20 M 13 21 l6 20" stroke="${COLORS.black}" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M -16 -14 Q -28 -13 -24 8 Q -18 27 3 26 Q 27 25 28 3 Q 26 -26 4 -31 Q -15 -32 -16 -14 Z" fill="${COLORS.black}"/><ellipse cx="-3" cy="-9" rx="3.2" ry="4.5" fill="white"/><ellipse cx="13" cy="-8" rx="3.2" ry="4.5" fill="white"/><path d="M 22 5 Q 31 -1 ${arm[0]} ${arm[1]}" stroke="${COLORS.black}" fill="none" stroke-width="3" stroke-linecap="round"/><circle cx="${arm[0]}" cy="${arm[1]}" r="3.2" fill="${COLORS.black}"/></g>`}
export function exportSVG(project,{metadata=true}={}) {
 const {spec,style}=project;if(validateSpec(spec).some(x=>x.level==='error'))throw Error('Önce şema hatalarını düzeltin');
 const defs=`<defs>${EDGES.map(kind=>{const color={data:COLORS.orange,control:COLORS.black,feedback:COLORS.blue,physical:COLORS.red}[kind];return `<marker id="arrow-${kind}" viewBox="0 0 14 14" refX="12" refY="7" markerWidth="5" markerHeight="5" orient="auto-start-reverse" markerUnits="strokeWidth"><path d="M 2 2 L 12 7 L 2 12" fill="none" stroke="${color}" stroke-width="2.2"/></marker>`}).join('')}</defs>`;
 const contents=`<rect x="0" y="0" width="${W}" height="${H}" fill="white"/>${defs}<g id="technical-base">${spec.edges.map((e,i)=>edgeMarkup(e,i,spec,style)).join('')}${spec.nodes.map(n=>nodeMarkup(n,style)).join('')}${creatureMarkup(spec.minimaladam)}</g>`;
 const meta=metadata?`<metadata id="minimaladam-editable-spec">${esc(JSON.stringify(project))}</metadata>`:'';
 return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(spec.concept)}">${meta}${contents}</svg>`;
}
// Safe import: SVG with embedded P4 metadata, or a confirmed legacy P3 schematic.
export function importSVGText(text) {
 const parsed=new DOMParser().parseFromString(text,'image/svg+xml');
 if(parsed.querySelector('parsererror'))throw Error('SVG XML geçersiz');
 const root=parsed.documentElement;
 if(root.localName!=='svg')throw Error('SVG gerekli');
 const meta=root.querySelector('metadata#minimaladam-editable-spec,metadata#xiaohei-editable-spec');
 if(meta)return unboxProject(JSON.parse(meta.textContent));
 const groups=[...root.querySelectorAll('#technical-base > g[id^="node-"]')],edges=[...root.querySelectorAll('#technical-base > path[id^="edge-"]')];
 if(groups.length<2||edges.length<1)throw Error('Bu SVG düzenlenebilir P3 şeması olarak tanınmadı; JSON kaynağını açın');
 const allTexts=[...root.querySelectorAll('#turkish-label-layer > text')];
 const nodes=groups.map(g=>{
  const id=g.getAttribute('id').slice(5),r=g.querySelector('rect');if(!r||!validID(id))throw Error('Eski SVG düğüm okunamadı');
  const a=+r.getAttribute('x'),b=+r.getAttribute('y'),w=+r.getAttribute('width'),h=+r.getAttribute('height');
  const label=allTexts.find(t=>Math.abs(+t.getAttribute('x')-(a+w/2))<2 && Math.abs(+t.getAttribute('y')-(b+h/2+12))<3)?.textContent;
  if(!label)throw Error(`Düğümün Türkçe etiketi belirlenemedi: ${id}`);
  const kind=g.getAttribute('data-kind')||'process';
  const colored=[...g.querySelectorAll('[stroke]')].map(e=>e.getAttribute('stroke'));const found=Object.entries(COLORS).find(([k,v])=>k!=='black'&&colored.includes(v));
  return {id,label,kind,x:norm((a+w/2)/W),y:norm((b+h/2)/H),w:norm(w/W),h:norm(h/H),...(found?{accent:found[0]}:{})};
 });
 const es=edges.map(el=>{
  const d=el.getAttribute('d')||'';
  const points=[...d.matchAll(/[ML]\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)/g)].map(m=>[+m[1],+m[2]]);
  if(points.length<2)throw Error('Eski SVG bağlantı okunamadı');
  const findAnchor=(p)=>{
   const opts=nodes.flatMap(n=>['left','right','top','bottom'].map(q=>({n,p:q,dist:Math.hypot(port(n,q)[0]-p[0],port(n,q)[1]-p[1])})));
   const best=opts.sort((a,b)=>a.dist-b.dist)[0];if(best.dist>3)throw Error('SVG bağlantı ucu belirsiz; orijinal JSON kaynağını açın');return best;
  };
  const source=findAnchor(points[0]),target=findAnchor(points.at(-1));
  if(source.n.id===target.n.id)throw Error('Eski SVG bağlantı uçları belirsiz');
  const color=el.getAttribute('stroke');const kind=color===COLORS.blue?'feedback':color===COLORS.red?'physical':color===COLORS.black?'control':'data';
  const mid=points[Math.floor(points.length/2)];
  const label=allTexts.filter(t=>!nodes.some(n=>n.label===t.textContent)).map(t=>({text:t.textContent,dist:nearestOnRoute([+t.getAttribute('x'),+t.getAttribute('y')],points)?.distance??999})).sort((a,b)=>a.dist-b.dist)[0];
  return {from:source.n.id,to:target.n.id,kind,from_port:source.p,to_port:target.p,...(points.length>2?{via:points.slice(1,-1).map(p=>[norm(p[0]/W),norm(p[1]/H)])}:{}),...(label&&label.dist<70?{label:label.text}:{})};
 });
 const c=root.querySelector('#minimaladam,#xiaohei');if(!c)throw Error('Eski SVG içinde karakter bulunamadı');
 const transform=c.getAttribute('transform')||'';
 const m=transform.match(/translate\(([-\d.]+)[, ]+([-\d.]+)\)\s*scale\(([-\d.]+)\)/);
 if(!m)throw Error('Eski SVG karakter konumu okunamadı');
 // The original P3 SVG did not serialize the logical action/edge; recover only if exactly one edge is within contact distance.
 const [x,y]=[+m[1],+m[2]],scale=+m[3];
 const candidates=[];
 es.forEach((e,i)=>Object.entries(ARM).forEach(([action,arm])=>{const hand=[x+arm[0]*scale,y+arm[1]*scale];const hit=nearestOnRoute(hand,route(e,nodes));if(hit&&hit.distance<4)candidates.push({i,action,distance:hit.distance})}));
 if(!candidates.length)throw Error('Eski SVG MinimalAdam bağlantısı belirlenemedi; JSON kaynağı gerekli');
 const best=candidates.sort((a,b)=>a.distance-b.distance)[0];
 const concept=root.getAttribute('aria-label')||'Eski P3 SVG içe aktarıldı';
 // Original SVG cannot identify original mode; use architecture as an explicitly editable default.
 const raw={version:1,mode:'architecture',concept,nodes,edges:es,minimaladam:{x:norm(x/W),y:norm(y/H),scale,action:best.action,edge:best.i}};
 const issues=validateSpec(raw).filter(x=>x.level==='error');if(issues.length)throw Error('Eski SVG beklenen P3 biçimine çevrilemedi: '+issues.map(x=>x.message).join('; '));
 return initialProject(raw);
}
