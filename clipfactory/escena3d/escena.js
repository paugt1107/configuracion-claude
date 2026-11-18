// FERNANDA · Escenas 3D de verdad (three.js), renderizadas fotograma a fotograma por render.mjs.
// window.SPEC = {tipo, texto, titulo, sub, color, n, dur}. La escena es una función pura del tiempo: window.frame(t).
import * as THREE from "three";
import { FontLoader } from "./vendor/FontLoader.js";
import { TextGeometry } from "./vendor/TextGeometry.js";
import { RoomEnvironment } from "./vendor/RoomEnvironment.js";

const S = Object.assign({ tipo: "numero", texto: "6", titulo: "", sub: "", color: "gold", n: 3, dur: 3 }, window.SPEC || {});
const PAL = { gold: 0xffc24b, orange: 0xff7a1a, cyan: 0x19d3ff, magenta: 0xff2e93, white: 0xf2f4ff, green: 0x3cbe5a, red: 0xeb283c };
const ACC = new THREE.Color(PAL[S.color] ?? PAL.gold);
const css = `rgb(${(ACC.r * 255) | 0},${(ACC.g * 255) | 0},${(ACC.b * 255) | 0})`;

// ---------- utilidades deterministas ----------
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const easeOutBack = (x) => { x = clamp(x); const c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
const easeOut = (x) => 1 - (1 - clamp(x)) ** 3;
const ascii = (s) => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[¿¡]/g, "").toUpperCase();

// ---------- fondo y textos (HTML, admite acentos) ----------
document.getElementById("bg").style.background =
  `radial-gradient(ellipse at 50% 38%, ${css}55 0%, #10131c 42%, #05060a 80%)`;
const tit = document.getElementById("titulo"), sub = document.getElementById("sub");
if (S.titulo) tit.innerHTML = `<span class="chip" style="text-shadow:0 0 28px ${css}">${S.titulo}</span>`;
if (S.sub) sub.innerHTML = `<span class="chip">${S.sub}</span>`;

// ---------- three.js ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(1080, 1920);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
document.body.insertBefore(renderer.domElement, document.getElementById("vig"));
const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const cam = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.1, 200);
const key = new THREE.PointLight(ACC, 60, 40); key.position.set(3, 4, 6); scene.add(key);
const rim = new THREE.DirectionalLight(0xffffff, 1.6); rim.position.set(-4, 6, -3); scene.add(rim);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

const gold = () => new THREE.MeshPhysicalMaterial({ color: ACC, metalness: 1, roughness: 0.22, clearcoat: 1, clearcoatRoughness: 0.15 });
function glowTex() {
  const c = document.createElement("canvas"); c.width = c.height = 256;
  const g = c.getContext("2d"), r = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(0.25, "rgba(255,255,255,.45)"); r.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = r; g.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
}
const GLOW = glowTex();
function glow(size, color = ACC, op = 0.8) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: GLOW, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false }));
  s.scale.set(size, size, 1); return s;
}

// polvo en suspensión
const dustGeo = new THREE.BufferGeometry(), N = 420, dp = new Float32Array(N * 3), dv = [];
for (let i = 0; i < N; i++) { dp.set([(rnd() - 0.5) * 14, (rnd() - 0.5) * 22, (rnd() - 0.5) * 10 - 2], i * 3); dv.push(0.05 + rnd() * 0.2); }
dustGeo.setAttribute("position", new THREE.BufferAttribute(dp, 3));
const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({ size: 0.05, map: GLOW, color: 0xffffff, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false }));
scene.add(dust);
const dust0 = dp.slice();

// ---------- objetos ----------
const font = await new Promise((ok) => new FontLoader().load("vendor/helvetiker_bold.typeface.json", ok));
function text3d(txt, size = 1.6, mat = gold()) {
  const g = new TextGeometry(ascii(txt), { font, size, depth: size * 0.35, curveSegments: 10, bevelEnabled: true, bevelThickness: size * 0.06, bevelSize: size * 0.04, bevelSegments: 6 });
  g.center();
  return new THREE.Mesh(g, mat);
}
function starShape(r = 1) {
  const sh = new THREE.Shape();
  for (let i = 0; i < 10; i++) {
    const a = Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 ? r * 0.45 : r;
    i ? sh.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : sh.moveTo(Math.cos(a) * rr, Math.sin(a) * rr);
  }
  return new THREE.ExtrudeGeometry(sh, { depth: 0.3, bevelEnabled: true, bevelThickness: 0.08, bevelSize: 0.06, bevelSegments: 4 }).center();
}
function fit(mesh, maxW) {
  const b = new THREE.Box3().setFromObject(mesh), w = b.max.x - b.min.x;
  if (w > maxW) mesh.scale.multiplyScalar(maxW / w);
  return mesh;
}

const root = new THREE.Group(); scene.add(root);
const halo = glow(9, ACC, 0.55); halo.position.z = -1.5; scene.add(halo);
const parts = []; // [{obj, t0}] para entradas escalonadas
const upd = []; // animaciones propias de cada tipo
let flotar = 1, giro = 1;
const T = S.tipo;

if (T === "numero" || T === "texto") {
  root.add(fit(text3d(S.texto, 1.8), 3.3));
} else if (T === "orbe") {
  const m = new THREE.Mesh(new THREE.SphereGeometry(1.45, 96, 96), new THREE.MeshPhysicalMaterial({ color: ACC, metalness: 0.85, roughness: 0.18, clearcoat: 1, emissive: ACC, emissiveIntensity: 0.18 }));
  root.add(m);
  if (S.texto) { const t = fit(text3d(S.texto, 0.8), 2.6); t.position.set(0, 0, 1.9); root.add(t); }
} else if (T === "moneda") {
  const coin = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.5, 0.28, 96), gold());
  coin.rotation.x = Math.PI / 2; root.add(coin);
  const sym = fit(text3d(S.texto || "$", 1.3), 2.2); sym.position.z = 0.2; sym.scale.z = 0.4; root.add(sym);
  const back = sym.clone(); back.position.z = -0.2; back.rotation.y = Math.PI; root.add(back);
} else if (T === "estrellas") {
  const n = clamp(S.n | 0, 1, 5), gap = 0.7, geo = starShape(0.32);
  for (let i = 0; i < 5; i++) {
    const on = i < n;
    const m = new THREE.Mesh(geo, on ? gold() : new THREE.MeshStandardMaterial({ color: 0x2a2d38, metalness: 0.4, roughness: 0.6 }));
    m.position.x = (i - 2) * gap; root.add(m); parts.push({ obj: m, t0: 0.15 + i * 0.18 });
  }
} else if (T === "billetes") {
  if (S.texto) root.add(fit(text3d(S.texto, 1.3), 3.3));
  const tex = (() => {
    const c = document.createElement("canvas"); c.width = 256; c.height = 120; const g = c.getContext("2d");
    g.fillStyle = "#2f8f4e"; g.fillRect(0, 0, 256, 120); g.strokeStyle = "#bfe8c6"; g.lineWidth = 6; g.strokeRect(8, 8, 240, 104);
    g.fillStyle = "#d9f5dc"; g.font = "bold 70px sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("$", 128, 62);
    return new THREE.CanvasTexture(c);
  })();
  const mat = new THREE.MeshStandardMaterial({ map: tex, side: THREE.DoubleSide, roughness: 0.6 });
  for (let i = 0; i < 70; i++) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.42), mat);
    b.userData = { x: (rnd() - 0.5) * 7, z: (rnd() - 0.5) * 5 - 0.5, y0: 6 + rnd() * 10, v: 1.6 + rnd() * 1.6, r: [rnd() * 6, rnd() * 6, rnd() * 6], w: 1 + rnd() * 3 };
    scene.add(b); parts.push({ obj: b, lluvia: true });
  }
} else if (T === "mapa") {
  const c = document.createElement("canvas"); c.width = c.height = 1024; const g = c.getContext("2d");
  g.fillStyle = "#0b1220"; g.fillRect(0, 0, 1024, 1024);
  g.strokeStyle = "rgba(120,180,255,.22)"; g.lineWidth = 2;
  for (let i = 0; i <= 1024; i += 48) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 1024); g.stroke(); g.beginPath(); g.moveTo(0, i); g.lineTo(1024, i); g.stroke(); }
  g.fillStyle = "rgba(40,90,70,.9)"; // costa inventada con forma de península
  g.beginPath(); g.moveTo(300, 0); g.bezierCurveTo(260, 300, 420, 420, 380, 640); g.bezierCurveTo(360, 820, 520, 900, 560, 1024); g.lineTo(1024, 1024); g.lineTo(1024, 0); g.fill();
  g.strokeStyle = "rgba(255,255,255,.35)"; g.lineWidth = 6;
  for (let i = 0; i < 9; i++) { g.beginPath(); g.moveTo(420 + rnd() * 500, rnd() * 1024); g.lineTo(420 + rnd() * 500, rnd() * 1024); g.stroke(); }
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c) }));
  plane.rotation.x = -Math.PI / 2.6; plane.position.y = -1.6; root.add(plane);
  const pin = new THREE.Group();
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.45, 48, 48), new THREE.MeshPhysicalMaterial({ color: PAL.red, metalness: 0.2, roughness: 0.2, clearcoat: 1 }));
  const tip = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.9, 32), head.material); tip.rotation.x = Math.PI; tip.position.y = -0.55;
  pin.add(head, tip); scene.add(pin); parts.push({ obj: pin, pin: true });
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.4, 0.5, 64), new THREE.MeshBasicMaterial({ color: ACC, transparent: true, side: THREE.DoubleSide, blending: THREE.AdditiveBlending }));
  ring.rotation.x = -Math.PI / 2.6; ring.position.set(0, -1.15, 0.3); scene.add(ring); parts.push({ obj: ring, ring: true });
  if (S.texto) { const t = fit(text3d(S.texto, 0.9), 3.2); t.position.set(0, 1.5, 0); scene.add(t); parts.push({ obj: t, t0: 0.5 }); }
} else if (T === "piedra") {
  // Lápida romana tallada (procedural): las letras se ENCIENDEN a mitad de escena.
  const W2 = 1024, H2 = 1280, base = document.createElement("canvas"), bump = document.createElement("canvas"), em = document.createElement("canvas");
  for (const c of [base, bump, em]) { c.width = W2; c.height = H2; }
  const g = base.getContext("2d"), b = bump.getContext("2d"), e = em.getContext("2d");
  g.fillStyle = "#8a785c"; g.fillRect(0, 0, W2, H2); b.fillStyle = "#808080"; b.fillRect(0, 0, W2, H2); e.fillStyle = "#000"; e.fillRect(0, 0, W2, H2);
  for (let i = 0; i < 9000; i++) { const v = 95 + rnd() * 80 | 0; g.fillStyle = `rgba(${v},${v - 12},${v - 30},.35)`; g.fillRect(rnd() * W2, rnd() * H2, 2 + rnd() * 5, 2 + rnd() * 5); }
  g.strokeStyle = "rgba(90,75,55,.35)"; g.lineWidth = 2;
  for (let i = 0; i < 7; i++) { g.beginPath(); let x = rnd() * W2, y = rnd() * H2; g.moveTo(x, y); for (let k = 0; k < 6; k++) { x += (rnd() - 0.5) * 120; y += rnd() * 90; g.lineTo(x, y); } g.stroke(); }
  const fondo = ["MIRACVLIS·CLARVS", "ANNO·DOMINI", "SPQR·ROMA", "DVM·VNVS·MOR", "AVE·VERITAS"];
  g.font = "64px serif"; b.font = g.font; g.textAlign = b.textAlign = e.textAlign = "center";
  fondo.forEach((l, i) => { const y = 120 + i * 120 + (i > 1 ? 560 : 0); g.fillStyle = "rgba(35,27,18,.6)"; g.fillText(l, W2 / 2, y); b.fillStyle = "#303030"; b.fillText(l, W2 / 2, y); });
  const big = ascii(S.texto || "LVX");
  for (const [ctx, col] of [[g, "#1e170f"], [b, "#000"], [e, "#fff"]]) { ctx.font = "bold 300px serif"; ctx.fillStyle = col; ctx.fillText(big, W2 / 2, 760, 900); }
  const tex = (c) => { const t = new THREE.CanvasTexture(c); t.colorSpace = c === base ? THREE.SRGBColorSpace : THREE.NoColorSpace; return t; };
  const mat = new THREE.MeshStandardMaterial({ map: tex(base), bumpMap: tex(bump), bumpScale: 6, roughness: 0.95, emissive: ACC, emissiveMap: tex(em), emissiveIntensity: 0 });
  const slab = new THREE.Mesh(new THREE.BoxGeometry(3.3, 4.1, 0.35), [null, null, null, null, mat, null].map((m) => m || new THREE.MeshStandardMaterial({ color: 0xb8a684, roughness: 1 })));
  root.add(slab);
  const burst = glow(9, ACC, 0); burst.position.z = -0.6; root.add(burst);
  upd.push((t) => { const k = easeOut((t - S.dur * 0.42) / 0.35); mat.emissiveIntensity = 5 * k; burst.material.opacity = 0.8 * k * (0.85 + 0.15 * Math.sin(t * 9)); halo.material.opacity = 0.15 + 0.3 * k; });
  flotar = 0.3;
} else if (T === "bombilla") {
  const glass = new THREE.MeshPhysicalMaterial({ color: 0xdfe6f0, metalness: 0, roughness: 0.08, clearcoat: 1, transparent: true, opacity: 0.92, emissive: ACC, emissiveIntensity: 0 });
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(1.25, 64, 64), glass); bulb.position.y = 0.35;
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.5, 0.7, 48), glass); neck.position.y = -0.85;
  const screw = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.48, 0.75, 48), new THREE.MeshPhysicalMaterial({ color: 0xcfd3dc, metalness: 1, roughness: 0.3 })); screw.position.y = -1.5;
  const fil = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.035, 12, 48, Math.PI * 1.4), new THREE.MeshStandardMaterial({ color: 0x553311, emissive: 0xffcc66, emissiveIntensity: 0 })); fil.position.y = 0.2; fil.rotation.z = Math.PI * 0.8;
  root.add(bulb, neck, screw, fil);
  const rays = new THREE.Group();
  for (let i = 0; i < 7; i++) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.55, 0.05), new THREE.MeshBasicMaterial({ color: ACC, transparent: true, opacity: 0 })); const a = Math.PI / 2 + (i - 3) * 0.42; r.position.set(Math.cos(a) * 2.05, 0.35 + Math.sin(a) * 2.05, 0); r.rotation.z = a - Math.PI / 2; rays.add(r); }
  root.add(rays);
  const burst = glow(8, ACC, 0); burst.position.set(0, 0.35, -0.8); root.add(burst);
  upd.push((t) => { const on = t > S.dur * 0.35 ? easeOut((t - S.dur * 0.35) / 0.12) * (t - S.dur * 0.35 < 0.25 ? 0.6 + 0.4 * Math.sin(t * 60) : 1) : 0;
    glass.emissiveIntensity = 1.4 * on; fil.material.emissiveIntensity = 4 * on; burst.material.opacity = 0.95 * on;
    rays.children.forEach((r, i) => { r.material.opacity = on; r.scale.y = 0.6 + 0.4 * Math.sin(t * 6 + i); }); halo.material.opacity = 0.15 + 0.7 * on; });
  flotar = 0.1;
} else if (T === "corazon") {
  const h = new THREE.Shape(); h.moveTo(0, -1.1);
  h.bezierCurveTo(-0.2, -0.9, -1.4, -0.2, -1.4, 0.45); h.bezierCurveTo(-1.4, 1.1, -0.6, 1.35, 0, 0.75);
  h.bezierCurveTo(0.6, 1.35, 1.4, 1.1, 1.4, 0.45); h.bezierCurveTo(1.4, -0.2, 0.2, -0.9, 0, -1.1);
  const heart = new THREE.Mesh(new THREE.ExtrudeGeometry(h, { depth: 0.5, bevelEnabled: true, bevelThickness: 0.2, bevelSize: 0.15, bevelSegments: 10, curveSegments: 32 }).center(),
    new THREE.MeshPhysicalMaterial({ color: PAL.red, metalness: 0.1, roughness: 0.2, clearcoat: 1, emissive: PAL.red, emissiveIntensity: 0.15 }));
  root.add(heart);
  const crosses = [];
  for (let i = 0; i < 16; i++) {
    const c = new THREE.Group(), m = new THREE.MeshBasicMaterial({ color: i % 3 ? 0x7dffa8 : 0xffffff, transparent: true, blending: THREE.AdditiveBlending });
    c.add(new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.08, 0.02), m), new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.28, 0.02), m));
    c.userData = { x: (rnd() - 0.5) * 3.4, ph: rnd(), z: 0.4 + rnd() }; scene.add(c); crosses.push(c);
  }
  upd.push((t) => { const beat = 1 + 0.12 * Math.max(0, Math.sin(t * 7.5)) ** 8 + 0.07 * Math.max(0, Math.sin(t * 7.5 - 0.9)) ** 8;
    heart.scale.setScalar(beat); heart.material.emissiveIntensity = 0.15 + 0.6 * (beat - 1) * 5;
    for (const c of crosses) { const k = (t * 0.45 + c.userData.ph) % 1; c.position.set(c.userData.x, -2 + k * 4.5, c.userData.z); c.children[0].material.opacity = Math.sin(k * Math.PI) * clamp(t / 0.6); c.scale.setScalar(0.6 + k); } });
  giro = 0.12;
} else if (T === "foto" && S.imagen) {
  // Foto real (oficial o propia) flotando en 3D sobre la misma foto desenfocada a pantalla completa.
  const ld = new THREE.TextureLoader(), tx = await ld.loadAsync(S.imagen); tx.colorSpace = THREE.SRGBColorSpace;
  if (S.fondo) { const bg = await ld.loadAsync(S.fondo); bg.colorSpace = THREE.SRGBColorSpace; document.getElementById("bg").style.background = `url(${S.fondo}) center/cover`; }
  const ar = tx.image.width / tx.image.height, w = 3.5, hh = Math.min(5.6, w / ar);
  const frameM = new THREE.Mesh(new THREE.BoxGeometry(w + 0.12, hh + 0.12, 0.06), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 }));
  const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, hh), new THREE.MeshBasicMaterial({ map: tx })); pic.position.z = 0.035;
  const shine = new THREE.Mesh(new THREE.PlaneGeometry(0.8, hh * 1.6), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.18, blending: THREE.AdditiveBlending, depthWrite: false }));
  shine.rotation.z = 0.5; shine.position.z = 0.05;
  root.add(frameM, pic, shine);
  halo.material.color.set(0xffffff); giro = 0.2;
  if (S.estilo === "lleno") {
    // imagen a pantalla completa con zoom lento (Ken Burns) + destello; el marco 3D no se ve
    root.visible = false; halo.visible = false;
    const bgEl = document.getElementById("bg"), dir = (S.texto || S.imagen).length % 2 ? 1 : -1;
    bgEl.style.background = `url(${S.imagen}) center/cover`;
    upd.push((t) => { const k = t / S.dur; bgEl.style.transform = `scale(${1.06 + 0.16 * k}) translateX(${dir * (k - 0.5) * 40}px)`; });
  } else if (S.estilo === "giro") {
    upd.push((t) => { shine.position.x = -4 + ((t * 2.2) % 9); root.rotation.y = -1.6 * (1 - easeOut(t / 0.8)); });
    giro = 0;
  } else {
    upd.push((t) => { shine.position.x = -4 + ((t * 2.2) % 9); root.rotation.x = -0.08 + 0.05 * Math.sin(t * 0.7); });
  }
} else if (T === "versus" || T === "foto") {
  const [a, b] = String(S.texto || "A|B").split("|").concat([""]);
  const A = fit(text3d(a, 1.2), 3.2), B = fit(text3d(b, 1.2, new THREE.MeshPhysicalMaterial({ color: 0xf2f4ff, metalness: 1, roughness: 0.25, clearcoat: 1 })), 3.2), vs = text3d("VS", 0.6);
  A.position.set(0, 1.25, 0); B.position.set(0, -1.25, 0); vs.material = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: ACC, emissiveIntensity: 1.2 });
  root.add(A, B, vs); parts.push({ obj: A, t0: 0.05, from: -1 }, { obj: B, t0: 0.35, from: 1 }, { obj: vs, t0: 0.65 });
}

// ---------- animación: todo depende solo de t ----------
window.frame = (t) => {
  const D = S.dur;
  // cámara: entrada rápida + acercamiento lento + leve órbita
  const push = easeOut(t / 0.6);
  cam.position.set(Math.sin(t * 0.35) * 0.9, 0.3 + Math.sin(t * 0.5) * 0.15, 13 - 3 * push - 0.35 * t);
  cam.lookAt(0, 0, 0);
  // objeto principal: pop con rebote, giro lento, flotación
  const pop = easeOutBack(t / 0.55);
  root.scale.setScalar(Math.max(0.001, T === "mapa" ? 1 : pop));
  root.rotation.y = T === "mapa" ? 0 : ((1 - easeOut(t / 0.9)) * -1.2 + Math.sin(t * 0.8) * 0.18) * giro + (T === "moneda" || T === "orbe" ? t * 0.9 : 0);
  root.position.y = 0.15 * flotar * Math.sin(t * 1.6);
  for (const f of upd) f(t);
  halo.material.opacity = 0.35 + 0.25 * Math.sin(t * 3) ** 2 + 0.3 * (1 - clamp(t / 0.4));
  key.position.x = 3 * Math.cos(t * 0.9); key.position.z = 6 + Math.sin(t * 0.9);
  for (const p of parts) {
    const o = p.obj;
    if (p.lluvia) {
      const u = o.userData, y = u.y0 - u.v * t * 2.2;
      o.position.set(u.x + Math.sin(t * u.w) * 0.3, ((y + 8) % 16 + 16) % 16 - 8, u.z);
      o.rotation.set(u.r[0] + t * u.w, u.r[1] + t * u.w * 0.7, u.r[2]);
    } else if (p.pin) {
      const k = clamp((t - 0.25) / 0.45);
      o.position.set(0, -0.55 + (1 - easeOutBack(k)) * 5 + 0.08 * Math.sin(t * 3), 0.3);
      o.visible = t > 0.25;
    } else if (p.ring) {
      const k = ((t - 0.7) % 1.1 + 1.1) % 1.1;
      o.visible = t > 0.7; o.scale.setScalar(1 + k * 4); o.material.opacity = 1 - k / 1.1;
    } else {
      const k = easeOutBack((t - p.t0) / 0.4);
      o.userData.s0 ??= o.scale.x;
      o.scale.setScalar(Math.max(0.001, k * o.userData.s0));
      if (p.from) o.position.x = (1 - easeOut((t - p.t0) / 0.4)) * 6 * p.from;
    }
  }
  // polvo que sube
  const a = dust.geometry.attributes.position;
  for (let i = 0; i < N; i++) a.array[i * 3 + 1] = ((dust0[i * 3 + 1] + dv[i] * t * 3 + 11) % 22 + 22) % 22 - 11;
  a.needsUpdate = true;
  // textos HTML: entran deslizando
  tit.style.transform = `translateY(${(1 - easeOutBack((t - 0.1) / 0.45)) * -80}px)`; tit.style.opacity = clamp((t - 0.1) / 0.2);
  sub.style.transform = `translateY(${(1 - easeOut((t - 0.4) / 0.4)) * 60}px)`; sub.style.opacity = clamp((t - 0.4) / 0.25);
  document.getElementById("rays").style.opacity = 0.55 + 0.25 * Math.sin(t * 1.3);
  renderer.render(scene, cam);
  return D;
};
await document.fonts.ready;
window.frame(0);
window.LISTO = true;
