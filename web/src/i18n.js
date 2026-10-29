// All visible copy, in Chinese and English. The Chinese is the original; the English is written for the same voice
// (plain, exploratory), not translated word for word. Epigraphs stay in English in both languages.

export const I = {
  zh: {
    title: "openbd1 · 一台可以自己打印的 BD-1",
    desc: "openbd1：把 BD-1 拆成 54 块，自己打印，用销子和胶水装回去。往下滑，看它散开、飞上打印板、一步步装好。",
    canvas: "BD-1 三维模型，可拖动旋转，点击零件查看信息",
    navLabel: "章节",
    brandLabel: "openbd1 回到顶部",
    langButton: "EN",
    langLabel: "Switch to English",
    "nav.colours": "采样", "nav.explode": "拆解", "nav.print": "制造", "nav.assemble": "组装",
    "hero.kicker": "已记录 54 件样本　/　同人作品，与官方无关",
    "hero.sub": "醒来，旅行者。这里有一台被拆成 54 块的 BD-1。",
    "hero.lede": "把它们一块块打印出来，用 3 毫米的销子穿起来，它就能站住，膝盖也会弯。没人规定你一定要做完。不过大多数人会做完。",
    "hero.cue": "向下滑动",
    "col.index": "01　采样", "col.h2": "颜色",
    "col.lead": "每种颜色都是从参考模型的贴图上量出来的，取一个表面的平均值。真正的 BD-1 又旧又脏，划痕和污渍只能靠你自己用手涂。",
    "col.dim": "点一个色块，同色的零件会亮起来。",
    "ex.index": "02　拆解", "ex.h2": "里面是什么",
    "ex.lead": "往下滑，它会一块块散开。零件大致沿着装进去的方向退出来，所以散开的样子，也是装回去的顺序。",
    "ex.unit": "% 已散开",
    "ex.dim": "拖动画面可以绕着它转。点任何一块，看它是什么。",
    "pr.index": "03　制造", "pr.h2": "打印",
    "pr.lead": "三块 256 × 256 毫米的床，大小和拜博 X1、P1 一样。每个零件都转到了悬垂最少的方向。朝上的面不用担心，朝下的面可能要加支撑。",
    "pr.n1t": "喷嘴", "pr.n1": "0.4 毫米，PLA 就够。小件和薄嵌件用 0.12 到 0.16 毫米的层高。头壳打 2 到 3 层壁，填充 10% 到 15%。",
    "pr.n2t": "先试一片", "pr.n2": "头壳上每个凹槽都留了 0.2 毫米的胶缝。先打一块 1 毫米的嵌件放进去，松还是紧，取决于你的机器。",
    "pr.n3t": "翘边", "pr.n3": "1 毫米厚的红片和灰片最容易翘。床温低一点，边缘加粘，或者几片挨在一起打。",
    "pr.tt": "可能要支撑的零件",
    "pr.fine": "悬垂面积超过 150 平方毫米的列在这里。这是按几何算的估计，没有在切片软件里验证过，以你的切片预览为准。",
    "th.part": "零件", "th.h": "高度 mm", "th.o": "悬垂 mm²",
    "as.index": "04　组装", "as.h2": "装配",
    "as.lead": "一共九步。往下滑，模型会拆开，只亮起这一步用到的零件。关节只靠摩擦站住，别涂胶，不然它就成了一座雕像。",
    "legal1": "脚本用 MIT。模型文件（<code>BD1.FCStd</code>、STL、预览图）用 CC BY-NC-SA 4.0：可以改，可以分享，别拿去卖。",
    "legal2": "BD-1 属于 Lucasfilm 和 Disney，这是一份与他们无关的同人作品。测量时用的参考网格没有许可证，不在这个仓库里。",
    "legal3": "源码、打印指南和装配说明在 <a href=\"https://github.com/homalozoa/openbd1\" rel=\"noopener\">github.com/homalozoa/openbd1</a>。",
    "legal4": "页面用 three.js 绘制，字体是 Sora、Inter、Newsreader 和 IBM Plex Mono，全部打包在页面里。",
    scenes: { hero: "01 · 抵达", colours: "02 · 采样", explode: "03 · 拆解", print: "04 · 制造", assemble: "05 · 组装", outro: "06 · 完成" },
    boot: { connect: "正在接入阿特拉斯", decode: "解码 54 个零件", polish: "打磨表面", ready: "准备就绪", lost: "信号丢失：" },
    parts: {
      head_shell: "头壳", head_top_band: "头顶带", head_light: "灯板", eye_ring: "眼筒", eye_band: "右眼红环", lens: "镜头",
      ear: "耳盘外圈", ear_centre: "耳盘中心", antenna: "天线", antenna_collar: "天线套", neck: "脖子", torso: "躯干",
      chest_plate: "胸板", chest_tab: "胸口红块", thigh: "大腿", thigh_channel: "槽上段凸块", thigh_channel_floor: "槽底",
      thigh_channel_tip: "槽顶小块", thigh_rod: "螺杆", thigh_piston: "螺纹柱", knee_cap: "膝盖盖", shin: "小腿",
      shin_plate: "小腿红板", foot_heel: "脚后半段", foot_front: "脚前半段", stand: "底座", paint: "头侧涂装嵌件",
      hip_pin: "髋销 3×65", knee_pin: "膝销 3×8", ankle_pin: "踝销 3×12",
    },
    left: "（左）", right: "（右）",
    colours: {
      "#C9CFB0": "米白", "#B2A696": "暖米白", "#80786B": "暖灰", "#999996": "灰", "#82827D": "中灰", "#B8BAB0": "浅灰",
      "#B2B5B2": "镜头浅灰", "#C40A08": "亮红", "#7A2B26": "暗红", "#5E3330": "深红褐", "#638599": "钢蓝", "#52A624": "绿",
      "#593D36": "深棕", "#595952": "深灰", "#B2B59E": "浅灰绿", "#424242": "炭灰", "#33363B": "黑灰",
    },
    pcs: (n) => `${n} 件`,
    plate: (n) => `打印板 ${n} 排版`,
    tag: { kicker: "发现物", colour: "颜色", bed: "打印板", height: "打印高度", overhang: "悬垂", support: "要支撑", none: "不用支撑", type: "类型", hardware: "硬件，不打印", close: "收起 ✕" },
    steps: [
      ["试配", "先别涂胶。把所有嵌件放进凹槽试一遍，太紧就用锉刀磨一点，别硬压。", "嵌件"],
      ["头部嵌件", "头顶带、两侧的涂装件和右眼红环嵌进头壳，灯板贴在头后凹槽的底上。右边和左边的图案不一样，装之前看一眼。", "头壳 · 涂装 · 灯板"],
      ["眼睛", "眼筒插进面板上 6 毫米深的眼窝，镜头放进眼筒里。右眼是钢蓝色的大镜头，左眼是浅灰色的。", "眼筒 · 镜头"],
      ["耳朵与天线", "耳盘中心有一根 3 毫米的凸销，插进头侧，外圈套在外面粘牢。天线先穿过锥形套，再插进 2.3 毫米的斜孔。", "耳盘 · 天线 · 套"],
      ["躯干与脖子", "胸板粘在胸口凹槽的底上，红块贴在正面和顶部斜面相交的地方。脖子两头各插进 8 毫米深的斜孔。", "脖子 · 躯干 · 胸板"],
      ["大腿", "槽里先放深棕槽底、槽顶小块和红色凸块。螺杆粘在槽底，粗的一端对着六角凹坑下方。螺纹柱粘进侧槽，膝盖盖压进凹槽。", "大腿 · 螺杆 · 螺纹柱"],
      ["小腿与脚", "红板嵌进 1 毫米深的凹槽，两头的凸耳要露在外面。脚的深色后半和浅色前半，在 x = 40.5 处对接粘牢。", "小腿 · 红板 · 脚"],
      ["关节销", "髋部一根 3×65 毫米的销，穿过左大腿、躯干和右大腿。每个膝盖一根 3×8，每个脚踝一根 3×12。只靠摩擦固定，所以不要涂胶。", "钢棒或 M3 螺丝"],
      ["底座", "重心在脚跟后面，只靠两只脚站不住。把脚粘进底座 1.2 毫米深的凹槽，它才不会倒。", "底座 · 脚"],
    ],
  },

  en: {
    title: "openbd1 · A BD-1 you can print yourself",
    desc: "openbd1: BD-1 in 54 pieces. Print them, pin them together, glue the rest. Scroll to watch it come apart, fly onto the print beds and go back together.",
    canvas: "3D model of BD-1. Drag to orbit, click a part to inspect it.",
    navLabel: "Sections",
    brandLabel: "openbd1, back to top",
    langButton: "中文",
    langLabel: "切换到中文",
    "nav.colours": "Colour", "nav.explode": "Teardown", "nav.print": "Print", "nav.assemble": "Build",
    "hero.kicker": "54 specimens logged　/　fan work, unaffiliated",
    "hero.sub": "Wake up, Traveller. Here is a BD-1, broken into 54 pieces.",
    "hero.lede": "Print them one at a time and thread them together with 3 mm pins. It will stand, and its knees will bend. Nobody says you have to finish. Most people do.",
    "hero.cue": "Scroll",
    "col.index": "01　Sampling", "col.h2": "Colour",
    "col.lead": "Every colour was measured off the texture of the reference model, averaged over one surface. The real BD-1 is old and dirty. The scratches and the grime are yours to paint by hand.",
    "col.dim": "Pick a swatch and the parts of that colour light up.",
    "ex.index": "02　Teardown", "ex.h2": "What's inside",
    "ex.lead": "Scroll and it comes apart, piece by piece. Each part slides out roughly the way it went in, so the way it comes apart is also the order to put it back.",
    "ex.unit": "% apart",
    "ex.dim": "Drag to orbit. Click any piece to find out what it is.",
    "pr.index": "03　Making", "pr.h2": "Print",
    "pr.lead": "Three beds of 256 × 256 mm, the size of a Bambu X1 or P1. Every part is turned to the orientation with the least overhang. Faces that point up are safe. Faces that point down may need support.",
    "pr.n1t": "Nozzle", "pr.n1": "0.4 mm, plain PLA is enough. Use 0.12 to 0.16 mm layers for small parts and thin inlays. Print the head shell with 2 to 3 walls and 10 to 15 percent infill.",
    "pr.n2t": "Try one first", "pr.n2": "Every pocket in the head shell has a 0.2 mm glue gap. Print one 1 mm inlay and fit it before anything else. Whether it comes out loose or tight depends on your machine.",
    "pr.n3t": "Warping", "pr.n3": "The 1 mm red and grey pieces curl first. Lower the bed temperature, add a brim, or print a few side by side.",
    "pr.tt": "Parts that may need support",
    "pr.fine": "Anything with more than 150 mm² of overhang is listed. This is a geometric estimate and has not been checked in a slicer, so trust your slicer's preview.",
    "th.part": "Part", "th.h": "Height mm", "th.o": "Overhang mm²",
    "as.index": "04　Assembly", "as.h2": "Build",
    "as.lead": "Nine steps. Scroll and the model comes apart and lights only what this step uses. The joints hold by friction alone. Don't glue them, or it becomes a statue.",
    "legal1": "Scripts are MIT. Model files (<code>BD1.FCStd</code>, the STLs, the preview) are CC BY-NC-SA 4.0: change them, share them, don't sell them.",
    "legal2": "BD-1 belongs to Lucasfilm and Disney. This is fan work with no connection to them. The reference mesh used for measuring has no licence and is not in this repository.",
    "legal3": "Source, printing guide and assembly notes are at <a href=\"https://github.com/homalozoa/openbd1\" rel=\"noopener\">github.com/homalozoa/openbd1</a>.",
    "legal4": "The page is drawn with three.js. Fonts are Sora, Inter, Newsreader and IBM Plex Mono, all bundled with it.",
    scenes: { hero: "01 · Arrival", colours: "02 · Sampling", explode: "03 · Teardown", print: "04 · Making", assemble: "05 · Assembly", outro: "06 · Done" },
    boot: { connect: "Connecting to the Atlas", decode: "Decoding 54 parts", polish: "Polishing surfaces", ready: "Ready", lost: "Signal lost: " },
    parts: {
      head_shell: "Head shell", head_top_band: "Top band", head_light: "Light panel", eye_ring: "Eye barrel", eye_band: "Right-eye ring", lens: "Lens",
      ear: "Ear ring", ear_centre: "Ear centre", antenna: "Antenna", antenna_collar: "Antenna collar", neck: "Neck", torso: "Torso",
      chest_plate: "Chest plate", chest_tab: "Chest tab", thigh: "Thigh", thigh_channel: "Channel block", thigh_channel_floor: "Channel floor",
      thigh_channel_tip: "Channel tip", thigh_rod: "Rod", thigh_piston: "Threaded piston", knee_cap: "Knee cap", shin: "Shin",
      shin_plate: "Shin plate", foot_heel: "Foot heel", foot_front: "Foot front", stand: "Stand", paint: "Side paint inlay",
      hip_pin: "Hip pin 3×65", knee_pin: "Knee pin 3×8", ankle_pin: "Ankle pin 3×12",
    },
    left: " (L)", right: " (R)",
    colours: {
      "#C9CFB0": "Ivory", "#B2A696": "Warm ivory", "#80786B": "Warm grey", "#999996": "Grey", "#82827D": "Mid grey", "#B8BAB0": "Light grey",
      "#B2B5B2": "Lens grey", "#C40A08": "Bright red", "#7A2B26": "Dark red", "#5E3330": "Oxblood", "#638599": "Steel blue", "#52A624": "Green",
      "#593D36": "Dark brown", "#595952": "Dark grey", "#B2B59E": "Pale sage", "#424242": "Charcoal", "#33363B": "Black-grey",
    },
    pcs: (n) => `${n} pcs`,
    plate: (n) => `Layout of print bed ${n}`,
    tag: { kicker: "Discovery", colour: "Colour", bed: "Bed", height: "Print height", overhang: "Overhang", support: "needs support", none: "no support", type: "Type", hardware: "Hardware, not printed", close: "Close ✕" },
    steps: [
      ["Dry fit", "Don't glue yet. Press every inlay into its pocket once. If one is tight, file it a little. Never force it.", "Inlays"],
      ["Head inlays", "The top band, the side paint pieces and the right-eye red ring go into the head shell, and the light panel lies on the floor of the recess at the back. The right and left patterns differ, so look before you fit.", "Shell · Paint · Light"],
      ["Eyes", "Each eye barrel goes into its 6 mm socket in the face panel, and the lens drops into the barrel. The right eye is the big steel-blue lens. The left is pale grey.", "Barrel · Lens"],
      ["Ears and antennae", "Each ear centre has a 3 mm peg that goes into the side of the head. Glue the outer ring over it. Thread the antenna through its cone collar, then into the slanted 2.3 mm hole.", "Ear · Antenna · Collar"],
      ["Torso and neck", "The chest plate is glued to the floor of the chest pocket, and the red tab sits where the front meets the sloped top. Each end of the neck goes into an 8 mm deep angled hole.", "Neck · Torso · Chest"],
      ["Thighs", "In each channel put the dark-brown floor, the small tip piece and the red block first. Glue the rod to the floor with its thick end below the hex pocket, glue the threaded piston into the side slot, and press the knee cap into its recess.", "Thigh · Rod · Piston"],
      ["Shins and feet", "The red plate goes into its 1 mm pocket with both lugs left sticking out. Butt the dark heel of each foot against the light front at x = 40.5 and glue them together.", "Shin · Plate · Foot"],
      ["Joint pins", "One 3 × 65 mm pin runs through the left thigh, the torso and the right thigh at the hip. Each knee gets a 3 × 8 and each ankle a 3 × 12. They hold by friction, so don't glue them.", "Steel rod or M3 screw"],
      ["Stand", "The centre of mass sits behind the heel, so two feet alone won't stand. Glue the feet into the 1.2 mm recesses in the stand and it stays up.", "Stand · Feet"],
    ],
  },
};

export const STEP_RE = [
  /^(paint_|head_top_band|head_light|eye_band|chest_)/,
  /^(head_shell|paint_|head_top_band|head_light|eye_band)/,
  /^(head_shell|eye_|lens_)/,
  /^(head_shell|ear_|antenna)/,
  /^(head_shell|neck|torso|chest_)/,
  /^(thigh_|knee_cap)/,
  /^(shin_|foot_)/,
  /^(torso|thigh_(left|right)$|shin_(left|right)$|foot_|hip_pin|knee_pin|ankle_pin)/,
  /^(stand|foot_)/,
];

function detect() {
  let saved = null;
  try { saved = localStorage.getItem("bd1lang"); } catch { /* storage blocked: fall through to the browser language */ }
  if (saved === "zh" || saved === "en") return saved;
  return (navigator.language || "zh").toLowerCase().startsWith("zh") ? "zh" : "en";
}
let cur = detect();

export const lang = () => cur;
export const T = () => I[cur];
export function setLang(l) {
  cur = l;
  try { localStorage.setItem("bd1lang", l); } catch { /* private mode: the choice just won't persist */ }
}

/** Fill every [data-i18n] / [data-i18n-html] / [data-i18n-aria] element and the document head. */
export function applyStatic() {
  const d = I[cur];
  document.documentElement.lang = cur === "zh" ? "zh-CN" : "en";
  document.title = d.title;
  const meta = document.querySelector('meta[name="description"]');
  if (meta) meta.setAttribute("content", d.desc);
  for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = d[el.dataset.i18n];
  for (const el of document.querySelectorAll("[data-i18n-html]")) el.innerHTML = d[el.dataset.i18nHtml];
  for (const el of document.querySelectorAll("[data-i18n-aria]")) el.setAttribute("aria-label", d[el.dataset.i18nAria]);
  const b = document.getElementById("lang");
  if (b) { b.textContent = d.langButton; b.setAttribute("aria-label", d.langLabel); }
}
