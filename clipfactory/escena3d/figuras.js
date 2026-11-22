// FIGURITAS · personajes y objetos 3D tipo juguete realista (sombreado suave, proporciones de verdad) para el MUNDO.
// Cada figura devuelve { g: Group, anim(t, estado) } y su animación es una función PURA del tiempo (se renderiza fotograma a
// fotograma, en paralelo, en varios navegadores: nada puede depender del fotograma anterior).
import * as THREE from "three";

export const COL = {
  blanco: 0xf6f1e7, crema: 0xfff1d6, marron: 0x9a5b2e, canela: 0xc98a4b, rojo: 0xd8322f, cresta: 0xe0262b, pico: 0xf2b134,
  pata: 0xf0a52a, negro: 0x15151a, verde: 0x3f9b4f, verdeOsc: 0x24603a, hoja: 0x3c9a46, hojaOsc: 0x23683a, tierra: 0x8a5a33,
  madera: 0x8b5a2b, maderaOsc: 0x5e3b1c, piedra: 0x8f8a83, paja: 0xe2c069, agua: 0x3fa9d8, lava: 0xff5a1f, oro: 0xffc83a,
  plata: 0xc9ced8, bronce: 0xc0814a, granero: 0xb3302a, tejado: 0x5b3a2e, blancoPuro: 0xffffff,
};
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const eo = (x) => 1 - (1 - clamp(x)) ** 3;
export const eob = (x) => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
export const suave = (x) => { x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10); };

const cacheMat = new Map();
export function mat(color, o = {}) {
  const k = JSON.stringify([color, o]);
  if (!cacheMat.has(k)) cacheMat.set(k, new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.02, ...o }));
  return cacheMat.get(k);
}
const sombra = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
export function bola(r, c, sx = 1, sy = 1, sz = 1, o) {
  const m = sombra(new THREE.Mesh(new THREE.SphereGeometry(r, 20, 14), mat(c, o)));
  m.scale.set(sx, sy, sz);
  return m;
}
export function caja(w, h, d, c, o) { return sombra(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(c, o))); }
export function cil(r1, r2, h, c, seg = 12, o) { return sombra(new THREE.Mesh(new THREE.CylinderGeometry(r1, r2, h, seg), mat(c, o))); }
export function cono(r, h, c, seg = 10, o) { return sombra(new THREE.Mesh(new THREE.ConeGeometry(r, h, seg), mat(c, o))); }
export const en = (m, x, y, z) => { m.position.set(x, y, z); return m; };

// ---------------------------------------------------------------- HUEVO (perfil de huevo de verdad, no una esfera)
const perfilHuevo = (alto, n = 22) => {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const y = -1 + (2 * i) / n, r = 0.74 * Math.sqrt(Math.max(0, 1 - y * y)) * (1 - 0.15 * y);
    pts.push(new THREE.Vector2(Math.max(0.0001, r) * alto * 0.5, (y + 1) * alto * 0.5));
  }
  return pts;
};
export function huevo(color = COL.crema, alto = 0.5, o = {}) {
  const g = new THREE.Group();
  const m = sombra(new THREE.Mesh(new THREE.LatheGeometry(perfilHuevo(alto), 24), mat(color, { roughness: 0.45, ...o })));
  g.add(m);
  g.userData.malla = m;
  return g;
}
// huevo que se agrieta y se abre: grietas en zigzag + mitad de arriba que salta
export function huevoQueNace(color = COL.crema, alto = 0.62) {
  const g = new THREE.Group(), corte = 0.62;
  const p = perfilHuevo(alto, 30), abajo = p.filter((v) => v.y <= alto * corte + 1e-6), arriba = p.filter((v) => v.y >= alto * corte - 1e-6);
  const mm = mat(color, { roughness: 0.45, side: THREE.DoubleSide });
  const inf = sombra(new THREE.Mesh(new THREE.LatheGeometry(abajo, 26), mm));
  const sup = sombra(new THREE.Mesh(new THREE.LatheGeometry(arriba.map((v) => new THREE.Vector2(v.x, v.y - alto * corte)), 26), mm));
  const tapa = new THREE.Group(); tapa.position.y = alto * corte; tapa.add(sup); g.add(inf, tapa);
  // grieta: línea quebrada alrededor del corte
  const pts = [], rC = p.find((v) => v.y >= alto * corte).x * 1.01;
  for (let i = 0; i <= 40; i++) { const a = (i / 40) * Math.PI * 2; pts.push(new THREE.Vector3(Math.cos(a) * rC, alto * corte + (i % 2 ? 0.025 : -0.025), Math.sin(a) * rC)); }
  const grieta = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, true, "catmullrom", 0), 80, 0.008, 4, true), mat(0x3a2a1a));
  g.add(grieta);
  const anim = (k) => { // k: 0 entero · 0-0.5 tiembla y se agrieta · 0.5-1 la tapa salta
    grieta.visible = k > 0.12; grieta.scale.setScalar(1);
    const s = clamp((k - 0.5) / 0.5);
    g.rotation.z = k < 0.5 ? Math.sin(k * 90) * 0.13 * clamp(k / 0.2) : 0;
    tapa.position.set(0.12 * eo(s), alto * corte + 0.55 * Math.sin(Math.PI * Math.min(1, s * 1.15)) + 0.25 * eo(s), 0);
    tapa.rotation.z = -2.2 * eo(s);
    tapa.visible = s < 0.98;
  };
  return { g, anim };
}

// ---------------------------------------------------------------- AVES: gallina, gallo bankiva, ave "casi gallina", pollito
export function ave(op = {}) {
  const c = { cuerpo: COL.blanco, pecho: null, ala: null, cola: null, cuello: null, cresta: COL.cresta, oreja: COL.cresta, gallo: false, escala: 1, ...op };
  c.pecho ??= c.cuerpo; c.ala ??= c.cuerpo; c.cola ??= c.cuerpo; c.cuello ??= c.cuerpo;
  const g = new THREE.Group(), cuerpo = new THREE.Group(); g.add(cuerpo);
  cuerpo.add(en(bola(0.36, c.cuerpo, 1.25, 0.92, 0.9), 0, 0.62, 0));
  cuerpo.add(en(bola(0.3, c.pecho, 1, 1.05, 0.95), 0.2, 0.58, 0));
  cuerpo.add(en(bola(0.22, c.cuerpo, 1.2, 0.8, 0.9), -0.28, 0.66, 0)); // grupa
  // cola: abanico de plumas (gallina) o hoces largas y curvas (gallo)
  const cola = new THREE.Group(); cola.position.set(-0.36, 0.74, 0); cuerpo.add(cola);
  if (c.gallo) {
    for (let i = 0; i < 7; i++) {
      const z = (i - 3) * 0.045, alto = 0.55 + (3 - Math.abs(i - 3)) * 0.09;
      const curva = new THREE.CatmullRomCurve3([new THREE.Vector3(0, 0, z), new THREE.Vector3(-0.12, alto * 0.75, z * 1.4), new THREE.Vector3(-0.38, alto, z * 1.8), new THREE.Vector3(-0.58, alto * 0.55, z * 2)]);
      cola.add(sombra(new THREE.Mesh(new THREE.TubeGeometry(curva, 16, 0.035 - Math.abs(i - 3) * 0.003, 6), mat(c.cola, { metalness: 0.35, roughness: 0.35 }))));
    }
  } else {
    for (let i = 0; i < 6; i++) { const p = bola(0.12, c.cola, 0.5, 1.6, 0.25); p.position.set(-0.04, 0.12, (i - 2.5) * 0.055); p.rotation.z = 0.5 + Math.abs(i - 2.5) * 0.05; p.rotation.x = (i - 2.5) * 0.12; cola.add(p); }
  }
  // alas (pivote en el hombro para aletear)
  const alas = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.set(0.08, 0.72, 0.27 * s); cuerpo.add(p);
    const a = bola(0.26, c.ala, 1.15, 0.6, 0.28); a.position.set(-0.12, -0.04, 0.02 * s); a.rotation.z = -0.22; p.add(a);
    const punta = bola(0.14, c.gallo ? COL.negro : c.ala, 1.2, 0.5, 0.25); punta.position.set(-0.32, -0.09, 0.03 * s); p.add(punta);
    return { p, s };
  });
  // cuello + cabeza (pivote en el hombro para picotear)
  const cuello = new THREE.Group(); cuello.position.set(0.3, 0.78, 0); cuerpo.add(cuello);
  const cu = bola(0.17, c.cuello, 0.95, 1.5, 0.95); cu.position.set(0.04, 0.12, 0); cu.rotation.z = -0.3; cuello.add(cu);
  if (c.gallo) for (let i = 0; i < 8; i++) { const h = bola(0.07, c.cuello, 0.6, 1.7, 0.4); const a = (i / 8) * Math.PI * 2; h.position.set(-0.02 + Math.cos(a) * 0.08, 0.04, Math.sin(a) * 0.12); h.rotation.z = 0.5; cuello.add(h); }
  const cab = new THREE.Group(); cab.position.set(0.12, 0.32, 0); cuello.add(cab);
  cab.add(bola(0.14, c.cuello, 1.1, 1, 0.92));
  const pico1 = cono(0.045, 0.14, COL.pico, 8); pico1.rotation.z = -Math.PI / 2 - 0.2; pico1.position.set(0.18, -0.01, 0); cab.add(pico1);
  const pico2 = cono(0.035, 0.1, 0xd99a2a, 8); pico2.rotation.z = -Math.PI / 2 + 0.15; pico2.position.set(0.16, -0.045, 0); cab.add(pico2);
  const nCr = c.gallo ? 5 : 4, rCr = c.gallo ? 0.055 : 0.04;
  for (let i = 0; i < nCr; i++) { const k = bola(rCr * (1 - Math.abs(i - (nCr - 1) / 2) * 0.14), c.cresta, 0.9, 1.4, 0.45); k.position.set(0.09 - i * 0.045, 0.13 + Math.sin((i / (nCr - 1)) * Math.PI) * 0.035, 0); cab.add(k); }
  for (const s of [-1, 1]) {
    cab.add(en(bola(c.gallo ? 0.042 : 0.032, c.cresta, 0.7, 1.4, 0.5), 0.12, -0.12, 0.025 * s)); // barbillas
    cab.add(en(bola(0.03, c.oreja, 0.6, 1, 0.4), -0.01, -0.03, 0.12 * s)); // orejilla
  }
  const ojos = [-1, 1].map((s) => {
    const o = new THREE.Group(); o.position.set(0.07, 0.03, 0.105 * s); cab.add(o);
    o.add(bola(0.03, 0xffb21d)); const pu = bola(0.019, COL.negro, 1, 1, 1, { roughness: 0.15 }); pu.position.set(0.006, 0, 0.014 * s); o.add(pu);
    const br = bola(0.006, 0xffffff, 1, 1, 1, { emissive: 0xffffff, emissiveIntensity: 1 }); br.position.set(0.016, 0.01, 0.024 * s); o.add(br);
    return o;
  });
  // patas (pivote en la cadera para caminar)
  const patas = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.set(0.02, 0.42, 0.11 * s); g.add(p);
    p.add(en(bola(0.1, c.cuerpo, 0.9, 1.1, 0.8), 0, 0.02, 0));
    const ca = cil(0.022, 0.02, 0.3, COL.pata, 8); ca.position.y = -0.2; p.add(ca);
    for (const a of [-0.45, 0, 0.45]) { const d = caja(0.13, 0.018, 0.022, COL.pata); d.position.set(0.06 * Math.cos(a), -0.35, 0.06 * Math.sin(a)); d.rotation.y = -a; p.add(d); }
    const tr = caja(0.06, 0.018, 0.02, COL.pata); tr.position.set(-0.04, -0.35, 0); p.add(tr);
    return p;
  });
  g.scale.setScalar(c.escala);
  // estado: {anda: velocidad de paso (0 = quieto), pica: 0-1, fase, mira: giro de cabeza, aletea: 0-1, canta: 0-1}
  const anim = (t, e = {}) => {
    const f = e.fase || 0, paso = e.anda ? t * 7 * e.anda + f : 0;
    const sen = e.sentada || 0; // echada sobre el nido: patas recogidas y cuerpo abajo
    patas.forEach((p, i) => { p.rotation.z = e.anda ? Math.sin(paso + i * Math.PI) * 0.55 : 0; p.scale.y = 1 - 0.8 * sen; p.position.y = 0.42 - 0.3 * sen; });
    cuerpo.position.y = (e.anda ? Math.abs(Math.sin(paso)) * 0.03 : Math.sin(t * 2.2 + f) * 0.008) - 0.3 * sen;
    // picoteo: bajadas rápidas cada ~1,6 s
    const ciclo = ((t * 0.62 + f * 0.13) % 1), pic = (e.pica || 0) * (ciclo < 0.32 ? Math.sin((ciclo / 0.32) * Math.PI) : 0);
    const canto = e.canta || 0;
    cuello.rotation.z = -1.25 * pic + 0.35 * canto + Math.sin(t * 3.1 + f) * 0.05;
    cuello.rotation.y = (e.mira ?? Math.sin(t * 0.9 + f) * 0.35) * (1 - pic);
    cuerpo.rotation.z = -0.18 * pic + 0.12 * canto;
    cab.rotation.z = canto * 0.5 * (0.8 + 0.2 * Math.sin(t * 30));
    pico2.rotation.z = -Math.PI / 2 + 0.15 + canto * 0.5;
    const ale = e.aletea || 0;
    alas.forEach(({ p, s }) => { p.rotation.x = -s * ale * (0.4 + 0.5 * Math.abs(Math.sin(t * 16))); });
    cola.rotation.z = Math.sin(t * 1.7 + f) * 0.04;
    const parp = ((t + f * 0.7) % 3.1) < 0.12 ? 0.1 : 1; // parpadeo
    ojos.forEach((o) => o.scale.set(1, parp, 1));
  };
  return { g, anim };
}
export const gallina = (color = COL.blanco, escala = 1) => ave({ cuerpo: color, escala });
export const bankiva = (escala = 1) => ave({ gallo: true, cuerpo: 0x7a2f1c, pecho: 0x1c1a17, ala: 0x9a3a1a, cola: 0x14382a, cuello: 0xf09a2c, oreja: 0xf4f0e6, escala });
export const bankivaHembra = (escala = 1) => ave({ cuerpo: 0x8c6239, pecho: 0xa77b4f, ala: 0x7a5230, cola: 0x5a3c22, cuello: 0xc9944e, oreja: 0xcc3b30, escala });
export const casiGallina = (escala = 1) => ave({ cuerpo: 0xb27a45, pecho: 0xd9b07a, ala: 0x9a6236, cola: 0x4a3a2a, cuello: 0xe2b87a, escala });

export function pollito(escala = 1) {
  const g = new THREE.Group(), cuerpo = new THREE.Group(); g.add(cuerpo);
  const am = 0xffd84a;
  cuerpo.add(en(bola(0.2, am, 1.1, 0.95, 1, { roughness: 0.9 }), 0, 0.24, 0));
  const cab = new THREE.Group(); cab.position.set(0.12, 0.44, 0); cuerpo.add(cab);
  cab.add(bola(0.13, am, 1, 1, 1, { roughness: 0.9 }));
  const pico = cono(0.035, 0.08, 0xf29a1d, 8); pico.rotation.z = -Math.PI / 2; pico.position.set(0.14, -0.01, 0); cab.add(pico);
  for (const s of [-1, 1]) { const o = bola(0.024, COL.negro, 1, 1, 1, { roughness: 0.15 }); o.position.set(0.08, 0.035, 0.085 * s); cab.add(o); const b = bola(0.006, 0xffffff, 1, 1, 1, { emissive: 0xffffff }); b.position.set(0.095, 0.045, 0.1 * s); cab.add(b); }
  const alas = [-1, 1].map((s) => { const a = bola(0.09, 0xf5c93a, 1.2, 0.6, 0.3, { roughness: 0.9 }); a.position.set(-0.02, 0.26, 0.19 * s); cuerpo.add(a); return a; });
  for (const s of [-1, 1]) { const p = cil(0.012, 0.012, 0.1, 0xf29a1d, 6); p.position.set(0.02, 0.05, 0.07 * s); g.add(p); const d = caja(0.07, 0.012, 0.03, 0xf29a1d); d.position.set(0.04, 0.005, 0.07 * s); g.add(d); }
  g.scale.setScalar(escala);
  const anim = (t, e = {}) => {
    const f = e.fase || 0;
    cuerpo.position.y = Math.abs(Math.sin(t * (e.salta ? 9 : 2.5) + f)) * (e.salta ? 0.08 : 0.01);
    const ciclo = (t * 0.9 + f * 0.21) % 1;
    cab.rotation.z = -(e.pica ?? 0.8) * (ciclo < 0.25 ? Math.sin((ciclo / 0.25) * Math.PI) * 0.9 : 0);
    alas.forEach((a, i) => { a.rotation.x = (e.aletea || 0) * Math.sin(t * 20 + i * Math.PI) * 0.6; });
  };
  return { g, anim };
}

// ---------------------------------------------------------------- DINOSAURIOS y el primer amniota (lagartito)
function cadena(n, r0, r1, col, paso, dir = -1, alarga = 1.5) { // segmentos encadenados (cola/cuello) que se doblan con una onda
  const raiz = new THREE.Group(); let padre = raiz; const seg = [];
  for (let i = 0; i < n; i++) {
    const k = i / (n - 1), r = r0 + (r1 - r0) * k, s = new THREE.Group();
    s.position.x = i === 0 ? 0 : dir * paso; padre.add(s);
    s.add(en(bola(r, col, alarga, 1, 1), dir * paso * 0.5, 0, 0)); seg.push(s); padre = s;
  }
  return { raiz, seg, punta: padre };
}
export function teropodo(op = {}) {
  const c = { piel: 0x4f8a3c, vientre: 0xc9c27a, lomo: 0xd9772a, escala: 1, ...op };
  const g = new THREE.Group(), cuerpo = new THREE.Group(); cuerpo.position.y = 1.15; g.add(cuerpo);
  cuerpo.add(bola(0.5, c.piel, 1.45, 0.95, 0.85));
  cuerpo.add(en(bola(0.42, c.vientre, 1.3, 0.7, 0.8), 0.1, -0.2, 0));
  const cola = cadena(11, 0.36, 0.07, c.piel, 0.2, -1, 2.0); cola.raiz.position.set(-0.6, 0.05, 0); cuerpo.add(cola.raiz);
  const cuello = cadena(3, 0.26, 0.2, c.piel, 0.2, 1); cuello.raiz.position.set(0.55, 0.2, 0); cuello.raiz.rotation.z = 0.7; cuerpo.add(cuello.raiz);
  const cab = new THREE.Group(); cab.position.set(0.18, 0, 0); cab.rotation.z = -0.75; cuello.punta.add(cab);
  cab.add(en(bola(0.24, c.piel, 1.55, 0.85, 0.85), 0.18, 0.04, 0));
  const mand = new THREE.Group(); mand.position.set(0.05, -0.08, 0); cab.add(mand);
  mand.add(en(bola(0.18, c.vientre, 1.7, 0.45, 0.75), 0.2, -0.02, 0));
  for (let i = 0; i < 6; i++) { const d = cono(0.018, 0.05, 0xfffbe8, 5); d.rotation.z = Math.PI; d.position.set(0.12 + i * 0.05, -0.04, 0.1); cab.add(d); const d2 = d.clone(); d2.position.z = -0.1; cab.add(d2); }
  for (const s of [-1, 1]) { cab.add(en(bola(0.045, 0xffd23a, 1, 1, 1, { emissive: 0x553300, emissiveIntensity: 0.3 }), 0.24, 0.14, 0.15 * s)); cab.add(en(bola(0.024, COL.negro), 0.265, 0.145, 0.185 * s)); }
  for (let i = 0; i < 9; i++) { const e = cono(0.07 - Math.abs(i - 3) * 0.006, 0.2, c.lomo, 6); e.position.set(0.45 - i * 0.2, 0.48 - Math.abs(i - 2) * 0.03, 0); if (i > 3) { e.position.y = 0.4 - (i - 3) * 0.05; } cuerpo.add(e); }
  const brazos = [-1, 1].map((s) => { const b = new THREE.Group(); b.position.set(0.5, -0.15, 0.28 * s); cuerpo.add(b); const a = bola(0.06, c.piel, 2.4, 0.8, 0.8); a.position.set(0.1, -0.06, 0); a.rotation.z = -0.8; b.add(a); return b; });
  const patas = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.set(0, 0.95, 0.3 * s); g.add(p);
    p.add(en(bola(0.24, c.piel, 1.1, 1.5, 0.9), 0.05, -0.15, 0));
    const rod = new THREE.Group(); rod.position.set(0.12, -0.45, 0); p.add(rod);
    const sh = cil(0.09, 0.07, 0.5, c.piel, 10); sh.position.set(-0.06, -0.22, 0); sh.rotation.z = 0.25; rod.add(sh);
    for (const a of [-0.35, 0, 0.35]) { const d = caja(0.22, 0.05, 0.06, c.piel); d.position.set(0.02 + 0.08 * Math.cos(a), -0.5, 0.08 * Math.sin(a)); d.rotation.y = -a; rod.add(d); }
    return { p, rod };
  });
  g.scale.setScalar(c.escala);
  const anim = (t, e = {}) => {
    const f = e.fase || 0, paso = t * 4.2 * (e.anda || 0) + f;
    patas.forEach(({ p, rod }, i) => { const s = Math.sin(paso + i * Math.PI); p.rotation.z = e.anda ? s * 0.45 : 0; rod.rotation.z = e.anda ? Math.max(0, -Math.cos(paso + i * Math.PI)) * 0.5 : 0; });
    cuerpo.position.y = 1.15 + (e.anda ? Math.abs(Math.sin(paso)) * 0.05 : Math.sin(t * 1.6 + f) * 0.02);
    cuerpo.rotation.z = Math.sin(t * 1.1 + f) * 0.04 - (e.agacha || 0) * 0.3;
    cola.seg.forEach((s, i) => { s.rotation.y = Math.sin(t * 2.2 - i * 0.55 + f) * 0.065; s.rotation.z = 0.02 + Math.sin(t * 1.3 - i * 0.4) * 0.015; });
    cuello.seg.forEach((s, i) => { s.rotation.y = Math.sin(t * 0.8 + f) * 0.12; });
    const rugido = e.ruge || 0;
    mand.rotation.z = -(0.08 + 0.5 * rugido * (0.7 + 0.3 * Math.sin(t * 25)));
    cab.rotation.z = -0.75 + rugido * 0.35;
    brazos.forEach((b, i) => { b.rotation.z = Math.sin(t * 2 + i) * 0.15; });
  };
  return { g, anim };
}
export function sauropodo(op = {}) {
  const c = { piel: 0x7f8c5a, vientre: 0xb9b98a, escala: 1, ...op };
  const g = new THREE.Group(), cuerpo = new THREE.Group(); cuerpo.position.y = 2.0; g.add(cuerpo);
  cuerpo.add(bola(0.9, c.piel, 1.5, 0.85, 0.85));
  cuerpo.add(en(bola(0.75, c.vientre, 1.4, 0.6, 0.8), 0, -0.35, 0));
  const cuello = cadena(14, 0.3, 0.17, c.piel, 0.19, 1, 2.2); cuello.raiz.position.set(1.1, 0.35, 0); cuello.raiz.rotation.z = 0.9; cuerpo.add(cuello.raiz);
  const cab = bola(0.2, c.piel, 1.6, 0.85, 0.85); cab.position.set(0.22, 0, 0); cuello.punta.add(cab);
  for (const s of [-1, 1]) { const o = bola(0.03, COL.negro); o.position.set(0.3, 0.06, 0.12 * s); cuello.punta.add(o); }
  const cola = cadena(15, 0.45, 0.06, c.piel, 0.24, -1, 2.2); cola.raiz.position.set(-1.2, 0.1, 0); cuerpo.add(cola.raiz);
  const patas = [[0.75, 0.45], [0.75, -0.45], [-0.75, 0.45], [-0.75, -0.45]].map(([x, z]) => { const p = new THREE.Group(); p.position.set(x, 1.6, z); g.add(p); const m = cil(0.22, 0.2, 1.6, c.piel, 12); m.position.y = -0.8; p.add(m); return p; });
  g.scale.setScalar(c.escala);
  const anim = (t, e = {}) => {
    const f = e.fase || 0, paso = t * 2.2 * (e.anda ?? 1) + f;
    patas.forEach((p, i) => { p.rotation.z = Math.sin(paso + (i === 0 || i === 3 ? 0 : Math.PI)) * 0.22; });
    cuerpo.position.y = 2.0 + Math.abs(Math.sin(paso)) * 0.04;
    cuello.seg.forEach((s, i) => { s.rotation.z = -0.04 + Math.sin(t * 0.7 + f - i * 0.25) * 0.016; s.rotation.y = Math.sin(t * 0.5 + f) * 0.04; });
    cola.seg.forEach((s, i) => { s.rotation.y = Math.sin(t * 1.4 - i * 0.45 + f) * 0.05; s.rotation.z = 0.035; });
  };
  return { g, anim };
}
export function lagarto(op = {}) { // primer amniota: pequeño reptil que ponía huevos con cáscara
  const c = { piel: 0x6f7a3a, vientre: 0xc8b86a, escala: 1, ...op };
  const g = new THREE.Group(), cuerpo = new THREE.Group(); cuerpo.position.y = 0.09; g.add(cuerpo);
  cuerpo.add(bola(0.1, c.piel, 2.1, 0.7, 1.0));
  const cab = new THREE.Group(); cab.position.set(0.24, 0.02, 0); cuerpo.add(cab); cab.add(bola(0.065, c.piel, 1.7, 0.75, 1));
  for (const s of [-1, 1]) cab.add(en(bola(0.016, 0xffd23a), 0.06, 0.03, 0.045 * s));
  const cola = cadena(7, 0.07, 0.015, c.piel, 0.07); cola.raiz.position.set(-0.2, 0, 0); cuerpo.add(cola.raiz);
  const patas = [[0.12, 1], [0.12, -1], [-0.12, 1], [-0.12, -1]].map(([x, s]) => { const p = new THREE.Group(); p.position.set(x, 0, 0.08 * s); cuerpo.add(p); const m = cil(0.018, 0.014, 0.13, c.piel, 6); m.rotation.x = s * 1.0; m.position.set(0, -0.03, 0.05 * s); p.add(m); return p; });
  g.scale.setScalar(c.escala);
  const anim = (t, e = {}) => {
    const f = e.fase || 0, v = e.anda ?? 0, paso = t * 14 * v + f;
    patas.forEach((p, i) => { p.rotation.y = Math.sin(paso + (i === 0 || i === 3 ? 0 : Math.PI)) * 0.6 * (v ? 1 : 0); });
    cuerpo.rotation.y = Math.sin(paso) * 0.12 * (v ? 1 : 0);
    cola.seg.forEach((s, i) => { s.rotation.y = Math.sin(paso - i * 0.6) * (v ? 0.25 : 0.05); });
    cab.rotation.y = Math.sin(t * 1.3 + f) * 0.3; cab.rotation.z = 0.15 * Math.max(0, Math.sin(t * 0.7 + f));
  };
  return { g, anim };
}

// ---------------------------------------------------------------- PLANTAS y paisaje
export function helechoArbol(alto = 1.6) {
  const g = new THREE.Group();
  const tr = cil(0.07, 0.11, alto, 0x5a4026, 8); tr.position.y = alto / 2; g.add(tr);
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2, p = new THREE.Group(); p.position.y = alto; p.rotation.y = a; g.add(p);
    const fr = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 0.24, 6, 1), mat(i % 2 ? COL.hoja : 0x4caf50, { side: THREE.DoubleSide, roughness: 0.8 }));
    const pos = fr.geometry.attributes.position; // fronda que se arquea hacia abajo
    for (let k = 0; k < pos.count; k++) { const x = pos.getX(k) + 0.5; pos.setY(k, pos.getY(k) * (1 - x * 0.7)); pos.setZ(k, -x * x * 0.45); }
    fr.geometry.computeVertexNormals(); fr.position.x = 0.5; fr.rotation.x = Math.PI / 2; fr.rotation.z = 0; p.add(fr); fr.castShadow = true;
    p.rotation.z = 0.25;
  }
  return g;
}
export function colaCaballo(alto = 0.9) {
  const g = new THREE.Group();
  for (let i = 0; i < 4; i++) { const s = cil(0.03, 0.035, alto / 4, i % 2 ? 0x6fae3d : 0x5e9a33, 6); s.position.y = alto / 8 + (i * alto) / 4; g.add(s); const n = cil(0.04, 0.04, 0.02, 0x2f4f1f, 6); n.position.y = ((i + 1) * alto) / 4; g.add(n); }
  return g;
}
export function arbol(op = {}) {
  const c = { alto: 1.6, copa: COL.hoja, tronco: 0x6b4426, bolas: 4, r: 0.55, ...op };
  const g = new THREE.Group();
  const tr = cil(0.08, 0.13, c.alto, c.tronco, 8); tr.position.y = c.alto / 2; g.add(tr);
  for (let i = 0; i < c.bolas; i++) { const a = i * 2.4, b = new THREE.Mesh(new THREE.IcosahedronGeometry(c.r * (1 - i * 0.08), 1), mat(i % 2 ? c.copa : COL.hojaOsc, { flatShading: true, roughness: 0.85 })); b.position.set(Math.cos(a) * c.r * 0.45, c.alto + (i % 2) * c.r * 0.4, Math.sin(a) * c.r * 0.45); b.castShadow = true; g.add(b); }
  return g;
}
export function palmera(alto = 1.6, hoja = COL.hoja) {
  const g = new THREE.Group();
  for (let i = 0; i < 6; i++) { const s = cil(0.07, 0.085, alto / 6, 0x7a5532, 7); s.position.set(i * 0.02, alto / 12 + (i * alto) / 6, 0); g.add(s); }
  for (let k = 0; k < 7; k++) {
    const p = new THREE.Group(); p.position.set(0.12, alto, 0); p.rotation.y = (k / 7) * Math.PI * 2; g.add(p);
    const h = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.22, 5, 1), mat(hoja, { side: THREE.DoubleSide, roughness: 0.8 }));
    const pos = h.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) { const x = pos.getX(i) + 0.45; pos.setY(i, pos.getY(i) * (1 - x * 0.8)); pos.setZ(i, -x * x * 0.5); }
    h.geometry.computeVertexNormals(); h.position.x = 0.45; h.rotation.x = Math.PI / 2; h.castShadow = true; p.add(h); p.rotation.z = 0.2;
  }
  return g;
}
export function bambu(alto = 2.6) {
  const g = new THREE.Group();
  for (let i = 0; i < 7; i++) { const s = cil(0.045, 0.05, alto / 7 - 0.02, i % 2 ? 0x8fbf4a : 0x7fb043, 7); s.position.y = alto / 14 + (i * alto) / 7; g.add(s); }
  for (let k = 0; k < 6; k++) { const h = bola(0.16, COL.hoja, 1.6, 0.12, 0.45); h.position.set(Math.cos(k * 2.1) * 0.15, alto * (0.55 + (k % 3) * 0.15), Math.sin(k * 2.1) * 0.15); h.rotation.y = k * 2.1; h.rotation.z = -0.4; g.add(h); }
  return g;
}
export function roca(r = 0.4, c = COL.piedra) {
  const m = new THREE.Mesh(new THREE.DodecahedronGeometry(r, 0), mat(c, { flatShading: true, roughness: 0.95 }));
  m.scale.set(1.2, 0.7, 1); m.castShadow = true; m.receiveShadow = true;
  return m;
}
export function volcan() {
  const g = new THREE.Group();
  const m = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 6.5, 7, 18, 3, true), mat(0x5b4a43, { flatShading: true, roughness: 1 }));
  const pos = m.geometry.attributes.position;
  for (let i = 0; i < pos.count; i++) { const y = pos.getY(i), a = Math.atan2(pos.getZ(i), pos.getX(i)); const k = 1 + 0.08 * Math.sin(a * 5 + y) ; pos.setX(i, pos.getX(i) * k); pos.setZ(i, pos.getZ(i) * k); }
  m.geometry.computeVertexNormals(); m.position.y = 3.5; g.add(m);
  const lava = new THREE.Mesh(new THREE.CircleGeometry(1.15, 18), new THREE.MeshBasicMaterial({ color: COL.lava })); lava.rotation.x = -Math.PI / 2; lava.position.y = 6.9; g.add(lava);
  for (let i = 0; i < 4; i++) { const r = new THREE.Mesh(new THREE.BoxGeometry(0.25, 3.2, 0.05), new THREE.MeshBasicMaterial({ color: 0xff7a2a })); r.position.set(Math.cos(i * 1.7) * 2.3, 5.0, Math.sin(i * 1.7) * 2.3 + 0.2); r.lookAt(0, 5, 0); r.rotation.x = 0.55; g.add(r); }
  return g;
}

// ---------------------------------------------------------------- GRANJA
export function granero() {
  const g = new THREE.Group();
  const w = 2.2, h = 1.5, d = 1.8;
  g.add(en(caja(w, h, d, COL.granero), 0, h / 2, 0));
  const sh = new THREE.Shape(); sh.moveTo(-w / 2 - 0.1, 0); sh.lineTo(0, 0.95); sh.lineTo(w / 2 + 0.1, 0); sh.lineTo(-w / 2 - 0.1, 0);
  const frente = new THREE.Mesh(new THREE.ExtrudeGeometry(sh, { depth: d + 0.2, bevelEnabled: false }), mat(COL.tejado)); frente.position.set(0, h, -d / 2 - 0.1); frente.castShadow = true; g.add(frente);
  const tri = new THREE.Shape(); tri.moveTo(-w / 2, 0); tri.lineTo(0, 0.85); tri.lineTo(w / 2, 0);
  const t1 = new THREE.Mesh(new THREE.ShapeGeometry(tri), mat(COL.granero)); t1.position.set(0, h, d / 2 + 0.01); g.add(t1);
  const puerta = caja(0.9, 1.05, 0.05, 0x8f241f); puerta.position.set(0, 0.53, d / 2 + 0.03); g.add(puerta);
  for (const [x, y, w2, h2, r] of [[0, 0.53, 0.95, 0.07, 0], [0, 1.05, 0.95, 0.07, 0], [0, 0.53, 1.25, 0.07, 0.86], [0, 0.53, 1.25, 0.07, -0.86], [-0.47, 0.53, 0.07, 1.1, 0], [0.47, 0.53, 0.07, 1.1, 0]]) {
    const b = caja(w2, h2, 0.03, 0xffffff); b.position.set(x, y, d / 2 + 0.065); b.rotation.z = r; g.add(b);
  }
  const vent = caja(0.4, 0.3, 0.05, 0xfff4c8, { emissive: 0xffd27a, emissiveIntensity: 0.25 }); vent.position.set(0, h + 0.35, d / 2 + 0.03); g.add(vent);
  return g;
}
export function gallinero() {
  const g = new THREE.Group();
  g.add(en(caja(0.9, 0.6, 0.7, 0xe8d7b0), 0, 0.55, 0));
  for (const x of [-0.38, 0.38]) for (const z of [-0.28, 0.28]) g.add(en(cil(0.03, 0.03, 0.3, COL.madera, 6), x, 0.15, z));
  const t = cono(0.72, 0.4, 0xb0412e, 4); t.rotation.y = Math.PI / 4; t.position.y = 1.05; t.scale.z = 0.8; g.add(t);
  const hueco = caja(0.22, 0.26, 0.02, 0x2a1d12); hueco.position.set(0, 0.5, 0.36); g.add(hueco);
  const rampa = caja(0.18, 0.02, 0.55, COL.madera); rampa.position.set(0, 0.2, 0.58); rampa.rotation.x = 0.6; g.add(rampa);
  return g;
}
export function pacaHeno() { const m = cil(0.32, 0.32, 0.5, COL.paja, 16, { roughness: 1 }); m.rotation.x = Math.PI / 2; m.position.y = 0.32; const g = new THREE.Group(); g.add(m); return g; }
export function valla(largo = 3, alto = 0.5) {
  const g = new THREE.Group();
  for (let x = 0; x <= largo + 0.01; x += 0.45) g.add(en(caja(0.07, alto, 0.07, 0xd9c7a2), x - largo / 2, alto / 2, 0));
  for (const y of [alto * 0.4, alto * 0.82]) g.add(en(caja(largo + 0.1, 0.06, 0.04, 0xe6d6b4), 0, y, 0));
  return g;
}
export function nido(r = 0.42) {
  const g = new THREE.Group();
  const m = sombra(new THREE.Mesh(new THREE.TorusGeometry(r, r * 0.38, 10, 22), mat(0xb98b4a, { roughness: 1, flatShading: true })));
  m.rotation.x = Math.PI / 2; m.scale.z = 0.7; m.position.y = r * 0.22; g.add(m);
  const fondo = new THREE.Mesh(new THREE.CircleGeometry(r, 20), mat(0x8c6a33, { roughness: 1 })); fondo.rotation.x = -Math.PI / 2; fondo.position.y = 0.03; g.add(fondo);
  for (let i = 0; i < 26; i++) { const p = caja(0.32, 0.015, 0.02, i % 2 ? COL.paja : 0xc9a24f); const a = i * 0.83; p.position.set(Math.cos(a) * r * 1.05, r * 0.32 + (i % 3) * 0.02, Math.sin(a) * r * 1.05); p.rotation.y = -a + 1.2; p.rotation.z = 0.3; g.add(p); }
  return g;
}

// ---------------------------------------------------------------- LABORATORIO
export function microscopio() {
  const g = new THREE.Group(), neg = 0x2b2e38, bl = 0xeef0f4;
  g.add(en(caja(0.5, 0.06, 0.38, neg, { metalness: 0.4, roughness: 0.35 }), 0, 0.03, 0));
  const brazo = caja(0.09, 0.62, 0.12, bl, { roughness: 0.3 }); brazo.position.set(-0.16, 0.36, 0); brazo.rotation.z = -0.15; g.add(brazo);
  g.add(en(caja(0.3, 0.025, 0.26, neg, { metalness: 0.5, roughness: 0.3 }), 0.02, 0.3, 0));
  const tubo = cil(0.05, 0.05, 0.42, bl, 16, { roughness: 0.25 }); tubo.position.set(0.0, 0.66, 0); tubo.rotation.z = 0.35; g.add(tubo);
  const ocular = cil(0.035, 0.035, 0.14, neg, 12); ocular.position.set(-0.09, 0.9, 0); ocular.rotation.z = 0.35; g.add(ocular);
  for (const a of [-0.5, 0, 0.5]) { const o = cil(0.022, 0.016, 0.1, 0xc9ced8, 10, { metalness: 0.9, roughness: 0.2 }); o.position.set(0.07 + Math.sin(a) * 0.04, 0.42, Math.cos(a) * 0.04 - 0.02); g.add(o); }
  const luz = bola(0.035, 0xfff6c8, 1, 0.4, 1, { emissive: 0xfff2a8, emissiveIntensity: 2 }); luz.position.set(0.02, 0.15, 0); g.add(luz);
  for (const s of [-1, 1]) { const r = cil(0.06, 0.06, 0.03, neg, 16); r.rotation.x = Math.PI / 2; r.position.set(-0.17, 0.3, 0.08 * s); g.add(r); }
  return g;
}
export function matraz(color = 0x4fd1ff) {
  const g = new THREE.Group();
  const vidrio = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.05, transmission: 0, transparent: true, opacity: 0.32, clearcoat: 1 });
  const pts = [new THREE.Vector2(0.001, 0), new THREE.Vector2(0.16, 0.01), new THREE.Vector2(0.17, 0.08), new THREE.Vector2(0.05, 0.3), new THREE.Vector2(0.045, 0.42)];
  const v = new THREE.Mesh(new THREE.LatheGeometry(pts, 18), vidrio); g.add(v);
  const lq = new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(0.001, 0.005), new THREE.Vector2(0.15, 0.015), new THREE.Vector2(0.155, 0.075), new THREE.Vector2(0.09, 0.17), new THREE.Vector2(0.001, 0.17)], 18), mat(color, { emissive: color, emissiveIntensity: 0.6, transparent: true, opacity: 0.85 }));
  g.add(lq);
  return g;
}
export function tuboEnsayo(color) {
  const g = new THREE.Group();
  g.add(en(new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.32, 10, 1, true), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.3, side: THREE.DoubleSide })), 0, 0.16, 0));
  g.add(en(cil(0.03, 0.03, 0.16, color, 10, { emissive: color, emissiveIntensity: 0.5 }), 0, 0.08, 0));
  return g;
}
// proteína (esquema): cadena de bolitas en hélice que se pliega, con colores del arcoíris
export function proteina(n = 46) {
  const g = new THREE.Group(), bolas = [];
  for (let i = 0; i < n; i++) { const c = new THREE.Color().setHSL(0.62 - (i / n) * 0.62, 0.75, 0.55); const b = bola(0.075, c.getHex(), 1, 1, 1, { roughness: 0.3, emissive: c.getHex(), emissiveIntensity: 0.25 }); g.add(b); bolas.push(b); }
  const anim = (t, k = 1) => bolas.forEach((b, i) => {
    const u = i / n, a = u * Math.PI * 6 + t * 0.6, hel = new THREE.Vector3(Math.cos(a) * 0.32, (u - 0.5) * 1.5, Math.sin(a) * 0.32);
    const lin = new THREE.Vector3((u - 0.5) * 2.4, Math.sin(u * 9) * 0.08, 0);
    b.position.copy(lin.lerp(hel, k)); b.scale.setScalar(0.6 + 0.4 * k);
  });
  return { g, anim };
}
export function balanza() {
  const g = new THREE.Group(), oro = { metalness: 0.85, roughness: 0.25 };
  g.add(en(cil(0.5, 0.6, 0.15, COL.maderaOsc, 20), 0, 0.075, 0));
  g.add(en(cil(0.06, 0.08, 1.7, COL.oro, 12, oro), 0, 0.9, 0));
  const brazo = new THREE.Group(); brazo.position.y = 1.75; g.add(brazo);
  brazo.add(caja(2.2, 0.07, 0.07, COL.oro, oro));
  brazo.add(en(bola(0.09, COL.oro, 1, 1, 1, oro), 0, 0, 0));
  const platos = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.x = 1.05 * s; brazo.add(p);
    for (const a of [0, 2.1, 4.2]) { const c = cil(0.006, 0.006, 0.62, 0x777777, 4); c.position.set(Math.cos(a) * 0.17, -0.31, Math.sin(a) * 0.17); c.rotation.z = -Math.cos(a) * 0.27; c.rotation.x = Math.sin(a) * 0.27; p.add(c); }
    const plato = cil(0.42, 0.34, 0.06, COL.oro, 24, oro); plato.position.y = -0.62; p.add(plato);
    const carga = new THREE.Group(); carga.position.y = -0.58; p.add(carga);
    return { p, carga };
  });
  const anim = (ang) => { brazo.rotation.z = ang; platos.forEach(({ p }) => { p.rotation.z = -ang; }); };
  return { g, anim, platos };
}

// ---------------------------------------------------------------- CARTELES (texto en lienzo) y MARCOS DE FOTO
export function lienzo(w, h, pinta) {
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  pinta(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return t;
}
function redondo(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
// cartel de madera con letras grandes (para los hitos del camino del tiempo)
export function cartel(lineas, op = {}) {
  const c = { ancho: 1.6, color: "#fff6e0", tinta: "#3b2412", acento: "#d8322f", poste: true, ...op };
  const L = Array.isArray(lineas) ? lineas : [lineas];
  const tex = lienzo(1024, 512, (g, w, h) => {
    g.fillStyle = "#8b5a2b"; redondo(g, 0, 0, w, h, 60); g.fill();
    g.fillStyle = "#a8703a"; for (let i = 0; i < 7; i++) g.fillRect(0, 30 + i * 70, w, 6);
    g.fillStyle = c.color; redondo(g, 26, 26, w - 52, h - 52, 44); g.fill();
    g.textAlign = "center"; g.textBaseline = "middle";
    L.forEach((l, i) => {
      const grande = i === 0 && L.length > 1 ? false : true;
      let s = grande ? 170 : 92; g.font = `900 ${s}px Inter, sans-serif`;
      while (g.measureText(l).width > w - 110 && s > 40) { s -= 6; g.font = `900 ${s}px Inter, sans-serif`; }
      g.fillStyle = i === 0 && L.length > 1 ? c.acento : c.tinta;
      g.fillText(l, w / 2, L.length === 1 ? h / 2 + 8 : i === 0 ? h * 0.3 : h * 0.64);
    });
  });
  const g = new THREE.Group(), alto = c.ancho / 2;
  const tabla = new THREE.Mesh(new THREE.BoxGeometry(c.ancho, alto, 0.06), [mat(COL.madera), mat(COL.madera), mat(COL.madera), mat(COL.madera), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.7 }), mat(COL.madera)]);
  tabla.castShadow = true;
  tabla.position.y = c.poste ? 1.0 + alto / 2 : alto / 2; g.add(tabla);
  if (c.poste) for (const s of [-1, 1]) g.add(en(cil(0.045, 0.05, 1.0 + alto * 0.6, COL.maderaOsc, 8), s * c.ancho * 0.36, (1.0 + alto * 0.6) / 2, -0.04));
  return g;
}
// marco de foto: polaroid (borde blanco + pie) o valla grande vertical (para entrar en la foto a pantalla completa)
export async function marcoFoto(src, op = {}) {
  const c = { alto: 1.0, pie: "", tipo: "polaroid", ...op };
  const tx = await new THREE.TextureLoader().loadAsync(src); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 4;
  const ar = tx.image.width / tx.image.height, g = new THREE.Group();
  const h = c.alto, w = h * ar;
  if (c.tipo === "valla") { // valla publicitaria de madera con la foto (9:16)
    const borde = 0.07;
    g.add(en(caja(w + borde * 2, h + borde * 2, 0.08, 0xf4efe4), 0, 0, -0.045));
    const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tx, toneMapped: false })); g.add(pic);
    for (const s of [-1, 1]) g.add(en(cil(0.06, 0.07, h * 0.7, COL.maderaOsc, 8), s * w * 0.35, -h / 2 - h * 0.35, -0.08));
    g.userData = { w, h, pic };
    return g;
  }
  const bx = 0.06 * h, pieH = c.pie ? 0.2 * h : bx;
  const papel = caja(w + bx * 2, h + bx + pieH, 0.02, 0xfbfaf6, { roughness: 0.9 }); papel.position.y = (bx - pieH) / 2; g.add(papel);
  const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tx, toneMapped: false })); pic.position.z = 0.012; g.add(pic);
  if (c.pie) {
    const t = lienzo(1024, 160, (gg, W, H) => { gg.fillStyle = "#fbfaf6"; gg.fillRect(0, 0, W, H); gg.fillStyle = "#2a2a35"; gg.textAlign = "center"; gg.textBaseline = "middle"; let s = 92; gg.font = `900 ${s}px Inter, sans-serif`; while (gg.measureText(c.pie).width > W - 60 && s > 30) { s -= 4; gg.font = `900 ${s}px Inter, sans-serif`; } gg.fillText(c.pie, W / 2, H / 2 + 4); });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, pieH * 0.8), new THREE.MeshBasicMaterial({ map: t, toneMapped: false })); m.position.set(0, -h / 2 - pieH / 2, 0.012); g.add(m);
  }
  g.userData = { w, h, pic };
  return g;
}
