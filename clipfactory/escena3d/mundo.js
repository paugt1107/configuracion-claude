// MUNDO · una sola maqueta grande y continua por la que la cámara VIAJA en orden (travelling con keyframes sincronizados
// con la voz). Cada frase del guion es una PARADA: {zona, etiquetas, foto, camara, cielo}. S.hitos = segundo en que empieza
// cada parada. Entre paradas la cámara vuela en arco (sin cortes) y el cielo cambia de hora poco a poco.
// Todo es función pura de t (se renderiza en trozos en paralelo).
import * as THREE from "three";
import * as F from "./figuras.js";

const { eo, eob, suave } = F;
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const rad = (d) => (d * Math.PI) / 180;
let semilla = 11;
const rnd = () => ((semilla = (semilla * 16807) % 2147483647) / 2147483647);

// ---------------------------------------------------------------- CIELOS (hora del día por parada)
const CIELOS = {
  dia: { top: "#3f95ec", mid: "#86c8f7", hor: "#dcf1ff", sol: 0xfff0d8, solI: 2.6, hemi: [0xdcecff, 0x5d6b3c, 1.05], expo: 1.0, est: 0, luna: 0 },
  prehistoria: { top: "#56709a", mid: "#c99a7d", hor: "#f0c08e", sol: 0xffc48a, solI: 2.4, hemi: [0xffe0c0, 0x4d3f2c, 0.95], expo: 1.0, est: 0, luna: 0 },
  selva: { top: "#3b8fd6", mid: "#8fd2c2", hor: "#d6f1d2", sol: 0xfff2c4, solI: 2.4, hemi: [0xe2ffe6, 0x3c5a2c, 1.0], expo: 1.0, est: 0, luna: 0 },
  atardecer: { top: "#2c2f6e", mid: "#c9607d", hor: "#ffb06a", sol: 0xffa060, solI: 2.0, hemi: [0xffc6a6, 0x3a2a40, 0.8], expo: 1.05, est: 0.25, luna: 0 },
  noche: { top: "#050d22", mid: "#10244a", hor: "#27426e", sol: 0x9db6ff, solI: 0.8, hemi: [0x7088cc, 0x10141f, 0.55], expo: 1.15, est: 1, luna: 1 },
  misterio: { top: "#0d0a26", mid: "#261e4c", hor: "#46366a", sol: 0xb6a6ff, solI: 0.55, hemi: [0x8a7cc8, 0x141020, 0.5], expo: 1.15, est: 0.8, luna: 0.6 },
  amanecer: { top: "#4f86d6", mid: "#f2b29c", hor: "#ffdcae", sol: 0xffd0a0, solI: 2.3, hemi: [0xffe4d0, 0x4a4a3a, 0.95], expo: 1.0, est: 0, luna: 0 },
  dorado: { top: "#34479a", mid: "#ec8a5c", hor: "#ffd07c", sol: 0xffb070, solI: 2.2, hemi: [0xffd8b0, 0x40362c, 0.9], expo: 1.0, est: 0.05, luna: 0 },
};
const col = (h) => new THREE.Color(h);
function mezclaCielo(a, b, k) {
  const r = {};
  for (const n of ["top", "mid", "hor"]) r[n] = col(a[n]).lerp(col(b[n]), k);
  r.sol = col(a.sol).lerp(col(b.sol), k); r.solI = lerp(a.solI, b.solI, k);
  r.hemi = [col(a.hemi[0]).lerp(col(b.hemi[0]), k), col(a.hemi[1]).lerp(col(b.hemi[1]), k), lerp(a.hemi[2], b.hemi[2], k)];
  r.expo = lerp(a.expo, b.expo, k); r.est = lerp(a.est, b.est, k); r.luna = lerp(a.luna, b.luna, k);
  return r;
}

// ---------------------------------------------------------------- PLANO DEL MUNDO: sitios a lo largo del camino del tiempo
const SITIOS = {
  intro: [0, 0], primeros: [-5, -13], dinos: [5, -26], selva: [-5, -39], granja: [5, -52], nido: [-4, -65],
  podio: [4, -78], lab: [-4, -91], matiz: [4, -104], final: [0, -116],
};
const ORDEN = ["intro", "primeros", "dinos", "selva", "granja", "nido", "podio", "lab", "matiz", "final"];
// qué sitio, cámara y cielo usa cada ZONA (una zona = lo que se ve mientras se dice una frase)
const ZONAS = {
  intro: { sitio: "intro", cielo: "dia", cam: { az: 14, dist: 8.2, alt: 1.7, look: [0, 1.15, 0], orbit: 2.5, push: 0.12 } },
  primeros: { sitio: "primeros", cielo: "prehistoria", cam: { az: -24, dist: 6.0, alt: 2.2, look: [0.3, 0.5, 0.4], orbit: 3, push: 0.1 } },
  dinos: { sitio: "dinos", cielo: "dia", cam: { az: 32, dist: 9.5, alt: 3.4, look: [0, 1.3, 0], orbit: 3, push: 0.1 } },
  dinos_noche: { sitio: "dinos", cielo: "noche", cam: { az: 62, dist: 6.2, alt: 2.0, look: [2.0, 1.1, 1.8], orbit: -3, push: 0.08 } },
  selva: { sitio: "selva", cielo: "selva", cam: { az: -20, dist: 6.8, alt: 2.1, look: [0, 1.1, 0], orbit: 3, push: 0.1 } },
  granja: { sitio: "granja", cielo: "dia", cam: { az: 24, dist: 9.0, alt: 3.2, look: [0, 0.8, 0], orbit: 3, push: 0.1 } },
  truco: { sitio: "nido", cielo: "misterio", cam: { az: -16, dist: 7.5, alt: 2.6, look: [0, 0.8, 0], orbit: 2, push: 0.22 } },
  pone: { sitio: "nido", cielo: "misterio", cam: { az: 14, dist: 6.0, alt: 1.8, look: [0, 0.75, 0], orbit: 3, push: 0.1 } },
  nace: { sitio: "nido", cielo: "amanecer", cam: { az: -10, dist: 5.0, alt: 1.6, look: [0, 0.75, 0], orbit: 4, push: 0.08 } },
  podio: { sitio: "podio", cielo: "dia", cam: { az: 16, dist: 7.4, alt: 2.4, look: [0, 1.5, 0], orbit: 4, push: 0.1 } },
  lab: { sitio: "lab", cielo: "dia", cam: { az: -22, dist: 7.4, alt: 2.6, look: [0, 1.3, 0], orbit: 3, push: 0.1 } },
  matiz: { sitio: "matiz", cielo: "dia", cam: { az: 20, dist: 7.0, alt: 2.4, look: [0, 1.4, 0], orbit: 3, push: 0.08 } },
  final: { sitio: "final", cielo: "dorado", cam: { az: 0, dist: 8.0, alt: 2.0, look: [0, 1.3, 0], orbit: 0, push: 0, sube: 1 } },
};

// camino: curva suave por el centro de los sitios (un poco desplazada para pasar al lado de las maquetas)
const caminoPts = ORDEN.map((n) => new THREE.Vector3(SITIOS[n][0] * 0.55, 0, SITIOS[n][1] + 2.4));
caminoPts.unshift(new THREE.Vector3(0, 0, 14)); caminoPts.push(new THREE.Vector3(0, 0, -136));
const CAMINO = new THREE.CatmullRomCurve3(caminoPts);
const caminoX = (() => { const tab = []; for (let i = 0; i <= 600; i++) { const p = CAMINO.getPoint(i / 600); tab.push([p.z, p.x]); } tab.sort((a, b) => a[0] - b[0]); return (z) => { let i = tab.findIndex((r) => r[0] >= z); if (i <= 0) return tab[Math.max(0, i)][1]; const [z0, x0] = tab[i - 1], [z1, x1] = tab[i]; return lerp(x0, x1, (z - z0) / (z1 - z0 || 1)); }; })();
const llano = (x, z) => { let m = 1; for (const n of ORDEN) { const [sx, sz] = SITIOS[n]; m = Math.min(m, clamp((Math.hypot(x - sx, z - sz) - 4.2) / 4)); } return m; };
export function altura(x, z) {
  const d = Math.abs(x - caminoX(z)), lejos = clamp((d - 4.5) / 9);
  const colinas = (1.6 + Math.sin(z * 0.19) * 0.9 + Math.sin(x * 0.31 + z * 0.11) * 0.8 + Math.sin(x * 0.9 - z * 0.7) * 0.25) * lejos;
  const montes = clamp((Math.abs(x) - 22) / 10) * (6 + 3 * Math.sin(z * 0.08 + x * 0.05));
  return Math.max(0, colinas * 1.5 * llano(x, z) + montes) + (1 - llano(x, z)) * 0;
}
// bioma (color del suelo) según la zona del camino
const BIOMAS = [[14, 0x7cc35a], [2, 0x7cc35a], [-8, 0x6f8a3c], [-18, 0x7a7a3a], [-22, 0xb8a060], [-32, 0xa99a58], [-35, 0x3f8f3a], [-45, 0x3a8a3c], [-48, 0x86c25c], [-58, 0x8cc860], [-61, 0x9fb05a], [-70, 0x8fae55], [-74, 0x7fc35f], [-136, 0x7fc35f]];
function colorSuelo(x, z, h) {
  let i = BIOMAS.findIndex((b) => b[0] < z); if (i <= 0) i = 1;
  const [z0, c0] = BIOMAS[i - 1], [z1, c1] = BIOMAS[i];
  const c = col(c0).lerp(col(c1), clamp((z0 - z) / (z0 - z1 || 1)));
  const n = 0.92 + 0.08 * Math.sin(x * 1.7 + z * 0.9) * Math.sin(z * 1.3 - x * 0.4);
  c.multiplyScalar(n * (1 - clamp(h / 14) * 0.25));
  if (h > 7) c.lerp(col(0x9a9a9a), clamp((h - 7) / 4));
  return c;
}

export async function crear(S, ctx) {
  const { scene, cam, renderer } = ctx;
  const paradas = (S.paradas || []).map((p) => ({ ...p, z: ZONAS[p.zona] || ZONAS.dinos }));
  const DUR = S.total ?? S.dur;
  const N = paradas.length, hitos = S.hitos && S.hitos.length === N ? S.hitos : paradas.map((_, i) => (i * DUR) / N);
  const finDe = (i) => (i + 1 < N ? hitos[i + 1] : DUR);
  const usa = (nombreZona) => paradas.map((p, i) => (p.zona === nombreZona ? { t0: hitos[i], d: finDe(i) - hitos[i], p } : null)).filter(Boolean)[0] || null;
  const ventana = (zona, t) => { const u = usa(zona); return u ? { tl: t - u.t0, d: u.d, k: (t - u.t0) / u.d, dentro: t >= u.t0 && t < u.t0 + u.d } : null; };

  // ---------- luces, sombras, niebla, cielo
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMappingExposure = 1.0;
  const hemi = new THREE.HemisphereLight(0xffffff, 0x445533, 1); scene.add(hemi);
  const sol = new THREE.DirectionalLight(0xffffff, 2.5); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); Object.assign(sol.shadow.camera, { left: -11, right: 11, top: 11, bottom: -11, near: 1, far: 60 }); sol.shadow.camera.updateProjectionMatrix();
  sol.shadow.bias = -0.0008; sol.shadow.normalBias = 0.02; scene.add(sol, sol.target);
  scene.fog = new THREE.Fog(0xdcf1ff, 16, 52);
  const cieloMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: col("#3f95ec") }, mid: { value: col("#86c8f7") }, hor: { value: col("#dcf1ff") }, solDir: { value: new THREE.Vector3(0.3, 0.4, -1).normalize() }, solCol: { value: col(0xffffff) }, luna: { value: 0 } },
    vertexShader: "varying vec3 vd; void main(){ vd = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    fragmentShader: `uniform vec3 top; uniform vec3 mid; uniform vec3 hor; uniform vec3 solDir; uniform vec3 solCol; uniform float luna; varying vec3 vd;
      void main(){ float y = vd.y; vec3 c = y < 0.0 ? hor : (y < 0.25 ? mix(hor, mid, y / 0.25) : mix(mid, top, clamp((y - 0.25) / 0.5, 0.0, 1.0)));
        float s = max(dot(normalize(vd), normalize(solDir)), 0.0);
        c += solCol * (pow(s, 600.0) * 1.2 * (1.0 - luna) + pow(s, 12.0) * 0.18);
        c = mix(c, vec3(0.93, 0.95, 1.0), smoothstep(0.9993, 0.9996, s) * luna);
        gl_FragColor = vec4(c, 1.0); }`,
  });
  const cielo = new THREE.Mesh(new THREE.SphereGeometry(90, 32, 16), cieloMat); scene.add(cielo);
  const estrellas = (() => {
    const n = 500, p = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const a = rnd() * Math.PI * 2, e = 0.12 + rnd() * 1.3; p.set([Math.cos(a) * Math.cos(e) * 80, Math.sin(e) * 80, Math.sin(a) * Math.cos(e) * 80], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3));
    return new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 0.28, sizeAttenuation: true, transparent: true, opacity: 0, fog: false, depthWrite: false }));
  })();
  scene.add(estrellas);

  // ---------- suelo con colinas y montes, camino del tiempo, agua
  const suelo = (() => {
    const g = new THREE.PlaneGeometry(90, 160, 120, 210); g.rotateX(-Math.PI / 2); g.translate(0, 0, -60);
    const pos = g.attributes.position, cols = new Float32Array(pos.count * 3);
    for (let i = 0; i < pos.count; i++) { const x = pos.getX(i), z = pos.getZ(i), h = altura(x, z); pos.setY(i, h); const c = colorSuelo(x, z, h); cols.set([c.r, c.g, c.b], i * 3); }
    g.setAttribute("color", new THREE.BufferAttribute(cols, 3)); g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, flatShading: true })); m.receiveShadow = true;
    return m;
  })();
  scene.add(suelo);
  (() => { // cinta del camino (tierra) + piedras
    const n = 420, w = 0.75, pos = [], idx = [], uv = [];
    for (let i = 0; i <= n; i++) {
      const u = i / n, p = CAMINO.getPoint(u), tg = CAMINO.getTangent(u), lado = new THREE.Vector3(-tg.z, 0, tg.x).normalize();
      for (const s of [-1, 1]) { const q = p.clone().addScaledVector(lado, s * w); pos.push(q.x, altura(q.x, q.z) + 0.03, q.z); uv.push(s < 0 ? 0 : 1, u * 60); }
      if (i < n) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals();
    const tex = F.lienzo(256, 256, (c, W, H) => { c.fillStyle = "#c9a26a"; c.fillRect(0, 0, W, H); for (let i = 0; i < 260; i++) { c.fillStyle = `rgba(${120 + rnd() * 60},${90 + rnd() * 40},${50 + rnd() * 30},.5)`; c.beginPath(); c.arc(rnd() * W, rnd() * H, 2 + rnd() * 9, 0, 7); c.fill(); } c.fillStyle = "rgba(90,130,60,.55)"; c.fillRect(0, 0, 18, H); c.fillRect(W - 18, 0, 18, H); });
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ map: tex, roughness: 1 })); m.receiveShadow = true; scene.add(m);
  })();
  const agua = (x, z, w, d, rot = 0) => { const m = new THREE.Mesh(new THREE.CircleGeometry(1, 28), new THREE.MeshStandardMaterial({ color: 0x3aa6d9, roughness: 0.15, metalness: 0.1, emissive: 0x0b3a55, emissiveIntensity: 0.4 })); m.scale.set(w, d, 1); m.rotation.x = -Math.PI / 2; m.rotation.z = rot; m.position.set(x, altura(x, z) + 0.05, z); m.receiveShadow = true; scene.add(m); return m; };

  // pasillos despejados delante de las vallas de fotos (la cámara entra en ellas sin que un árbol tape)
  const VALLAS = { dinos: [5 - 3.3, -26 + 1.0, 0.75], selva: [-5 + 3.3, -39 + 1.1, -0.7], lab: [-4 - 2.9, -91 - 1.0, 0.55] };
  const despejado = (x, z) => Object.values(VALLAS).every(([vx, vz, r]) => { const nx = Math.sin(r), nz = Math.cos(r), px = x - vx, pz = z - vz, a = px * nx + pz * nz, b = Math.abs(px * nz - pz * nx); return a < -0.8 || a > 7 || b > 1.8; });
  const colocar = (obj, x, z, rotY = 0, esc = 1) => { obj.position.set(x, altura(x, z), z); obj.rotation.y = rotY; obj.scale.multiplyScalar(esc); scene.add(obj); return obj; };
  const sitio = (n) => SITIOS[n];
  const anim = []; // fn(t)
  const anclas = {}; // nombre → Vector3 (mundo)
  const ancla = (n, x, y, z) => { anclas[n] = new THREE.Vector3(x, altura(x, z) + y, z); };
  const vallas = {}; // sitio → {pos, normal, alto, uv de la nota}

  // vegetación de relleno a lo largo de todo el camino (lejos del camino y de las maquetas)
  const relleno = (z0, z1, fab, n, dmin = 5, dmax = 18) => {
    for (let i = 0; i < n; i++) {
      const z = lerp(z0, z1, rnd()), lado = rnd() < 0.5 ? -1 : 1, x = caminoX(z) + lado * lerp(dmin, dmax, rnd() ** 1.4);
      if (llano(x, z) < 0.6 || !despejado(x, z)) continue;
      colocar(fab(), x, z, rnd() * 6.28, 0.8 + rnd() * 0.6);
    }
  };
  relleno(10, -7, () => F.arbol({ alto: 1.3 + rnd() * 0.6 }), 16);
  relleno(-7, -20, () => (rnd() < 0.6 ? F.helechoArbol(1.4 + rnd()) : F.colaCaballo(0.8 + rnd() * 0.6)), 34, 4, 16);
  relleno(-20, -33, () => (rnd() < 0.7 ? F.palmera(1.6 + rnd(), 0x4f9a3a) : F.roca(0.4 + rnd() * 0.4, 0xa08a6a)), 24);
  relleno(-33, -46, () => (rnd() < 0.5 ? F.arbol({ alto: 2.2 + rnd(), copa: 0x2f8a3a, r: 0.85 }) : F.bambu(2.4 + rnd())), 46, 3.8, 15);
  relleno(-46, -59, () => (rnd() < 0.7 ? F.arbol({ alto: 1.4 + rnd() * 0.5, copa: 0x5aa84a }) : F.pacaHeno()), 20);
  relleno(-59, -72, () => F.arbol({ alto: 1.6 + rnd() * 0.6, copa: 0x3f8a4a }), 20);
  relleno(-72, -125, () => (rnd() < 0.8 ? F.arbol({ alto: 1.4 + rnd() * 0.7 }) : F.roca(0.35 + rnd() * 0.3)), 50);
  relleno(-125, -140, () => F.arbol({ alto: 1.8 }), 10);
  // flores por todas partes (puntitos de color)
  (() => {
    const n = 1400, p = new Float32Array(n * 3), c = new Float32Array(n * 3), cs = [0xffffff, 0xffd84a, 0xff6fa5, 0xb27cff, 0xff8a3a].map(col);
    for (let i = 0; i < n; i++) { const z = lerp(14, -130, rnd()), x = caminoX(z) + (rnd() - 0.5) * 22; if (z > -46 && z < -7) { p.set([0, -50, 0], i * 3); continue; } p.set([x, altura(x, z) + 0.06, z], i * 3); const k = cs[i % cs.length]; c.set([k.r, k.g, k.b], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); g.setAttribute("color", new THREE.BufferAttribute(c, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 0.09, vertexColors: true })));
  })();
  // hitos del camino del tiempo (carteles)
  const hito = (n, lineas, dx = -2.6, dz = 2.6, rot = 0.35, op = {}) => { const [x, z] = sitio(n); const c = F.cartel(lineas, op); colocar(c, x + dx, z + dz, rot); return c; };

  // ======================================================= SITIOS
  { // INTRO: el huevo contra la gallina, en dos pedestales
    const [x, z] = sitio("intro");
    for (const [dx, cpd] of [[-0.85, 0xffc83a], [0.85, 0x4f7cff]]) { const p = F.cil(0.55, 0.62, 0.5, cpd, 24, { metalness: 0.3, roughness: 0.4 }); colocar(p, x + dx, z, 0); p.position.y += 0.25; }
    const h = F.huevo(F.COL.crema, 1.05); colocar(h, x - 0.85, z, 0); h.position.y += 0.5;
    const ga = F.gallina(F.COL.blanco, 1.1); colocar(ga.g, x + 0.85, z, Math.PI * 0.85); ga.g.position.y += 0.5;
    const rayo = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.8), new THREE.MeshBasicMaterial({ map: F.lienzo(256, 256, (c, W) => { c.font = "900 150px Inter"; c.textAlign = "center"; c.textBaseline = "middle"; c.lineWidth = 16; c.strokeStyle = "#1d1d2b"; c.strokeText("VS", W / 2, W / 2 + 6); c.fillStyle = "#ffd23a"; c.fillText("VS", W / 2, W / 2 + 6); }), transparent: true, depthWrite: false }));
    rayo.position.set(x, 1.55, z + 0.2); scene.add(rayo);
    hito("intro", ["HOY", "¿QUIÉN FUE PRIMERO?"], 2.6, 1.8, -0.4, { acento: "#2f6fd8" });
    anim.push((t) => {
      ga.anim(t, { pica: 0.15, mira: -0.4 + Math.sin(t * 1.3) * 0.3, canta: t < 1.2 ? 0 : 0 });
      h.rotation.y = t * 0.6; h.position.y = altura(x - 0.85, z) + 0.5 + Math.sin(t * 2.4) * 0.04;
      rayo.lookAt(cam.position); rayo.scale.setScalar(1 + 0.08 * Math.sin(t * 7));
    });
    ancla("intro_huevo", x - 0.85, 1.9, z); ancla("intro_gallina", x + 0.85, 2.0, z);
  }
  { // PRIMEROS AMNIOTAS (+300 M años): pantano con helechos gigantes, volcán humeante y lagartitos junto a sus huevos
    const [x, z] = sitio("primeros");
    const v = F.volcan(); v.position.set(x - 14, altura(x - 14, z - 14) - 0.5, z - 14); v.scale.setScalar(1.3); scene.add(v);
    agua(x + 2.4, z - 1.0, 2.2, 1.3, 0.4);
    for (let i = 0; i < 9; i++) { const a = Math.PI * (1.02 + i * 0.12); colocar(F.helechoArbol(1.4 + (i % 3) * 0.5), x + Math.cos(a) * (3.2 + (i % 2)), z + Math.sin(a) * 2.6 - 0.6, a); } // solo detrás: la cámara mira desde el sur
    for (let i = 0; i < 9; i++) colocar(F.colaCaballo(0.6 + (i % 3) * 0.25), x - 1.8 + (i % 3) * 0.25, z + 1.2 + Math.floor(i / 3) * 0.25, 0);
    colocar(F.roca(0.5, 0x7d6f62), x - 1.2, z - 0.6, 0.3);
    const huevos = [];
    for (let i = 0; i < 7; i++) { const e = F.huevo(0xefe3c4, 0.27); const a = i * 0.9; colocar(e, x + 0.4 + Math.cos(a) * 0.28, z + 0.5 + Math.sin(a) * 0.22, 0); huevos.push(e); }
    const lag = [0, 1, 2].map((i) => { const l = F.lagarto({ escala: 1.6 - i * 0.25, piel: [0x6f7a3a, 0x7d6a3a, 0x5d7a4a][i] }); scene.add(l.g); return l; });
    const humo = [];
    for (let i = 0; i < 10; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: ctx.GLOW, color: 0x8a7a70, transparent: true, opacity: 0.5, depthWrite: false })); scene.add(s); humo.push(s); }
    hito("primeros", ["HACE +300", "MILLONES DE AÑOS"], -2.4, 2.4, 0.5);
    anim.push((t) => {
      const w = ventana("primeros", t), k = w ? w.tl : -9;
      huevos.forEach((e, i) => { const s = eob(clamp((k - 0.5 - i * 0.18) / 0.4)); e.scale.setScalar(Math.max(0.001, s)); });
      lag.forEach((l, i) => {
        const u = (t * 0.07 + i * 0.33) % 1, a = u * Math.PI * 2;
        const px = x + 0.4 + Math.cos(a) * (0.9 + i * 0.3), pz = z + 0.5 + Math.sin(a) * (0.6 + i * 0.2);
        l.g.position.set(px, altura(px, pz), pz); l.g.rotation.y = -a - Math.PI / 2 + Math.PI; l.anim(t, { anda: 1, fase: i * 2 });
      });
      humo.forEach((s, i) => { const u = (t * 0.12 + i / humo.length) % 1; s.position.set(v.position.x + Math.sin(i * 3 + t * 0.3) * 1.5 * u, v.position.y + 9 + u * 9, v.position.z + u * 2); s.scale.setScalar(2 + u * 7); s.material.opacity = 0.55 * Math.sin(u * Math.PI); });
    });
    ancla("primeros_huevos", x + 0.4, 0.6, z + 0.5); ancla("primeros_lagarto", x - 0.6, 0.8, z + 1.1);
  }
  { // DINOSAURIOS (195 M años): terópodo junto a su nido, saurópodo que cruza al fondo, foto de huevos fósiles en un caballete
    const [x, z] = sitio("dinos");
    const ni = F.nido(0.75); colocar(ni, x + 1.4, z + 0.9, 0);
    const hs = [];
    for (let i = 0; i < 7; i++) { const a = (i / 6) * Math.PI * 2, e = F.huevo(i % 2 ? 0xe8dcc0 : 0xf2e8d0, 0.42); colocar(e, x + 1.4 + (i < 6 ? Math.cos(a) * 0.36 : 0), z + 0.9 + (i < 6 ? Math.sin(a) * 0.36 : 0), 0); e.position.y += 0.08; e.rotation.z = i < 6 ? 0.25 : 0; e.rotation.y = -a; hs.push(e); }
    const ter = F.teropodo({ escala: 0.95 }); scene.add(ter.g);
    const sau = F.sauropodo({ escala: 1.15 }); scene.add(sau.g);
    for (let i = 0; i < 6; i++) if (despejado(x - 3 + i * 1.3, z - 3.2 - (i % 2) * 1.2)) colocar(F.palmera(1.8 + (i % 3) * 0.6, 0x4f9a3a), x - 3 + i * 1.3, z - 3.2 - (i % 2) * 1.2, i);
    colocar(F.roca(0.7, 0xa08a6a), x - 1.6, z + 1.6, 0.4); colocar(F.roca(0.45, 0x9a8466), x + 3.0, z + 0.2, 1.2);
    const cartelNoche = F.cartel(["GALLINAS", "0"], { ancho: 1.2, acento: "#d8322f" }); colocar(cartelNoche, x + 2.7, z + 2.6, -0.9);
    const luci = (() => { const n = 70, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) p.set([x + (rnd() - 0.5) * 9, 0.4 + rnd() * 2.2, z + (rnd() - 0.5) * 7], i * 3); const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.12, map: ctx.GLOW, color: 0xfff27a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); scene.add(m); return { m, p0: p.slice() }; })();
    hito("dinos", ["HACE 195", "MILLONES DE AÑOS"], -2.8, 2.6, 0.45);
    anim.push((t) => {
      const w = ventana("dinos", t), k = w ? w.tl : 99;
      hs.forEach((e, i) => { const s = eob(clamp((k - 0.3 - i * 0.12) / 0.35)); e.scale.setScalar(Math.max(0.001, s)); });
      // terópodo: llega andando al nido y se agacha a mirarlo
      const llega = clamp((t - hitos[Math.max(0, paradas.findIndex((p) => p.zona === "dinos"))] + 0.6) / 2.6), px = lerp(x - 2.6, x + 0.1, eo(llega)), pz = lerp(z - 0.6, z + 0.5, eo(llega));
      ter.g.position.set(px, altura(px, pz), pz); ter.g.rotation.y = 0.35;
      ter.anim(t, { anda: llega < 1 ? 1 : 0, agacha: llega >= 1 ? 0.5 + 0.2 * Math.sin(t * 1.5) : 0, ruge: clamp(1 - Math.abs(t - (usa("dinos_noche")?.t0 ?? -9) - 0.4) / 0.5) });
      const u = (t * 0.022) % 1, sx = x - 9 + u * 18, sz = z - 6.5;
      sau.g.position.set(sx, altura(sx, sz), sz); sau.g.rotation.y = 0; sau.anim(t, { anda: 1 });
      const noche = ventana("dinos_noche", t), on = noche ? clamp(noche.tl / 0.6) * clamp((noche.d + 0.8 - noche.tl) / 0.8) : 0;
      luci.m.material.opacity = on * 0.95; const a = luci.m.geometry.attributes.position;
      for (let i = 0; i < a.count; i++) { a.array[i * 3 + 1] = luci.p0[i * 3 + 1] + Math.sin(t * 1.3 + i) * 0.25; a.array[i * 3] = luci.p0[i * 3] + Math.sin(t * 0.7 + i * 2) * 0.3; }
      a.needsUpdate = true;
    });
    ancla("dinos_nido", x + 1.4, 1.0, z + 0.9); ancla("dinos_dino", x, 2.4, z + 0.5); ancla("dinos_cartel", x + 2.7, 1.9, z + 2.6);
    vallas.dinos = { x: x - 3.3, z: z + 1.0, rot: 0.75, alto: 2.6 };
  }
  { // SELVA del sudeste asiático: gallo bankiva cantando sobre un tronco, su hembra picoteando, bambú, árboles y lianas
    const [x, z] = sitio("selva");
    agua(x + 3.5, z - 1.5, 4.5, 1.0, -0.3);
    for (let i = 0; i < 12; i++) { const a = Math.PI * (1.0 + i * 0.09), r = 3.0 + (i % 3) * 0.9; if (!despejado(x + Math.cos(a) * r, z + Math.sin(a) * r * 0.8 - 1.4)) continue; colocar(i % 3 ? F.arbol({ alto: 2.2 + (i % 4) * 0.4, copa: 0x2f8a3a, r: 0.9 }) : F.bambu(2.8 + (i % 2)), x + Math.cos(a) * r, z + Math.sin(a) * r * 0.8 - 1.4, a); }
    const tronco = F.cil(0.22, 0.26, 2.0, 0x6b4426, 12); tronco.rotation.z = Math.PI / 2; tronco.rotation.y = 0.3; colocar(tronco, x - 0.2, z + 0.2, 0.3); tronco.position.y += 0.24;
    const gallo = F.bankiva(1.1); colocar(gallo.g, x - 0.2, z + 0.2, 0.35); gallo.g.position.y += 0.46;
    const hembra = F.bankivaHembra(0.95); scene.add(hembra.g);
    const pols = [0, 1, 2].map((i) => { const p = F.pollito(0.75); scene.add(p.g); return p; });
    const hojas = [];
    for (let i = 0; i < 18; i++) { const h = F.bola(0.06, i % 2 ? 0x3f9a3a : 0x8ab83a, 1.6, 0.15, 0.9); scene.add(h); hojas.push(h); }
    hito("selva", ["SUDESTE", "ASIÁTICO"], 2.5, 2.3, -0.45, { acento: "#2f9a4a" });
    anim.push((t) => {
      const w = ventana("selva", t);
      gallo.anim(t, { canta: w ? clamp(1 - Math.abs(w.tl - 0.9) / 0.6) : 0, aletea: w ? clamp(1 - Math.abs(w.tl - 0.7) / 0.4) : 0, mira: 0.3 * Math.sin(t * 0.8) });
      const u = t * 0.25, hx = x + 1.0 + Math.cos(u) * 0.6, hz = z + 1.0 + Math.sin(u) * 0.4;
      hembra.g.position.set(hx, altura(hx, hz), hz); hembra.g.rotation.y = -u - Math.PI / 2; hembra.anim(t, { anda: 0.5, pica: 0.8, fase: 1 });
      pols.forEach((p, i) => { const a = u + 0.6 + i * 0.5, px = x + 1.0 + Math.cos(a) * (0.6 + 0.25 * i), pz = z + 1.0 + Math.sin(a) * (0.45 + 0.2 * i); p.g.position.set(px, altura(px, pz), pz); p.g.rotation.y = -a - Math.PI / 2; p.anim(t, { pica: 0.9, fase: i * 1.7 }); });
      hojas.forEach((h, i) => { const k = (t * 0.09 + i / hojas.length) % 1; h.position.set(x + Math.sin(i * 7.1) * 3 + Math.sin(t + i) * 0.4, 3.6 - k * 3.6, z + Math.cos(i * 3.3) * 2.4); h.rotation.set(t * 2 + i, t + i, t * 1.4); });
    });
    ancla("selva_gallo", x - 0.2, 2.0, z + 0.2); ancla("selva_hembra", x + 1.0, 1.2, z + 1.0);
    vallas.selva = { x: x + 3.3, z: z + 1.1, rot: -0.7, alto: 2.6 };
  }
  { // GRANJA (gallina doméstica, hace 3.500 años): granero, gallinero, valla, pacas, gallinas que pasean y picotean, pollitos
    const [x, z] = sitio("granja");
    colocar(F.granero(), x - 1.6, z - 2.2, 0.25);
    colocar(F.gallinero(), x + 2.0, z - 1.4, -0.4);
    for (const [dx, dz, r] of [[-3.0, 1.5, Math.PI / 2], [0, 3.3, 0], [3.2, 1.5, Math.PI / 2]]) colocar(F.valla(3.4), x + dx, z + dz, r);
    for (let i = 0; i < 4; i++) colocar(F.pacaHeno(), x - 3.6 + (i % 2) * 0.7, z - 0.6 + Math.floor(i / 2) * 0.75, 0.2 * i);
    const colores = [F.COL.blanco, 0xc0743a, 0x8a4a28, F.COL.blanco, 0xd9a066, 0x2a2a30];
    const gs = colores.map((c, i) => { const a = F.gallina(c, 0.82 + (i % 3) * 0.06); scene.add(a.g); return a; });
    const pols = Array.from({ length: 5 }, () => { const p = F.pollito(0.7); scene.add(p.g); return p; });
    const cesta = new THREE.Group(); const cj = F.cil(0.32, 0.26, 0.26, 0xa8703a, 16); cj.position.y = 0.13; cesta.add(cj);
    for (let i = 0; i < 6; i++) { const e = F.huevo(i % 2 ? 0xf0dcc0 : 0xfff6e6, 0.2); e.position.set(Math.cos(i) * 0.14, 0.18, Math.sin(i) * 0.14); e.rotation.z = 0.6; cesta.add(e); }
    colocar(cesta, x + 1.1, z + 1.6, 0);
    hito("granja", ["HACE 3.500", "AÑOS"], -2.6, 2.6, 0.5);
    anim.push((t) => {
      gs.forEach((a, i) => {
        const r = 0.55 + i * 0.42, v = 0.2 / (1 + i * 0.25), u = t * v * (i % 2 ? 1 : -1) + i * 0.9; // un anillo por gallina: no se atraviesan
        const px = x + 0.2 + Math.cos(u) * r * 1.3, pz = z + 0.6 + Math.sin(u) * r * 0.8;
        a.g.position.set(px, altura(px, pz), pz); a.g.rotation.y = -u + (i % 2 ? -Math.PI / 2 : Math.PI / 2);
        const anda = Math.sin(t * 0.7 + i) > -0.2; a.anim(t, { anda: anda ? 0.55 : 0, pica: anda ? 0.2 : 1, fase: i * 1.3 });
        if (!anda) a.g.position.x -= 0; // quieta picoteando
      });
      pols.forEach((p, i) => { const g = gs[i % 3], a = t * 0.8 + i * 1.3; const px = g.g.position.x + Math.cos(a) * 0.45 - 0.3, pz = g.g.position.z + Math.sin(a) * 0.35; p.g.position.set(px, altura(px, pz), pz); p.g.rotation.y = -a; p.anim(t, { pica: 0.9, fase: i, salta: i % 2 }); });
    });
    ancla("granja_gallinas", x + 0.2, 1.4, z + 0.6); ancla("granja_granero", x - 1.6, 3.0, z - 2.2);
  }
  { // EL TRUCO: claro con un nido bajo un foco, un ave "casi gallina" pone el huevo y de él nace la primera gallina
    const [x, z] = sitio("nido");
    const tarima = F.cil(1.7, 1.85, 0.16, 0x9a7a44, 32, { roughness: 1 }); colocar(tarima, x, z, 0); tarima.position.y += 0.08;
    const ni = F.nido(0.5); colocar(ni, x + 0.15, z + 0.2, 0); ni.position.y += 0.16;
    const ave = F.casiGallina(1.15); scene.add(ave.g);
    const hv = F.huevoQueNace(0xfff1d8, 0.62); scene.add(hv.g);
    const brillo = new THREE.Sprite(new THREE.SpriteMaterial({ map: ctx.GLOW, color: 0xffe08a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); scene.add(brillo);
    const pol = F.pollito(1.25); scene.add(pol.g);
    const foco = new THREE.SpotLight(0xfff0c8, 0, 14, 0.42, 0.5, 1.2); foco.position.set(x + 0.5, 6.5, z + 1.5); foco.target.position.set(x + 0.15, 0, z + 0.2); foco.castShadow = false; scene.add(foco, foco.target);
    const cono = new THREE.Mesh(new THREE.ConeGeometry(2.0, 6.3, 32, 1, true), new THREE.MeshBasicMaterial({ color: 0xfff2c8, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }));
    cono.position.set(x + 0.32, 3.3, z + 0.85); cono.lookAt(x + 0.15, 0, z + 0.2); cono.rotateX(Math.PI / 2); cono.rotateX(Math.PI); scene.add(cono);
    const preg = [0, 1, 2].map((i) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: F.lienzo(256, 256, (c, W) => { c.font = "900 220px Inter"; c.textAlign = "center"; c.textBaseline = "middle"; c.lineWidth = 18; c.strokeStyle = "#2a1640"; c.strokeText("?", W / 2, W / 2 + 10); c.fillStyle = ["#ffd23a", "#ff7ab8", "#7ad8ff"][i]; c.fillText("?", W / 2, W / 2 + 10); }), transparent: true, depthWrite: false })); scene.add(s); return s; });
    // hélice de ADN (mutaciones) que sube al nacer
    const adn = new THREE.Group(); const bolasAdn = [];
    for (let i = 0; i < 28; i++) for (const s of [0, 1]) { const b = F.bola(0.045, s ? 0x4fd1ff : 0xff6fa5, 1, 1, 1, { emissive: s ? 0x4fd1ff : 0xff6fa5, emissiveIntensity: 0.9 }); adn.add(b); bolasAdn.push({ b, i, s }); }
    adn.position.set(x + 1.15, altura(x, z) + 0.3, z - 0.2); scene.add(adn);
    const confeti = (() => { const n = 90, p = new Float32Array(n * 3), c = new Float32Array(n * 3), cs = [0xffd23a, 0xff6fa5, 0x4fd1ff, 0x7dff9a, 0xffffff].map(col); for (let i = 0; i < n; i++) { const k = cs[i % 5]; c.set([k.r, k.g, k.b], i * 3); } const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); g.setAttribute("color", new THREE.BufferAttribute(c, 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.07, vertexColors: true, transparent: true, opacity: 0 })); scene.add(m); return m; })();
    const yN = altura(x, z) + 0.2;
    anim.push((t) => {
      const tr = ventana("truco", t), po = ventana("pone", t), na = ventana("nace", t);
      if (!tr || !po || !na) return;
      const misterio = tr.dentro ? clamp(tr.tl / 0.8) : po.dentro ? 1 : na.dentro ? clamp(1 - na.tl / 1.2) : 0;
      foco.intensity = 22 * misterio; cono.material.opacity = 0.1 * misterio; cono.visible = misterio > 0.01;
      preg.forEach((s, i) => { const on = tr.dentro ? clamp((tr.tl - 0.3 - i * 0.25) / 0.3) * clamp((tr.d + 0.3 - tr.tl) / 0.4) : 0; s.material.opacity = on; s.position.set(x - 0.9 + i * 0.9, yN + 1.9 + Math.sin(t * 2 + i) * 0.12 + i % 2 * 0.25, z + 0.3); s.scale.setScalar(0.55 * Math.max(0.001, eob(on))); });
      // el ave: llega, se sienta en el nido (pone), se levanta y se aparta
      const kPone = clamp(po.k);
      const sentada = clamp(kPone / 0.25) * (1 - clamp((kPone - 0.6) / 0.25));
      const aparta = clamp((kPone - 0.6) / 0.4);
      const ax = x + 0.15 - 0.15 + lerp(0, -1.0, eo(aparta)) + lerp(-1.2, 0, eo(clamp(tr.tl / tr.d))), az = z + 0.2 + lerp(0, 0.2, aparta);
      ave.g.position.set(ax, yN + 0.12 * sentada, az); ave.g.rotation.y = lerp(0.3, 1.0, aparta);
      ave.anim(t, { sentada: eo(sentada), anda: tr.dentro && tr.k < 0.95 ? 0.5 : aparta > 0 && aparta < 1 ? 0.6 : 0, pica: 0.1, mira: aparta >= 1 ? 0.8 : 0.2 * Math.sin(t), aletea: clamp(1 - Math.abs(po.k - 0.62) / 0.12), canta: clamp(1 - Math.abs(na.tl - 1.3) / 0.5) });
      // el huevo aparece al levantarse el ave
      const ve = clamp((po.k - 0.55) / 0.1);
      hv.g.visible = ve > 0; hv.g.position.set(x + 0.15, yN + 0.02, z + 0.2); hv.g.scale.setScalar(Math.max(0.001, eob(ve)));
      hv.anim(clamp(na.tl / 1.3));
      brillo.position.set(x + 0.15, yN + 0.4, z + 0.2); brillo.scale.setScalar(1.6 + Math.sin(t * 5) * 0.1); brillo.material.opacity = po.dentro ? ve * 0.9 : na.dentro ? clamp(1 - na.tl / 1.5) * 0.9 : 0;
      // nace el pollito (la 1.ª gallina)
      const sale = clamp((na.tl - 0.95) / 0.45);
      pol.g.visible = sale > 0; pol.g.position.set(x + 0.15, yN + 0.02 + eob(sale) * 0.25, z + 0.2); pol.g.rotation.y = 0.4;
      pol.anim(t, { pica: 0.2, aletea: clamp(1 - Math.abs(na.tl - 1.8) / 0.6), salta: sale >= 1 ? 1 : 0 });
      const kad = clamp((na.tl - 0.2) / 0.8) * clamp((na.d + 1.5 - na.tl) / 0.6);
      adn.visible = kad > 0; adn.scale.setScalar(Math.max(0.001, eob(kad)));
      bolasAdn.forEach(({ b, i, s }) => { const a = i * 0.45 + t * 2 + s * Math.PI; b.position.set(Math.cos(a) * 0.22, i * 0.075, Math.sin(a) * 0.22); });
      const kc = clamp((na.tl - 1.2) / 2.5); confeti.material.opacity = kc > 0 && kc < 1 ? 1 : 0;
      const ca = confeti.geometry.attributes.position; for (let i = 0; i < ca.count; i++) { const a = i * 2.39, r = 0.3 + (i % 7) * 0.12; ca.array.set([x + 0.15 + Math.cos(a) * r * (0.5 + kc * 2), yN + 0.4 + Math.sin(kc * Math.PI) * (1.2 + (i % 5) * 0.25) - kc * 0.6, z + 0.2 + Math.sin(a) * r * (0.5 + kc * 2)], i * 3); } ca.needsUpdate = true;
    });
    ancla("nido_ave", x - 0.2, 1.6, z + 0.2); ancla("nido_huevo", x + 0.15, 1.1, z + 0.2); ancla("nido_adn", x + 1.15, 2.4, z - 0.2); ancla("nido_pollito", x + 0.15, 1.0, z + 0.2);
  }
  { // PODIO: el huevo gana
    const [x, z] = sitio("podio");
    for (const [dx, h, c, num] of [[0, 1.2, F.COL.oro, "1"], [-1.25, 0.8, F.COL.plata, "2"], [1.25, 0.5, F.COL.bronce, "3"]]) {
      const b = F.caja(1.15, h, 1.0, c, { metalness: 0.55, roughness: 0.3 }); colocar(b, x + dx, z, 0); b.position.y += h / 2;
      const n = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.5), new THREE.MeshBasicMaterial({ map: F.lienzo(128, 128, (g, W) => { g.font = "900 110px Inter"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillStyle = "#ffffff"; g.fillText(num, W / 2, W / 2 + 6); }), transparent: true }));
      n.position.set(x + dx, altura(x, z) + h * 0.5, z + 0.51); scene.add(n);
    }
    const h = F.huevo(F.COL.crema, 1.0); scene.add(h);
    const corona = new THREE.Group(); const aro = F.cil(0.24, 0.26, 0.16, F.COL.oro, 24, { metalness: 0.9, roughness: 0.2 }); corona.add(aro);
    for (let i = 0; i < 6; i++) { const p = F.cono(0.06, 0.18, F.COL.oro, 6, { metalness: 0.9, roughness: 0.2 }); const a = (i / 6) * Math.PI * 2; p.position.set(Math.cos(a) * 0.22, 0.15, Math.sin(a) * 0.22); corona.add(p); const j = F.bola(0.03, i % 2 ? 0xff3a5a : 0x3a8aff, 1, 1, 1, { emissive: i % 2 ? 0xff3a5a : 0x3a8aff, emissiveIntensity: 0.5 }); j.position.set(Math.cos(a) * 0.255, 0.02, Math.sin(a) * 0.255); corona.add(j); }
    scene.add(corona);
    const ga = F.gallina(F.COL.blanco, 0.85); colocar(ga.g, x - 1.25, z, 0.5); ga.g.position.y += 0.8;
    const dino = F.teropodo({ escala: 0.38 }); colocar(dino.g, x + 1.25, z, -0.5); dino.g.position.y += 0.5;
    const conf = (() => { const n = 160, p = new Float32Array(n * 3), c = new Float32Array(n * 3), cs = [0xffd23a, 0xff6fa5, 0x4fd1ff, 0x7dff9a, 0xff8a3a].map(col); for (let i = 0; i < n; i++) { const k = cs[i % 5]; c.set([k.r, k.g, k.b], i * 3); } const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); g.setAttribute("color", new THREE.BufferAttribute(c, 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.08, vertexColors: true })); scene.add(m); return m; })();
    const y0 = altura(x, z) + 1.2;
    anim.push((t) => {
      const w = ventana("podio", t), k = w ? w.tl : 9;
      const cae = eob(clamp((k - 0.15) / 0.6));
      h.position.set(x, y0 + (1 - cae) * 3 + Math.sin(t * 2.4) * 0.03, z); h.rotation.y = t * 0.9;
      corona.position.set(x, y0 + 1.02 + (1 - eob(clamp((k - 0.6) / 0.5))) * 2.5 + Math.sin(t * 2.4) * 0.03, z); corona.rotation.y = t * 0.9; corona.visible = k > 0.55;
      ga.anim(t, { pica: 0.1, mira: -0.6, aletea: w ? clamp(1 - Math.abs(k - 1.2) / 0.5) * 0.6 : 0 }); dino.anim(t, { ruge: w ? clamp(1 - Math.abs(k - 1.5) / 0.4) : 0 });
      const ca = conf.geometry.attributes.position; for (let i = 0; i < ca.count; i++) { const u = ((t * 0.35 + (i * 0.618) % 1) % 1); ca.array.set([x + Math.sin(i * 12.9) * 2.4 + Math.sin(t + i) * 0.2, altura(x, z) + 4.2 - u * 4.2, z + Math.cos(i * 7.3) * 1.6], i * 3); } ca.needsUpdate = true;
      conf.visible = k > 0.6 && k < 30;
    });
    ancla("podio_huevo", x, 2.9, z); ancla("podio_gallina", x - 1.25, 2.2, z);
  }
  { // LABORATORIO 2010: suelo de baldosas, mesa, microscopio, matraces que burbujean, la proteína que se pliega
    const [x, z] = sitio("lab");
    const losa = new THREE.Mesh(new THREE.BoxGeometry(5.2, 0.14, 4.2), new THREE.MeshStandardMaterial({ map: (() => { const t = F.lienzo(512, 512, (g, W) => { for (let i = 0; i < 8; i++) for (let j = 0; j < 8; j++) { g.fillStyle = (i + j) % 2 ? "#e9eef5" : "#d4dde8"; g.fillRect(i * 64, j * 64, 64, 64); } }); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t; })(), roughness: 0.5 }));
    losa.receiveShadow = true; colocar(losa, x, z, 0.15); losa.position.y += 0.07;
    const mesa = new THREE.Group(); mesa.add(F.en(F.caja(2.6, 0.08, 1.0, 0xf6f7fb), 0, 0.9, 0));
    for (const sx of [-1.2, 1.2]) for (const sz of [-0.42, 0.42]) mesa.add(F.en(F.cil(0.04, 0.04, 0.9, 0x9aa3b5, 8), sx, 0.45, sz));
    colocar(mesa, x, z - 0.6, 0.15); mesa.position.y += 0.14;
    const mic = F.microscopio(); mic.scale.setScalar(1.25); mesa.add(mic); mic.position.set(-0.75, 0.94, 0.05); mic.rotation.y = 0.5;
    const mts = [0x4fd1ff, 0xff6fa5, 0x7dff9a].map((c, i) => { const m = F.matraz(c); mesa.add(m); m.position.set(0.1 + i * 0.42, 0.94, 0.15 - (i % 2) * 0.2); m.scale.setScalar(1.2); return m; });
    const gradilla = new THREE.Group(); gradilla.add(F.en(F.caja(0.5, 0.05, 0.16, 0xffffff), 0, 0.12, 0));
    [0xffd23a, 0xff6fa5, 0x4fd1ff, 0x7dff9a].forEach((c, i) => { const tb = F.tuboEnsayo(c); tb.position.set(-0.18 + i * 0.12, 0.02, 0); gradilla.add(tb); });
    mesa.add(gradilla); gradilla.position.set(0.95, 0.94, -0.25);
    const prot = F.proteina(); scene.add(prot.g); prot.g.position.set(x + 0.5, altura(x, z) + 2.35, z - 0.2);
    const cascara = F.huevoQueNace(0xfff3dc, 0.75); colocar(cascara.g, x - 1.7, z + 0.9, 0); cascara.g.position.y += 0.14; cascara.anim(0.75);
    const burb = (() => { const n = 40, g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(n * 3), 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.05, color: 0xdff8ff, transparent: true, opacity: 0.85 })); scene.add(m); return m; })();
    hito("lab", ["AÑO", "2010"], 2.7, 2.2, -0.45, { acento: "#2f6fd8" });
    anim.push((t) => {
      const w = ventana("lab", t); prot.anim(t, w ? 0.25 + 0.75 * eo(clamp((w.tl - 0.4) / 2.2)) : 1);
      prot.g.rotation.y = t * 0.5;
      mesa.updateMatrixWorld(true);
      const ba = burb.geometry.attributes.position, v = new THREE.Vector3();
      for (let i = 0; i < ba.count; i++) { const m = mts[i % 3], u = (t * 0.6 + (i * 0.37) % 1) % 1; v.set(Math.sin(i * 5) * 0.05, 0.1 + u * 0.6, Math.cos(i * 3) * 0.05); m.localToWorld(v); ba.array.set([v.x, v.y, v.z], i * 3); }
      ba.needsUpdate = true;
    });
    ancla("lab_proteina", x + 0.5, 3.2, z - 0.2); ancla("lab_microscopio", x - 0.75, 2.1, z - 0.55); ancla("lab_cascara", x - 1.7, 1.3, z + 0.9);
    vallas.lab = { x: x - 2.9, z: z - 1.0, rot: 0.55, alto: 2.4 };
  }
  { // LO MATIZAN: balanza con una gallina y un huevo que no se decide
    const [x, z] = sitio("matiz");
    const b = F.balanza(); colocar(b.g, x, z, 0);
    const ga = F.gallina(F.COL.blanco, 0.62); b.platos[0].carga.add(ga.g); ga.g.rotation.y = 0.6;
    const h = F.huevo(F.COL.crema, 0.62); b.platos[1].carga.add(h);
    for (const dx of [-2.6, 2.6]) colocar(F.arbol({ alto: 1.6 }), x + dx, z - 1.6, 0);
    anim.push((t) => {
      const w = ventana("matiz", t), k = w ? w.tl : 0;
      b.anim(Math.sin(k * 2.6) * 0.22 * Math.exp(-k * 0.15) + (w ? 0 : 0.0));
      ga.anim(t, { pica: 0.1, mira: 0.3 * Math.sin(t) });
    });
    ancla("matiz_gallina", x - 1.05, 2.3, z); ancla("matiz_huevo", x + 1.05, 2.3, z);
  }
  { // FINAL: plaza con los dos candidatos y la votación
    const [x, z] = sitio("final");
    const plaza = F.cil(3.2, 3.3, 0.12, 0xd9d2c3, 40, { roughness: 0.9 }); colocar(plaza, x, z, 0); plaza.position.y += 0.06;
    const ped = [[-1.1, 0xffc83a], [1.1, 0x4f7cff]].map(([dx, c]) => { const p = F.cil(0.6, 0.7, 0.7, c, 24, { metalness: 0.3, roughness: 0.4 }); p.material = p.material.clone(); colocar(p, x + dx, z, 0); p.position.y += 0.47; return p; });
    const h = F.huevo(F.COL.crema, 1.1); colocar(h, x - 1.1, z, 0); h.position.y += 0.82;
    const ga = F.gallina(F.COL.blanco, 1.3); colocar(ga.g, x + 1.1, z, -0.6); ga.g.position.y += 0.82;
    const carteles = [["🥚", "HUEVO", -1.1, "#e8a400"], ["🐔", "GALLINA", 1.1, "#2f6fd8"]].map(([e, txt, dx, c]) => { const s = F.cartel([e + " " + txt], { ancho: 1.5, acento: c, tinta: c, poste: false }); colocar(s, x + dx, z + 0.9, 0); s.position.y += 0.15; return s; });
    anim.push((t) => {
      const w = ventana("final", t), k = w ? w.tl : 0;
      h.rotation.y = t * 0.8; h.position.y = altura(x, z) + 0.82 + Math.abs(Math.sin(t * 3)) * 0.05 * (w ? 1 : 0);
      ga.anim(t, { pica: 0.1, aletea: w ? clamp(1 - Math.abs(k - 1.0) / 0.4) : 0, canta: w ? clamp(1 - Math.abs(k - 1.6) / 0.4) : 0, mira: -0.4 });
      carteles.forEach((s, i) => { s.scale.setScalar(1 + 0.05 * Math.sin(t * 4 + i * Math.PI)); });
      ped.forEach((p, i) => { p.material.emissive?.set?.(i ? 0x2a4fbf : 0xa86f00); p.material.emissiveIntensity = 0.25 + 0.25 * Math.sin(t * 4 + i * Math.PI); });
    });
    ancla("final_huevo", x - 1.1, 2.4, z); ancla("final_gallina", x + 1.1, 2.6, z);
  }

  // ---------- fotos dibujadas: vallas (para entrar a pantalla completa) y polaroids colgando
  const fotos = S.fotos || {};
  const fotoVallas = {}; // id de foto → {centro, normal, alto, pic, nota}
  for (const [i, p] of paradas.entries()) {
    const f = p.foto && fotos[p.foto.id]; const v = vallas[p.z.sitio];
    if (!f || !v || fotoVallas[p.foto.id]) continue;
    const m = await F.marcoFoto(f.src, { tipo: "valla", alto: v.alto });
    const y = altura(v.x, v.z) + v.alto / 2 + v.alto * 0.7 - 0.05;
    m.position.set(v.x, y, v.z); m.rotation.y = v.rot; scene.add(m);
    m.updateMatrixWorld(true);
    const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(m.quaternion);
    fotoVallas[p.foto.id] = { m, centro: new THREE.Vector3(v.x, y, v.z), normal, alto: v.alto, ancho: m.userData.w, f, parada: i };
  }
  const galeria = S.galeria || [];
  const cuerdas = [{ sitio: "granja", dx: 0.6, dz: -3.6, rot: 0.1 }, { sitio: "lab", dx: 0.4, dz: -2.4, rot: 0.1 }];
  let gi = 0;
  for (const cu of cuerdas) {
    if (gi >= galeria.length) break;
    const [sx, sz] = sitio(cu.sitio), x = sx + cu.dx, z = sz + cu.dz, n = Math.min(3, galeria.length - gi), largo = 1.5 * n + 0.6;
    const grupo = new THREE.Group(); grupo.position.set(x, altura(x, z), z); grupo.rotation.y = cu.rot; scene.add(grupo);
    for (const s of [-1, 1]) grupo.add(F.en(F.cil(0.05, 0.06, 2.6, F.COL.maderaOsc, 8), (s * largo) / 2, 1.3, 0));
    const cuerda = new THREE.Mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(new THREE.Vector3(-largo / 2, 2.5, 0), new THREE.Vector3(0, 2.25, 0), new THREE.Vector3(largo / 2, 2.5, 0)), 20, 0.012, 4), F.mat(0xf2f2f2)); grupo.add(cuerda);
    for (let k = 0; k < n; k++, gi++) {
      const pf = await F.marcoFoto(galeria[gi].src, { alto: 0.95, pie: galeria[gi].pie || "" });
      const px = -largo / 2 + 0.3 + 0.75 + k * 1.5; pf.position.set(px, 2.3 - 0.06 * Math.sin(((px + largo / 2) / largo) * Math.PI) - 0.6, 0.02); pf.rotation.z = (k % 2 ? 1 : -1) * 0.05; grupo.add(pf);
      const pinza = F.caja(0.05, 0.12, 0.04, 0xd8a050); pinza.position.set(px, 2.3 - 0.06 * Math.sin(((px + largo / 2) / largo) * Math.PI) + 0.02, 0.03); grupo.add(pinza);
      anim.push((t) => { pf.rotation.z = (k % 2 ? 1 : -1) * 0.05 + Math.sin(t * 1.4 + k) * 0.03; });
    }
  }

  // ---------- bandada de pájaros a lo lejos y mariposas: siempre pasa algo en el aire
  const bandada = Array.from({ length: 9 }, (_, i) => {
    const g = new THREE.Group(), m = F.mat(0x2a2a35);
    const alas = [-1, 1].map((s) => { const a = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.015, 0.1), m); a.geometry.translate(0.17 * s, 0, 0); g.add(a); return { a, s }; });
    g.add(new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.05, 0.2), m)); scene.add(g);
    return { g, alas, i };
  });
  const mariposas = Array.from({ length: 10 }, (_, i) => {
    const g = new THREE.Group(), c = [0xffd23a, 0xff6fa5, 0x7ad8ff, 0xffffff][i % 4];
    const alas = [-1, 1].map((s) => { const a = new THREE.Mesh(new THREE.CircleGeometry(0.07, 8), F.mat(c, { side: THREE.DoubleSide, emissive: c, emissiveIntensity: 0.2 })); a.geometry.translate(0.07 * s, 0, 0); a.rotation.x = -Math.PI / 2; const p = new THREE.Group(); p.add(a); g.add(p); return { p, s }; });
    scene.add(g); return { g, alas, i, sitio: ["granja", "intro", "selva", "matiz", "final"][i % 5] };
  });
  anim.push((t) => {
    const c = cam.position;
    bandada.forEach(({ g, alas, i }) => {
      const u = ((t * 0.035 + 0.13) % 1);
      g.position.set(c.x - 14 + u * 28 + (i % 3) * 0.6, 7.5 + Math.sin(i * 1.7) * 0.6 + (i % 3) * 0.3 + Math.sin(t + i) * 0.15, c.z - 16 - Math.floor(i / 3) * 0.7 - (i % 3) * 0.5);
      g.rotation.y = -Math.PI / 2; alas.forEach(({ a, s }) => { a.rotation.z = s * Math.sin(t * 9 + i) * 0.6; });
    });
    mariposas.forEach(({ g, alas, i, sitio: n }) => {
      const [sx, sz] = SITIOS[n], a = t * 0.6 + i * 2.1, px = sx + Math.cos(a) * (1.6 + (i % 3) * 0.5), pz = sz + 1.2 + Math.sin(a * 1.3) * 1.2;
      g.position.set(px, altura(px, pz) + 0.7 + Math.sin(t * 2.3 + i) * 0.25, pz); g.rotation.y = -a;
      alas.forEach(({ p, s }) => { p.rotation.z = s * (0.3 + Math.abs(Math.sin(t * 14 + i)) * 1.0); });
    });
  });

  // ---------- polen/polvo en el aire (da profundidad)
  const polvo = (() => { const n = 260, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) p.set([(rnd() - 0.5) * 16, rnd() * 5, (rnd() - 0.5) * 16], i * 3); const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.035, map: ctx.GLOW, color: 0xffffff, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false })); scene.add(m); return { m, p0: p.slice() }; })();

  // ======================================================= CÁMARA: poses por parada y vuelo en arco entre ellas
  const fov = 46; cam.fov = fov; cam.near = 0.1; cam.far = 95; cam.updateProjectionMatrix();
  const centro = (p) => { const [x, z] = SITIOS[p.z.sitio]; return new THREE.Vector3(x, altura(x, z), z); };
  function pose3d(i, tl) {
    const p = paradas[i], c = { ...p.z.cam, ...(p.camara || {}) }, d = finDe(i) - hitos[i], o = centro(p);
    const look = o.clone().add(new THREE.Vector3(...c.look));
    const az = rad(c.az + (c.orbit || 0) * tl), r = c.dist * (1 - (c.push || 0) * eo(tl / Math.max(d, 0.5)));
    const subida = c.sube ? eo(clamp((tl - 0.6) / Math.max(1, d - 0.6))) : 0;
    const pos = look.clone().add(new THREE.Vector3(Math.sin(az) * r, c.alt, Math.cos(az) * r));
    if (subida) { // final: la cámara se eleva despacio (plano de grúa) sin perder a los dos candidatos
      pos.lerp(new THREE.Vector3(o.x, o.y + 6.5, o.z + 9.5), subida * 0.8); look.lerp(new THREE.Vector3(o.x, o.y + 0.9, o.z - 0.5), subida * 0.8);
    }
    return { pos, look };
  }
  function poseFoto(id, tl, d) {
    const v = fotoVallas[id]; if (!v) return null;
    const dist = (v.alto / 2 / Math.tan(rad(fov / 2))) * lerp(0.98, 0.9, eo(tl / Math.max(d, 0.5))); // zoom muy suave hacia dentro
    return { pos: v.centro.clone().addScaledVector(v.normal, dist), look: v.centro.clone() };
  }
  function pose(i, tl) {
    const p = paradas[i], base = pose3d(i, tl);
    if (!p.foto || !fotoVallas[p.foto.id]) return base;
    const d = finDe(i) - hitos[i], desde = (p.foto.desde ?? 0.42) * d, k = suave((tl - desde) / Math.min(1.1, d * 0.45));
    if (k <= 0) return base;
    const pf = poseFoto(p.foto.id, Math.max(0, tl - desde), d - desde);
    return vuelo(base, pf, k);
  }
  function vuelo(a, b, k) {
    const dist = a.pos.distanceTo(b.pos), arco = Math.sin(Math.PI * k) * Math.min(3.2, dist * 0.18);
    // en pleno vuelo la mirada también sube y se adelanta un poco: se ve el paisaje y hacia dónde vamos, no solo el suelo
    const adelante = b.look.clone().sub(a.look).setY(0).multiplyScalar(0.25 * Math.sin(Math.PI * k));
    return { pos: a.pos.clone().lerp(b.pos, k).add(new THREE.Vector3(0, arco, 0)), look: a.look.clone().lerp(b.look, k).add(adelante).add(new THREE.Vector3(0, arco * 0.75, 0)) };
  }
  // duración de cada transición según la distancia (más lejos = vuelo más largo), sin comerse las frases cortas
  const trans = paradas.map((_, i) => {
    if (i === 0) return { a: 0, b: 0 };
    const dPrev = hitos[i] - hitos[i - 1], dAct = finDe(i) - hitos[i];
    const L = clamp(0.8 + pose(i - 1, dPrev).pos.distanceTo(pose(i, 0).pos) * 0.05, 0.9, 1.7);
    return { a: Math.min(L * 0.45, dPrev * 0.3), b: Math.min(L * 0.55, dAct * 0.35) }; // cada frase conserva su plano quieto
  });
  function camara(t) {
    let i = 0; while (i + 1 < N && t >= hitos[i + 1]) i++;
    const sig = i + 1 < N ? trans[i + 1] : null;
    if (sig && t >= hitos[i + 1] - sig.a) { const k = suave((t - (hitos[i + 1] - sig.a)) / (sig.a + sig.b)); return { ...vuelo(pose(i, t - hitos[i]), pose(i + 1, t - hitos[i + 1]), k), i, j: i + 1, k }; }
    const act = trans[i];
    if (i > 0 && t < hitos[i] + act.b) { const k = suave((t - (hitos[i] - act.a)) / (act.a + act.b)); return { ...vuelo(pose(i - 1, t - hitos[i - 1]), pose(i, t - hitos[i]), k), i: i - 1, j: i, k }; }
    return { ...pose(i, t - hitos[i]), i, j: i, k: 0 };
  }
  const cieloDe = (i) => CIELOS[paradas[i].cielo || paradas[i].z.cielo] || CIELOS.dia;

  // ======================================================= ETIQUETAS (tarjetas con icono) y ANILLOS sobre las fotos
  const capa = document.createElement("div"); capa.style.cssText = "position:absolute;inset:0;pointer-events:none"; document.body.appendChild(capa);
  const colores = ["#ff6b4a", "#ffb02e", "#2fbf71", "#4f7cff", "#b25cff"];
  const tarjetas = [];
  paradas.forEach((p, i) => {
    const lista = (p.etiquetas || []).slice(0, 3), d = finDe(i) - hitos[i];
    lista.forEach((e, k) => {
      const el = document.createElement("div"), c = e.color || colores[(i + k) % colores.length];
      el.style.cssText = "position:absolute;display:flex;gap:16px;align-items:center;background:rgba(255,255,255,.96);border-radius:24px;padding:14px 26px 14px 14px;" +
        "box-shadow:0 12px 34px rgba(0,0,0,.35);font-family:Inter,sans-serif;transform-origin:50% 100%;max-width:600px;white-space:nowrap";
      el.innerHTML = `<div style="width:72px;height:72px;border-radius:18px;background:${c};display:grid;place-items:center;font-size:42px;flex:none">${e.icono || "●"}</div>` +
        `<div><div style="font-weight:900;font-size:26px;letter-spacing:2px;color:${c}">${(e.titulo || "").toUpperCase()}</div>` +
        `<div style="font-weight:900;font-size:44px;color:#1d1f2b;line-height:1.05">${e.texto || ""}</div></div>`;
      const pico = document.createElement("div"); pico.style.cssText = `position:absolute;width:0;height:0;border-left:16px solid transparent;border-right:16px solid transparent;border-top:18px solid rgba(255,255,255,.96);left:50%;margin-left:-16px;bottom:-17px`;
      el.appendChild(pico); capa.appendChild(el);
      const t0 = hitos[i] + (e.t ?? (Math.min(0.45, d * 0.15) + k * Math.min(0.9, d * 0.3)));
      tarjetas.push({ el, ancla: e.ancla, t0, t1: finDe(i) - (i + 1 < N ? 0.3 : -9), k, i, lado: e.lado });
    });
  });
  const anillos = [];
  paradas.forEach((p, i) => {
    const fv = p.foto && fotoVallas[p.foto.id]; if (!fv || !(p.foto.nota || fv.f.nota)) return;
    const ring = document.createElement("div"), lin = document.createElement("div"), lab = document.createElement("div"), c = "#ffd25a";
    ring.style.cssText = `position:absolute;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:9px solid ${c};box-shadow:0 0 26px ${c},inset 0 0 20px ${c}66`;
    lin.style.cssText = `position:absolute;height:7px;background:${c};transform-origin:0 50%;border-radius:4px;box-shadow:0 0 12px ${c}`;
    lab.style.cssText = `position:absolute;background:#fff;border-left:16px solid ${c};border-radius:18px;padding:14px 26px;font:900 46px Inter,sans-serif;color:#14161f;box-shadow:0 10px 30px rgba(0,0,0,.45);white-space:nowrap`;
    lab.textContent = p.foto.nota || fv.f.nota; capa.append(lin, ring, lab);
    const d = finDe(i) - hitos[i], desde = (p.foto.desde ?? 0.42) * d;
    const u = fv.f.x ?? 0.5, v = fv.f.y ?? 0.5;
    const punto = new THREE.Vector3((u - 0.5) * fv.ancho, (0.5 - v) * fv.alto, 0.02); fv.m.localToWorld(punto);
    anillos.push({ ring, lin, lab, punto, t0: hitos[i] + desde + Math.min(1.1, d * 0.45) * 0.8, t1: finDe(i) + 0.05 });
  });
  const proy = new THREE.Vector3();
  const aPantalla = (v) => { proy.copy(v).project(cam); return { x: (proy.x * 0.5 + 0.5) * 1080, y: (-proy.y * 0.5 + 0.5) * 1920, delante: proy.z < 1 }; };
  function pintaEtiquetas(t) {
    const usadas = [];
    for (const e of tarjetas) {
      const vis = t >= e.t0 && t < e.t1 + 0.25;
      if (!vis) { e.el.style.opacity = 0; continue; }
      const a = anclas[e.ancla] || anclas[Object.keys(anclas)[0]], s = aPantalla(a);
      const k = eob((t - e.t0) / 0.38), fuera = clamp((e.t1 + 0.25 - t) / 0.25), w = e.el.offsetWidth, h = e.el.offsetHeight;
      let x = Math.min(1080 - 36 - w, Math.max(36, s.x - w / 2)), y = Math.min(1060 - h, Math.max(300, s.y - h - 26));
      for (const u of usadas) if (Math.abs(u.y - y) < h + 14 && Math.abs(u.x - x) < w) y = Math.min(1060 - h, u.y + u.h + 18) > u.y + 4 ? u.y + u.h + 18 : u.y - h - 18; // sin solaparse
      y = Math.min(1060 - h, Math.max(300, y));
      usadas.push({ x, y, h });
      e.el.style.left = `${x}px`; e.el.style.top = `${y}px`;
      const enPantalla = s.delante && s.x > -60 && s.x < 1140 && s.y > 150 && s.y < 1700;
      e.el.style.opacity = enPantalla ? clamp((t - e.t0) / 0.15) * fuera : 0;
      e.el.style.transform = `scale(${Math.max(0.001, k)})`;
    }
    for (const o of anillos) {
      const vis = t >= o.t0 && t < o.t1 ? 1 : 0, s = aPantalla(o.punto), a = eob((t - o.t0) / 0.4);
      const LX = s.x < 540 ? s.x + 170 : s.x - 170, LY = Math.max(320, Math.min(980, s.y - 190));
      o.ring.style.left = `${s.x}px`; o.ring.style.top = `${s.y}px`; o.ring.style.opacity = vis; o.ring.style.transform = `scale(${Math.max(0.001, a) * (1 + 0.05 * Math.sin(t * 7))})`;
      const dx = LX - s.x, dy = LY - s.y, L = Math.hypot(dx, dy) - 75;
      o.lin.style.left = `${s.x}px`; o.lin.style.top = `${s.y}px`; o.lin.style.opacity = vis; o.lin.style.width = `${Math.max(0, L) * Math.min(1, a)}px`; o.lin.style.transform = `rotate(${Math.atan2(dy, dx)}rad) translateX(75px)`;
      const w = o.lab.offsetWidth;
      o.lab.style.opacity = vis * clamp((t - o.t0 - 0.2) / 0.2); o.lab.style.top = `${LY - 44}px`;
      o.lab.style.left = `${Math.max(30, Math.min(1080 - 30 - w, s.x < 540 ? LX : LX - w))}px`;
      o.lab.style.transform = `scale(${Math.max(0.001, eob((t - o.t0 - 0.2) / 0.35))})`;
    }
  }

  // ======================================================= FOTOGRAMA
  function frame(t) {
    const c = camara(t);
    cam.position.copy(c.pos); cam.lookAt(c.look); cam.updateMatrixWorld();
    // cielo y luz: mezcla de la hora de las dos paradas implicadas
    const cl = mezclaCielo(cieloDe(c.i), cieloDe(c.j), c.k);
    cieloMat.uniforms.top.value.copy(cl.top); cieloMat.uniforms.mid.value.copy(cl.mid); cieloMat.uniforms.hor.value.copy(cl.hor);
    scene.fog.color.copy(cl.hor);
    hemi.color.copy(cl.hemi[0]); hemi.groundColor.copy(cl.hemi[1]); hemi.intensity = cl.hemi[2];
    sol.color.copy(cl.sol); sol.intensity = cl.solI; renderer.toneMappingExposure = cl.expo;
    const solDir = new THREE.Vector3(lerp(0.45, -0.3, cl.luna), lerp(0.55, 0.65, cl.luna), lerp(-0.7, -0.7, cl.luna)).normalize();
    cieloMat.uniforms.solDir.value.copy(solDir); cieloMat.uniforms.solCol.value.copy(cl.sol); cieloMat.uniforms.luna.value = cl.luna;
    sol.target.position.copy(c.look); sol.position.copy(c.look).addScaledVector(new THREE.Vector3(0.45, 0.8, 0.35).normalize(), 25);
    cielo.position.copy(cam.position); estrellas.position.copy(cam.position); estrellas.material.opacity = cl.est;
    polvo.m.position.set(cam.position.x, altura(cam.position.x, cam.position.z) - 0.5, cam.position.z - 6);
    const pa = polvo.m.geometry.attributes.position; for (let i = 0; i < pa.count; i++) pa.array[i * 3 + 1] = (polvo.p0[i * 3 + 1] + t * 0.15 * (1 + (i % 3))) % 5; pa.needsUpdate = true;
    for (const f of anim) f(t);
    scene.updateMatrixWorld(true);
    pintaEtiquetas(t);
  }
  return { frame };
}
