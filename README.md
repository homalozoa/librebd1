# BD-1 分模块打印模型（FreeCAD）

外形按 `bd-1-droid-star-wars-jedi-fallen-order/` 里的参考网格测量建模。头、躯干、大腿、小腿、脖子的轮廓都是从参考网格上描下来的。面部罩壳、大腿上的螺杆和螺纹柱、小腿红板凸耳这些细节，是从参考网格的表面高度图上量出来的。每个颜色区域都是单独零件，可以分色打印，也可以全部打成白色再分件上色。零件之间用 3 mm 销和胶连接。

![preview](preview.png)

与参考网格的正交视图对比（详见 `compare_sheet.png`）：

| 视图 | 轮廓重合度 IoU |
|---|---|
| 正视 | 0.965 |
| 侧视 | 0.975 |
| 俯视 | 0.990 |

主要细节：
- **面部**：口鼻部分是一个罩壳，由 2.5 mm 厚的顶板和两侧侧壁组成。面板退在罩壳前沿后面 10–16 mm，两眼中间再往里凹 8 mm。两个眼筒从面板伸出来，左眼镜头中心有一个小凸钮。
- **大腿**：外侧有一道红槽。槽的下半段比板面低 1.5 mm，里面横着一根灰色螺杆，上粗下细；上半段几乎和板面齐平，有一个六角凹坑。红槽旁边的侧槽里放一根灰色螺纹柱。膝盖螺栓盖分三层：外圈、凸台，中间是六角星凹坑。
- **小腿**：外侧红板高出 2.7 mm，两头各有一个凸耳，凸耳高出 5.6 mm。

还剩的差异：
- 脚和踝关节做了简化。
- 罩壳边角和面板边缘没有倒圆。
- 颜色分区是从参考贴图上取的，边界是近似的。

参考文件夹里没有许可证说明，只适合个人打印，不要分发它和由它导出的东西。

## 文件

| 文件 | 作用 |
|---|---|
| `bd1_model.py` | 参数化模型：尺寸、轮廓、关节位置、配合间隙都在文件里 |
| `BD1.FCStd` | 带颜色的 FreeCAD 装配文件 |
| `stl/*.stl` | 每个零件一个 STL（40 个），坐标就是装配位置，打印前要在切片软件里平放 |
| `export_stl.py` | 重新生成 STL |
| `preview_gui.py` | 重新生成带颜色的 `BD1.FCStd` 和 `preview.png` |
| `check_fit.py` | 检查零件之间有没有互相穿插，并输出重心位置 |
| `glb_ref.py` | 读取参考 GLB（带骨骼蒙皮和贴图颜色），换成本项目的坐标和尺寸，存为 `ref/bd1_ref.npz` |
| `ref_profiles.py` | 从参考网格描出零件的二维轮廓，用来更新 `bd1_model.py` 里的轮廓点 |
| `render_views.py` | 输出模型和参考网格的正视、侧视、俯视正交渲染，存到 `views/` |
| `compare.py` | 对比两者的轮廓，输出 IoU、逐段偏差（mm）和叠加图 |

改完尺寸后重新生成：

```bash
cd ~/bdx/bd1_print && /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd export_stl.py
```

尺寸用 `BD1_HEIGHT` 控制，表示头顶高度（mm），默认 190。`BD1_HEIGHT=316` 接近真人大小。外形整体缩放，销孔、天线孔和胶缝保持实际尺寸不变，所以五金件不用换。

## 零件与颜色

| 颜色 | 零件 |
|---|---|
| 米白 | head_shell, ear ×2, antenna ×2, neck, torso, thigh ×2, shin ×2 |
| 灰 | head_top_band, head_side_panel ×2, eye_ring_left, ear_centre ×2, chest_plate, knee_cap ×2, thigh_rod ×2, thigh_piston ×2 |
| 红 | head_red_stripe ×2, snout_red ×2, eye_ring_right, chest_tab, thigh_channel ×2（红槽底板）, shin_plate ×2 |
| 蓝 | lens_right（BD-1 自己的右眼，较大） |
| 浅灰 | lens_left |
| 绿 | head_light（头后斜面的灯条） |
| 深灰 | foot ×2, stand |

耳盘外圈有一道细槽，用来涂红圈。

## 装配

- **五金件**：
  - 3 mm 钢棒、铝棒或 M3 螺丝，销孔 3.3 mm，关节可以转动，靠摩擦定位。
    - 髋：一根 3×70 mm 的销，穿过左大腿、躯干、右大腿。
    - 膝：每侧一根 3×10 mm 的销，从小腿内侧穿进去；外侧由 knee_cap 自带的 3 mm 短销堵住。
    - 踝：每侧一根 3×12 mm 的销，穿过脚上的叉口和小腿末端。
  - 天线：2 mm 黄铜棒，每根约 79 mm，插进耳盘上 2.3 mm 的斜孔。也可以用打印的 antenna 零件，但只有 2.1 mm 粗，很容易断。
- **胶粘件**：凹槽每边留了 0.2 mm 间隙，用 CA 胶或 AB 胶。
  - 嵌件嵌进 1 mm 深的凹槽：头顶带、侧板、红条、口鼻红块、灯条、胸板、胸口红块。小腿红板也是嵌进 1 mm 凹槽，但会凸出小腿表面。
  - 大腿：先把红槽底板粘进红槽，再把螺杆粘在底板上（螺杆粗的一头对准六角凹坑下方），螺纹柱粘进侧槽，膝盖盖压进膝盖的凹槽。
  - 眼筒插进面板上 6 mm 深的眼窝，再把镜头塞进眼筒。
  - 耳盘用自带的 3 mm 凸销插进头侧。
  - 脖子两端各插进 8 mm 的斜孔。
- **底座（必需）**：面部做成罩壳以后头前部变轻，重心落到了脚跟后面约 1.2 mm，只靠两只脚站不住。必须把脚粘进 stand 的 1.2 mm 凹槽里。

## 打印建议

- **头壳**：最大的件，137×111×40 mm。侧面朝下平放打印，这样罩壳顶板、侧壁和面板都是竖直的，几乎不用支撑。实心建模，用 2–3 层壁、10–15 % 填充。
- **螺杆、螺纹柱**：平的底面朝下打印。螺纹凸棱只有 0.25–0.3 mm，用 0.2 mm 喷嘴或 0.08 mm 层高会更清楚；也可以直接用 3 mm 螺丝截一段代替螺杆。
- **腿件、脚**：侧面平放打印，层线顺着腿的方向。
- **薄嵌件**：大多是 1 mm 厚，平放打印。用 0.4 mm 喷嘴、0.12–0.16 mm 层高。
- **上色**：先上底漆，再喷米白。红色和灰色部分是单独零件，不需要遮盖。最后用深灰渗线液填面板线、面部边框槽和大腿上的两道槽。

## 与参考网格对比

```bash
cd ~/bdx/bd1_print
/Applications/FreeCAD.app/Contents/Resources/bin/python -I glb_ref.py
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd render_views.py
/Applications/FreeCAD.app/Contents/Resources/bin/python compare.py
```

两者按世界坐标对齐，比例都是 6 px/mm，所以不需要拟合，偏差直接以 mm 读出。

`views/<view>_overlay.png` 的颜色：灰色是两者重合，红色是只有模型有，蓝色是只有参考有。`views/<view>_ghost.png` 是带贴图的参考和模型半透明叠在一起。

也可以改用截图对比：把 `front.png`、`side.png`、`top.png` 放进 `ref/`，`compare.py` 会优先用截图，并自动搜索缩放、镜像和平移。背景要用纯色，或者另外提供 `ref/<view>_mask.png`。
