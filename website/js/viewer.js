/* ============================================================
   BabyBox v3 "Tower" — interactive 3D viewer
   Loads the real OpenSCAD-exported STLs, lets you orbit/zoom,
   and toggles the internal electronics (ghosting the shell so
   you can see inside) and an exploded view.
   ============================================================ */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const MODELS = 'models/';

// Site palette
const C = {
  body:    0xEFE7D6,
  tray:    0xE2D8C2,
  top:     0x4ECDC4,
  lid:     0xFFE66D,
  keycap:  0xFF6B6B,
  diffuser:0xFFFFFF,
};

// Hub (figurine hole) center and the stack heights — kept in sync with the
// SCAD assembly(): box 90x90, body_h 32, top_plate_h 10, well_floor 5.
const HX = 45, HY = 50;          // figurine hole center
const Z_TOP = 47;                // top of the body = bottom of the top plate
const BTN1 = 28, BTN2 = 62, BTN_Y = 15;

// Printed parts: file, color, base position (mm, Z-up — matches the SCAD
// assembly() offsets), an explode vector, and whether it's the ghostable shell.
const PARTS = [
  { key:'tray',     file:'v3-tray.stl',        color:C.tray, pos:[0,0,0],         explode:[0,0,-30], shell:true },
  { key:'body',     file:'v3-body.stl',        color:C.body, pos:[0,0,5],         explode:[0,0,-10], shell:true },
  { key:'top',      file:'v3-top.stl',         color:C.top,  pos:[0,0,Z_TOP-10],  explode:[0,0,30],  shell:true },
  { key:'diffuser', file:'v3-diffuser.stl',    color:C.diffuser, pos:[HX,HY,Z_TOP], explode:[0,0,58], glow:true },
  { key:'fig',      file:'v3-figurine.stl',    color:C.lid,  pos:[HX,HY,42],       explode:[0,0,86] },
  { key:'kplay',    file:'v3-keycap-play.stl', color:C.keycap, pos:[BTN1,BTN_Y,44], explode:[0,0,54] },
  { key:'kstop',    file:'v3-keycap-stop.stl', color:C.keycap, pos:[BTN2,BTN_Y,44], explode:[0,0,54] },
];

const mount = document.getElementById('viewer');
if (mount) init(mount);

function init(mount) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xFFF8F0);

  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 5000);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  mount.appendChild(renderer.domElement);

  // Lights — soft, toy-product look
  scene.add(new THREE.HemisphereLight(0xffffff, 0xe7d9c5, 0.95));
  const key = new THREE.DirectionalLight(0xffffff, 1.6);
  key.position.set(120, 200, 140);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 1; key.shadow.camera.far = 800;
  key.shadow.camera.left = -150; key.shadow.camera.right = 150;
  key.shadow.camera.top = 150; key.shadow.camera.bottom = -150;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xfff0e0, 0.5);
  fill.position.set(-140, 80, -120);
  scene.add(fill);

  // Root group: SCAD is Z-up; rotate so Z becomes screen-up.
  const root = new THREE.Group();
  root.rotation.x = -Math.PI / 2;
  scene.add(root);

  const ledLight = new THREE.PointLight(0x66e0ff, 0, 120, 2);
  root.add(ledLight);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 60;
  controls.maxDistance = 900;

  const shellMats = [];
  let diffuserMat = null;
  const meshByKey = {};
  const loader = new STLLoader();

  const status = document.getElementById('viewerStatus');

  Promise.all(PARTS.map(p => loadPart(p))).then(() => {
    buildElectronics(root, meshByKey);
    frame();
    applyElectronics(false);
    applyExplode(0);
    if (status) status.style.display = 'none';
  }).catch(err => {
    console.error(err);
    if (status) status.textContent = '3D viewer failed to load — see the renders below.';
  });

  function loadPart(p) {
    return new Promise((resolve, reject) => {
      loader.load(MODELS + p.file, geo => {
        const isGlow = !!p.glow;
        const mat = new THREE.MeshStandardMaterial({
          color: p.color,
          roughness: isGlow ? 0.25 : 0.62,
          metalness: 0.0,
          transparent: isGlow,
          opacity: isGlow ? 0.4 : 1,
          flatShading: false,
        });
        if (isGlow) { mat.emissive = new THREE.Color(0x335577); mat.emissiveIntensity = 0; diffuserMat = mat; }
        const mesh = new THREE.Mesh(geo, mat);
        mesh.castShadow = true; mesh.receiveShadow = true;
        mesh.position.set(p.pos[0], p.pos[1], p.pos[2]);
        mesh.userData.base = mesh.position.clone();
        mesh.userData.explode = new THREE.Vector3(...p.explode || [0,0,0]);
        if (p.shell) shellMats.push(mat);
        meshByKey[p.key] = mesh;
        root.add(mesh);
        resolve();
      }, undefined, reject);
    });
  }

  // ---- Electronics (illustrative primitive proxies, positioned in mm) ----
  const elec = new THREE.Group();
  function buildElectronics(root) {
    const dark = (c=0x1d1f24, r=0.55, m=0.2) =>
      new THREE.MeshStandardMaterial({ color:c, roughness:r, metalness:m });

    // Raspberry Pi Zero 2 W on the tray standoffs (sits at the back)
    elec.add(box(65,30,1.6, 45,68,9.8, dark(0x2f7d46,0.5)));     // green PCB
    elec.add(box(10,10,2,  45,68,11.4,dark(0x0c0c0c)));          // SoC
    [ -6, 8, 20 ].forEach(dx => elec.add(box(8,4.5,3, 45+dx,82,11.5, dark(0xb9c0c8,0.3,0.8)))); // back ports

    // Buzzer in the tray cradle
    elec.add(cyl(6,9, 16,16,9.6, dark(0x101010,0.45)));

    // MFRC522 — mounted FLUSH under the hole floor (antenna up, reads close)
    elec.add(box(60,40,1.6, HX,HY,Z_TOP-1.0, dark(0x12428f,0.5)));  // blue PCB
    elec.add(box(22,3,5,    HX,HY-12,Z_TOP-4, dark(0x0c0c0c)));     // solder/pads below

    // MX switches under the keycaps
    elec.add(box(14,14,11, BTN1,BTN_Y,42, dark(0x161616,0.5)));
    elec.add(box(14,14,11, BTN2,BTN_Y,42, dark(0x161616,0.5)));

    // WS2812B — 8 emissive LEDs wrapped around the raised ring
    const hue = [0,0.08,0.14,0.33,0.5,0.6,0.75,0.9];
    for (let i = 0; i < 8; i++) {
      const a = (i/8)*Math.PI*2;
      const r = 21, x = HX + r*Math.cos(a), y = HY + r*Math.sin(a);
      const m = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(hue[i], 0.85, 0.6),
        emissive: new THREE.Color().setHSL(hue[i], 0.9, 0.55),
        emissiveIntensity: 1.3, roughness: 0.4,
      });
      const led = box(2.6,4.2,10, x,y,Z_TOP+5, m);
      led.rotation.z = a;
      elec.add(led);
    }
    root.add(elec);
    elec.visible = false;
  }

  function box(w,h,d, x,y,z, mat) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
    m.position.set(x,y,z); m.castShadow = true; m.userData.base = m.position.clone();
    return m;
  }
  function cyl(r,h, x,y,z, mat) {
    const g = new THREE.CylinderGeometry(r,r,h,28);
    const m = new THREE.Mesh(g, mat);
    m.rotation.x = Math.PI/2;                 // axis along Z
    m.position.set(x,y,z); m.castShadow = true; m.userData.base = m.position.clone();
    return m;
  }

  // ---- Framing & ground ----
  let center = new THREE.Vector3();
  function frame() {
    const bbAll = new THREE.Box3().setFromObject(root);
    center = bbAll.getCenter(new THREE.Vector3());
    const size = bbAll.getSize(new THREE.Vector3());
    const radius = Math.max(size.x, size.y, size.z);
    controls.target.copy(center);
    camera.position.set(center.x + radius*0.9, center.y + radius*0.55, center.z + radius*1.5);
    camera.near = radius/50; camera.far = radius*40; camera.updateProjectionMatrix();

    // soft ground shadow
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(2000, 2000),
      new THREE.ShadowMaterial({ opacity: 0.12 })
    );
    ground.position.y = bbAll.min.y;
    ground.rotation.x = -Math.PI/2;
    ground.receiveShadow = true;
    scene.add(ground);
    resize();
  }

  // ---- Toggle handlers ----
  function applyElectronics(on) {
    elec.visible = on;
    shellMats.forEach(m => { m.transparent = on; m.opacity = on ? 0.30 : 1.0; m.depthWrite = !on; });
    if (diffuserMat) { diffuserMat.emissiveIntensity = on ? 0.9 : 0; diffuserMat.opacity = on ? 0.55 : 0.4; }
    ledLight.intensity = on ? 1.1 : 0;
    ledLight.position.set(HX, HY, Z_TOP + 6);
  }
  let explodeAmt = 0, explodeTarget = 0;
  function applyExplode(t) { explodeTarget = t; }

  bindToggle('toggleElectronics', applyElectronics);
  bindToggle('toggleExploded', on => applyExplode(on ? 1 : 0));
  bindToggle('toggleRotate', on => { controls.autoRotate = on; controls.autoRotateSpeed = 1.2; });
  const resetBtn = document.getElementById('viewerReset');
  if (resetBtn) resetBtn.addEventListener('click', () => { frame(); });

  function bindToggle(id, fn) {
    const el = document.getElementById(id);
    if (el) { el.addEventListener('change', () => fn(el.checked)); fn(el.checked); }
  }

  // ---- Resize & render loop ----
  function resize() {
    const w = mount.clientWidth  || (mount.parentElement && mount.parentElement.clientWidth);
    const h = mount.clientHeight || (mount.parentElement && mount.parentElement.clientHeight);
    if (!w || !h) return;
    renderer.setSize(w, h);                 // updateStyle=true; CSS !important keeps it 100%
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  resize();                                 // size immediately so nothing overflows pre-load
  window.addEventListener('resize', resize);
  const ro = new ResizeObserver(resize); ro.observe(mount);

  function animate() {
    requestAnimationFrame(animate);
    // ease the explode amount
    explodeAmt += (explodeTarget - explodeAmt) * 0.12;
    root.children.forEach(o => {
      if (o.userData && o.userData.explode) {
        o.position.copy(o.userData.base).addScaledVector(o.userData.explode, explodeAmt);
      }
    });
    elec.children.forEach(o => {
      if (o.userData && o.userData.base) {
        // electronics drift with the nearest shell layer when exploded
        const dz = o.userData.base.z > 40 ? 30 : (o.userData.base.z < 20 ? -28 : 0);
        o.position.z = o.userData.base.z + dz * explodeAmt;
      }
    });
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}
