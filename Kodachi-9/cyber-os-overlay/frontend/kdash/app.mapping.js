// KDASH: mapping loader/editor + accessibility enhancements
(function(){
  const CONFIG_PATH = 'config/node_map.yaml';
  // keep existing references
  const API_BASE = 'http://127.0.0.1:8765';
  const canvas = document.getElementById('three-canvas');
  const refreshBtn = document.getElementById('refreshTools');
  const checkHealthBtn = document.getElementById('checkHealth');
  const apiStatusEl = document.getElementById('apiStatus');
  const toolListEl = document.getElementById('toolList');
  const showAvailableOnly = document.getElementById('showAvailableOnly');
  const toggleRotateBtn = document.getElementById('toggleAutoRotate');
  const openMappingBtn = document.getElementById('openMapping');
  const mappingModal = document.getElementById('mappingModal');
  const mappingClose = document.getElementById('mappingClose');
  const mappingText = document.getElementById('mappingText');
  const mappingSave = document.getElementById('mappingSave');
  const mappingApply = document.getElementById('mappingApply');

  let nodeMap = {};

  // existing init (simplified) -- reuse previous app.js logic but add mapping integration
  // For brevity reuse the cube fallback only; GLTF loading from previous commit remains available through tryLoadModel

  // --- Three.js minimal scene setup ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setClearColor(0x000000, 0);
  const ambient = new THREE.AmbientLight(0xffffff, 0.7); scene.add(ambient);
  const dir = new THREE.DirectionalLight(0xffffff, 0.6); dir.position.set(5,5,5); scene.add(dir);

  function makeFaceTexture(text, colorBG='#071018', colorText='#00d1b2'){
    const size = 512; const c = document.createElement('canvas'); c.width = size; c.height = size; const ctx = c.getContext('2d');
    ctx.fillStyle = colorBG; ctx.fillRect(0,0,size,size);
    ctx.beginPath(); ctx.fillStyle = 'rgba(0,209,178,0.04)'; ctx.arc(size/2,size/2,size*0.45,0,Math.PI*2); ctx.fill();
    ctx.fillStyle = colorText; ctx.textAlign = 'center'; ctx.font = '48px monospace'; wrapText(ctx, text, size/2, size/2, 420, 28);
    return new THREE.CanvasTexture(c);
  }
  function wrapText(ctx, text, x, y, maxWidth, lineHeight){
    const words = text.split(' '); let line=''; let test=''; const lines=[]; for(let w of words){ test += w + ' '; if(ctx.measureText(test).width>maxWidth){ lines.push(line); line = w + ' '; test = w + ' '; } else { line += w + ' '; } } lines.push(line); const startY = y - (lines.length/2)*lineHeight + (lineHeight/2); for(let i=0;i<lines.length;i++) ctx.fillText(lines[i], x, startY + (i*lineHeight)); }

  const faces = [
    makeFaceTexture('Home Workspace'),
    makeFaceTexture('Security Workspace'),
    makeFaceTexture('Red Team Workspace'),
    makeFaceTexture('Forensics Workspace'),
    makeFaceTexture('Tools & Integrations'),
    makeFaceTexture('System & Status')
  ];
  const materials = faces.map(t => new THREE.MeshStandardMaterial({map:t}));
  const geometry = new THREE.BoxGeometry(3,3,3); const cube = new THREE.Mesh(geometry, materials); scene.add(cube);
  camera.position.z = 6; window.addEventListener('resize', ()=>{ const r = canvas.getBoundingClientRect(); renderer.setSize(r.width||window.innerWidth, r.height||window.innerHeight); camera.aspect = (r.width||window.innerWidth)/(r.height||window.innerHeight); camera.updateProjectionMatrix(); });

  let last = performance.now(); let autoRotate = true; function animate(now){ const dt = (now-last)/1000; last = now; if(autoRotate) { cube.rotation.x += 0.25*dt; cube.rotation.y += 0.4*dt; } renderer.render(scene, camera); requestAnimationFrame(animate); } requestAnimationFrame(animate);

  // Mapping loader
  async function loadNodeMap(){
    try{
      const r = await fetch(CONFIG_PATH, {cache:'no-cache'});
      if(!r.ok) throw new Error('not found');
      const text = await r.text();
      // simple YAML parse for our small format (no dependency). Accept key: value lines
      const lines = text.split('\n');
      const map = {};
      for(const line of lines){
        const t = line.trim(); if(!t || t.startsWith('#')) continue; const idx = t.indexOf(':'); if(idx<0) continue; const key = t.slice(0,idx).trim(); const val = t.slice(idx+1).trim(); if(key) map[key]=val;
      }
      nodeMap = map;
      mappingText.value = Object.entries(nodeMap).map(([k,v])=>`${k}: ${v}`).join('\n');
      console.info('Loaded node map', nodeMap);
    }catch(e){
      console.info('No mapping file found locally; using defaults');
    }
  }

  // Mapping editor
  openMappingBtn.addEventListener('click', ()=>{ mappingModal.setAttribute('aria-hidden','false'); mappingText.focus(); });
  mappingClose.addEventListener('click', ()=>{ mappingModal.setAttribute('aria-hidden','true'); });
  mappingApply.addEventListener('click', ()=>{ applyMappingFromText(mappingText.value); mappingModal.setAttribute('aria-hidden','true'); });
  mappingSave.addEventListener('click', ()=>{ downloadMapping(mappingText.value); });

  function applyMappingFromText(txt){ const map={}; const lines = txt.split('\n'); for(const line of lines){ const t=line.trim(); if(!t||t.startsWith('#')) continue; const idx=t.indexOf(':'); if(idx<0) continue; const key=t.slice(0,idx).trim(); const val=t.slice(idx+1).trim(); if(key) map[key]=val; } nodeMap = map; // reapply visuals (best-effort)
    applyMappingToScene();
  }

  function downloadMapping(txt){ const blob = new Blob([txt], {type:'text/yaml'}); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'node_map.yaml'; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url); }

  // Apply mapping to scene: find meshes whose names contain key fragments and set an initial emissive color based on category
  function applyMappingToScene(){
    const nodes = [];
    scene.traverse(n=>{ if(n.isMesh) nodes.push(n); });
    for(const n of nodes){
      const lname = (n.name||'').toLowerCase();
      let matched = false;
      for(const [frag, cat] of Object.entries(nodeMap)){
        if(!frag) continue;
        if(lname.includes(frag.toLowerCase())){
          matched = true;
          // color per category
          const color = categoryColor(cat);
          n.material = n.material || new THREE.MeshStandardMaterial();
          if(n.material && n.material.color) n.material.color.set(color.fill);
          if(n.material) n.material.emissive = new THREE.Color(color.emissive);
          break;
        }
      }
      if(!matched){
        // default appearance
        if(n.material && n.material.color) n.material.color.set(0x071018);
        if(n.material) n.material.emissive = new THREE.Color(0x002a22);
      }
    }
  }

  function categoryColor(cat){
    switch((cat||'').toLowerCase()){
      case 'home': return {fill:0x0b2f2a, emissive:0x003827};
      case 'system': return {fill:0x22120b, emissive:0x4a220a};
      case 'vcs': return {fill:0x071a2f, emissive:0x002a66};
      case 'network': return {fill:0x0b1a2f, emissive:0x002a6a};
      case 'ui': return {fill:0x08121a, emissive:0x003033};
      default: return {fill:0x071018, emissive:0x002a22};
    }
  }

  // Apply mapping after tools loaded to highlight missing tools
  function highlightByTools(tools){
    // group by category
    const byCat = {};
    for(const t of tools){ const c = (t.category||'misc'); if(!byCat[c]) byCat[c]=[]; byCat[c].push(t); }
    const nodes = []; scene.traverse(n=>{ if(n.isMesh) nodes.push(n); });
    for(const n of nodes){
      const lname = (n.name||'').toLowerCase();
      for(const [frag, cat] of Object.entries(nodeMap)){
        if(lname.includes(frag.toLowerCase())){
          const toolsInCat = byCat[cat]||[];
          const anyMissing = toolsInCat.some(tt=>!tt.available);
          if(n.material){
            n.material.emissive = new THREE.Color(anyMissing ? 0x481010 : 0x002a22);
            n.material.emissiveIntensity = anyMissing ? 0.6 : 0.12;
          }
          break;
        }
      }
    }
  }

  // --- API interactions ---
  async function checkHealth(){ try{ const r = await fetch(API_BASE + '/health', {cache:'no-cache'}); if(!r.ok) throw new Error('bad'); const j = await r.json(); apiStatusEl.textContent = 'OK — ' + JSON.stringify(j); apiStatusEl.style.color = '#00d1b2'; return true;}catch(e){ apiStatusEl.textContent = 'Unavailable'; apiStatusEl.style.color = '#ff6b6b'; return false;} }

  let lastTools = [];
  async function fetchTools(refresh=false){ toolListEl.innerHTML = '<li>Loading…</li>'; try{ const url = API_BASE + '/tools' + (refresh? '?refresh=true':''); const r = await fetch(url, {cache:'no-cache'}); if(!r.ok) throw new Error('bad'); const j = await r.json(); lastTools = j.tools || []; renderTools(lastTools); highlightByTools(lastTools); }catch(e){ toolListEl.innerHTML = '<li>Error loading tools — is the API running?</li>'; } }

  function renderTools(list){ const availOnly = showAvailableOnly.checked; toolListEl.innerHTML=''; if(!list.length){ toolListEl.innerHTML = '<li>No tools found</li>'; return; } list.forEach(t=>{ if(availOnly && !t.available) return; const li = document.createElement('li'); const name = document.createElement('div'); name.className='name'; name.textContent = t.name || t.id; const avail = document.createElement('div'); avail.className='avail'; avail.textContent = t.available ? 'available' : 'missing'; avail.style.color = t.available ? '#00d1b2' : '#ff6b6b'; li.appendChild(name); li.appendChild(avail); toolListEl.appendChild(li); }); }

  // UI wiring
  refreshBtn.addEventListener('click', ()=>fetchTools(true)); checkHealthBtn.addEventListener('click', ()=>checkHealth()); showAvailableOnly.addEventListener('change', ()=>fetchTools(false)); toggleRotateBtn.addEventListener('click', ()=>{ autoRotate = !autoRotate; toggleRotateBtn.textContent = autoRotate ? 'Toggle Rotate' : 'Resume Rotate'; });

  // initial
  loadNodeMap().then(()=>{ applyMappingToScene(); checkHealth().then(()=>fetchTools(false)); });

})();
