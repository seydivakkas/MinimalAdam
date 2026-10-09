import {W,H,MODES,KINDS,EDGES,ACCENTS,STYLES,clone,norm,clamp,esc,box,boundsOverlap,initialProject,unboxProject,validateSpec,exportSVG,importSVGText,snapMinimalAdam,route,nearestOnRoute,ARM} from './core.mjs';
import {SAMPLES} from './samples.mjs';
import {auditProject} from './quality.mjs';
const $=id=>document.getElementById(id);
const names={'architecture':'Yazılım mimarisi','data-flow':'Veri akışı','ml-pipeline':'Makine öğrenmesi hattı','engineering-system':'Mühendislik sistemi'};
const labels={client:'İstemci',process:'İşlem',service:'Servis',data:'Veri',model:'Model',sensor:'Sensör',actuator:'Eyleyici',system:'Sistem',result:'Sonuç'};
const edgeLabels={data:'Veri akışı',control:'Kontrol',feedback:'Geri besleme',physical:'Fiziksel etki'};
const styleLabels={sketch:'El çizimi',technical:'Teknik',contrast:'Kontrast'};
let project=initialProject(SAMPLES['03-ml-pipeline']);
let selected={type:'project'},history=[],redoStack=[],connectSource=null,tool='select',drag=null,zoom=1,grid=false;
let toastTimer;
let legacySourceNote=false;
function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),4200)}
function checkpoint(){history.push(JSON.stringify(project));if(history.length>70)history.shift();redoStack=[]}
function applyHistory(stackFrom,stackTo){if(!stackFrom.length)return;stackTo.push(JSON.stringify(project));project=JSON.parse(stackFrom.pop());selected={type:'project'};tool='select';connectSource=null;renderAll()}
function byId(id){return project.spec.nodes.find(n=>n.id===id)}
function select(type,id){selected={type,id};renderAll()}
function input(name,value,type='text',options=[],hint=''){
 const optionsHTML=options.map(o=>{const [v,label]=Array.isArray(o)?o:[o,o];return `<option value="${esc(v)}" ${String(value)===String(v)?'selected':''}>${esc(label)}</option>`}).join('');
 return `<div class="prop-group"><label class="prop-label" for="field-${esc(name)}">${esc(hint||name)}</label>${type==='select'?`<select id="field-${esc(name)}" data-field="${esc(name)}">${optionsHTML}</select>`:type==='textarea'?`<textarea id="field-${esc(name)}" data-field="${esc(name)}">${esc(value??'')}</textarea>`:`<input id="field-${esc(name)}" data-field="${esc(name)}" type="${type}" value="${esc(value??'')}" ${type==='number'?'step="0.01"':''}>`}</div>`
}
function inspector(){const s=project.spec;let html='';let tag='PROJE';
 if(selected.type==='node') {
  const n=byId(selected.id);if(!n){selected={type:'project'};return inspector()}
  tag='DÜĞÜM';html=`<h2>${esc(n.label)}</h2><p class="intro">Bir bileşenin adını, türünü, rengini ve boyutunu değiştir.</p>`;
  html+=input('label',n.label,'text',[],'Türkçe etiket')+input('kind',n.kind,'select',KINDS.map(x=>[x,labels[x]]),'Bileşen türü')+input('accent',n.accent||'black','select',ACCENTS.map(x=>[x,{black:'Siyah',orange:'Turuncu',red:'Kırmızı',blue:'Mavi'}[x]]),'Vurgu rengi');
  html+=`<div class="field-row">${input('x',(n.x*100).toFixed(2),'number',[],'X (%)')}${input('y',(n.y*100).toFixed(2),'number',[],'Y (%)')}</div><div class="field-row">${input('w',(n.w*100).toFixed(2),'number',[],'Genişlik (%)')}${input('h',(n.h*100).toFixed(2),'number',[],'Yükseklik (%)')}</div>`;
  html+=`<div class="info-box">ID: ${esc(n.id)}<br>Bağlantılar düğüm taşındığında otomatik yönlendirilir.</div>`;
 } else if(selected.type==='edge'){
  const e=s.edges[selected.id];if(!e){selected={type:'project'};return inspector()}
  tag='BAĞLANTI';html=`<h2>Bağlantı ${selected.id+1}</h2><p class="intro">Kaynak ve hedef uçları, tür, etiket ve isteğe bağlı ara noktaları değiştir.</p>`;
  const opts=s.nodes.map(n=>[n.id,`${n.label} (${n.id})`]);
  html+=input('from',e.from,'select',opts,'Kaynak')+input('to',e.to,'select',opts,'Hedef')+input('kind',e.kind||'data','select',EDGES.map(x=>[x,edgeLabels[x]]),'Bağlantı türü')+input('label',e.label||'','text',[],'Bağlantı etiketi (isteğe bağlı)');
  html+=`<div class="field-row">${input('from_port',e.from_port||'auto','select',[['auto','Otomatik'],...['left','right','top','bottom'].map(x=>[x,x])],'Kaynak port')}${input('to_port',e.to_port||'auto','select',[['auto','Otomatik'],...['left','right','top','bottom'].map(x=>[x,x])],'Hedef port')}</div>`;
  html+=input('via',JSON.stringify(e.via||[]),'textarea',[],'Ara noktalar (0–1 koordinatları)')+`<div class="info-box">Örnek: [[0.45,0.2],[0.7,0.2]]<br>Boş dizi otomatik rota kullanır.</div>`;
 } else if(selected.type==='creature') {
  const c=s.minimaladam;tag='MINIMALADAM';html='<h2>MinimalAdam karakteri</h2><p class="intro">Karakter ana bağlantıya gerçekten temas etmeli. Yeri değiştikçe bağlantıya tekrar hizalanabilir.</p>';
  html+=input('action',c.action||'connect','select',[['connect','Bağla'],['inspect','İncele'],['carry','Taşı'],['guard','Koru']],'Eylem')+input('edge',c.edge,'select',s.edges.map((e,i)=>[i,`${i+1} · ${e.from} → ${e.to}`]),'Etkileşilen bağlantı');
  html+=input('scale',c.scale||1,'number',[],'Ölçek (0.65–1.5)')+`<div class="prop-actions"><button id="snap">Bağlantıya hizala</button></div>`;
 } else {
  html='<h2>Proje ayarları</h2><p class="intro">Kaynak tanımlı teknik şema. Etiketleri ve çizim düzenini değiştir; sistem mimarisi uydurulmaz.</p>';
  html+=input('concept',s.concept,'textarea',[],'Kavramsal açıklama')+input('mode',s.mode,'select',MODES.map(x=>[x,names[x]]),'Teknik mod');
  html+=`<div class="info-box">Kaynak: P3 JSON v1<br>Çizim: 1600 × 900 · 16:9<br>Üretim: SVG + PNG + JSON<br>Seçili stil: ${esc(styleLabels[project.style])}</div>`;
 }
 $('selection-type').textContent=tag;$('properties').innerHTML=html;
}
function segmentHitsBox(p,q,b,pad=7){
 const [l,t,r,bt]=[b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad];
 if(Math.abs(p[0]-q[0])<.01)return l<=p[0]&&p[0]<=r&&Math.max(Math.min(p[1],q[1]),t)<Math.min(Math.max(p[1],q[1]),bt);
 if(Math.abs(p[1]-q[1])<.01)return t<=p[1]&&p[1]<=bt&&Math.max(Math.min(p[0],q[0]),l)<Math.min(Math.max(p[0],q[0]),r);
 for(let i=1;i<40;i++){const a=i/40,x=p[0]+(q[0]-p[0])*a,y=p[1]+(q[1]-p[1])*a;if(l<x&&x<r&&t<y&&y<bt)return true}return false;
}
let latestAudit=null;
let qaAcceptedSnapshot=null;
function quality(){
 const canvas=document.createElement('canvas').getContext('2d');
 const measureText=(text,size)=>{canvas.font=`${size}px Segoe UI, Arial, sans-serif`;return canvas.measureText(text).width};
 if($('qa-accept').checked&&qaAcceptedSnapshot!==JSON.stringify(project)){$('qa-accept').checked=false;qaAcceptedSnapshot=null;}
 latestAudit=auditProject(project,{measureText});
 const {issues,summary,manualChecks}=latestAudit;
 if(legacySourceNote)issues.push({id:'LEGACY_P3_SOURCE',severity:'warning',category:'Kaynak doğrulaması',message:'Eski P3 SVG kurtarma: mod/eylem bilgisi tam kanıtlanmadı; kaynak JSON ile kontrol et.',subject:null});
 const warnings=issues.filter(i=>i.severity==='warning').length,errors=issues.filter(i=>i.severity==='error').length;
 summary.errors=errors;summary.warnings=warnings;summary.automatedStatus=errors?'FAIL':warnings?'REVIEW':'PASS';
 const status=$('status');status.className=errors?'status-error':warnings?'status-warn':'status-ok';
 status.textContent=errors?`● ${errors} hata`:warnings?`● ${warnings} uyarı`:'● QA PASS';
 $('quality').innerHTML=errors?`<strong>QA FAIL:</strong> ${errors} hata. Dışa aktarma engellendi.`:warnings?`<strong>QA REVIEW:</strong> ${warnings} uyarı incelenmeli. Uyarılara rağmen dışa aktarmak için onay ver.`:'<strong>QA PASS:</strong> Tanımlı otomatik kontroller geçti. Anlam ve estetik ayrıca incelenmeli.';
 $('qa-counts').textContent=`${summary.automatedStatus} · ${errors} hata · ${warnings} uyarı`;
 $('qa-findings').innerHTML=issues.length?issues.map(i=>`<button type="button" class="qa-finding ${i.severity}" data-qa-id="${esc(i.id)}"><span>${i.severity==='error'?'HATA':'UYARI'} · ${esc(i.category)}</span><small>${esc(i.message)}</small></button>`).join(''):'<p class="qa-ok">Otomatik kurallarda sorun bulunmadı.</p>';
 $('qa-manual').textContent=`${manualChecks.length} manuel kontrol henüz doğrulanmadı.`;
 $('qa-preflight').hidden=warnings===0;
 $('qa-report').disabled=false;
 return {errors,warnings};
}
$('qa-findings').addEventListener('click',e=>{
 const el=e.target.closest('[data-qa-id]');if(!el)return;
 const item=latestAudit?.issues.find(x=>x.id===el.dataset.qaId);
 if(item?.subject){selected=item.subject;renderAll();}
});
$('qa-accept').addEventListener('change',()=>{qaAcceptedSnapshot=$('qa-accept').checked?JSON.stringify(project):null;});
$('qa-report').onclick=()=>{
 quality();latestAudit.provenance={mode:project.spec.mode,concept:project.spec.concept,sourceProject:JSON.parse(JSON.stringify(project)),warningsAcknowledged:!!($('qa-accept').checked&&qaAcceptedSnapshot===JSON.stringify(project))};downloadBlob(`${slug()}-qa-report.json`,new Blob([JSON.stringify(latestAudit,null,2)],{type:'application/json;charset=utf-8'}));
 toast('P5 kalite raporu JSON indirildi. Manuel maddeler doğrulanmadı.');
};

function renderCanvas(){const svg=$('diagram');let output;try{output=exportSVG(project)}catch(e){quality();toast(e.message);return}
 const parsed=new DOMParser().parseFromString(output,'image/svg+xml');svg.replaceChildren(...Array.from(parsed.documentElement.childNodes).map(x=>document.importNode(x,true)));
 if(selected.type==='node')svg.querySelectorAll('[data-node-id]').forEach(el=>el.classList.toggle('selected',el.getAttribute('data-node-id')===selected.id));
 if(selected.type==='edge')svg.querySelectorAll('[data-edge-index]').forEach(el=>el.classList.toggle('selected',+el.getAttribute('data-edge-index')===selected.id));
 if(selected.type==='creature')svg.querySelector('#minimaladam')?.classList.add('selected');
}
function renderAll(){renderCanvas();inspector();quality();$('project-label').textContent=names[project.spec.mode];$('concept-title').textContent=project.spec.concept;$('mode-label').textContent=names[project.spec.mode];$('counter').textContent=`${project.spec.nodes.length} düğüm · ${project.spec.edges.length} bağlantı`;document.querySelectorAll('[data-style]').forEach(b=>b.classList.toggle('selected',b.dataset.style===project.style));$('connect').classList.toggle('active',tool==='connect');$('interaction').textContent=tool==='connect'?(connectSource?`${byId(connectSource)?.label||connectSource} seçildi. Şimdi hedef düğüme tıkla.`:'Bağlamak için önce kaynak düğüme, sonra hedef düğüme tıkla.'):'Düğümü tutup taşıyabilir veya bir bağlantı seçebilirsin.';$('undo').disabled=!history.length;$('redo').disabled=!redoStack.length;}
function toWorld(event){const svg=$('diagram'),p=svg.createSVGPoint();p.x=event.clientX;p.y=event.clientY;const ctm=svg.getScreenCTM();if(!ctm)return [0,0];const q=p.matrixTransform(ctm.inverse());return [q.x,q.y]}
$('diagram').addEventListener('pointerdown',e=>{
 if(e.button!==0)return;
 const nodeEl=e.target.closest('[data-node-id]'),edgeEl=e.target.closest('[data-edge-index]'),c=e.target.closest('[data-creature]');
 if(nodeEl){const id=nodeEl.getAttribute('data-node-id');if(tool==='connect'){
   if(!connectSource){connectSource=id;renderAll();return}
   if(connectSource===id){toast('Kaynak ve hedef farklı olmalı');return}
   if(project.spec.edges.length>=12){toast('P3 en fazla 12 bağlantıyı destekler');return}
   if(project.spec.edges.some(e=>e.from===connectSource&&e.to===id&&e.kind==='data')){toast('Aynı veri bağlantısı zaten var');return}
   checkpoint();project.spec.edges.push({from:connectSource,to:id,kind:'data'});selected={type:'edge',id:project.spec.edges.length-1};tool='select';connectSource=null;renderAll();toast('Bağlantı eklendi');return;
 }
  selected={type:'node',id};const world=toWorld(e),n=byId(id);drag={type:'node',id,origin:[...world],initial:[n.x,n.y],before:JSON.stringify(project)};$('diagram').setPointerCapture(e.pointerId);renderAll();return;
 }
 if(c){selected={type:'creature'};const world=toWorld(e);drag={type:'creature',origin:world,initial:[project.spec.minimaladam.x,project.spec.minimaladam.y],before:JSON.stringify(project)};$('diagram').setPointerCapture(e.pointerId);renderAll();return}
 if(edgeEl){selected={type:'edge',id:+edgeEl.getAttribute('data-edge-index')};renderAll();return}
 if(tool==='connect'){connectSource=null;tool='select'}selected={type:'project'};renderAll();
});
$('diagram').addEventListener('pointermove',e=>{
 if(!drag)return;const world=toWorld(e),dx=(world[0]-drag.origin[0])/W,dy=(world[1]-drag.origin[1])/H;
 if(drag.type==='node'){const n=byId(drag.id);if(!n)return;n.x=norm(clamp(drag.initial[0]+dx,n.w/2+.04,1-n.w/2-.04));n.y=norm(clamp(drag.initial[1]+dy,n.h/2+.08,1-n.h/2-.08));snapMinimalAdam(project.spec)}
 if(drag.type==='creature'){const c=project.spec.minimaladam;c.x=norm(clamp(drag.initial[0]+dx,.065,.935));c.y=norm(clamp(drag.initial[1]+dy,.12,.9))}
 renderCanvas();quality();
});
function endDrag(){if(!drag)return;const original=drag.before;if(JSON.stringify(project)!==original){history.push(original);if(history.length>70)history.shift();redoStack=[]}drag=null;renderAll()}
$('diagram').addEventListener('pointerup',endDrag);$('diagram').addEventListener('pointercancel',endDrag);
$('properties').addEventListener('change',ev=>{
 const field=ev.target.dataset.field;if(!field)return;const value=ev.target.value;let obj=selected.type==='node'?byId(selected.id):selected.type==='edge'?project.spec.edges[selected.id]:selected.type==='creature'?project.spec.minimaladam:project.spec;
 if(!obj)return;
 let v=value;
 if(['x','y','w','h'].includes(field)){v=+value/100;if(!Number.isFinite(v)){toast('Sayısal değer gerekli');return}v=norm(v)}
 else if(field==='scale'){v=+value;if(!Number.isFinite(v)||v<.65||v>1.5){toast('Ölçek 0.65–1.5 olmalı');return}}
 else if(field==='edge'){v=+value}
 else if(field==='via'){try{v=JSON.parse(value);if(!Array.isArray(v)||v.length>6||v.some(p=>!Array.isArray(p)||p.length!==2||p.some(x=>!Number.isFinite(x)||x<=.0175||x>=.9825)))throw Error();}catch{toast('Ara noktalar [[0.4,0.2]] biçiminde olmalı');return}}
 else if(field==='from_port'||field==='to_port'){v=value==='auto'?undefined:value}
 else if(field==='label'||field==='concept'){
  v=value.normalize('NFC');if(/[<>\r\n\t]/.test(v)&&field==='label'){toast('Etiket tek satır olmalı');return}
  const lim=selected.type==='edge'?22:field==='label'?32:120;if(v.length>lim||!v.trim()){if(selected.type!=='edge'||v.length>lim){toast(`Metin en fazla ${lim} karakter olmalı`);return}}
 }
 if(['from','to'].includes(field)&&selected.type==='edge'){
   const other=field==='from'?'to':'from';if(v===obj[other]){toast('Kaynak ve hedef farklı olmalı');return}
 }
 checkpoint();if(v===undefined)delete obj[field];else obj[field]=v;
 if(selected.type==='node'||selected.type==='edge'||selected.type==='creature')snapMinimalAdam(project.spec);
 renderAll();
});
$('properties').addEventListener('click',e=>{if(e.target.id==='snap'){checkpoint();snapMinimalAdam(project.spec);renderAll();toast('MinimalAdam bağlantıya hizalandı')}});
$('add-node').onclick=()=>{
 const s=project.spec;if(s.nodes.length>=8){toast('P3 en fazla 8 düğüm destekler');return}
 const pts=[[.50,.73],[.25,.70],[.78,.7],[.5,.5],[.25,.47],[.77,.47],[.18,.25],[.8,.25],[.5,.25]];
 const w=.17,h=.16;let found=null;
 for(const [x,y] of pts){const n={x,y,w,h};if(box(n)[0]<64||box(n)[2]>W-64||box(n)[1]<70||box(n)[3]>H-70)continue;if(!s.nodes.some(old=>boundsOverlap(box(old),box(n),28))){found={x,y};break}}
 if(!found){toast('Yeterli boşluk yok: önce düğümleri taşı');return}
 let idx=1;while(s.nodes.some(n=>n.id===`yeni_${idx}`))idx++;
 const n={id:`yeni_${idx}`,label:'Yeni Düğüm',kind:'process',...found,w,h,accent:'black'};
 checkpoint();s.nodes.push(n);selected={type:'node',id:n.id};renderAll();toast('Yeni düğüm eklendi');
};
$('connect').onclick=()=>{tool=tool==='connect'?'select':'connect';connectSource=null;renderAll()};
function deleteSelected(){const s=project.spec;
 if(selected.type==='node'){
  if(s.nodes.length<=2){toast('En az 2 düğüm gerekli');return}
  const kept=s.edges.map((e,i)=>({...e,oldIndex:i})).filter(e=>e.from!==selected.id&&e.to!==selected.id);
  if(!kept.length){toast('Silme sonucunda hiç bağlantı kalmaz; önce bağlantı oluştur');return}
  checkpoint();const oldIndex=s.minimaladam.edge;s.nodes=s.nodes.filter(n=>n.id!==selected.id);s.edges=kept.map(({oldIndex,...e})=>e);const now=kept.findIndex(e=>e.oldIndex===oldIndex);s.minimaladam.edge=now>=0?now:0;snapMinimalAdam(s);
 }else if(selected.type==='edge'){
  if(s.edges.length<=1){toast('En az 1 bağlantı gerekli');return}
  checkpoint();s.edges.splice(selected.id,1);if(s.minimaladam.edge===selected.id)s.minimaladam.edge=0;else if(s.minimaladam.edge>selected.id)s.minimaladam.edge--;snapMinimalAdam(s);
 }else{toast('Önce bir düğüm veya bağlantı seç');return}
 selected={type:'project'};renderAll();toast('Seçim silindi');
}
$('delete').onclick=deleteSelected;$('undo').onclick=()=>applyHistory(history,redoStack);$('redo').onclick=()=>applyHistory(redoStack,history);
document.querySelectorAll('[data-style]').forEach(btn=>btn.onclick=()=>{if(project.style===btn.dataset.style)return;checkpoint();project.style=btn.dataset.style;renderAll()});
$('examples').onchange=()=>{project=initialProject(SAMPLES[$('examples').value]);legacySourceNote=false;history=[];redoStack=[];selected={type:'project'};tool='select';renderAll();toast('Örnek proje açıldı')};
$('grid').onclick=()=>{grid=!grid;$('canvas-wrap').classList.toggle('grid-active',grid);$('grid').style.color=grid?'#d2782f':''};
function setZoom(z){zoom=clamp(z,.6,2);$('canvas-size').style.width=`${zoom*100}%`;$('zoom-label').textContent=`${Math.round(zoom*100)}%`}
$('zoom-in').onclick=()=>setZoom(zoom+.2);$('zoom-out').onclick=()=>setZoom(zoom-.2);$('reset-view').onclick=()=>setZoom(1);
function downloadBlob(name,blob){const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(link.href),1200)}
const slug=()=>String(project.spec.mode||'diagram')+'-minimaladam';
function sourceWarning(){const results=quality();if(results.errors){toast('QA FAIL: Hatalar giderilmeden dışa aktarılamaz');return false}if(results.warnings&&(!$('qa-accept').checked||qaAcceptedSnapshot!==JSON.stringify(project))){toast(`QA REVIEW: ${results.warnings} uyarıyı incele ve onay kutusunu işaretle`);$('qa-accept').focus();return false}if(results.warnings)toast(`QA REVIEW: ${results.warnings} uyarı kabul edilerek aktarılıyor`);return true}
$('save-project').onclick=()=>{if(!sourceWarning())return;downloadBlob(`${slug()}.project.json`,new Blob([JSON.stringify(project,null,2)],{type:'application/json;charset=utf-8'}));toast('Düzenlenebilir proje kaydedildi')};
$('export-p3').onclick=()=>{if(!sourceWarning())return;downloadBlob(`${slug()}.json`,new Blob([JSON.stringify(project.spec,null,2)],{type:'application/json;charset=utf-8'}));toast('P3 JSON indirildi')};
$('export-svg').onclick=()=>{if(!sourceWarning())return;downloadBlob(`${slug()}.svg`,new Blob([exportSVG(project)],{type:'image/svg+xml;charset=utf-8'}));toast('Düzenlenebilir SVG indirildi (proje metadata içerir)')};
$('export-png').onclick=async()=>{if(!sourceWarning())return;try{
 const txt=exportSVG(project);const svgblob=new Blob([txt],{type:'image/svg+xml;charset=utf-8'});const url=URL.createObjectURL(svgblob);
 const image=new Image();await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('SVG rasterize edilemedi'));image.src=url});
 const canvas=document.createElement('canvas');canvas.width=W;canvas.height=H;const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);ctx.drawImage(image,0,0,W,H);URL.revokeObjectURL(url);
 const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!blob)throw Error('PNG oluşturulamadı');downloadBlob(`${slug()}.png`,blob);toast('PNG kaydedildi');
 }catch(e){toast('PNG hatası: '+e.message)}};
$('import').onclick=()=>$('file').click();
$('file').onchange=async e=>{const file=e.target.files?.[0];if(!file)return;
 try{const text=await file.text();const pr=file.name.toLowerCase().endsWith('.svg')?importSVGText(text):unboxProject(JSON.parse(text));
  project=pr;legacySourceNote=file.name.toLowerCase().endsWith('.svg')&&!text.includes('minimaladam-editable-spec')&&!text.includes('xiaohei-editable-spec');selected={type:'project'};history=[];redoStack=[];tool='select';connectSource=null;renderAll();toast(legacySourceNote?'Eski P3 SVG yaklaşık içe aktarıldı. Mod/eylem bilgisini JSON ile karşılaştır.':file.name.toLowerCase().endsWith('.svg')?'P4 SVG tüm proje verisiyle içe aktarıldı':'Proje yüklendi');
 }catch(err){toast('Dosya açılamadı: '+err.message)}finally{e.target.value=''};
};
document.addEventListener('keydown',e=>{
 const el=document.activeElement;if(el?.matches('input,select,textarea')||el?.isContentEditable)return;
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();applyHistory(e.shiftKey?redoStack:history,e.shiftKey?history:redoStack)}
 else if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='y'){e.preventDefault();applyHistory(redoStack,history)}
 else if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();deleteSelected()}
 else if(e.key.toLowerCase()==='n')$('add-node').click();
 else if(e.key.toLowerCase()==='c')$('connect').click();
 else if(e.key==='Escape'){selected={type:'project'};tool='select';connectSource=null;renderAll()}
});
renderAll();
