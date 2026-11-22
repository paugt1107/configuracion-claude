// DIORAMAS · maquetas low-poly en 3D con etiquetas que aparecen una tras otra (estilo vídeo explicativo viral).
// Presets: consola (descarga con barra que se llena), discos (pila que crece), almacen (disco duro que se llena),
// red (router → cable con pulsos de luz → casas), isla (manzana de ciudad con palmeras y coche) y mapa_pin (zona + pin).
// Cada preset devuelve { upd: [fn(t)], anclas: {nombre: Vector3} }; las etiquetas se pegan a las anclas.
import * as THREE from "three";

const C = {
  cesped: 0x58c26a, tierra: 0xc98f54, tierra2: 0xa8733f, agua: 0x3fb6e8, asfalto: 0x4a4f5c, linea: 0xf4f1e6,
  blanco: 0xf3f4f8, gris: 0x9aa3b5, oscuro: 0x2b2f3a, rojo: 0xe9505a, naranja: 0xff9b3d, amarillo: 0xffd25a,
  azul: 0x4f7cff, morado: 0x8f6bff, rosa: 0xff5fa8, cian: 0x3fe0d0, madera: 0x8a5a33, hoja: 0x2f9e5a, ventana: 0xffe9a8,
};
const mat = (c, extra = {}) => new THREE.MeshStandardMaterial({ color: c, roughness: 0.75, metalness: 0.05, flatShading: true, ...extra });
const caja = (w, h, d, c, extra) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(c, extra));
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const eob = (x) => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };
const eo = (x) => 1 - (1 - clamp(x)) ** 3;

// isla flotante: césped encima, tierra con estratos debajo
function isla(w, d, color = C.cesped) {
  const g = new THREE.Group();
  const top = caja(w, 0.22, d, color); top.position.y = -0.11; g.add(top);
  const t1 = caja(w, 0.45, d, C.tierra); t1.position.y = -0.45; g.add(t1);
  const t2 = caja(w * 0.96, 0.35, d * 0.96, C.tierra2); t2.position.y = -0.85; g.add(t2);
  return g;
}
function palmera(alto = 1.2) {
  const g = new THREE.Group();
  for (let i = 0; i < 5; i++) { const s = caja(0.09, alto / 5, 0.09, C.madera); s.position.set(i * 0.025, alto / 10 + (i * alto) / 5, 0); g.add(s); }
  for (let k = 0; k < 6; k++) {
    const h = caja(0.55, 0.04, 0.16, C.hoja); h.position.set(0.12, alto + 0.02, 0);
    const p = new THREE.Group(); p.add(h); p.rotation.y = (k * Math.PI) / 3; p.rotation.z = -0.25; p.position.y = 0; g.add(p);
  }
  return g;
}
function arbol() {
  const g = new THREE.Group(); const tr = caja(0.1, 0.35, 0.1, C.madera); tr.position.y = 0.17; g.add(tr);
  const copa = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 0), mat(C.hoja)); copa.position.y = 0.55; g.add(copa); return g;
}
function edificio(w, h, d, color, ventanas = true) {
  const g = new THREE.Group(); const b = caja(w, h, d, color); b.position.y = h / 2; g.add(b);
  if (ventanas) {
    const vm = mat(C.ventana, { emissive: C.ventana, emissiveIntensity: 0.6 });
    for (let y = 0.25; y < h - 0.15; y += 0.3) for (let x = -w / 2 + 0.15; x < w / 2 - 0.05; x += 0.25) {
      const v = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.14, 0.02), vm); v.position.set(x + 0.02, y, d / 2 + 0.011); g.add(v);
    }
  }
  const tejado = caja(w * 1.04, 0.06, d * 1.04, C.oscuro); tejado.position.y = h + 0.03; g.add(tejado);
  return g;
}
function casa(color = C.blanco, tejado = C.rojo) {
  const g = new THREE.Group(); const b = caja(0.8, 0.55, 0.7, color); b.position.y = 0.275; g.add(b);
  const t = new THREE.Mesh(new THREE.ConeGeometry(0.62, 0.38, 4), mat(tejado)); t.rotation.y = Math.PI / 4; t.position.y = 0.74; g.add(t);
  const p = caja(0.16, 0.28, 0.02, C.madera); p.position.set(0.15, 0.14, 0.36); g.add(p);
  const v = caja(0.18, 0.14, 0.02, C.ventana, { emissive: C.ventana, emissiveIntensity: 0.5 }); v.position.set(-0.18, 0.32, 0.36); g.add(v);
  return g;
}
function coche(color = C.rojo) {
  const g = new THREE.Group(); const b = caja(0.6, 0.16, 0.3, color); b.position.y = 0.14; g.add(b);
  const c = caja(0.32, 0.13, 0.26, C.ventana); c.position.set(-0.03, 0.28, 0); g.add(c);
  for (const [x, z] of [[-0.2, 0.15], [0.2, 0.15], [-0.2, -0.15], [0.2, -0.15]]) {
    const r = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.05, 10), mat(C.oscuro)); r.rotation.x = Math.PI / 2; r.position.set(x, 0.07, z); g.add(r);
  }
  return g;
}
// consola genérica (sin marcas) + tele
function consola() {
  const g = new THREE.Group();
  const cuerpo = caja(0.42, 1.0, 0.22, C.blanco); cuerpo.position.y = 0.5; g.add(cuerpo);
  const franja = caja(0.08, 1.02, 0.235, C.oscuro); franja.position.y = 0.5; g.add(franja);
  const led = caja(0.02, 0.06, 0.02, C.cian, { emissive: C.cian, emissiveIntensity: 2 }); led.position.set(0, 0.95, 0.12); g.add(led);
  return { g, led };
}

// ---------- figuritas (huevos, gallinas, pollitos, dinosaurios) ----------
const bola = (r, c, sx = 1, sy = 1, sz = 1, extra) => { const m = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 16), mat(c, { flatShading: false, roughness: 0.55, ...extra })); m.scale.set(sx, sy, sz); return m; };
const cono = (r, h, c) => new THREE.Mesh(new THREE.ConeGeometry(r, h, 8), mat(c));
function huevo(c = 0xfff3dc, k = 1) { const m = bola(0.24 * k, c, 0.8, 1.12, 0.8); m.position.y = 0.27 * k; const g = new THREE.Group(); g.add(m); return g; }
function ojos(g, x, y, z, r = 0.035) { for (const s of [-1, 1]) { const o = bola(r, 0x111111); o.position.set(x, y, z * s); g.add(o); } }
function gallina(color = C.blanco) {
  const g = new THREE.Group();
  const cuerpo = bola(0.4, color, 1.15, 0.9, 0.85); cuerpo.position.y = 0.6; g.add(cuerpo);
  for (let i = -2; i <= 2; i++) { const pl = bola(0.2, i % 2 ? 0xe9e2d0 : color, 0.35, 1.5, 0.12); pl.position.set(-0.52, 0.92, i * 0.07); pl.rotation.z = 0.55 + Math.abs(i) * 0.06; pl.rotation.x = i * 0.18; g.add(pl); }
  for (let r = 0; r < 3; r++) for (let c2 = 0; c2 < 4; c2++) { const pl = bola(0.1, c2 % 2 ? 0xeee8d8 : color, 1.4, 0.55, 0.5); pl.position.set(0.18 - c2 * 0.16, 0.5 + r * 0.14 - c2 * 0.01, 0.31 - r * 0.02); pl.rotation.z = -0.3; g.add(pl); const p2 = pl.clone(); p2.position.z *= -1; g.add(p2); }
  const cuello = new THREE.Group(); cuello.position.set(0.32, 0.8, 0); g.add(cuello);
  const cab = bola(0.2, color); cab.position.set(0.08, 0.28, 0); cuello.add(cab);
  const pico = cono(0.07, 0.2, C.naranja); pico.rotation.z = -Math.PI / 2; pico.position.set(0.3, 0.26, 0); cuello.add(pico);
  const cresta = caja(0.1, 0.14, 0.05, C.rojo); cresta.position.set(0.08, 0.5, 0); cuello.add(cresta);
  const barba = caja(0.05, 0.1, 0.05, C.rojo); barba.position.set(0.22, 0.12, 0); cuello.add(barba);
  ojos(cuello, 0.2, 0.34, 0.14);
  for (const s of [-1, 1]) {
    const ala = bola(0.22, color, 0.9, 0.55, 0.3); ala.position.set(-0.02, 0.62, 0.34 * s); ala.rotation.z = -0.25; g.add(ala);
    const pata = caja(0.045, 0.3, 0.045, C.naranja); pata.position.set(0.02, 0.15, 0.13 * s); g.add(pata);
    const pie = caja(0.16, 0.03, 0.07, C.naranja); pie.position.set(0.07, 0.02, 0.13 * s); g.add(pie);
  }
  return { g, cuello };
}
function pollito() {
  const g = new THREE.Group();
  const c = bola(0.26, C.amarillo, 1, 0.95, 1); c.position.y = 0.3; g.add(c);
  const cab = bola(0.17, C.amarillo); cab.position.set(0.1, 0.58, 0); g.add(cab);
  const pico = cono(0.05, 0.12, C.naranja); pico.rotation.z = -Math.PI / 2; pico.position.set(0.28, 0.56, 0); g.add(pico);
  ojos(g, 0.2, 0.63, 0.09, 0.03);
  for (const s of [-1, 1]) { const p = caja(0.03, 0.12, 0.03, C.naranja); p.position.set(0, 0.06, 0.08 * s); g.add(p); }
  return g;
}
function dino(color = C.hoja) {
  const g = new THREE.Group();
  const cuerpo = bola(0.5, color, 1.5, 0.85, 0.85); cuerpo.position.y = 0.85; g.add(cuerpo);
  const cuello = caja(0.2, 0.7, 0.2, color); cuello.position.set(0.6, 1.2, 0); cuello.rotation.z = -0.35; g.add(cuello);
  const cab = bola(0.22, color, 1.3, 0.9, 0.9); cab.position.set(0.82, 1.58, 0); g.add(cab);
  ojos(g, 0.92, 1.64, 0.15, 0.035);
  const cola = cono(0.25, 1.1, color); cola.rotation.z = Math.PI / 2 + 0.2; cola.position.set(-1.0, 0.8, 0); g.add(cola);
  for (let i = 0; i < 5; i++) { const e = cono(0.08, 0.2, C.naranja); e.position.set(-0.5 + i * 0.28, 1.28 - Math.abs(i - 2) * 0.05, 0); g.add(e); }
  const patas = [];
  for (const [x, z] of [[0.4, 0.22], [0.4, -0.22], [-0.4, 0.22], [-0.4, -0.22]]) { const p = caja(0.16, 0.5, 0.16, color); p.position.set(x, 0.25, z); g.add(p); patas.push(p); }
  return { g, patas, cab };
}
function confeti(root, cols, n = 26) {
  const arr = [];
  for (let i = 0; i < n; i++) { const c = caja(0.07, 0.07, 0.02, cols[i % cols.length], { emissive: cols[i % cols.length], emissiveIntensity: 0.4 }); root.add(c); arr.push(c); }
  return (t) => arr.forEach((c, i) => { const f = (t * 0.55 + i / arr.length) % 1; c.position.set(Math.sin(i * 12.9) * 1.7, 3.0 - f * 3.0, Math.cos(i * 7.3) * 1.0); c.rotation.set(t * 3 + i, t * 2, t); });
}
function valla(root, x0, x1, z) { for (let x = x0; x <= x1; x += 0.3) { const p = caja(0.08, 0.5, 0.06, C.madera); p.position.set(x, 0.25, z); root.add(p); } const t = caja(x1 - x0 + 0.1, 0.07, 0.05, C.madera); t.position.set((x0 + x1) / 2, 0.38, z); root.add(t); }

export function construir(nombre, S, root, scene, ACC) {
  const upd = [], anclas = {};
  const n = Number(S.n ?? 0);
  if (nombre === "consola") {
    const base = isla(3.2, 2.2); root.add(base);
    const mueble = caja(1.8, 0.35, 0.6, C.madera); mueble.position.set(0, 0.17, -0.5); root.add(mueble);
    const tv = caja(1.7, 0.95, 0.06, C.oscuro); tv.position.set(0, 0.95, -0.62); root.add(tv);
    const pant = new THREE.Mesh(new THREE.PlaneGeometry(1.58, 0.84), new THREE.MeshBasicMaterial({ color: 0x14203a })); pant.position.set(0, 0.95, -0.585); root.add(pant);
    // barra de descarga en la tele
    const fondo = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.1), new THREE.MeshBasicMaterial({ color: 0x2b3554 })); fondo.position.set(0, 0.78, -0.58); root.add(fondo);
    const barra = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.1), new THREE.MeshBasicMaterial({ color: ACC })); barra.position.set(0, 0.78, -0.578); root.add(barra);
    const { g: cons, led } = consola(); cons.position.set(1.15, 0, -0.35); cons.scale.setScalar(0.85); root.add(cons);
    const sofa = caja(1.2, 0.3, 0.45, C.morado); sofa.position.set(0, 0.15, 0.6); root.add(sofa);
    const resp = caja(1.2, 0.35, 0.12, C.morado); resp.position.set(0, 0.42, 0.8); root.add(resp);
    const pl = palmera(0.9); pl.position.set(-1.35, 0, 0.7); root.add(pl);
    // cubitos de datos que caen hacia la consola
    const cubos = [];
    for (let i = 0; i < 14; i++) { const c = caja(0.12, 0.12, 0.12, i % 2 ? ACC : C.cian, { emissive: i % 2 ? ACC : C.cian, emissiveIntensity: 0.5 }); root.add(c); cubos.push(c); }
    const fin = clamp(Number(S.progreso ?? 1));
    upd.push((t) => {
      const k = eo(t / (S.dur * 0.8)) * fin;
      barra.scale.x = Math.max(0.001, k); barra.position.x = -0.6 + 0.6 * k;
      led.material.emissiveIntensity = 1 + Math.sin(t * 10);
      cubos.forEach((c, i) => { const f = ((t * 0.7 + i / cubos.length) % 1); c.position.set(1.15 + Math.sin(i * 2.1) * 0.3 * (1 - f), 2.6 - f * 1.9, -0.35 + Math.cos(i * 1.3) * 0.25 * (1 - f)); c.rotation.set(t * 2 + i, t * 3, 0); c.scale.setScalar(1 - f * 0.7); });
    });
    anclas.a = new THREE.Vector3(1.15, 1.2, -0.35); anclas.b = new THREE.Vector3(0, 1.5, -0.6); anclas.c = new THREE.Vector3(-0.6, 0.8, 0.6);
  } else if (nombre === "discos") {
    const base = isla(2.6, 2.6); root.add(base);
    const total = Math.max(1, Math.min(60, n || 45));
    const discos = [];
    for (let i = 0; i < total; i++) {
      const d = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 0.035, 28), mat(i % 2 ? 0xdfe6f2 : 0xc7d2e6, { metalness: 0.6, roughness: 0.25 }));
      d.position.y = 0.02 + i * 0.04; root.add(d); discos.push(d);
    }
    const agujero = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, total * 0.04 + 0.05, 12), mat(C.oscuro)); agujero.position.y = (total * 0.04) / 2; root.add(agujero);
    const ar = arbol(); ar.position.set(-0.95, 0, 0.8); root.add(ar); const ar2 = arbol(); ar2.position.set(0.95, 0, -0.85); ar2.scale.setScalar(0.8); root.add(ar2);
    upd.push((t) => { const vis = Math.floor(eo(t / (S.dur * 0.75)) * total); discos.forEach((d, i) => { d.visible = i < vis; d.rotation.y = t * 0.6; }); agujero.scale.y = Math.max(0.01, vis / total); agujero.position.y = (vis * 0.04) / 2; });
    anclas.a = new THREE.Vector3(0, total * 0.04 + 0.3, 0); anclas.b = new THREE.Vector3(0.7, 0.4, 0.5); anclas.c = new THREE.Vector3(-0.7, 0.4, -0.5);
  } else if (nombre === "almacen") {
    const base = isla(2.8, 2.2); root.add(base);
    const carcasa = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.1, 1.0), mat(C.gris, { transparent: true, opacity: 0.35 })); carcasa.position.y = 0.6; root.add(carcasa);
    const marco = new THREE.LineSegments(new THREE.EdgesGeometry(carcasa.geometry), new THREE.LineBasicMaterial({ color: 0xffffff })); marco.position.copy(carcasa.position); root.add(marco);
    const lleno = clamp(Number(S.progreso ?? 0.58)), libre = clamp(Number(S.ocupado ?? 0));
    const bloqueOtros = caja(2.0 * libre, 1.0, 0.9, C.gris); root.add(bloqueOtros);
    const bloque = caja(2.0, 1.0, 0.9, ACC, { emissive: ACC, emissiveIntensity: 0.25 }); root.add(bloque);
    upd.push((t) => {
      const k = eo((t - 0.4) / (S.dur * 0.6)) * lleno;
      bloqueOtros.position.set(-1 + libre, 0.55, 0); bloqueOtros.scale.x = Math.max(0.001, 1);
      bloque.scale.x = Math.max(0.001, k); bloque.position.set(-1 + 2 * libre + k, 0.55, 0);
    });
    const pl = palmera(1.0); pl.position.set(1.2, 0, 0.75); root.add(pl);
    anclas.a = new THREE.Vector3(-0.3, 1.4, 0); anclas.b = new THREE.Vector3(0.9, 1.3, 0); anclas.c = new THREE.Vector3(-1.0, 0.3, 0.6);
  } else if (nombre === "red") {
    const base = isla(3.6, 2.2); root.add(base);
    const torre = edificio(0.7, 1.6, 0.7, C.azul); torre.position.set(-1.3, 0, -0.4); root.add(torre);
    const ant = caja(0.04, 0.5, 0.04, C.gris); ant.position.set(-1.3, 1.85, -0.4); root.add(ant);
    const c1 = casa(C.blanco, C.rojo); c1.position.set(1.1, 0, -0.5); root.add(c1);
    const c2 = casa(0xffe2b8, C.azul); c2.position.set(1.3, 0, 0.6); c2.scale.setScalar(0.85); root.add(c2);
    // cable con postes y pulsos de luz que viajan
    const puntos = [new THREE.Vector3(-1.3, 1.5, -0.4), new THREE.Vector3(-0.4, 1.1, 0.1), new THREE.Vector3(0.4, 1.0, 0.1), new THREE.Vector3(1.1, 0.75, -0.5)];
    const curva = new THREE.CatmullRomCurve3(puntos);
    root.add(new THREE.Mesh(new THREE.TubeGeometry(curva, 40, 0.02, 6), mat(C.oscuro)));
    for (const x of [-0.4, 0.4]) { const p = caja(0.06, 1.05, 0.06, C.madera); p.position.set(x, 0.52, 0.1); root.add(p); }
    const pulsos = Array.from({ length: 5 }, () => { const s = new THREE.Mesh(new THREE.SphereGeometry(0.07, 10, 10), new THREE.MeshBasicMaterial({ color: ACC })); root.add(s); return s; });
    upd.push((t) => pulsos.forEach((s, i) => s.position.copy(curva.getPoint((t * 0.45 + i / pulsos.length) % 1))));
    anclas.a = puntos[0].clone().add(new THREE.Vector3(0, 0.6, 0)); anclas.b = puntos[2].clone().add(new THREE.Vector3(0, 0.4, 0)); anclas.c = new THREE.Vector3(1.2, 1.2, 0);
  } else if (nombre === "isla" || nombre === "mapa_pin") {
    const base = isla(3.6, 3.0); root.add(base);
    const carretera = caja(3.6, 0.02, 0.5, C.asfalto); carretera.position.set(0, 0.01, 0.55); root.add(carretera);
    for (let x = -1.5; x < 1.6; x += 0.45) { const l = caja(0.22, 0.021, 0.04, C.linea); l.position.set(x, 0.02, 0.55); root.add(l); }
    const agua = caja(3.6, 0.03, 0.6, C.agua, { emissive: C.agua, emissiveIntensity: 0.15 }); agua.position.set(0, -0.0, 1.2); root.add(agua);
    const cols = [C.rosa, C.cian, C.amarillo, C.morado, C.naranja];
    [[-1.2, -0.7, 0.6, 1.6], [-0.45, -0.75, 0.55, 2.3], [0.3, -0.7, 0.6, 1.3], [1.05, -0.75, 0.6, 1.9]].forEach(([x, z, w, h], i) => { const e = edificio(w, h, 0.6, cols[i % cols.length]); e.position.set(x, 0, z); root.add(e); });
    [[-1.5, 0.95], [-0.5, 0.95], [0.6, 0.95], [1.5, 0.95]].forEach(([x, z]) => { const p = palmera(0.8); p.position.set(x, 0, z); root.add(p); });
    const auto = coche(C.rojo); root.add(auto);
    upd.push((t) => { const x = ((t * 0.9) % 4.2) - 2.1; auto.position.set(x, 0.02, 0.45); auto.visible = Math.abs(x) < 1.75; });
    if (nombre === "mapa_pin") {
      const pin = new THREE.Group();
      const cab = new THREE.Mesh(new THREE.SphereGeometry(0.22, 20, 20), mat(C.rojo, { emissive: C.rojo, emissiveIntensity: 0.3 }));
      const pun = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.4, 16), mat(C.rojo)); pun.rotation.x = Math.PI; pun.position.y = -0.27;
      pin.add(cab, pun); root.add(pin);
      const aro = new THREE.Mesh(new THREE.RingGeometry(0.2, 0.26, 32), new THREE.MeshBasicMaterial({ color: ACC, transparent: true, side: THREE.DoubleSide })); aro.rotation.x = -Math.PI / 2; aro.position.set(0.3, 0.04, 0.0); root.add(aro);
      upd.push((t) => { const k = clamp((t - 0.3) / 0.5); pin.position.set(0.3, 0.55 + (1 - eob(k)) * 3 + 0.06 * Math.sin(t * 3), 0); pin.visible = t > 0.3; const r = ((t - 0.8) % 1.2 + 1.2) % 1.2; aro.scale.setScalar(1 + r * 3); aro.material.opacity = 1 - r / 1.2; aro.visible = t > 0.8; });
      anclas.a = new THREE.Vector3(0.3, 1.2, 0);
    } else anclas.a = new THREE.Vector3(-0.45, 2.6, -0.75);
    anclas.b = new THREE.Vector3(1.05, 2.1, -0.75); anclas.c = new THREE.Vector3(-1.4, 0.9, 0.6);
  } else if (nombre === "gallina") {
    root.add(isla(3.2, 2.4)); valla(root, -1.4, 1.4, -1.0);
    const { g: ga, cuello } = gallina(C.blanco); ga.position.set(-0.7, 0, 0); root.add(ga);
    const h = huevo(0xfff3dc, 1.5); root.add(h);
    const ph = palmera(0.8); ph.position.set(1.4, 0, -0.7); root.add(ph);
    upd.push((t) => {
      cuello.rotation.z = Math.sin(t * 6) * 0.18 - 0.1; ga.position.y = Math.abs(Math.sin(t * 3)) * 0.06;
      const k = clamp((t - 0.35) / 0.55); h.visible = t > 0.35; h.position.set(0.7 - 0.35 * (1 - eo(k)) * 0, 0.0 + (1 - eob(k)) * 1.6, 0.25); h.rotation.y = t * 1.4; h.rotation.z = Math.sin(t * 2) * 0.1;
    });
    anclas.a = new THREE.Vector3(-0.7, 1.6, 0); anclas.b = new THREE.Vector3(0.7, 1.15, 0.25); anclas.c = new THREE.Vector3(0, 0.3, 1.0);
  } else if (nombre === "huevos") {
    root.add(isla(3.4, 2.6));
    const total = Math.max(3, Math.min(48, n || 24)), cols = [0xfff3dc, 0xf3dfc0, 0xe8c9a0, 0xffffff];
    const hs = [];
    for (let i = 0; i < total; i++) { const e = huevo(cols[i % cols.length], 0.9); const cx = i % 8, cz = Math.floor(i / 8); e.position.set(-1.4 + cx * 0.4, 0, -0.8 + cz * 0.42); root.add(e); hs.push(e); }
    const oro = huevo(0xffd25a, 2.2); oro.children[0].material.emissive = new THREE.Color(0xffb300); oro.children[0].material.emissiveIntensity = 0.5; oro.position.set(0, 0, 0.7); root.add(oro);
    const lluvia = confeti(root, [C.amarillo, C.rosa, C.cian, C.naranja]);
    upd.push((t) => {
      const vis = eo(t / (S.dur * 0.65)) * total;
      hs.forEach((e, i) => { const k = clamp(vis - i); e.visible = k > 0; e.scale.setScalar(Math.max(0.001, eob(k))); e.position.y = Math.abs(Math.sin(t * 4 + i * 0.7)) * 0.04 * k; });
      const kk = clamp((t - S.dur * 0.35) / 0.5); oro.visible = kk > 0; oro.scale.setScalar(Math.max(0.001, eob(kk))); oro.rotation.y = t * 2; oro.position.y = 0.05 + Math.sin(t * 3) * 0.06;
      lluvia(t);
    });
    anclas.a = new THREE.Vector3(-0.8, 1.0, -0.3); anclas.b = new THREE.Vector3(0.9, 1.2, 0); anclas.c = new THREE.Vector3(0, 1.5, 0.7);
  } else if (nombre === "dino") {
    root.add(isla(3.6, 2.6));
    const { g: d, patas } = dino(); d.position.set(-0.9, 0, 0); d.scale.setScalar(0.85); root.add(d);
    const nido = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.7, 0.14, 14), mat(C.madera)); nido.position.set(1.15, 0.07, 0.2); root.add(nido);
    const hs = [];
    for (let i = 0; i < 6; i++) { const a = (i / 6) * Math.PI * 2, e = huevo(i % 2 ? 0xe8e0c8 : 0xfff3dc, 1.1); e.position.set(1.15 + Math.cos(a) * 0.3, 0.12, 0.2 + Math.sin(a) * 0.3); root.add(e); hs.push(e); }
    const pl = palmera(1.1); pl.position.set(0.2, 0, -1.0); root.add(pl); const pl2 = palmera(0.8); pl2.position.set(1.7, 0, -0.9); root.add(pl2);
    upd.push((t) => {
      patas.forEach((p, i) => { p.position.y = 0.25 + Math.max(0, Math.sin(t * 5 + (i % 2) * Math.PI)) * 0.06; });
      d.position.y = Math.abs(Math.sin(t * 5)) * 0.03; d.rotation.y = Math.sin(t * 0.8) * 0.15;
      hs.forEach((e, i) => { const k = clamp((t - 0.2 - i * 0.12) / 0.4); e.visible = k > 0; e.scale.setScalar(Math.max(0.001, eob(k))); });
    });
    anclas.a = new THREE.Vector3(-0.8, 2.0, 0); anclas.b = new THREE.Vector3(1.15, 1.0, 0.2); anclas.c = new THREE.Vector3(0, 0.3, 1.0);
  } else if (nombre === "pila") {
    root.add(isla(3.0, 2.4));
    const hs = []; let idx = 0;
    for (let fila = 0; fila < 4; fila++) for (let c = 0; c < 4 - fila; c++) { const e = huevo(idx % 2 ? 0xf3dfc0 : 0xfff3dc, 1.15); e.position.set((c - (3 - fila) / 2) * 0.5, 0.08 + fila * 0.42, 0); root.add(e); hs.push({ e, i: idx++ }); }
    const oro = huevo(0xffd25a, 1.5); oro.children[0].material.emissive = new THREE.Color(0xffb300); oro.children[0].material.emissiveIntensity = 0.6; root.add(oro);
    const lluvia = confeti(root, [C.amarillo, C.morado, C.cian], 18);
    upd.push((t) => {
      hs.forEach(({ e, i }) => { const k = clamp((t - i * 0.12) / 0.4); e.visible = k > 0; e.scale.setScalar(Math.max(0.001, eob(k))); e.rotation.z = Math.sin(t * 3 + i) * 0.05; });
      const kk = clamp((t - 1.4) / 0.5); oro.visible = kk > 0; oro.position.set(0, 1.45 + (1 - eob(kk)) * 1.5 + Math.sin(t * 3) * 0.05, 0); oro.rotation.y = t * 2.2; oro.scale.setScalar(Math.max(0.001, eob(kk)));
      lluvia(t);
    });
    anclas.a = new THREE.Vector3(0, 2.4, 0); anclas.b = new THREE.Vector3(-0.9, 1.0, 0.3); anclas.c = new THREE.Vector3(0.9, 0.6, 0.3);
  } else if (nombre === "trio") {
    root.add(isla(3.4, 2.4)); valla(root, -1.5, 1.5, -1.0);
    const cols = [C.blanco, 0xd9a066, 0x6b4a36], bichos = [];
    cols.forEach((c, i) => { const { g, cuello } = gallina(c); g.position.set(-1.0 + i * 1.0, 0, 0.15 + (i % 2) * 0.25); g.scale.setScalar(0.62); g.rotation.y = 0.35 - i * 0.3; root.add(g); bichos.push({ g, cuello, y0: g.position.y }); });
    const pols = [0, 1].map((i) => { const p = pollito(); p.scale.setScalar(0.5); p.position.set(-0.5 + i * 1.1, 0, 0.85); root.add(p); return p; });
    const pl = palmera(0.9); pl.position.set(1.55, 0, -0.75); root.add(pl);
    upd.push((t) => {
      bichos.forEach((b, i) => { b.cuello.rotation.z = Math.sin(t * 6 + i * 2) * 0.2 - 0.1; b.g.position.y = Math.abs(Math.sin(t * 3 + i * 1.7)) * 0.08; });
      pols.forEach((p, i) => { p.position.y = Math.abs(Math.sin(t * 7 + i * 2)) * 0.12; p.position.x += Math.sin(t * 2 + i) * 0.002; });
    });
    anclas.a = new THREE.Vector3(-1.0, 1.4, 0.3); anclas.b = new THREE.Vector3(0.9, 1.4, 0.4); anclas.c = new THREE.Vector3(0, 0.3, 1.0);
  } else if (nombre === "cesta") {
    root.add(isla(3.0, 2.4));
    const cj = caja(1.5, 0.45, 1.0, C.madera); cj.position.set(0, 0.23, 0); root.add(cj);
    const interior = caja(1.3, 0.05, 0.8, C.tierra2); interior.position.set(0, 0.46, 0); root.add(interior);
    const gs = [], total = 14;
    for (let i = 0; i < total; i++) { const e = huevo(i % 3 ? 0xfff3dc : 0xe8c9a0, 0.8); root.add(e); gs.push(e); }
    const lluvia = confeti(root, [C.amarillo, C.rosa, C.cian, C.naranja], 26);
    upd.push((t) => {
      gs.forEach((e, i) => {
        const t0 = 0.2 + i * 0.16, k = clamp((t - t0) / 0.5), fx = ((i % 5) - 2) * 0.24, fz = (Math.floor(i / 5) - 1) * 0.25;
        e.visible = t > t0; e.position.set(fx, 0.46 + (1 - eo(k)) * 2.6 + Math.floor(i / 5) * 0.06, fz); e.rotation.z = (1 - k) * 2;
      });
      lluvia(t);
    });
    anclas.a = new THREE.Vector3(0, 1.4, 0); anclas.b = new THREE.Vector3(-0.8, 0.9, 0.5); anclas.c = new THREE.Vector3(0.8, 0.9, 0.5);
  } else if (nombre === "nacer") {
    root.add(isla(2.8, 2.4));
    const R = 0.5, mitadAlta = new THREE.Mesh(new THREE.SphereGeometry(R, 14, 10, 0, Math.PI * 2, 0, Math.PI * 0.45), mat(0xfff3dc, { side: THREE.DoubleSide }));
    const mitadBaja = new THREE.Mesh(new THREE.SphereGeometry(R, 14, 10, 0, Math.PI * 2, Math.PI * 0.45, Math.PI * 0.55), mat(0xfff3dc, { side: THREE.DoubleSide }));
    const eg = new THREE.Group(); eg.add(mitadAlta, mitadBaja); eg.scale.set(0.85, 1.2, 0.85); eg.position.y = R * 1.2; root.add(eg);
    const p = pollito(); p.scale.setScalar(0.9); root.add(p);
    const lluvia = confeti(root, [C.amarillo, C.rosa, C.cian, C.naranja, C.blanco], 30);
    upd.push((t) => {
      const grieta = 0.9;
      eg.rotation.z = t < grieta ? Math.sin(t * 22) * 0.12 * (t / grieta) : 0;
      const k = clamp((t - grieta) / 0.5);
      mitadAlta.position.set(0.05 * k, k * 1.2, 0); mitadAlta.rotation.set(0, 0, -k * 1.3); mitadAlta.visible = k < 1 || t < grieta + 1.2;
      p.visible = t > grieta; p.position.y = -0.2 + eob(clamp((t - grieta - 0.1) / 0.5)) * 0.55 + (t > grieta + 0.8 ? Math.abs(Math.sin((t - grieta) * 6)) * 0.08 : 0);
      lluvia.visible = t > grieta; if (t > grieta) lluvia(t - grieta);
    });
    anclas.a = new THREE.Vector3(0, 1.6, 0); anclas.b = new THREE.Vector3(-0.9, 0.7, 0.4); anclas.c = new THREE.Vector3(0.9, 0.7, 0.4);
  } else if (nombre === "podio") {
    root.add(isla(3.4, 2.4));
    const alturas = [[0, 1.0, C.amarillo], [-0.95, 0.65, C.gris], [0.95, 0.4, 0xc58b4d]];
    alturas.forEach(([x, h, c]) => { const b = caja(0.9, h, 0.9, c); b.position.set(x, h / 2, 0); root.add(b); });
    const h = huevo(0xfff3dc, 1.6); root.add(h);
    const corona = cono(0.28, 0.3, C.amarillo); corona.position.y = 1.0 + 0.95; root.add(corona);
    const { g: ga, cuello } = gallina(C.blanco); ga.scale.setScalar(0.8); ga.position.set(-0.95, 0.65, 0); ga.rotation.y = 0.5; root.add(ga);
    const lluvia = confeti(root, [C.amarillo, C.rosa, C.cian, C.naranja, C.morado], 34);
    upd.push((t) => {
      const k = clamp(t / 0.6); h.position.set(0, 1.0 + (1 - eob(k)) * 2 + Math.sin(t * 3) * 0.05, 0); h.rotation.y = t * 1.6;
      corona.position.set(0, 1.0 + 0.82 + (1 - eob(k)) * 2 + Math.sin(t * 3) * 0.05, 0); corona.rotation.y = t * 1.6;
      cuello.rotation.z = Math.sin(t * 5) * 0.15; lluvia(t);
    });
    anclas.a = new THREE.Vector3(0, 2.5, 0); anclas.b = new THREE.Vector3(-0.95, 1.9, 0); anclas.c = new THREE.Vector3(0.95, 1.0, 0);
  }
  return { upd, anclas };
}

// ---------- etiquetas tipo tarjeta (icono de color + antetítulo + texto) que aparecen en secuencia ----------
export function etiquetas(lista, anclas, cam, S) {
  const capa = document.createElement("div");
  capa.style.cssText = "position:absolute;inset:0;pointer-events:none";
  document.body.appendChild(capa);
  const colores = ["#ff6b4a", "#ffb02e", "#2fbf71", "#4f7cff", "#b25cff"];
  const nombres = Object.keys(anclas);
  const els = (lista || []).slice(0, 4).map((e, i) => {
    const d = document.createElement("div");
    const col = e.color || colores[i % colores.length];
    d.style.cssText = "position:absolute;display:flex;gap:14px;align-items:center;background:#fff;border-radius:22px;padding:14px 22px 14px 14px;" +
      "box-shadow:0 10px 30px rgba(0,0,0,.35);font-family:Inter,sans-serif;transform-origin:left bottom;max-width:560px";
    d.innerHTML = `<div style="width:64px;height:64px;border-radius:16px;background:${col};display:grid;place-items:center;font-size:38px;color:#fff;flex:none">${e.icono || "●"}</div>` +
      `<div><div style="font-weight:900;font-size:24px;letter-spacing:2px;color:${col}">${(e.titulo || "").toUpperCase()}</div>` +
      `<div style="font-weight:900;font-size:40px;color:#1d1f2b;line-height:1.05">${e.texto || ""}</div></div>`;
    capa.appendChild(d);
    return { d, ancla: anclas[e.ancla || nombres[i % nombres.length]] || anclas[nombres[0]], t0: e.t ?? (0.5 + i * Math.max(0.6, (S.dur - 1) / Math.max(1, lista.length))) };
  });
  const v = new THREE.Vector3();
  return (t, root) => {
    for (const e of els) {
      v.copy(e.ancla).applyMatrix4(root.matrixWorld).project(cam);
      const x = (v.x * 0.5 + 0.5) * 1080, y = (-v.y * 0.5 + 0.5) * 1920;
      const k = eob((t - e.t0) / 0.35);
      e.d.style.left = `${Math.min(1080 - 40 - e.d.offsetWidth, Math.max(40, x - 40))}px`;
      e.d.style.top = `${Math.max(420, y - e.d.offsetHeight - 30)}px`;
      e.d.style.opacity = clamp((t - e.t0) / 0.15);
      e.d.style.transform = `scale(${Math.max(0.001, k)})`;
    }
  };
}
