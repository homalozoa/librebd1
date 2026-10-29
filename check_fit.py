"""Report volume overlap between every pair of parts (should be ~0, pins aside)."""
import itertools, os, sys
sys.path.insert(0, os.getcwd())
import FreeCAD as App
import bd1_model
ps = bd1_model.parts()
for (a, sa, *_), (b, sb, *_) in itertools.combinations(ps, 2):
    if not sa.BoundBox.intersect(sb.BoundBox):
        continue
    v = sa.common(sb).Volume
    if v > 1.0:
        print(f"OVERLAP {a} x {b}: {v:.1f} mm3")
lo = min(s.BoundBox.ZMin for _, s, *_ in ps); hi = max(s.BoundBox.ZMax for _, s, *_ in ps)
print("height", hi - lo, "zmin", lo)
# Centre of mass of the whole figure (uniform density) against the feet's footprint.
solids = [so for _, s, *_ in ps for so in s.Solids]
vol = sum(so.Volume for so in solids)
com = sum((so.CenterOfMass * so.Volume for so in solids), App.Vector()) / vol
feet = [s.BoundBox for n, s, *_ in ps if n.startswith("foot")]
print(f"centre of mass x {com.x:.1f} y {com.y:.1f} z {com.z:.1f}; feet x {min(b.XMin for b in feet):.1f}..{max(b.XMax for b in feet):.1f}")
