// KDASH app logic with GLTF model integration + DRACO decoder support + inspector UI
(function(){
  const API_BASE = 'http://127.0.0.1:8765';
  const canvas = document.getElementById('three-canvas');
  const refreshBtn = document.getElementById('refreshTools');
  const checkHealthBtn = document.getElementById('checkHealth');
  const apiStatusEl = document.getElementById('apiStatus');
  const toolListEl = document.getElementById('toolList');
  const showAvailableOnly = document.getElementById('showAvailableOnly');
  const toggleRotateBtn = document.getElementById('toggleAutoRotate');
  const inspectModal = document.getElementById('inspectModal');
  const modalClose = document.getElementById('modalClose');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');

  let autoRotate = true;
  let lastTools = [];

  // --- Three.js scene ---
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setClearColor(0x000000, 0);

  // Lighting
  const ambient = new THREE.AmbientLight(0xffffff, 0.7);
  scene.add(ambient);
  const dir = new THREE.DirectionalLight(0xffffff, 0.6);
  dir.position.set(5,5,5);
  scene.add(dir);

  // Raycaster for inspector
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();

  // Fallback cube (used while model loads or if loading fails)
  function makeFaceTexture(text, colorBG='#071018', colorText='#00d1b2'){
    const size = 512;
    const c = document.createElement('canvas');
    c.width = size; c.height = size;
    const ctx = c.getContext('2d');
    // background
    ctx.fillStyle = colorBG; ctx.fillRect(0,0,size,size);
    // glow circle
    ctx.beginPath(); ctx.fillStyle = 'rgba(0,209,178,0.04)'; ctx.arc(size/2,size/2,size*0.45,0,Math.PI*2); ctx.fill();
    // text
    ctx.fillStyle = colorText; ctx.textAlign = 'center'; ctx.font = '48px monospace';
    wrapText(ctx, text, size/2, size/2, 420, 28);
    return new THREE.CanvasTexture(c);
  }

  function wrapText(ctx, text, x, y, maxWidth, lineHeight){
    const words = text.split(' ');
    let line = '';
    let testLine = '';
    let lineArray = [];
    for(let n=0;n<words.length;n++){
      testLine += words[n] + ' ';
      const metrics = ctx.measureText(testLine);
      if(metrics.width > maxWidth){
        lineArray.push(line);
        line = words[n] + ' ';
        testLine = words[n] + ' ';
      } else {
        line += words[n] + ' ';
      }
    }
    lineArray.push(line);
    const startY = y - (lineArray.length/2)*lineHeight + (lineHeight/2);
    for(let i=0;i<lineArray.length;i++){
      ctx.fillText(lineArray[i], x, startY + (i*lineHeight));
    }
  }

  const faces = [
    makeFaceTexture('Home Workspace'),
    makeFaceTexture('Security Workspace'),
    makeFaceTexture('Red Team Workspace'),
    makeFaceTexture('Forensics Workspace'),
    makeFaceTexture('Tools & Integrations'),
    makeFaceTexture('System & Status')
  ];

  const materials = faces.map(t => new THREE.MeshStandardMaterial({map:t}));
  const geometry = new THREE.BoxGeometry(3,3,3);
  const cube = new THREE.Mesh(geometry, materials);
  scene.add(cube);

  camera.position.z = 6;

  function onResize(){
    const rect = canvas.getBoundingClientRect();
    const w = rect.width || window.innerWidth; const h = rect.height || window.innerHeight;
    renderer.setSize(w,h);
    camera.aspect = w/h; camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', onResize);
  onResize();

  let last = performance.now();
  function animate(now){
    const dt = (now - last)/1000; last = now;
    if(autoRotate){
      cube.rotation.x += 0.25*dt;
      cube.rotation.y += 0.4*dt;
    }
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  // pointer interaction
  canvas.addEventListener('pointerdown', (ev)=>{
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = - ((ev.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);
    if(intersects.length){
      const mesh = intersects[0].object;
      inspectMesh(mesh);
    }
  });

  function inspectMesh(mesh){
    // climb to top-most named parent
    let node = mesh;
    while(node && !node.name && node.parent) node = node.parent;
    const name = node && node.name ? node.name : mesh.name || 'unknown';
    // map name to category heuristics
    const category = guessCategoryFromName(name);
    showInspector(name, category);
  }

  function guessCategoryFromName(name){
    const n = name.toLowerCase();
    if(n.includes('home')) return 'home';
    if(n.includes('sys') || n.includes('system')) return 'system';
    if(n.includes('git') || n.includes('vcs')) return 'vcs';
    if(n.includes('net') || n.includes('router') || n.includes('network')) return 'network';
    if(n.includes('ui') || n.includes('dashboard') || n.includes('screen')) return 'ui';
    return 'misc';
  }

  function showInspector(nodeName, category){
    modalTitle.textContent = `Inspect: ${nodeName}`;
    const tools = lastTools.filter(t=> (t.category || 'misc') === category);
    if(!tools.length){
      modalBody.innerHTML = `<p>No tools mapped to category <strong>${category}</strong>.</p>`;
    } else {
      const ul = document.createElement('ul');
      tools.forEach(t=>{
        const li = document.createElement('li');
        li.textContent = `${t.name || t.id} — ${t.executable || ''} — ${t.available ? 'available' : 'missing'}`;
        ul.appendChild(li);
      });
      modalBody.innerHTML = '';
      modalBody.appendChild(ul);
    }
    inspectModal.setAttribute('aria-hidden','false');
  }
  modalClose.addEventListener('click', ()=>inspectModal.setAttribute('aria-hidden','true'));

  // Attempt to load a rich GLTF model and replace the cube
  const LOCAL_MODEL = 'assets/models/dashboard_model.glb';
  const RICH_MODEL = 'assets/models/dashboard_model_rich.glb';
  const REMOTE_FALLBACK = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Avocado/glTF-Binary/Avocado.glb';

  function tryLoadModel(){
    if(typeof THREE.GLTFLoader === 'undefined'){
      console.warn('GLTFLoader not available; skipping model load');
      return;
    }
    const loader = new THREE.GLTFLoader();
    // configure DRACO loader to use local assets if present, else CDN
    try{
      const dracoPathLocal = 'assets/draco/';
      // check if local draco files exist (best-effort)
      fetch(dracoPathLocal + 'draco_decoder.js', {method:'HEAD'}).then(res=>{
        if(res.ok && typeof THREE.DRACOLoader !== 'undefined'){
          const dracoLoader = new THREE.DRACOLoader();
          dracoLoader.setDecoderPath(dracoPathLocal);
          loader.setDRACOLoader(dracoLoader);
        }
      }).catch(()=>{
        // fallback to CDN decoder path
        if(typeof THREE.DRACOLoader !== 'undefined'){
          const dracoLoader = new THREE.DRACOLoader();
          dracoLoader.setDecoderPath('https://unpkg.com/three@0.152.2/examples/js/libs/draco/');
          loader.setDRACOLoader(dracoLoader);
        }
      }).finally(()=>{
        // try local model first, then rich, then remote
        attemptLoadSequence(loader, [LOCAL_MODEL, RICH_MODEL, REMOTE_FALLBACK]);
      });
    }catch(e){
      console.warn('DRACO not configured', e);
      attemptLoadSequence(loader, [LOCAL_MODEL, RICH_MODEL, REMOTE_FALLBACK]);
    }
  }

  function attemptLoadSequence(loader, list){
    if(!list.length) return;
    const url = list.shift();
    loader.load(url, gltf => {
      console.info('Loaded model', url);
      replaceWithModel(gltf.scene);
    }, undefined, err => {
      console.warn('Failed to load', url, err);
      attemptLoadSequence(loader, list);
    });
  }

  function replaceWithModel(model){
    // Remove cube
    scene.remove(cube);
    // Basic fit/scale
    model.position.set(0, -0.5, 0);
    const bbox = new THREE.Box3().setFromObject(model);
    const size = bbox.getSize(new THREE.Vector3()).length();
    const scale = 3.2 / size;
    model.scale.setScalar(scale * 0.95);
    scene.add(model);
    // store model on global for mapping
    window.kdash_model = model;
    // make clickable by ensuring meshes cast/receive
    model.traverse(node=>{ if(node.isMesh){ node.castShadow=true; node.receiveShadow=true; } });
  }

  tryLoadModel();

  // toggle rotate
  toggleRotateBtn.addEventListener('click', ()=>{autoRotate = !autoRotate; toggleRotateBtn.textContent = autoRotate ? 'Toggle Rotate' : 'Resume Rotate';});

  // --- API interactions ---
  async function checkHealth(){
    try{
      const r = await fetch(API_BASE + '/health', {cache:'no-cache'});
      if(!r.ok) throw new Error('bad');
      const j = await r.json();
      apiStatusEl.textContent = 'OK — ' + JSON.stringify(j);
      apiStatusEl.style.color = '#00d1b2';
      return true;
    }catch(e){
      apiStatusEl.textContent = 'Unavailable';
      apiStatusEl.style.color = '#ff6b6b';
      return false;
    }
  }

  async function fetchTools(refresh=false){
    toolListEl.innerHTML = '<li>Loading…</li>';
    try{
      const url = API_BASE + '/tools' + (refresh? '?refresh=true':'');
      const r = await fetch(url, {cache:'no-cache'});
      if(!r.ok) throw new Error('bad');
      const j = await r.json();
      lastTools = j.tools || [];
      renderTools(lastTools);
    }catch(e){
      toolListEl.innerHTML = '<li>Error loading tools — is the API running?</li>';
    }
  }

  function renderTools(list){
    const availOnly = showAvailableOnly.checked;
    toolListEl.innerHTML = '';
    if(!list.length){ toolListEl.innerHTML = '<li>No tools found</li>'; return; }
    list.forEach(t =>{
      if(availOnly && !t.available) return;
      const li = document.createElement('li');
      const name = document.createElement('div'); name.className='name'; name.textContent = t.name || t.id;
      const avail = document.createElement('div'); avail.className='avail'; avail.textContent = t.available ? 'available' : 'missing';
      avail.style.color = t.available ? '#00d1b2' : '#ff6b6b';
      li.appendChild(name); li.appendChild(avail);
      toolListEl.appendChild(li);
    });
  }

  // wire up UI
  refreshBtn.addEventListener('click', ()=>fetchTools(true));
  checkHealthBtn.addEventListener('click', ()=>checkHealth());
  showAvailableOnly.addEventListener('change', ()=>fetchTools(false));

  // initial load
  checkHealth().then(()=>fetchTools(false));

})();
