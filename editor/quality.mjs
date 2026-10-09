/** P5: Explainable, deterministic preflight for source-defined MinimalAdam P3/P4 diagrams.
 * No AI aesthetic claims. Geometry uses nominal SVG coordinates, not browser font layout.
 */
import {W,H,ARM,box,route,nearestOnRoute,validateSpec,pointToSegment,boundsOverlap} from './core.mjs';

export const QA_VERSION='p5-qa-v1';
export const QA_LIMITS=Object.freeze({
  canvasWidth:W,canvasHeight:H,minBlankFraction:0.35,maxNodeBoxFraction:0.47,
  labelInsetPx:28,edgeSafePaddingPx:7,contactWarningPx:28,edgeCrossingTolerancePx:5,
  nodeMarginPx:64,terminalMarginPx:48,
});
const MANUAL=[
 {code:'MANUAL_MEANING',label:'Bileşen ve oklar gerçek sistemin anlamını doğru temsil ediyor mu?'},
 {code:'MANUAL_IP',label:'MinimalAdam karakterinin özgünlük, görsel tutarlılık ve eylem rolü uygun mu?'},
 {code:'MANUAL_AESTHETICS',label:'Metafor, okunurluk, görsel denge ve özgünlük yeterli mi?'},
 {code:'MANUAL_FONTS',label:'Hedef cihazda seçilen font ve Türkçe glifler doğru görünüyor mu?'},
];
const round=v=>Math.round(v*1000)/1000;
function doesSegmentHitBox(a,b,bb,padding=0){
 const [l,t,r,bt]=[bb[0]-padding,bb[1]-padding,bb[2]+padding,bb[3]+padding];
 // Liang–Barsky segment–rectangle clipping; also supports diagonal segments.
 let u0=0,u1=1;const dx=b[0]-a[0],dy=b[1]-a[1];
 for(const [p,q] of [[-dx,a[0]-l],[dx,r-a[0]],[-dy,a[1]-t],[dy,bt-a[1]]]){
  if(Math.abs(p)<1e-10){if(q<0)return false;continue}
  const v=q/p;
  if(p<0)u0=Math.max(u0,v);else u1=Math.min(u1,v);
  if(u0>u1)return false;
 }
 return u1>u0+1e-6;
}
function intersectInterior(a,b,c,d,epsilon){
 const cross=(u,v)=>u[0]*v[1]-u[1]*v[0];const r=[b[0]-a[0],b[1]-a[1]],s=[d[0]-c[0],d[1]-c[1]];
 const den=cross(r,s);if(Math.abs(den)<1e-8)return false;
 const ca=[c[0]-a[0],c[1]-a[1]],t=cross(ca,s)/den,u=cross(ca,r)/den;
 const lenA=Math.hypot(...r),lenB=Math.hypot(...s);
 return t>epsilon/lenA&&t<1-epsilon/lenA&&u>epsilon/lenB&&u<1-epsilon/lenB;
}
function edgeLabelAnchor(points){
 const segs=points.slice(1).map((p,i)=>[points[i],p]).sort((u,v)=>
   Math.hypot(v[0][0]-v[1][0],v[0][1]-v[1][1])-Math.hypot(u[0][0]-u[1][0],u[0][1]-u[1][1]));
 const [[a,b],[c,d]]=segs.length?[segs[0][0],segs[0][1]]:[[0,0],[0,0]];
 // a,b and c,d are endpoints of longest segment.
 let x=(a+c)/2,y=(b+d)/2;
 if(Math.abs(a-c)>=Math.abs(b-d))y-=23;else x+=22;
 return [x,y];
}
function widthOf(text,size,measureText){
 const v=measureText?.(text,size);
 return typeof v==='number'&&Number.isFinite(v)&&v>=0?v:[...text].reduce((sum,c)=>sum+('İıMWŞĞÖÜ@'.includes(c)?0.75:/[.,:;!|]/.test(c)?.3:0.58)*size,0);
}
export function auditProject(project,{measureText}={}){
 const spec=project?.spec;
 const issues=[];
 const push=(id,severity,category,message,subject=null,detail='')=>issues.push({id,severity,category,message,subject,detail});
 const coreIssues=validateSpec(spec);
 coreIssues.forEach((v,i)=>push(`STRUCT_${i}`,v.level==='error'?'error':'warning','Şema yapısı',v.message));
 const creature=spec?.minimaladam;
 if(creature&&creature.scale!==undefined&&(!Number.isFinite(creature.scale)||creature.scale<.65||creature.scale>1.5))push('MINIMALADAM_SCALE','error','Karakter','MinimalAdam ölçeği 0.65–1.5 aralığında sayısal olmalı.');
 if(creature&&Number.isFinite(creature.x)&&Number.isFinite(creature.y)&&(creature.x<0||creature.x>1||creature.y<0||creature.y>1))push('MINIMALADAM_BOUNDS','error','Karakter','MinimalAdam konumu 0–1 tuval koordinatlarını aşmamalı.');
 const metrics={canvas:{width:W,height:H,aspect:'16:9'},nodes:spec?.nodes?.length??0,edges:spec?.edges?.length??0,
   nodeBoxAreaFraction:null,estimatedWhitespaceLowerBound:null,maxContactDistancePx:null,
   crossingPairs:0,disconnectedNodes:0};
 if(!issues.some(v=>v.severity==='error')&&spec){
  const nodes=spec.nodes,edges=spec.edges;
  const nodeById=new Map(nodes.map(n=>[n.id,n]));
  let boxSum=0;
  for(const n of nodes){
   const b=box(n);boxSum+=(b[2]-b[0])*(b[3]-b[1]);
   const width=widthOf(n.label,24,measureText);
   if(width>n.w*W-QA_LIMITS.labelInsetPx)push(`TEXT_NODE_${n.id}`,'warning','Türkçe etiket',`${n.id}: “${n.label}” düğüm kutusuna sığmayabilir (${Math.ceil(width)} px).`,{type:'node',id:n.id},'Etiketi kısalt veya düğümü genişlet.');
  }
  const fraction=boxSum/(W*H);metrics.nodeBoxAreaFraction=round(fraction);
  metrics.estimatedWhitespaceLowerBound=round(Math.max(0,1-fraction));
  if(fraction>QA_LIMITS.maxNodeBoxFraction)push('LAYOUT_DENSITY','warning','Yerleşim',`Düğüm kutuları tuvalin %${Math.round(fraction*100)} kadarını kaplıyor.`,null,'Fazla bileşeni ayrı bir çizime böl. Bu metrik gerçek boş alan ölçümü değildir.');
  const hitPaths=edges.map(e=>route(e,nodes));
  edges.forEach((e,i)=>{
   const points=hitPaths[i];
   nodes.filter(n=>n.id!==e.from&&n.id!==e.to).forEach(n=>{
    if(points.slice(1).some((p,j)=>doesSegmentHitBox(points[j],p,box(n),QA_LIMITS.edgeSafePaddingPx)))
     push(`EDGE_NODE_${i}_${n.id}`,'warning','Bağlantı geometrisi',`${e.from} → ${e.to} oku “${n.label}” düğümünü kesiyor.`,{type:'edge',id:i},'Bağlantının ara noktalarını veya düğüm yerleşimini düzenle.');
   });
   if(e.label){
    const [cx,cy]=edgeLabelAnchor(points),half=widthOf(e.label,19,measureText)/2;
    const labelBounds=[cx-half-5,cy-11,cx+half+5,cy+11];
    if(labelBounds[0]<QA_LIMITS.terminalMarginPx||labelBounds[2]>W-QA_LIMITS.terminalMarginPx||labelBounds[1]<QA_LIMITS.terminalMarginPx||labelBounds[3]>H-QA_LIMITS.terminalMarginPx)
     push(`EDGE_TEXT_BOUND_${i}`,'warning','Türkçe etiket',`Bağlantı ${i+1} etiketi tuval kenarına fazla yakın.`,{type:'edge',id:i});
    for(const n of nodes)if(boundsOverlap(labelBounds,box(n),2))
      push(`EDGE_TEXT_NODE_${i}_${n.id}`,'warning','Türkçe etiket',`Bağlantı ${i+1} etiketi “${n.label}” kutusuyla çakışabilir.`,{type:'edge',id:i});
   }
  });
  for(let i=0;i<edges.length;i++)for(let j=i+1;j<edges.length;j++){
   const a=hitPaths[i],b=hitPaths[j];let crossing=false;
   for(let x=1;x<a.length&&!crossing;x++)for(let y=1;y<b.length&&!crossing;y++){
    if(intersectInterior(a[x-1],a[x],b[y-1],b[y],QA_LIMITS.edgeCrossingTolerancePx))crossing=true;
   }
   if(crossing){metrics.crossingPairs++;push(`EDGE_CROSS_${i}_${j}`,'warning','Bağlantı geometrisi',`Bağlantı ${i+1} ve ${j+1} birbirini kesiyor.`,{type:'edge',id:i},'Kesişme kasıtlıysa uyarıyı inceleyerek kabul et.');}
  }
  const graph=new Map(nodes.map(n=>[n.id,new Set()]));
  for(const e of edges){graph.get(e.from)?.add(e.to);graph.get(e.to)?.add(e.from)}
  for(const [id,links] of graph){if(!links.size){metrics.disconnectedNodes++;push(`GRAPH_ORPHAN_${id}`,'warning','Graf bütünlüğü',`${id} düğümünün bağlantısı yok.`,{type:'node',id})}}
  const seen=new Set(),stack=[nodes[0].id];while(stack.length){const id=stack.pop();if(seen.has(id))continue;seen.add(id);for(const to of graph.get(id)||[])stack.push(to)}
  if(seen.size<nodes.length)push('GRAPH_DISCONNECTED','warning','Graf bütünlüğü',`Graf ${nodes.length-seen.size} düğüme ana bileşenden ulaşamıyor.`,null,'Bu bağımsız alt sistemler için bilinçli olabilir.');
  const c=spec.minimaladam,arm=ARM[c.action]||ARM.connect;
  const hand=[c.x*W+arm[0]*(c.scale||1),c.y*H+arm[1]*(c.scale||1)];
  const match=nearestOnRoute(hand,hitPaths[c.edge]);if(match){metrics.maxContactDistancePx=round(match.distance);
   if(match.distance>QA_LIMITS.contactWarningPx)push('MINIMALADAM_CONTACT','warning','Karakter',`MinimalAdam’nin eli etkileştiği oka ${Math.ceil(match.distance)} px uzak.`,{type:'creature'},'Karakteri bağlantıya hizala.');}
  const creatureBox=[c.x*W-33*(c.scale||1),c.y*H-38*(c.scale||1),c.x*W+33*(c.scale||1),c.y*H+48*(c.scale||1)];
  for(const n of nodes)if(boundsOverlap(creatureBox,box(n),-4))push(`MINIMALADAM_NODE_${n.id}`,'warning','Karakter',`MinimalAdam, “${n.label}” kutusuyla örtüşebilir.`,{type:'creature'});
 }
 const summary={errors:issues.filter(x=>x.severity==='error').length,warnings:issues.filter(x=>x.severity==='warning').length,info:issues.filter(x=>x.severity==='info').length,automatedStatus:'PASS'};
 summary.automatedStatus=summary.errors?'FAIL':summary.warnings?'REVIEW':'PASS';
 return {version:QA_VERSION,subject:'P3/P4 teknik çizim',style:project?.style||'unknown',limits:{...QA_LIMITS},metrics,summary,issues,manualChecks:MANUAL.map(x=>({...x,status:'NOT_VERIFIED'})),disclaimer:'PASS yalnız tanımlı otomatik kuralların geçtiğini gösterir; özgünlük, anlam, kullanıcı algısı ve font render görünümü manuel kontrol gerektirir.'};
}
