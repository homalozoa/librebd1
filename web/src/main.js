import "@fontsource-variable/inter";
import "@fontsource-variable/newsreader";
import "./style.css";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = (s, r = document) => r.querySelector(s);

/* ---------------- labels, colours, steps ---------------- */
const LABEL = {
  head_shell: "头壳", head_top_band: "头顶带", head_light: "灯板", eye_ring: "眼筒", eye_band: "右眼红环", lens: "镜头",
  ear: "耳盘外圈", ear_centre: "耳盘中心", antenna: "天线", antenna_collar: "天线套", neck: "脖子", torso: "躯干",
  chest_plate: "胸板", chest_tab: "胸口红块", thigh: "大腿", thigh_channel: "槽上段凸块", thigh_channel_floor: "槽底",
  thigh_channel_tip: "槽顶小块", thigh_rod: "螺杆", thigh_piston: "螺纹柱", knee_cap: "膝盖盖", shin: "小腿",
  shin_plate: "小腿红板", foot_heel: "脚后半段", foot_front: "脚前半段", stand: "底座", paint: "头侧涂装嵌件",
  hip_pin: "髋销 3×65", knee_pin: "膝销 3×8", ankle_pin: "踝销 3×12",
};
const baseOf = (n) => (/^paint_/.test(n) ? "paint" : n.replace(/_(left|right)$/, ""));
const labelOf = (n) => (LABEL[baseOf(n)] || n) + (/_left$/.test(n) ? "（左）" : /_right$/.test(n) ? "（右）" : "");
const sideOf = (n) => (/left/.test(n) ? 1 : /right/.test(n) ? -1 : 0);
const COLOUR_NAME = {
  "#C9CFB0": "米白", "#B2A696": "暖米白", "#80786B": "暖灰", "#999996": "灰", "#82827D": "中灰", "#B8BAB0": "浅灰",
  "#B2B5B2": "镜头浅灰", "#C40A08": "亮红", "#7A2B26": "暗红", "#5E3330": "深红褐", "#638599": "钢蓝", "#52A624": "绿",
  "#593D36": "深棕", "#595952": "深灰", "#B2B59E": "浅灰绿", "#424242": "炭灰", "#33363B": "黑灰（底座）",
};

/** Explode offsets in assembly coordinates (x forward, y to the left, z up, mm). */
function explodeOf(n) {
  const s = sideOf(n) || 1;
  const t = [
    [/^stand/, [0, 0, -95]], [/^head_shell/, [0, 0, 80]], [/^head_top_band/, [0, 0, 125]], [/^head_light/, [-60, 0, 95]],
    [/^paint_.*top_edge/, [0, s * 15, 120]], [/^paint_.*hood_grey/, [30, s * 40, 95]], [/^paint_/, [0, s * 55, 85]],
    [/^eye_ring/, [70, 0, 80]], [/^eye_band/, [95, 0, 80]], [/^lens/, [115, 0, 80]],
    [/^ear_centre/, [0, s * 95, 80]], [/^ear_/, [0, s * 65, 80]], [/^antenna_collar/, [-10, s * 85, 115]], [/^antenna/, [-20, s * 85, 130]],
    [/^neck/, [0, 0, 42]], [/^torso/, [0, 0, 0]], [/^chest_plate/, [60, 0, 0]], [/^chest_tab/, [60, 0, 35]],
    [/^thigh_channel_floor/, [0, s * 70, 0]], [/^thigh_channel_tip/, [0, s * 80, 0]], [/^thigh_channel/, [0, s * 90, 0]],
    [/^thigh_rod/, [0, s * 105, 12]], [/^thigh_piston/, [0, s * 105, 0]], [/^knee_cap/, [0, s * 105, -15]], [/^thigh_/, [0, s * 45, 0]],
    [/^shin_plate/, [0, s * 90, -35]], [/^shin_/, [0, s * 45, -35]],
    [/^foot_heel/, [0, s * 45, -80]], [/^foot_front/, [30, s * 45, -80]],
    [/^hip_pin/, [0, 120, 0]], [/^knee_pin/, [0, s * 40, 0]], [/^ankle_pin/, [0, s * 40, -45]],
  ];
  return (t.find(([re]) => re.test(n)) || [0, [0, 0, 0]])[1];
}

const STEPS = [
  ["试配", "先不涂胶，把所有嵌件放进各自的凹槽。太紧的用锉刀轻磨，不要硬压。", /^(paint_|head_top_band|head_light|eye_band|chest_)/, "嵌件"],
  ["头部嵌件", "头顶带、两侧涂装件和右眼红环按凹槽方向粘进头壳，灯板粘在头后凹槽底。右侧（-y）和左侧（+y）图案不同，别装反。", /^(head_shell|paint_|head_top_band|head_light|eye_band)/, "头壳 · 涂装 · 灯板"],
  ["眼睛", "眼筒插进面板上 6 mm 深的眼窝，再把镜头塞进眼筒。右眼是钢蓝的大镜头，左眼是浅灰的。", /^(head_shell|eye_|lens_)/, "眼筒 · 镜头"],
  ["耳朵和天线", "耳盘中心灰件用自带的 3 mm 凸销插进头侧，外圈套在外面粘住。天线先套上锥形套，再插进 2.3 mm 的斜孔。", /^(head_shell|ear_|antenna)/, "耳盘 · 天线 · 套"],
  ["躯干与脖子", "胸板粘进胸口凹槽底，红块粘在正面和顶部斜面的交界处。脖子两端各插进 8 mm 的斜孔。", /^(head_shell|neck|torso|chest_)/, "脖子 · 躯干 · 胸板"],
  ["大腿", "先把深棕槽底、槽顶小块和红色凸块拼进槽里，再把螺杆粘在槽底（粗的一头对准六角凹坑下方），螺纹柱粘进侧槽，膝盖盖压进凹槽。", /^(thigh_|knee_cap)/, "大腿 · 螺杆 · 螺纹柱"],
  ["小腿和脚", "红板嵌进 1 mm 凹槽，凸耳在两头。脚的深色后半段和浅色前半段在 x = 40.5 处对接粘牢。", /^(shin_|foot_)/, "小腿 · 红板 · 脚"],
  ["关节销，不要涂胶", "髋：3×65 mm 的销穿过左大腿、躯干、右大腿。膝：每侧一根 3×8 mm。踝：每侧一根 3×12 mm。靠摩擦定位，关节才能转。", /^(torso|thigh_(left|right)$|shin_(left|right)$|foot_|hip_pin|knee_pin|ankle_pin)/, "钢棒或 M3 螺丝"],
  ["底座（必需）", "重心在脚跟后面，只靠两只脚站不住。把脚粘进底座的 1.2 mm 凹槽里。", /^(stand|foot_)/, "底座 · 脚"],
];

/* ---------------- scene ---------------- */
const host = $("#viewer");
const canvas = document.createElement("canvas");
host.insertBefore(canvas, host.firstChild);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.toneMapping = THREE.NeutralToneMapping;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 5, 4000);
camera.up.set(0, 0, 1);

// soft studio light: a room environment for reflections plus one warm key
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;
scene.add(new THREE.HemisphereLight(0xfffaf0, 0xd8cfbd, 0.9));
const key = new THREE.DirectionalLight(0xfff3e2, 2.0);
key.position.set(260, -320, 520);
scene.add(key);
const fill = new THREE.DirectionalLight(0xe9eef7, 0.7);
fill.position.set(-300, 260, 160);
scene.add(fill);

// soft contact shadow under the droid
const shadow = (() => {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  const grad = g.createRadialGradient(128, 128, 0, 128, 128, 128);
  grad.addColorStop(0, "rgba(40,30,20,.34)");
  grad.addColorStop(0.55, "rgba(40,30,20,.14)");
  grad.addColorStop(1, "rgba(40,30,20,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 256, 256);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(330, 330),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  m.position.set(12, 0, -4.8);
  scene.add(m);
  return m;
})();

const items = []; // { name, mesh, mat, home, exv, hex, pPos, pQuat, hardware, p, op, glow }
const byName = new Map();
const bedGroup = new THREE.Group();
scene.add(bedGroup);
let DATA = null;

const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const GAP = 34;
const plateX0 = (n) => -(n * 256 + (n - 1) * GAP) / 2;
const CLAY = new THREE.Color("#d97757");

function addItem(name, geom, hex, home, extra = {}) {
  const mat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(hex), roughness: extra.rough ?? 0.6, metalness: extra.metal ?? 0.03, flatShading: true, transparent: true,
  });
  mat.emissive.copy(CLAY);
  mat.emissiveIntensity = 0;
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.copy(home);
  mesh.userData.name = name;
  scene.add(mesh);
  const it = {
    name, mesh, mat, home: home.clone(), exv: V(explodeOf(name)), hex, pPos: home.clone(), pQuat: new THREE.Quaternion(),
    hardware: !!extra.hardware, p: extra.p || null, op: 1, glow: 0,
  };
  items.push(it);
  byName.set(name, it);
  return it;
}

async function load() {
  const [meta, buf] = await Promise.all([
    fetch("data/parts.json").then((r) => r.json()),
    fetch("data/bd1.bin").then((r) => r.arrayBuffer()),
  ]);
  DATA = meta;
  let tris = 0;
  const nPlates = meta.plates;
  for (const p of meta.parts) {
    const vq = new Uint16Array(buf, p.voff, p.nv * 3);
    const pos = new Float32Array(p.nv * 3);
    for (let i = 0; i < p.nv; i++) for (let k = 0; k < 3; k++) pos[i * 3 + k] = vq[i * 3 + k] * p.scale[k] + p.lo[k] - p.centre[k];
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    geo.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, p.ioff, p.nt * 3), 1));
    geo.computeBoundingSphere();
    const lens = /^lens/.test(p.name);
    const metal = /^(knee_cap|thigh_rod|thigh_piston)/.test(p.name);
    const it = addItem(p.name, geo, p.colour, V(p.centre), { p, rough: lens ? 0.15 : metal ? 0.35 : 0.6, metal: lens ? 0.25 : metal ? 0.45 : 0.03 });
    tris += p.nt;
    // print pose: rotate about the part's own centre, then put the rotated min corner on its bed slot
    const m = p.rot;
    const m4 = new THREE.Matrix4().set(m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0, 0, 0, 0, 1);
    it.pQuat.setFromRotationMatrix(m4);
    const t = new THREE.Vector3(plateX0(nPlates) + p.plate * (256 + GAP) + p.bed[0] - p.rotMin[0], -128 + p.bed[1] - p.rotMin[1], p.dz);
    it.pPos.copy(V(p.centre).applyMatrix4(m4)).add(t);
  }
  // hardware: steel pins (not printed)
  const pin = (name, len, c) => addItem(name, new THREE.CylinderGeometry(1.5, 1.5, len, 20), "#c8ccd2", V(c), { hardware: true, metal: 0.85, rough: 0.25 });
  pin("hip_pin", 65, [5, 0, 110.5]);
  for (const [tag, s] of [["left", 1], ["right", -1]]) {
    pin(`knee_pin_${tag}`, 8, [-17.5, s * 23, 72]);
    pin(`ankle_pin_${tag}`, 12, [39.3, s * 22.5, 9.8]);
  }
  // print beds
  for (let i = 0; i < nPlates; i++) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(256, 256), new THREE.MeshBasicMaterial({ color: "#faf9f5", transparent: true, opacity: 0 }));
    b.position.set(plateX0(nPlates) + i * (256 + GAP) + 128, 0, -0.3);
    const edge = new THREE.LineSegments(new THREE.EdgesGeometry(b.geometry), new THREE.LineBasicMaterial({ color: "#b9b3a2", transparent: true, opacity: 0 }));
    edge.position.copy(b.position);
    bedGroup.add(b, edge);
  }
  $("#statTris").textContent = tris.toLocaleString("zh-CN");
  $("#statParts").textContent = meta.parts.length;
  $("#loading").remove();
  buildPage();
}

/* ---------------- state + animation ---------------- */
const HOME_AZ = -0.75;
const S = {
  mode: "assembled", ex: 0, exT: 0, pr: 0, prT: 0, az: HOME_AZ, el: 0.3, r: 470, target: new THREE.Vector3(10, 0, 100),
  azT: HOME_AZ, elT: 0.3, rT: 470, tgT: new THREE.Vector3(10, 0, 100), idle: 0, sel: null, hover: null, set: null,
};

function printDist() {
  // fit the three beds side by side: horizontal half-angle from the vertical fov and the aspect
  const half = Math.atan(Math.tan((camera.fov * Math.PI) / 360) * camera.aspect);
  return Math.min(2200, ((3 * 256 + 2 * GAP) / 2 / Math.tan(half)) * 1.12);
}
const CAM = {
  assembled: () => ({ tg: [10, 0, 100], r: 470, el: 0.3 }),
  exploded: () => ({ tg: [10, 0, 105], r: 740, el: 0.26 }),
  print: () => ({ tg: [0, 0, 0], r: printDist(), el: 0.95 }),
};

function setMode(m, opts = {}) {
  S.mode = m;
  for (const b of document.querySelectorAll(".seg button")) b.setAttribute("aria-pressed", String(b.dataset.mode === m));
  S.prT = m === "print" ? 1 : 0;
  if (m === "assembled") S.exT = 0;
  if (m === "exploded") S.exT = opts.ex ?? Math.max(S.ex, 0.75);
  if (m === "print") { S.exT = 0; S.azT = -Math.PI / 2; }
  else if (Math.abs(S.azT + Math.PI / 2) < 0.2) S.azT = HOME_AZ;
  $("#ex").value = S.exT;
  $("#exWrap").style.visibility = m === "exploded" ? "visible" : "hidden";
  const c = CAM[m]();
  S.tgT.set(...c.tg);
  S.rT = c.r;
  S.elT = c.el;
}

function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.fov = w / h < 0.9 ? 46 : 32; // keep the droid in frame on narrow screens
  camera.updateProjectionMatrix();
  if (S.mode === "print") S.rT = printDist();
}
addEventListener("resize", resize);

const tmp = new THREE.Vector3(), idQ = new THREE.Quaternion();
const lerp = (a, b, k) => a + (b - a) * k;
let last = performance.now(), visible = true;
new IntersectionObserver((e) => { visible = e[0].isIntersecting; }, { threshold: 0 }).observe(host);

function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  if (!visible || !items.length) return;
  const k = reduce ? 1 : 1 - Math.exp(-dt * 5.5);
  S.ex = lerp(S.ex, S.exT, k); S.pr = lerp(S.pr, S.prT, k);
  S.az = lerp(S.az, S.azT, k); S.el = lerp(S.el, S.elT, k); S.r = lerp(S.r, S.rT, k); S.target.lerp(S.tgT, k);
  if (!reduce && S.mode !== "print" && S.idle <= 0) S.azT += dt * 0.1;
  S.idle -= dt;
  const pr = S.pr;
  for (const it of items) {
    tmp.copy(it.home).addScaledVector(it.exv, S.ex);
    if (it.hardware) {
      it.mesh.position.copy(tmp);
      it.mesh.scale.setScalar(Math.max(1 - pr * 1.05, 1e-4));
      it.mesh.visible = pr < 0.98;
    } else {
      it.mesh.position.lerpVectors(tmp, it.pPos, pr);
      it.mesh.quaternion.slerpQuaternions(idQ, it.pQuat, pr);
    }
    const dim = S.set && !S.set.has(it.name);
    it.op = lerp(it.op, dim ? 0.1 : 1, k);
    it.mat.opacity = it.op;
    it.mat.depthWrite = it.op > 0.95;
    it.glow = lerp(it.glow, (S.hover === it.name ? 0.22 : 0) + (S.sel === it.name ? 0.3 : 0), k);
    it.mat.emissiveIntensity = it.glow;
  }
  shadow.material.opacity = 1 - pr;
  shadow.visible = pr < 0.98;
  bedGroup.children.forEach((c) => { c.material.opacity = pr; c.visible = pr > 0.01; });
  const ce = Math.cos(S.el);
  camera.position.set(S.target.x + S.r * ce * Math.cos(S.az), S.target.y + S.r * ce * Math.sin(S.az), S.target.z + S.r * Math.sin(S.el));
  camera.lookAt(S.target);
  renderer.render(scene, camera);
}

/* ---------------- interaction ---------------- */
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function pick(ev) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(items.filter((i) => i.mesh.visible && i.op > 0.5).map((i) => i.mesh), false)[0];
  return hit ? hit.object.userData.name : null;
}
let drag = null, moved = 0, hoverT = 0;
canvas.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY }; moved = 0; canvas.setPointerCapture(e.pointerId); S.idle = 4; });
canvas.addEventListener("pointermove", (e) => {
  if (drag) {
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    drag = { x: e.clientX, y: e.clientY };
    moved += Math.abs(dx) + Math.abs(dy);
    S.azT -= dx * 0.008;
    S.elT = Math.max(-0.2, Math.min(1.45, S.elT + dy * 0.006));
    S.az = S.azT; S.el = S.elT; S.idle = 4;
  } else if (performance.now() - hoverT > 60 && e.pointerType === "mouse") {
    hoverT = performance.now();
    S.hover = pick(e);
    canvas.style.cursor = S.hover ? "pointer" : "grab";
  }
});
canvas.addEventListener("pointerup", (e) => { drag = null; if (moved < 5) select(pick(e)); });
canvas.addEventListener("pointerleave", () => { S.hover = null; });
canvas.addEventListener("wheel", (e) => {
  e.preventDefault();
  S.rT = Math.max(160, Math.min(2200, S.rT * (1 + Math.sign(e.deltaY) * 0.08)));
  S.idle = 4;
}, { passive: false });

function select(name) {
  S.sel = name;
  S.set = name ? new Set([name]) : null;
  renderInfo(name ? [name] : []);
}
function highlight(names, label) {
  S.sel = null;
  S.set = names && names.length ? new Set(names) : null;
  renderInfo(names || [], label);
}

function renderInfo(names, label) {
  const el = $("#info");
  $("#hint").style.display = names.length ? "none" : "";
  if (!names.length) { el.classList.remove("on"); return; }
  el.classList.add("on");
  let html;
  if (names.length === 1) {
    const it = byName.get(names[0]), p = it.p;
    html = `<h3>${labelOf(it.name)}</h3><div class="meta"><code>${it.name}</code></div>` +
      `<p><span class="sw" style="background:${it.hex}"></span>${COLOUR_NAME[it.hex.toUpperCase()] || it.hex}　${it.hex}</p>`;
    html += p
      ? `<p>放在打印板 ${p.plate + 1}，高 ${p.height} mm，悬垂 ${Math.round(p.overhang)} mm²。<br>` +
        (p.overhang > 150 ? `<span class="warn">这个方向可能需要支撑。</span>` : "基本不需要支撑。") + "</p>"
      : "<p>硬件，不打印。3 mm 钢棒、铝棒或 M3 螺丝，靠摩擦定位，不涂胶。</p>";
  } else {
    html = `<h3>${label || "已选中"}</h3><p>${names.length} 个零件亮起，其余变淡。</p>`;
  }
  el.innerHTML = html + `<button id="clr">清除选择</button>`;
  $("#clr").onclick = () => { S.sel = null; S.set = null; renderInfo([]); };
}

for (const b of document.querySelectorAll(".seg button")) b.onclick = () => { setMode(b.dataset.mode); S.idle = 2; };
$("#ex").oninput = (e) => { S.exT = +e.target.value; if (S.mode !== "exploded") setMode("exploded", { ex: S.exT }); };

const toViewer = () => host.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
const match = (re) => items.filter((i) => re.test(i.name)).map((i) => i.name);

/* ---------------- page sections ---------------- */
function buildPage() {
  const groups = new Map();
  for (const it of items) {
    if (it.hardware) continue;
    const h = it.hex.toUpperCase();
    (groups.get(h) || groups.set(h, []).get(h)).push(it.name);
  }
  const pal = $("#palette");
  [...groups.entries()].sort((a, b) => b[1].length - a[1].length).forEach(([hex, names]) => {
    const bases = [...new Set(names.map((n) => labelOf(n).replace(/（[左右]）/, "")))];
    const b = document.createElement("button");
    b.className = "chip";
    b.innerHTML = `<i style="background:${hex}"></i><span><b>${COLOUR_NAME[hex] || hex}　${hex}</b><small>${bases.slice(0, 4).join("、")}${bases.length > 4 ? " 等" : ""} · ${names.length} 件</small></span>`;
    b.onclick = () => { highlight(names, `${COLOUR_NAME[hex] || hex} ${hex}`); toViewer(); };
    pal.appendChild(b);
  });

  const pl = $("#plates");
  for (let i = 0; i < DATA.plates; i++) {
    const box = document.createElement("div");
    box.className = "plate";
    const rects = DATA.parts.filter((p) => p.plate === i).map((p) =>
      `<rect data-n="${p.name}" x="${p.bed[0]}" y="${256 - p.bed[1] - p.foot[1]}" width="${p.foot[0]}" height="${p.foot[1]}" rx="1.5" fill="${p.colour}"><title>${labelOf(p.name)}</title></rect>`).join("");
    box.innerHTML = `<h3>打印板 ${i + 1}</h3><svg viewBox="0 0 256 256" role="img" aria-label="打印板 ${i + 1} 排版">${rects}</svg>`;
    box.querySelectorAll("rect").forEach((r) => { r.onclick = () => { setMode("print"); select(r.dataset.n); toViewer(); }; });
    pl.appendChild(box);
  }

  const tb = $("#oh tbody");
  DATA.parts.filter((p) => p.overhang > 150).sort((a, b) => b.overhang - a.overhang).forEach((p) => {
    const tr = document.createElement("tr");
    tr.className = "go";
    tr.innerHTML = `<td>${labelOf(p.name)} <code>${p.name}</code></td><td>${p.height}</td><td>${Math.round(p.overhang)}</td>`;
    tr.onclick = () => { setMode("print"); select(p.name); toViewer(); };
    tb.appendChild(tr);
  });

  const ol = $("#steps");
  STEPS.forEach(([title, text, re, tag]) => {
    const li = document.createElement("li"), b = document.createElement("button");
    b.innerHTML = `<div><b>${title}</b><span>${text}</span><em>${tag}</em></div>`;
    b.onclick = () => { setMode("exploded", { ex: 0.85 }); highlight(match(re), title); toViewer(); };
    li.appendChild(b);
    ol.appendChild(li);
  });
}

resize();
setMode("assembled");
S.az = HOME_AZ;
requestAnimationFrame(frame);
load().catch((err) => {
  const l = $("#loading");
  if (l) l.textContent = "载入失败：" + err;
});
