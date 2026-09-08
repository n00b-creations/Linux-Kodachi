// KDASH app logic with GLTF model integration + three.js
(function(){
  const API_BASE = 'http://127.0.0.1:8765';
  const canvas = document.getElementById('three-canvas');
  const refreshBtn = document.getElementById('refreshTools');
  const checkHealthBtn = document.getElementById('checkHealth');
  const apiStatusEl = document.getElementById('apiStatus');
  const toolListEl = document.getElementById('toolList');
  const showAvailableOnly = document.getElementById('showAvailableOnly');
  const toggleRotateBtn = document.getElementById('toggleAutoRotate');

  let autoRotate = true;

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

  // Attempt to load a rich GLTF model and replace the cube
  const MODEL_PATH = 'assets/models/dashboard_model.glb';
  const REMOTE_FALLBACK = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Cube/glTF-Binary/Cube.glb';

  function tryLoadModel(){
    if(typeof THREE.GLTFLoader === 'undefined'){
      console.warn('GLTFLoader not available; skipping model load');
      return;
    }
    const loader = new THREE.GLTFLoader();
    // optional: configure DRACO if present
    try{
      if(typeof THREE.DRACOLoader !== 'undefined'){
        const dracoLoader = new THREE.DRACOLoader();
        // set decoder path to CDN
        dracoLoader.setDecoderPath('https://unpkg.com/three@0.152.2/examples/js/libs/draco/');
        loader.setDRACOLoader(dracoLoader);
      }
    }catch(e){console.warn('DRACO not configured', e)}

    loader.load(MODEL_PATH, gltf => {
      console.info('Loaded local model', MODEL_PATH);
      replaceWithModel(gltf.scene);
    }, undefined, err => {
      console.warn('Local model failed, trying remote fallback', err);
      // try remote
      loader.load(REMOTE_FALLBACK, gltf => {
        console.info('Loaded remote model fallback');
        replaceWithModel(gltf.scene);
      }, undefined, e2 => {
        console.warn('Failed to load fallback model', e2);
        // nothing to do; keep cube
      });
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
    // attempt to map some named meshes to tool categories
    mapModelNodesToFaces(model);
  }

  function mapModelNodesToFaces(model){
    const names = ['home','system','vcs','network','ui','misc'];
    // collect mesh nodes
    const meshes = [];
    model.traverse(node=>{ if(node.isMesh) meshes.push(node); });
    // assign first up to 6 meshes
    for(let i=0;i<Math.min(6, meshes.length); i++){
      const m = meshes[i];
      // apply an initial label texture onto the material
      const label = makeFaceTextureSimple(m.name || names[i]);
      m.material = new THREE.MeshStandardMaterial({map:label});
      m.material.needsUpdate = true;
    }
  }

  function makeFaceTextureSimple(text){
    const size = 512; const c = document.createElement('canvas'); c.width = size; c.height = size; const ctx = c.getContext('2d');
    ctx.fillStyle = '#071018'; ctx.fillRect(0,0,size,size);
    ctx.fillStyle = '#00d1b2'; ctx.textAlign = 'center'; ctx.font = '36px monospace';
    ctx.fillText(text, size/2, size/2);
    return new THREE.CanvasTexture(c);
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
      renderTools(j.tools || []);
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
