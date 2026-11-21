import json
D=json.load(open('dashboard_data.json',encoding='utf-8'))
data=json.dumps(D,ensure_ascii=False)
html = r'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Panel de control KPIs - Cadena de suministro (UAIN1008V)</title>
<style>
:root{--bg:#f4f6fa;--card:#fff;--ink:#1f2937;--mut:#6b7280;--az:#2F5597;--na:#ED7D31;--gr:#7F7F7F;--vd:#2e9e5b;--am:#e8a317;--rj:#d64545;--line:#e5e7eb}
@media (prefers-color-scheme:dark){:root{--bg:#111827;--card:#1f2937;--ink:#e5e7eb;--mut:#9ca3af;--line:#374151}}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;background:var(--bg);color:var(--ink);font-size:13px}
header{background:var(--az);color:#fff;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}
header h1{font-size:16px;margin:0}header small{opacity:.85}
nav{display:flex;gap:6px}nav button{border:0;padding:7px 14px;border-radius:6px;background:#ffffff33;color:#fff;cursor:pointer;font-size:13px}
nav button.on{background:#fff;color:var(--az);font-weight:bold}
.filters{display:flex;gap:12px;flex-wrap:wrap;padding:10px 16px;background:var(--card);border-bottom:1px solid var(--line);align-items:end}
.filters label{display:flex;flex-direction:column;font-size:11px;color:var(--mut);gap:3px}
select{padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);font-size:13px}
.filters button{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);cursor:pointer}
main{padding:12px 16px;max-width:1180px;margin:auto}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:8px;margin-bottom:10px}
.k{background:var(--card);border-radius:8px;padding:8px 10px;border-left:5px solid var(--gr);box-shadow:0 1px 2px #0001}
.k .n{font-size:11px;color:var(--mut)}.k .v{font-size:19px;font-weight:bold;margin:2px 0}.k .s{font-size:10.5px;color:var(--mut)}
.k.vd{border-color:var(--vd)}.k.am{border-color:var(--am)}.k.rj{border-color:var(--rj)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:10px}
.c{background:var(--card);border-radius:8px;padding:8px 10px;box-shadow:0 1px 2px #0001}
.c h3{margin:0 0 4px;font-size:12px}.c svg{width:100%;height:170px;display:block}
.q{font-size:11.5px;color:var(--mut);margin:10px 2px}.page{display:none}.page.on{display:block}
text{fill:var(--ink);font-size:10px}.axis{stroke:var(--line)}
</style></head><body>
<header><div><h1>Panel de control · Optimización de la cadena de suministro</h1><small>Ventas de consumo masivo, nov-2025 a oct-2026 · datos limpios (__N__ registros · 25 variables)</small></div>
<nav><button id="b1" class="on" onclick="pg(1)">Página 1 · Desempeño comercial</button><button id="b2" onclick="pg(2)">Página 2 · Inventario y Data Health</button></nav></header>
<div class="filters">
<label>País<select id="fp"></select></label><label>Canal<select id="fc"></select></label>
<label>Categoría<select id="fk"></select></label><label>Mes<select id="fm"></select></label>
<button onclick="reset()">Limpiar filtros</button><span id="cnt" style="color:var(--mut);font-size:11px"></span></div>
<main>
<div class="kpis" id="kpis"></div>
<div class="page on" id="p1"><div class="grid">
<div class="c"><h3>V1 · Ventas netas mensuales (millones S/)</h3><svg id="v1" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V2 · Ventas por categoría (millones S/)</h3><svg id="v2" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V3 · Mix de canal (% del valor)</h3><svg id="v3" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V4 · Ventas por país (millones S/)</h3><svg id="v4" viewBox="0 0 300 170"></svg></div>
</div><p class="q">Preguntas que responde: (1) ¿qué meses concentran la demanda? (2) ¿qué canal y país aportan más ventas y margen? (3) ¿cuánto pesa el canal tradicional frente al 68 % de referencia del caso? (4) ¿qué tan preciso es el pronóstico?</p></div>
<div class="page" id="p2"><div class="grid">
<div class="c"><h3>V5 · Tasa de quiebre por país (%)</h3><svg id="v5" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V6 · OTIF por país (%)</h3><svg id="v6" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V7 · Error de pronóstico WAPE por canal (%)</h3><svg id="v7" viewBox="0 0 300 170"></svg></div>
<div class="c"><h3>V8 · Data Health: nulos por variable en el dato crudo (%)</h3><svg id="v8" viewBox="0 0 300 170"></svg></div>
</div><p class="q">Preguntas que responde: (5) ¿dónde hay riesgo de desabastecimiento? (6) ¿qué país incumple entregas? (7) ¿en qué canal falla más el pronóstico? (8) ¿qué tan confiables eran los datos de origen? Los filtros aplican a V1–V7; Data Health muestra siempre el dato crudo.</p></div>
</main>
<script>
const D=__DATA__;const ROWS=D.clean;
const P=["Perú","Chile","Ecuador","Bolivia"],C=["Tradicional","Moderno","Mayorista","E-commerce"],K=["Alimentos","Cuidado del hogar","Cuidado personal"];
const MES=[...new Set(ROWS.map(r=>r.mes))].sort();
const COL=["#2F5597","#ED7D31","#7F7F7F","#70AD47"];
function fill(id,arr,all){const s=document.getElementById(id);s.innerHTML='<option value="">'+all+'</option>'+arr.map(x=>'<option>'+x+'</option>').join('');s.onchange=draw}
fill('fp',P,'Todos');fill('fc',C,'Todos');fill('fk',K,'Todas');fill('fm',MES,'Todos');
function reset(){['fp','fc','fk','fm'].forEach(i=>document.getElementById(i).value='');draw()}
function pg(n){[1,2].forEach(i=>{document.getElementById('p'+i).classList.toggle('on',i==n);document.getElementById('b'+i).classList.toggle('on',i==n)})}
const sum=(a,f)=>a.reduce((s,r)=>s+f(r),0);
const fmt=(x,d=1)=>x.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d});
function filt(skipMes){const p=fp.value,c=fc.value,k=fk.value,m=fm.value;return ROWS.filter(r=>(!p||r.pais==p)&&(!c||r.canal==c)&&(!k||r.categoria==k)&&(skipMes||!m||r.mes==m))}
function sem(v,t){// t: [tipo, verde, amarillo] tipo 'hi' = mayor es mejor, 'lo' = menor es mejor, 'rg' = rango
 if(t[0]=='hi')return v>=t[1]?'vd':(v>=t[2]?'am':'rj');if(t[0]=='lo')return v<=t[1]?'vd':(v<=t[2]?'am':'rj');return(v>=t[1]&&v<=t[2])?'vd':'am'}
function bar(id,labels,vals,fmtf,colors,horiz){const s=document.getElementById(id);const W=300,H=170,m={l:horiz?92:30,r:12,t:10,b:horiz?12:34};
 const mx=Math.max(...vals,1e-9)*1.12;let o='';
 if(horiz){const bh=(H-m.t-m.b)/vals.length;vals.forEach((v,i)=>{const w=(W-m.l-m.r)*v/mx;o+=`<text x="${m.l-4}" y="${m.t+i*bh+bh*.65}" text-anchor="end">${labels[i]}</text><rect x="${m.l}" y="${m.t+i*bh+2}" width="${Math.max(w,0)}" height="${bh-4}" fill="${colors?colors[i]:COL[0]}"/><text x="${m.l+w+3}" y="${m.t+i*bh+bh*.65}">${fmtf(v)}</text>`})}
 else{const bw=(W-m.l-m.r)/vals.length;o+=`<line class="axis" x1="${m.l}" x2="${W-m.r}" y1="${H-m.b}" y2="${H-m.b}"/>`;vals.forEach((v,i)=>{const h=(H-m.t-m.b)*v/mx;o+=`<rect x="${m.l+i*bw+4}" y="${H-m.b-h}" width="${bw-8}" height="${Math.max(h,0)}" fill="${colors?colors[i]:COL[0]}"/><text x="${m.l+i*bw+bw/2}" y="${H-m.b-h-3}" text-anchor="middle">${fmtf(v)}</text><text x="${m.l+i*bw+bw/2}" y="${H-m.b+12}" text-anchor="middle">${labels[i]}</text>`})}
 s.innerHTML=o}
function line(id,labels,vals){const s=document.getElementById(id);const W=300,H=170,m={l:34,r:10,t:12,b:26};const mx=Math.max(...vals,1e-9)*1.1,mn=0;
 const x=i=>m.l+i*(W-m.l-m.r)/Math.max(vals.length-1,1),y=v=>H-m.b-(H-m.t-m.b)*(v-mn)/(mx-mn);
 let o=`<line class="axis" x1="${m.l}" x2="${W-m.r}" y1="${H-m.b}" y2="${H-m.b}"/>`;
 [0,.5,1].forEach(f=>{const v=mx*f;o+=`<line class="axis" x1="${m.l}" x2="${W-m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l-3}" y="${y(v)+3}" text-anchor="end">${fmt(v,2)}</text>`});
 o+=`<polyline fill="none" stroke="${COL[0]}" stroke-width="2" points="${vals.map((v,i)=>x(i)+','+y(v)).join(' ')}"/>`;
 vals.forEach((v,i)=>{o+=`<circle cx="${x(i)}" cy="${y(v)}" r="2.6" fill="${COL[0]}"/>`;if(i%2==0)o+=`<text x="${x(i)}" y="${H-m.b+12}" text-anchor="middle">${labels[i].slice(2)}</text>`});s.innerHTML=o}
function draw(){
 const rs=filt(false),rm=filt(true);const n=rs.length;document.getElementById('cnt').textContent=n+' de '+ROWS.length+' registros';
 const V=sum(rs,r=>r.ventas_netas),cost=sum(rs,r=>r.costo_unitario*r.unidades_vendidas),U=sum(rs,r=>r.unidades_vendidas);
 const k={}; k.ventas=V; k.margen=V?(V-cost)/V*100:0; k.wape=U?sum(rs,r=>Math.abs(r.pronostico_unidades-r.unidades_vendidas))/U*100:0;
 k.quiebre=n?sum(rs,r=>r.dias_quiebre)/(30*n)*100:0; k.cob=U?sum(rs,r=>r.inventario_final)/(U/30):0; k.otif=sum(rs,r=>r.pedidos_totales)?sum(rs,r=>r.pedidos_a_tiempo)/sum(rs,r=>r.pedidos_totales)*100:0;
 const Vall=sum(rs,r=>r.ventas_netas);k.trad=Vall?sum(rs.filter(r=>r.canal=='Tradicional'),r=>r.ventas_netas)/Vall*100:0;
 const mm=MES.map(m=>sum(rm.filter(r=>r.mes==m),r=>r.ventas_netas));
 const cards=[
 ['K1 Ventas netas (S/ M)',fmt(V/1e6,2),'MoM último mes: '+(mm[11]&&mm[10]?fmt((mm[11]/mm[10]-1)*100,1)+' %':'n/d'),mm[11]&&mm[10]?sem((mm[11]/mm[10]-1)*100,['hi',0,-5]):'am'],
 ['K2 Margen bruto (%)',fmt(k.margen),'Verde ≥ 25 · amarillo 20–25',sem(k.margen,['hi',25,20])],
 ['K3 Error de pronóstico WAPE (%)',fmt(k.wape),'Verde ≤ 7 · amarillo ≤ 10',sem(k.wape,['lo',7,10])],
 ['K4 Tasa de quiebre (%)',fmt(k.quiebre),'Verde ≤ 5 · amarillo ≤ 8',sem(k.quiebre,['lo',5,8])],
 ['K5 Cobertura (días)',fmt(k.cob),'Verde 7–14',sem(k.cob,['rg',7,14])],
 ['K6 OTIF (%)',fmt(k.otif),'Verde ≥ 92 · amarillo ≥ 88',sem(k.otif,['hi',92,88])],
 ['K7 Peso canal tradicional (%)',fmt(k.trad),'Ref. caso: 68 %; verde ≥ 60',sem(k.trad,['hi',60,50])],
 ['Data Health (crudo)',fmt(D.dh.nulos,2)+' % nulos',fmt(D.dh.dup,1)+' % duplicados · limpio: 0 %','am']];
 document.getElementById('kpis').innerHTML=cards.map(c=>`<div class="k ${c[3]}"><div class="n">${c[0]}</div><div class="v">${c[1]}</div><div class="s">${c[2]}</div></div>`).join('');
 line('v1',MES,mm.map(v=>v/1e6));
 const kv=K.map(c=>sum(rs.filter(r=>r.categoria==c),r=>r.ventas_netas)/1e6);bar('v2',['Alimentos','Hogar','Personal'],kv,v=>fmt(v,2),[COL[0],COL[1],COL[2]]);
 bar('v3',C,C.map(c=>Vall?sum(rs.filter(r=>r.canal==c),r=>r.ventas_netas)/Vall*100:0),v=>fmt(v,1)+'%',COL,true);
 bar('v4',P,P.map(c=>sum(rs.filter(r=>r.pais==c),r=>r.ventas_netas)/1e6),v=>fmt(v,2),COL);
 const gp=c=>rs.filter(r=>r.pais==c);
 bar('v5',P,P.map(c=>{const g=gp(c);return g.length?sum(g,r=>r.dias_quiebre)/(30*g.length)*100:0}),v=>fmt(v,1),COL);
 bar('v6',P,P.map(c=>{const g=gp(c),t=sum(g,r=>r.pedidos_totales);return t?sum(g,r=>r.pedidos_a_tiempo)/t*100:0}),v=>fmt(v,1),COL);
 bar('v7',C,C.map(c=>{const g=rs.filter(r=>r.canal==c),u=sum(g,r=>r.unidades_vendidas);return u?sum(g,r=>Math.abs(r.pronostico_unidades-r.unidades_vendidas))/u*100:0}),v=>fmt(v,1),COL,true);
 const nl=Object.entries(D.nulos_raw).filter(e=>e[1]>0).sort((a,b)=>b[1]-a[1]).slice(0,7);
 bar('v8',nl.map(e=>e[0].replace('_unidades','').replace('_unitario','').replace('_dias','').slice(0,16)),nl.map(e=>e[1]),v=>fmt(v,1),null,true);
}
draw();
</script></body></html>'''
open('Panel_de_control_KPIs.html','w',encoding='utf-8').write(html.replace('__DATA__',data).replace('__N__',str(len(D['clean']))))
print(len(html)//1024,'KB')
