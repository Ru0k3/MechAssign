const svg = document.getElementById('city-map');
const popup = document.getElementById('popup');
const damage = document.getElementById('damage-type');
const answer = document.getElementById('answer');
const questionLabel = document.getElementById('question-label');
const logs = document.getElementById('logs');
const stage = document.getElementById('stage');
const delayButton = document.getElementById('delay-button');
const requestPanel = document.getElementById('request-panel');
let city = null;
let selected = {road_id:null, position:null};
let lastPlan = null;
let lastCoordination = null;
let lastShopName = '';
let lastPartsSource = '';

function renderCoordination(){
  const technicianEta=lastCoordination.technician_eta;
  const partsEta=lastCoordination.parts_eta;
  requestPanel.replaceChildren();
  const shop=document.createElement('strong');
  shop.textContent=lastShopName;
  const details=document.createElement('span');
  details.className='muted';
  details.append(document.createTextNode('Technician ETA '+technicianEta.toFixed(1)+' min · parts from '+lastPartsSource+' ETA '+partsEta.toFixed(1)+' min'));
  details.append(document.createElement('br'));
  details.append(document.createTextNode('Repair ready in '+Math.max(technicianEta,partsEta).toFixed(1)+' min'));
  requestPanel.append(shop,document.createElement('br'),details);
}

function node(id){ for(const item of city.nodes){ if(item.id===id) return item; } return null; }
function make(tag, attrs, text=''){ const item=document.createElementNS('http://www.w3.org/2000/svg',tag); for(const key in attrs){item.setAttribute(key,attrs[key]);} item.textContent=text; return item; }
function roadPath(points, cls){
  let d='';
  for(let i=0;i<points.length;i++){ d+=(i===0?'M ':' L ')+points[i].x+' '+points[i].y; }
  return make('path',{d,class:cls});
}
function label(x,y,text,cls){ return make('text',{x,y,class:cls},text); }
function edgeBetween(first,second){
  for(const edge of city.edges){
    if((edge.node_a===first&&edge.node_b===second)||(edge.node_a===second&&edge.node_b===first)) return edge;
  }
  return null;
}

function drawMap(){
  svg.replaceChildren();
  svg.appendChild(make('rect',{x:0,y:0,width:540,height:420,class:'maze-background'}));
  const defs=make('defs',{});
  const grid=make('pattern',{id:'maze-grid',width:24,height:24,patternUnits:'userSpaceOnUse'});
  grid.appendChild(make('path',{d:'M 24 0 L 0 0 0 24',class:'grid-line'}));
  defs.appendChild(grid);
  svg.appendChild(defs);
  svg.appendChild(make('rect',{x:0,y:0,width:540,height:420,fill:'url(#maze-grid)',class:'maze-grid'}));
  svg.appendChild(label(24,30,'MAZE DISTRICT  /  ROUTE NETWORK','zone-label'));
  svg.appendChild(label(24,402,'38 NODES  ·  MULTIPLE ROUTES  ·  WEIGHTED CORRIDORS','map-caption'));
  for(const edge of city.edges){
    const points=[];
    if(edge.geometry){ for(const point of edge.geometry){points.push(point);} }
    else {points.push(node(edge.node_a),node(edge.node_b));}
    svg.appendChild(roadPath(points,'corridor-shadow'));
    svg.appendChild(roadPath(points,'corridor'));
    const target=roadPath(points,'hit-road');
    target.dataset.roadId=edge.road_id;
    target.addEventListener('click',event=>openPopup(edge.road_id,node(edge.node_a),node(edge.node_b),event));
    svg.appendChild(target);
    const mid=points[Math.floor((points.length-1)/2)];
    const next=points[Math.floor((points.length-1)/2)+1]||points[points.length-1];
    const midX=(mid.x+next.x)/2, midY=(mid.y+next.y)/2;
    const roadLabel=label(midX,midY,edge.road_id,'road-label');
    roadLabel.setAttribute('text-anchor','middle');
    roadLabel.setAttribute('dominant-baseline','middle');
    roadLabel.style.pointerEvents='none';
    svg.appendChild(roadLabel);
  }
  for(const item of city.nodes){
    svg.appendChild(make('circle',{cx:item.x,cy:item.y,r:3,class:'junction'}));
    const nodeLabel=label(item.x,item.y-6,item.id,'node-label');
    nodeLabel.setAttribute('text-anchor','middle');
    svg.appendChild(nodeLabel);
  }
  for(const entity of window.entities){
    const n=node(entity.location); if(!n) continue;
    const group=make('g',{class:'entity-marker'});
    group.appendChild(make('circle',{cx:n.x,cy:n.y,r:8,class:entity.type==='store'?'store-marker':'shop-marker'}));
    group.appendChild(label(n.x+11,n.y+4,entity.id,'entity-label'));
    svg.appendChild(group);
  }
}

function openPopup(roadId,a,b,event){
  const point=svg.createSVGPoint(); point.x=event.clientX; point.y=event.clientY;
  const local=point.matrixTransform(svg.getScreenCTM().inverse());
  const denominator=(b.x-a.x)**2+(b.y-a.y)**2;
  let t=((local.x-a.x)*(b.x-a.x)+(local.y-a.y)*(b.y-a.y))/denominator;
  t=Math.max(0,Math.min(1,t));
  selected={road_id:roadId,position:{x:a.x+t*(b.x-a.x),y:a.y+t*(b.y-a.y)}};
  document.getElementById('selected-road').textContent=roadId+' selected';
  popup.classList.remove('hidden');
}

function renderRoutes(result){
  const drawnRoutes=[];
  for(const key of ['shop_route','store_route']){
    const route=result[key]; if(!route) continue;
    const color=key==='shop_route'?'tech':'parts';
    for(let i=0;i<route.path.length-1;i++){
      const edge=edgeBetween(route.path[i],route.path[i+1]);
      let points=[node(route.path[i]),node(route.path[i+1])];
      if(edge && edge.geometry){ points=edge.node_a===route.path[i]?edge.geometry:edge.geometry.slice().reverse(); }
      const item=roadPath(points,'route '+color);
      item.style.strokeDasharray='10 7'; item.style.strokeDashoffset='0'; svg.appendChild(item); drawnRoutes.push(item);
      let offset=0; const timer=setInterval(()=>{offset-=2;item.style.strokeDashoffset=offset;if(offset<-90)clearInterval(timer);},25);
    }
  }
  svg.appendChild(make('circle',{cx:selected.position.x,cy:selected.position.y,r:10,class:'breakdown-marker'}));
  svg.appendChild(label(selected.position.x+14,selected.position.y+4,'BREAKDOWN','breakdown-label'));
  setTimeout(()=>{ for(const route of drawnRoutes){route.remove();} stage.textContent='Repair complete — route cleared'; },5000);
}

async function dispatch(){
  popup.classList.add('hidden'); stage.textContent='Running forward chaining…';
  const payload={...selected,damage_type:damage.value,answers:{follow_up:answer.value},has_part:document.getElementById('has-part').checked};
  const response=await fetch('/dispatch',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const result=await response.json();
  if(result.error){stage.textContent=result.error;return;}
  lastPlan=result.plan; lastCoordination=result.coordination; logs.textContent='';
  for(const item of result.logs){logs.textContent+=item+'\n';stage.textContent=item.split(']')[0].replace('[','')+'…';await new Promise(resolve=>setTimeout(resolve,30));}
  renderRoutes(result); delayButton.disabled=false;
  lastShopName=result.shop.name;
  lastPartsSource=result.store?result.store.name:'vehicle';
  renderCoordination();
  stage.textContent='Plan ready — routes synchronized';
}

async function simulateDelay(){
  delayButton.disabled=true;
  stage.textContent='Replanning after a 10-minute technician delay…';
  try{
    const previousCoordination=lastCoordination;
    const delayMinutes=10;
    const response=await fetch('/simulate-delay',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
      plan:lastPlan,
      completed_actions:['diagnose','assign shop'],
      reason:'technician held at previous job',
      technician_eta:previousCoordination.technician_eta,
      parts_eta:previousCoordination.parts_eta,
      delay_minutes:delayMinutes
    })});
    const result=await response.json();
    if(!response.ok){throw new Error(result.error||'The server could not replan the dispatch.');}
    if(!result.updated_coordination){throw new Error('The server did not return updated arrival coordination.');}

    lastPlan=result.steps;
    lastCoordination=result.updated_coordination;
    renderCoordination();
    const technicianEta=lastCoordination.technician_eta;
    const partsEta=lastCoordination.parts_eta;
    const remaining=result.steps.map(step=>step.action);
    logs.textContent+='\n[SIMULATION] Technician delayed by '+delayMinutes+' min: technician held at previous job.\n'
      +'[ETA UPDATE] Technician: '+previousCoordination.technician_eta.toFixed(1)+' → '+technicianEta.toFixed(1)+' min; parts: '+partsEta.toFixed(1)+' min.\n'
      +'[REPLAN] Remaining actions: '+(remaining.length?remaining.join(', '):'none')+'. Repair ready in '+Math.max(technicianEta,partsEta).toFixed(1)+' min.\n';
    stage.textContent='Delay applied — repair now ready in '+Math.max(technicianEta,partsEta).toFixed(1)+' min';
  }catch(error){
    const message=error instanceof Error?error.message:'Unexpected replanning error.';
    logs.textContent+='\n[ERROR] '+message+'\n';
    stage.textContent='Replan failed: '+message;
  }finally{
    delayButton.disabled=false;
  }
}

damage.addEventListener('change',()=>{questionLabel.firstChild.textContent=' '+(window.questions[damage.value]||'Follow-up answer');});
document.getElementById('close-popup').onclick=()=>popup.classList.add('hidden');
document.getElementById('dispatch-button').onclick=dispatch;
delayButton.onclick=simulateDelay;
Promise.all([fetch('/api/questions').then(r=>r.json()),fetch('/api/entities').then(r=>r.json()),fetch('/api/city').then(r=>r.json())]).then(([questions,entities,map])=>{
  window.questions=questions; window.entities=entities; city=map;
  for(const key of Object.keys(questions)){const option=document.createElement('option');option.value=key;option.textContent=key;damage.appendChild(option);}
  drawMap();
});