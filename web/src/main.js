import "@fontsource-variable/inter";
import "@fontsource-variable/sora";
import "@fontsource-variable/newsreader/wght-italic.css";
import "@fontsource/ibm-plex-mono/400.css";
import "./style.css";
import { STEP_RE, T, setLang, lang, applyStatic } from "./i18n.js";
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";

const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;

/* ============================================================
   Copy and part metadata
   ============================================================ */
const baseOf = (n) => (/^paint_/.test(n) ? "paint" : n.replace(/_(left|right)$/, ""));
const labelOf = (n) => (T().parts[baseOf(n)] || n) + (/_left$/.test(n) ? T().left : /_right$/.test(n) ? T().right : "");
const stripSide = (n) => labelOf(n).replace(T().left, "").replace(T().right, "");
const sideOf = (n) => (/left/.test(n) ? 1 : /right/.test(n) ? -1 : 0);
const colourName = (hex) => T().colours[hex.toUpperCase()] || hex;

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


/* ============================================================
   Renderer, post-processing, scene
   ============================================================ */
const canvas = $("#gl");
const DEBUG = location.search.includes("debug"); // ?debug keeps the drawing buffer so frames can be sampled
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: "high-performance", preserveDrawingBuffer: DEBUG });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(36, 1, 5, 9000);
camera.up.set(0, 0, 1);

const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, samples: 4 }));
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), 0.22, 0.6, 1.05);
composer.addPass(bloom);
composer.addPass(new OutputPass());

/* ---- sky ---------------------------------------------------- */
const NOISE = /* glsl */ `
  float h21(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
    return mix(mix(h21(i), h21(i+vec2(1,0)), f.x), mix(h21(i+vec2(0,1)), h21(i+vec2(1,1)), f.x), f.y); }
  float fbm(vec2 p){ float a = .5, s = 0.; for (int i = 0; i < 5; i++){ s += a*vn(p); p = p*2.03 + 7.1; a *= .5; } return s; }
`;
const SKY_FN = /* glsl */ `
  vec3 skyColour(vec3 d, float t){
    float e = d.z;
    vec3 c0 = vec3(.027,.043,.141), c1 = vec3(.10,.11,.39), c2 = vec3(.35,.18,.60), c3 = vec3(.82,.33,.60), c4 = vec3(1.,.70,.48);
    vec3 col = mix(c4, c3, smoothstep(0., .10, e));
    col = mix(col, c2, smoothstep(.06, .34, e));
    col = mix(col, c1, smoothstep(.28, .70, e));
    col = mix(col, c0, smoothstep(.62, 1., e));
    col = mix(col, vec3(.30,.14,.34), smoothstep(0., -.06, e));
    vec2 uv = vec2(atan(d.y, d.x) * 2.2, e * 3.5);
    float cl = fbm(uv * 1.1 + vec2(0., t * .004)), cl2 = fbm(uv * 2.3 + 9.);
    float neb = smoothstep(.45, .85, cl) * smoothstep(.02, .45, e) * (1. - smoothstep(.55, 1., e) * .6);
    col += neb * mix(vec3(.08,.55,.68), vec3(.70,.18,.55), cl2) * .30;
    return col;
  }
`;
const skyMat = new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, depthTest: false, toneMapped: false,
  uniforms: { uTime: { value: 0 } },
  vertexShader: "varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }",
  fragmentShader: `varying vec3 vDir; uniform float uTime; ${NOISE} ${SKY_FN}
    void main(){ gl_FragColor = vec4(pow(skyColour(normalize(vDir), uTime), vec3(2.2)), 1.); }`,
});
const sky = new THREE.Mesh(new THREE.SphereGeometry(5000, 48, 24), skyMat);
sky.renderOrder = -100;
sky.frustumCulled = false;
scene.add(sky);

// stars (world fixed), twinkling in the vertex shader
{
  const N = 2600, pos = new Float32Array(N * 3), size = new Float32Array(N), ph = new Float32Array(N), tint = new Float32Array(N * 3);
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < N; i++) {
    const u = rnd() * 2 - 1, a = rnd() * Math.PI * 2, r = Math.sqrt(1 - u * u);
    const z = Math.abs(u) * 0.97 + 0.03; // upper hemisphere only
    const x = r * Math.cos(a), y = r * Math.sin(a), k = Math.sqrt((1 - z * z) / Math.max(x * x + y * y, 1e-6));
    pos.set([x * k * 4800, y * k * 4800, z * 4800], i * 3);
    size[i] = Math.pow(rnd(), 5) * 3.2 + 0.7;
    ph[i] = rnd() * 6.28;
    const c = rnd();
    tint.set(c < 0.2 ? [1, 0.86, 0.7] : c < 0.45 ? [0.75, 0.88, 1] : [1, 1, 1], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  g.setAttribute("aSize", new THREE.BufferAttribute(size, 1));
  g.setAttribute("aPhase", new THREE.BufferAttribute(ph, 1));
  g.setAttribute("aTint", new THREE.BufferAttribute(tint, 3));
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending, toneMapped: false,
    uniforms: { uTime: { value: 0 }, uPx: { value: renderer.getPixelRatio() }, uFade: { value: 1 } },
    vertexShader: `attribute float aSize; attribute float aPhase; attribute vec3 aTint; uniform float uTime, uPx; varying vec3 vC; varying float vA;
      void main(){ vec4 mv = modelViewMatrix * vec4(position, 1.); gl_Position = projectionMatrix * mv;
        float tw = .85 + .15 * sin(uTime * (.5 + aSize * .2) + aPhase);
        gl_PointSize = aSize * uPx * (.8 + .2 * tw); vC = aTint; vA = tw * smoothstep(0., .12, position.z / 4800.); }`,
    fragmentShader: `varying vec3 vC; varying float vA; uniform float uFade;
      void main(){ vec2 q = gl_PointCoord - .5; float d = length(q); float a = smoothstep(.5, 0., d); a *= a;
        gl_FragColor = vec4(vC * (0.95 * a) * vA * uFade, 1.); }`,
  });
  const pts = new THREE.Points(g, m);
  pts.frustumCulled = false;
  pts.renderOrder = -90;
  pts.userData.mat = m;
  scene.add(pts);
  sky.userData.stars = pts;
}

// planet, ring and moon ride a rig that follows the camera and turns only part of the way with it (slow parallax)
const rig = new THREE.Group();
scene.add(rig);
{
  const planetMat = new THREE.ShaderMaterial({
    depthWrite: true, toneMapped: false,
    uniforms: { uSun: { value: new THREE.Vector3(-0.62, -0.25, 0.74).normalize() } },
    vertexShader: "varying vec3 vP; varying vec3 vN; varying vec3 vV; void main(){ vP = position; vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position,1.); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }",
    fragmentShader: `varying vec3 vP; varying vec3 vN; varying vec3 vV; uniform vec3 uSun; ${NOISE}
      void main(){
        vec3 p = normalize(vP);
        float lat = p.z;
        float w = fbm(vec2(atan(p.y, p.x) * 1.6, lat * 5.)) ;
        float band = sin(lat * 15. + w * 6.5) * .5 + .5;
        vec3 cream = vec3(1., .86, .66), rose = vec3(.92, .42, .50), vio = vec3(.38, .20, .62), gold = vec3(1., .70, .42);
        vec3 col = mix(cream, rose, smoothstep(.2, .8, band));
        col = mix(col, vio, smoothstep(.55, .95, fbm(vec2(lat * 9., w * 3.))) * .75);
        col = mix(col, gold, smoothstep(.7, 1., band) * .5);
        vec3 N = normalize(vN);
        float nd = dot(N, normalize(uSun));
        float diff = smoothstep(-.12, .85, nd);
        col *= .05 + .95 * diff;
        col += vec3(.18, .06, .30) * (1. - diff) * .35;
        float fr = pow(1. - max(dot(N, normalize(vV)), 0.), 3.2);
        col += fr * mix(vec3(.35, .80, 1.), vec3(1., .55, .45), .35) * (.15 + .85 * diff) * .9;
        gl_FragColor = vec4(pow(col, vec3(2.2)), 1.);
      }`,
  });
  const ringMat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, side: THREE.DoubleSide, toneMapped: false,
    vertexShader: "varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }",
    fragmentShader: `varying vec3 vP; ${NOISE}
      void main(){
        float r = length(vP.xy);
        float d = fbm(vec2(r * 26., 1.3));
        float a = smoothstep(.30, .72, d) * smoothstep(1.42, 1.58, r) * (1. - smoothstep(2.28, 2.42, r));
        a *= 1. - smoothstep(.05, .0, abs(r - 1.96) - .035);
        a *= .85;
        vec3 col = mix(vec3(1., .80, .60), vec3(.95, .55, .55), smoothstep(1.5, 2.4, r)) * (.55 + .55 * d);
        gl_FragColor = vec4(pow(col, vec3(2.2)), a);
      }`,
  });
  const planet = new THREE.Group();
  planet.add(new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), planetMat), new THREE.Mesh(new THREE.RingGeometry(1.42, 2.42, 160, 1), ringMat));
  planet.scale.setScalar(200);
  planet.rotation.set(1.05, 0.12, -0.38);
  planet.position.set(-2300, 800, 300);
  planet.children.forEach((c) => { c.frustumCulled = false; });
  planet.renderOrder = -80;
  planet.children[0].renderOrder = -80; planet.children[1].renderOrder = -79;
  rig.add(planet);
  rig.userData.planet = planet;

  // moon: a painted crescent sprite
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  g.beginPath(); g.arc(128, 128, 120, 0, 7); g.clip();
  const lg = g.createRadialGradient(92, 88, 8, 128, 128, 124);
  lg.addColorStop(0, "#fffaf0"); lg.addColorStop(0.55, "#b9cdf2"); lg.addColorStop(1, "#4b5aa0");
  g.fillStyle = lg; g.fillRect(0, 0, 256, 256);
  const sh = g.createRadialGradient(196, 190, 40, 196, 190, 190);
  sh.addColorStop(0, "rgba(8,8,40,.95)"); sh.addColorStop(0.6, "rgba(8,8,40,.7)"); sh.addColorStop(1, "rgba(8,8,40,0)");
  g.fillStyle = sh; g.fillRect(0, 0, 256, 256);
  const moon = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), toneMapped: false, depthWrite: false, depthTest: false }));
  moon.scale.setScalar(110);
  moon.position.set(-2200, -760, 380);
  moon.renderOrder = -70;
  rig.add(moon);
}

/* ---- ground: plum plain, faint grid, glowing pad, haze --------- */
const groundMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, toneMapped: false,
  uniforms: { uOpacity: { value: 1 }, uTime: { value: 0 }, uPad: { value: 1 } },
  vertexShader: "varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }",
  fragmentShader: `varying vec3 vW; uniform float uOpacity, uTime, uPad;
    // a ring of half-width h at radius r, filtered by the pixel footprint aa so it never crawls when the camera moves
    float ringLine(float d, float aa, float r, float h){ float e = abs(d - r); return clamp((h + .5 * aa - e) / aa, 0., 1.) * min(1., 2. * h / aa); }
    void main(){
      vec2 c = vW.xy - vec2(12., 0.);
      float dist = length(c);
      vec3 near = vec3(.045, .028, .12), far = vec3(.30, .14, .34);
      vec3 col = mix(near, far, smoothstep(180., 4200., dist));
      vec2 q = vW.xy / 44.;
      vec2 gw = abs(fract(q - .5) - .5) / max(fwidth(q), vec2(1e-4));
      float line = 1. - min(min(gw.x, gw.y), 1.);
      col += vec3(.45, .85, 1.) * line * .20 * (1. - smoothstep(200., 1500., dist)) * uPad;
      // The dashed outer ring that used to be here shimmered badly where it is seen edge-on, so it is gone.
      float aa = max(fwidth(dist), 1e-3);
      float ring = ringLine(dist, aa, 134., 1.4) + .42 * ringLine(dist, aa, 176., .7) + .25 * ringLine(dist, aa, 84., .6);
      col += vec3(.55, .92, 1.) * ring * uPad;
      col += vec3(.30, .70, .85) * .10 * exp(-abs(dist - 134.) / 22.) * uPad;
      col += vec3(1., .55, .45) * .12 * exp(-dist / 260.) * uPad;
      float a = uOpacity * (1. - smoothstep(3800., 5200., dist));
      gl_FragColor = vec4(pow(col, vec3(2.2)), a);
    }`,
});
const ground = new THREE.Mesh(new THREE.CircleGeometry(5400, 128), groundMat);
ground.position.z = -5.5;
ground.renderOrder = -60;
ground.frustumCulled = false;
scene.add(ground);

const shadowCatcher = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), new THREE.ShadowMaterial({ color: 0x08031c, opacity: 0.55, depthWrite: false }));
shadowCatcher.position.set(12, 0, -5.4);
shadowCatcher.receiveShadow = true;
shadowCatcher.renderOrder = -59;
scene.add(shadowCatcher);

/* ---- lights and image-based reflections ------------------------ */
{
  const env = new THREE.Scene();
  const dome = new THREE.Mesh(new THREE.SphereGeometry(50, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide, toneMapped: false, uniforms: { uTime: { value: 0 } },
    vertexShader: "varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }",
    fragmentShader: `varying vec3 vDir; uniform float uTime; ${NOISE} ${SKY_FN}
      void main(){ gl_FragColor = vec4(pow(skyColour(normalize(vDir), 0.), vec3(2.2)) * 1.1, 1.); }`,
  }));
  env.add(dome);
  const panel = (col, k, w, h, pos) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(col).multiplyScalar(k), side: THREE.DoubleSide, toneMapped: false }));
    m.position.set(...pos); m.lookAt(0, 0, 0); env.add(m);
  };
  panel("#fff0dc", 4.2, 30, 20, [18, -26, 34]);   // warm key softbox
  panel("#ff5fa8", 2.8, 26, 18, [-30, 22, 14]);    // magenta rim
  panel("#6fe9ff", 2.0, 24, 16, [30, 20, 6]);    // cyan kicker
  panel("#ffd7a8", 1.6, 60, 12, [0, 0, -30]);    // warm bounce from below
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(env, 0.03).texture;
  scene.environmentIntensity = 0.9;
}
scene.add(new THREE.HemisphereLight(0xb9d8ff, 0x6a2c5f, 0.35));
const key = new THREE.DirectionalLight(0xffe0b8, 2.6);
key.position.set(260, -320, 520);
key.castShadow = true;
key.shadow.mapSize.set(innerWidth < 800 ? 2048 : 3072, innerWidth < 800 ? 2048 : 3072);
key.shadow.bias = -0.0004;
key.shadow.normalBias = 0.6;
key.shadow.radius = 4;
Object.assign(key.shadow.camera, { near: 10, far: 1400, left: -260, right: 260, top: 260, bottom: -260 });
scene.add(key, key.target);
const rim = new THREE.DirectionalLight(0xff6bb0, 1.7);
rim.position.set(-340, 300, 200);
scene.add(rim);
const kick = new THREE.DirectionalLight(0x7ae8ff, 0.9);
kick.position.set(320, 240, 80);
scene.add(kick);

/* ============================================================
   Parts
   ============================================================ */
const items = []; // { name, mesh, mat, home, exv, hex, pPos, pQuat, hardware, p, op, glow }
const byName = new Map();
const bedGroup = new THREE.Group();
scene.add(bedGroup);
let DATA = null;

const V = (a) => new THREE.Vector3(a[0], a[1], a[2]);
const GAP = 34;
const plateX0 = (n) => -(n * 256 + (n - 1) * GAP) / 2;
const CYAN = new THREE.Color("#8ff0ff"), YELLOW = new THREE.Color("#ffe14d");

function addItem(name, geom, hex, home, extra = {}) {
  const mat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(hex), roughness: extra.rough ?? 0.52, metalness: extra.metal ?? 0.02,
    clearcoat: extra.coat ?? 0.35, clearcoatRoughness: extra.coatRough ?? 0.32, envMapIntensity: extra.env ?? 1,
    transparent: true, // stays true: flipping it later would not rebuild the shader and the fade would be ignored
  });
  mat.emissive.copy(CYAN);
  mat.emissiveIntensity = 0;
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.copy(home);
  mesh.castShadow = mesh.receiveShadow = true;
  mesh.userData.name = name;
  scene.add(mesh);
  const it = { name, mesh, mat, home: home.clone(), exv: V(explodeOf(name)), hex, pPos: home.clone(), pQuat: new THREE.Quaternion(), hardware: !!extra.hardware, p: extra.p || null, op: 1, glow: 0 };
  items.push(it);
  byName.set(name, it);
  return it;
}

const boot = { bar: $("#bootBar"), text: $("#bootText"), el: $("#boot") };
const bootTo = (f, t) => { boot.bar.style.width = `${Math.round(f * 100)}%`; if (t) boot.text.textContent = t; };
const frameWait = () => new Promise((r) => setTimeout(r, 0));
let ready = false; // nothing is drawn behind the boot screen until the parts are in

async function load() {
  const t0 = performance.now();
  bootTo(0.08, T().boot.connect);
  const [meta, buf] = await Promise.all([
    fetch("data/parts.json").then((r) => r.json()),
    fetch("data/bd1.bin").then((r) => r.arrayBuffer()),
  ]);
  DATA = meta;
  bootTo(0.3, T().boot.decode);
  await frameWait();
  let tris = 0;
  const nPlates = meta.plates;
  let done = 0;
  for (const p of meta.parts) {
    const vq = new Uint16Array(buf, p.voff, p.nv * 3);
    const pos = new Float32Array(p.nv * 3);
    for (let i = 0; i < p.nv; i++) for (let k = 0; k < 3; k++) pos[i * 3 + k] = vq[i * 3 + k] * p.scale[k] + p.lo[k] - p.centre[k];
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    // creased normals are precomputed by pack_web.py: smooth across shallow angles, hard edges kept
    geo.setAttribute("normal", new THREE.BufferAttribute(new Int8Array(buf, p.noff, p.nv * 3), 3, true));
    geo.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, p.ioff, p.nt * 3), 1));
    geo.computeBoundingSphere();
    const lens = /^lens/.test(p.name), metal = /^(knee_cap|thigh_rod|thigh_piston)/.test(p.name);
    const it = addItem(p.name, geo, p.colour, V(p.centre), lens
      ? { p, rough: 0.1, metal: 0.25, coat: 1, coatRough: 0.1, env: 1.1 }
      : metal ? { p, rough: 0.32, metal: 0.85, coat: 0.1, env: 1.3 }
        : /^stand/.test(p.name) ? { p, rough: 0.55, coat: 0.15, env: 0.55 } : { p });
    tris += p.nt;
    // print pose: rotate about the part's own centre, then put the rotated min corner on its bed slot
    const m = p.rot;
    const m4 = new THREE.Matrix4().set(m[0][0], m[0][1], m[0][2], 0, m[1][0], m[1][1], m[1][2], 0, m[2][0], m[2][1], m[2][2], 0, 0, 0, 0, 1);
    it.pQuat.setFromRotationMatrix(m4);
    const t = new THREE.Vector3(plateX0(nPlates) + p.plate * (256 + GAP) + p.bed[0] - p.rotMin[0], -128 + p.bed[1] - p.rotMin[1], p.dz);
    it.pPos.copy(V(p.centre).applyMatrix4(m4)).add(t);
    if (++done % 18 === 0) { bootTo(0.3 + 0.6 * (done / meta.parts.length), T().boot.polish); await frameWait(); }
  }
  console.info(`openbd1: decoded in ${Math.round(performance.now() - t0)} ms`);
  // hardware: steel pins (not printed)
  const pin = (name, len, c) => addItem(name, new THREE.CylinderGeometry(1.5, 1.5, len, 24), "#d0d4da", V(c), { hardware: true, rough: 0.22, metal: 1, coat: 0, env: 1.4 });
  pin("hip_pin", 65, [5, 0, 110.5]);
  for (const [tag, s] of [["left", 1], ["right", -1]]) {
    pin(`knee_pin_${tag}`, 8, [-17.5, s * 23, 72]);
    pin(`ankle_pin_${tag}`, 12, [39.3, s * 22.5, 9.8]);
  }
  // print beds: dark glass with a thin edge
  for (let i = 0; i < nPlates; i++) {
    const b = new THREE.Mesh(new THREE.PlaneGeometry(256, 256), new THREE.MeshBasicMaterial({ color: "#120a33", transparent: true, opacity: 0, depthWrite: false }));
    b.position.set(plateX0(nPlates) + i * (256 + GAP) + 128, 0, -0.35);
    const edge = new THREE.LineSegments(new THREE.EdgesGeometry(b.geometry), new THREE.LineBasicMaterial({ color: "#ffb27a", transparent: true, opacity: 0 }));
    edge.position.copy(b.position);
    bedGroup.add(b, edge);
  }
  ready = true;
  $$("#plates, #palette, #steps, #oh tbody").forEach((e) => { e.innerHTML = ""; });
  buildPage();
  bootTo(1, T().boot.ready);
  setTimeout(() => boot.el.classList.add("off"), 250);
  console.info(`openbd1: ${meta.parts.length} parts, ${tris} triangles, ready in ${Math.round(performance.now())} ms`);
}

/* ============================================================
   Camera director: scroll decides the scene
   ============================================================ */
const HOME_AZ = -0.62;
const S = {
  ex: 0, exT: 0, pr: 0, prT: 0,
  az: HOME_AZ, azT: HOME_AZ, el: 0.1, elT: 0.1, r: 480, rT: 480, tg: new THREE.Vector3(10, 0, 118), tgT: new THREE.Vector3(10, 0, 118),
  offX: 0.17, offXT: 0.17, offY: 0, offYT: 0, idle: 0, spin: 0.1,
  scene: "hero", sceneP: 0, step: -1, sel: null, hover: null, set: null, userSet: null, chip: null,
};
const SCENES = ["hero", "colours", "explode", "print", "assemble", "outro"];
const narrow = () => innerWidth <= 860;

function printDist(w, h) {
  const half = Math.atan(Math.tan((camera.fov * Math.PI) / 360) * (w / h));
  return Math.min(2600, ((3 * 256 + 2 * GAP) / 2 / Math.tan(half)) * 1.1);
}

function readScroll() {
  const mid = innerHeight * 0.5;
  let cur = "hero", p = 0;
  for (const name of SCENES) {
    const el = document.querySelector(`[data-scene="${name}"]`);
    if (!el) continue;
    const r = el.getBoundingClientRect();
    if (r.top <= mid) { cur = name; p = clamp01((mid - r.top) / Math.max(r.height - innerHeight * 0.5, 1)); }
  }
  if (cur !== S.scene) { S.userSet = null; S.chip = null; $$(".chip.on").forEach((c) => c.classList.remove("on")); S.scene = cur; }
  S.sceneP = p;
  // active assembly step: the one nearest the viewport centre
  let best = -1, bestD = 1e9;
  if (cur === "assemble") {
    $$(".step").forEach((el, i) => {
      const r = el.getBoundingClientRect(), d = Math.abs(r.top + r.height / 2 - mid);
      if (d < bestD) { bestD = d; best = i; }
    });
    if (bestD > innerHeight * 0.42) best = -1;
  }
  if (best !== S.step) { S.step = best; $$(".step").forEach((el, i) => el.classList.toggle("on", i === best)); }
  $$("[data-nav]").forEach((a) => a.classList.toggle("on", a.dataset.nav === cur));
}

function direct(w, h) {
  const n = narrow(), sc = S.scene, p = S.sceneP;
  const side = n ? 0 : 0.19, up = n ? 0.2 : 0;
  let ex = 0, pr = 0, tg = [10, 0, 118], r = n ? 700 : 590, el = 0.1, spin = 0.1, offX = side, offY = up;
  let set = null;
  if (sc === "hero") { /* defaults */ }
  if (sc === "colours") { el = 0.15; r = n ? 660 : 520; offX = side; }
  if (sc === "explode") {
    ex = smooth((p - 0.06) / 0.62);
    r = lerp(n ? 700 : 590, n ? 1100 : 860, ex); tg = [10, 0, lerp(118, 108, ex)]; el = lerp(0.1, 0.2, ex); spin = 0.06;
  }
  if (sc === "print") {
    pr = smooth((p - 0.1) / 0.3);
    offX = side * (1 - pr); offY = up * (1 - pr) + (n ? 0.14 : -0.12) * pr;
  }
  if (sc === "assemble") {
    ex = S.step >= 0 ? 0.85 : 0.35; r = n ? 980 : 720; tg = [10, 0, 108]; el = 0.17; spin = 0.05; offX = side;
    if (S.step >= 0) set = new Set(items.filter((i) => STEP_RE[S.step].test(i.name)).map((i) => i.name));
  }
  if (sc === "outro") { r = n ? 700 : 560; offX = 0; offY = n ? 0.2 : 0; el = 0.13; spin = 0.07; }
  S.exT = ex; S.prT = pr; S.spin = spin; S.offXT = offX; S.offYT = offY;
  S.rT = r; S.elT = el; S.tgT.set(...tg);
  S.set = S.userSet || set;
  if (S.sel) S.set = new Set([S.sel]);
}

/* ============================================================
   Frame loop
   ============================================================ */
const tmp = new THREE.Vector3(), idQ = new THREE.Quaternion(), tagV = new THREE.Vector3();
let W = 1, H = 1, last = performance.now(), frameN = 0;
const tagEl = $("#tag");

function resize() {
  W = innerWidth; H = innerHeight;
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setSize(W, H, false);
  composer.setPixelRatio(renderer.getPixelRatio());
  composer.setSize(W, H);
  camera.aspect = W / H;
  camera.fov = W / H < 0.9 ? 46 : 36;
  camera.updateProjectionMatrix();
}
addEventListener("resize", resize);

function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min((now - last) / 1000, 0.05);
  last = now;
  frameN++;
  if (!ready) return;
  readScroll();
  direct(W, H);
  const k = reduce ? 1 : 1 - Math.exp(-dt * 4.2), kc = reduce ? 1 : 1 - Math.exp(-dt * 3.2);

  S.ex = lerp(S.ex, S.exT, k); S.pr = lerp(S.pr, S.prT, k);
  const pr = S.pr;
  if (pr > 0.02 || S.prT > 0.5) S.azT = -Math.PI / 2;
  else if (Math.abs(S.azT + Math.PI / 2) < 0.15) S.azT = HOME_AZ;
  if (!reduce && S.idle <= 0 && S.prT < 0.5 && !S.sel) S.azT += dt * S.spin;
  S.idle -= dt;
  const printR = printDist(W, H);
  S.az = lerp(S.az, S.azT, kc);
  S.el = lerp(S.el, S.prT > 0.5 ? 0.95 : S.elT, kc);
  S.r = lerp(S.r, S.prT > 0.5 ? printR : S.rT, kc);
  S.tg.lerp(S.prT > 0.5 ? tmp.set(0, 0, 0) : S.tgT, kc);
  S.offX = lerp(S.offX, S.offXT, kc); S.offY = lerp(S.offY, S.offYT, kc);

  // parts
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
    it.op = lerp(it.op, dim ? 0.09 : 1, k);
    it.mat.opacity = it.op;
    it.mat.depthWrite = it.op > 0.9;
    it.mesh.castShadow = it.op > 0.5;
    it.glow = lerp(it.glow, S.sel === it.name ? 0.16 : S.hover === it.name ? 0.12 : 0, k);
    it.mat.emissive.copy(S.sel === it.name ? YELLOW : CYAN);
    it.mat.emissiveIntensity = it.glow;
  }
  groundMat.uniforms.uPad.value = 1 - pr;
  groundMat.uniforms.uOpacity.value = 1 - 0.0 * pr;
  shadowCatcher.position.z = lerp(-5.4, -0.2, pr);
  const sc = lerp(260, 520, pr);
  if (Math.abs(key.shadow.camera.right - sc) > 0.5) { Object.assign(key.shadow.camera, { left: -sc, right: sc, top: sc, bottom: -sc }); key.shadow.camera.updateProjectionMatrix(); }
  key.target.position.set(lerp(10, 0, pr), 0, lerp(80, 0, pr));
  bedGroup.children.forEach((c) => { c.material.opacity = (c.isMesh ? 0.82 : 0.75) * pr; c.visible = pr > 0.01; });

  // camera
  const ce = Math.cos(S.el);
  camera.position.set(S.tg.x + S.r * ce * Math.cos(S.az), S.tg.y + S.r * ce * Math.sin(S.az), S.tg.z + S.r * Math.sin(S.el));
  camera.lookAt(S.tg);
  camera.setViewOffset(W, H, -S.offX * W, S.offY * H, W, H);
  camera.updateMatrixWorld();

  // sky rig
  sky.position.copy(camera.position);
  sky.userData.stars.position.copy(camera.position);
  rig.position.copy(camera.position);
  rig.rotation.z = S.az * 0.78;
  const t = now / 1000;
  skyMat.uniforms.uTime.value = t;
  sky.userData.stars.userData.mat.uniforms.uTime.value = reduce ? 0 : t;
  sky.userData.stars.userData.mat.uniforms.uPx.value = renderer.getPixelRatio();

  composer.render();
  placeTag();
  if (frameN % 6 === 0) {
    $("#roScene").textContent = T().scenes[S.scene];
    $("#roCam").textContent = `AZ ${String(Math.round(((S.az * 57.2958) % 360 + 360) % 360)).padStart(3, "0")}°  EL ${String(Math.round(S.el * 57.2958)).padStart(2, "0")}°`;
    const pct = $("#exPct");
    if (pct) pct.textContent = String(Math.round(S.ex * 100)).padStart(3, "0");
  }
}

function placeTag() {
  if (!S.sel) { tagEl.classList.remove("on"); return; }
  const it = byName.get(S.sel);
  if (!it || !it.mesh.visible) { tagEl.classList.remove("on"); return; }
  tagV.copy(it.mesh.position).project(camera);
  const x = (tagV.x * 0.5 + 0.5) * W, y = (-tagV.y * 0.5 + 0.5) * H;
  tagEl.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
  tagEl.classList.toggle("flip", x > W - 380);
  tagEl.classList.add("on");
}

/* ============================================================
   Interaction
   ============================================================ */
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
function pick(ev) {
  ndc.set((ev.clientX / W) * 2 - 1, -(ev.clientY / H) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(items.filter((i) => i.mesh.visible && i.op > 0.5).map((i) => i.mesh), false)[0];
  return hit ? hit.object.userData.name : null;
}
let drag = null, moved = 0, hoverT = 0;
canvas.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY }; moved = 0; canvas.setPointerCapture(e.pointerId); S.idle = 5; });
canvas.addEventListener("pointermove", (e) => {
  if (drag) {
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    drag = { x: e.clientX, y: e.clientY };
    moved += Math.abs(dx) + Math.abs(dy);
    if (S.prT < 0.5) { S.azT -= dx * 0.008; S.az = S.azT; }
    if (e.pointerType === "mouse" && S.prT < 0.5) S.elT = Math.max(-0.05, Math.min(1.3, S.elT + dy * 0.005));
    S.idle = 5;
  } else if (performance.now() - hoverT > 60 && e.pointerType === "mouse") {
    hoverT = performance.now();
    S.hover = pick(e);
    canvas.style.cursor = S.hover ? "pointer" : "grab";
  }
});
canvas.addEventListener("pointerup", (e) => { drag = null; if (moved < 5) select(pick(e)); });
canvas.addEventListener("pointerleave", () => { S.hover = null; });
addEventListener("keydown", (e) => { if (e.key === "Escape") select(null); });

function select(name) {
  S.sel = name;
  S.userSet = null;
  S.chip = null;
  $$(".chip.on").forEach((c) => c.classList.remove("on"));
  renderTag(name);
}

function renderTag(name) {
  if (!name) { tagEl.innerHTML = ""; return; }
  const it = byName.get(name), p = it.p, L = T().tag;
  const rows = [`<dt>${L.colour}</dt><dd><span class="sw" style="background:${it.hex}"></span>${colourName(it.hex)}</dd>`];
  if (p) rows.push(`<dt>${L.bed}</dt><dd>${p.plate + 1}</dd>`, `<dt>${L.height}</dt><dd>${p.height} mm</dd>`,
    `<dt>${L.overhang}</dt><dd class="${p.overhang > 150 ? "warn" : ""}">${Math.round(p.overhang)} mm² · ${p.overhang > 150 ? L.support : L.none}</dd>`);
  else rows.push(`<dt>${L.type}</dt><dd>${L.hardware}</dd>`);
  tagEl.innerHTML = `<i class="dot"></i><i class="lead-line"></i><div class="card"><div class="k">${L.kicker}</div><h4>${labelOf(name)}</h4><div class="id">${name}</div><dl>${rows.join("")}</dl><button class="close" id="tagClose">${L.close}</button></div>`;
  $("#tagClose").onclick = () => select(null);
}

/* ============================================================
   Page content built from the data
   ============================================================ */
function buildPage() {
  const groups = new Map();
  for (const it of items) {
    if (it.hardware) continue;
    const h = it.hex.toUpperCase();
    (groups.get(h) || groups.set(h, []).get(h)).push(it.name);
  }
  const pal = $("#palette");
  [...groups.entries()].sort((a, b) => b[1].length - a[1].length).forEach(([hex, names]) => {
    const bases = [...new Set(names.map(stripSide))];
    const b = document.createElement("button");
    b.className = "chip";
    b.innerHTML = `<i style="background:${hex}"></i><span><b>${colourName(hex)}</b><small>${hex} · ${T().pcs(names.length)} · ${bases.slice(0, 2).join(lang() === "zh" ? "、" : ", ")}${bases.length > 2 ? "…" : ""}</small></span>`;
    b.onclick = () => {
      const on = S.chip === hex;
      $$(".chip.on").forEach((c) => c.classList.remove("on"));
      S.sel = null; renderTag(null);
      if (on) { S.chip = null; S.userSet = null; return; }
      S.chip = hex; S.userSet = new Set(names); b.classList.add("on");
    };
    pal.appendChild(b);
  });

  const pl = $("#plates");
  for (let i = 0; i < DATA.plates; i++) {
    const box = document.createElement("div");
    box.className = "plate";
    const rects = DATA.parts.filter((p) => p.plate === i).map((p) =>
      `<rect data-n="${p.name}" x="${p.bed[0]}" y="${256 - p.bed[1] - p.foot[1]}" width="${p.foot[0]}" height="${p.foot[1]}" rx="1.2" fill="${p.colour}"><title>${labelOf(p.name)}</title></rect>`).join("");
    box.innerHTML = `<h3>PLATE ${i + 1} · 256 × 256</h3><svg viewBox="0 0 256 256" role="img" aria-label="${T().plate(i + 1)}">${rects}</svg>`;
    box.querySelectorAll("rect").forEach((r) => { r.onclick = () => { select(r.dataset.n); document.getElementById("print").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); }; });
    pl.appendChild(box);
  }

  const tb = $("#oh tbody");
  DATA.parts.filter((p) => p.overhang > 150).sort((a, b) => b.overhang - a.overhang).forEach((p) => {
    const tr = document.createElement("tr");
    tr.className = "go";
    tr.innerHTML = `<td>${labelOf(p.name)} <code>${p.name}</code></td><td>${p.height}</td><td>${Math.round(p.overhang)}</td>`;
    tr.onclick = () => { select(p.name); document.getElementById("print").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" }); };
    tb.appendChild(tr);
  });

  const ol = $("#steps");
  T().steps.forEach(([title, text, tag]) => {
    const li = document.createElement("li");
    li.className = "step";
    li.innerHTML = `<h3>${title}</h3><p>${text}</p><em>${tag}</em>`;
    li.onclick = () => li.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
    ol.appendChild(li);
  });
}

function rebuild() {
  $$("#plates, #palette, #steps, #oh tbody").forEach((e) => { e.innerHTML = ""; });
  buildPage();
  renderTag(S.sel);
  S.step = -2; // force the active-step class to be re-applied on the next frame
}

$("#lang").addEventListener("click", () => {
  setLang(lang() === "zh" ? "en" : "zh");
  applyStatic();
  if (ready) rebuild();
  else boot.text.textContent = T().boot.connect;
});

applyStatic();
boot.text.textContent = T().boot.connect;
if (DEBUG) window.__bd1 = { renderer, composer, S, bloom };
resize();
requestAnimationFrame(frame);
load().catch((err) => { console.error(err); boot.text.textContent = T().boot.lost + err; });
