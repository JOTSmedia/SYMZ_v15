"""Photo -> Figure, print step: the figure (a relief of img/p2f/fig.webp with Depth-Anything depth) printed layer by layer
on a textured PEI plate, rendered in Cycles. Writes, in the page's figure coordinates (the 619x1080 canvas of img/p2f):
  print-NN.png   plate + the print up to layer NN (transparent background), print-00 = the bare plate
  head-K.png / beam-K.png   the toolhead and the X beam alone at three heights (the page slides them between)
  print.json     region of the canvas the frames cover, the nozzle path per frame and the sprite anchors
env: OUT, NP (frames, default 24), SAMPLES, RS (render pixels per canvas pixel, default 0.8), FIG, DEPTH
usage: python3 depth_symz.py depth_anything_v2_vits.onnx ../img/p2f/fig.webp fig_depth.npy
       DEPTH=fig_depth.npy python3 p2f_print.py"""
import bpy, bmesh, math, os, sys, json
import numpy as np, cv2
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', 'p2f_out'); os.makedirs(OUT, exist_ok=True)
NP = int(os.environ.get('NP', '24')); SAMPLES = int(os.environ.get('SAMPLES', '24')); RS = float(os.environ.get('RS', '0.8'))
FIG = os.environ.get('FIG', os.path.join(HERE, '..', '..', 'img', 'p2f', 'fig.webp')); DEPTH = os.environ.get('DEPTH', 'fig_depth.npy')
D = {'w': 619, 'h': 1080, 'feet': 1040, 'top': 26, 'ax': 168}
X0d, X1d, Y0d, Y1d = -170, 789, -30, 1180           # canvas region the frames cover
RW, RH = round((X1d - X0d) * RS), round((Y1d - Y0d) * RS)
FH = 0.18                                           # figure height (feet to horn tip), metres
S = FH / (D['feet'] - D['top'])                     # metres per canvas pixel
EL = math.radians(12)                               # camera looks down 12 degrees

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sys.path.insert(0, HERE); import printkit as K; K.sc = sc
K.setup_cycles(SAMPLES, RW, RH, transparent=True)
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.03, 0.026, 0.028, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1
M = K.kit_materials()

# ---------------- the figure: closed relief, painted with the photo of the real printed figure ----------------
def relief(step=2):
    im = cv2.imread(FIG, cv2.IMREAD_UNCHANGED); Hh, Ww = im.shape[:2]
    if im.shape[2] == 3: im = np.dstack([im, np.full((Hh, Ww), 255, np.uint8)])
    mask = (im[..., 3] > 127).astype(np.uint8)
    dep = np.load(DEPTH).astype(np.float32); dn = np.clip((dep - dep[mask > 0].min()) / (np.ptp(dep[mask > 0]) + 1e-6), 0, 1)
    dn = cv2.bilateralFilter(dn, 9, 0.08, 5)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    infl = np.clip(np.sqrt(dist / 40.0), 0, 1.6); edge = np.clip(dist / 10.0, 0, 1); edge = edge * edge * (3 - 2 * edge)
    zf = cv2.GaussianBlur((0.05 * infl + 0.14 * dn * edge) * (FH / 2.0), (0, 0), 1.2); zb = zf * 0.85 + 0.004 * FH * edge
    ys = np.arange(0, Hh, step); xs = np.arange(0, Ww, step); gx, gy = np.meshgrid(xs, ys); inside = mask[gy, gx] > 0
    idx = -np.ones(inside.shape, np.int64); n = int(inside.sum()); idx[inside] = np.arange(n); px, py = gx[inside], gy[inside]
    X = (px - Ww / 2) * S; Zc = (D['feet'] - py) * S; yf = -zf[py, px]; yb = zb[py, px]
    # sheared so that, seen by the tilted camera, every point lands exactly on its pixel of the photo
    verts = np.vstack([np.stack([X, yf, (Zc - yf * math.sin(EL)) / math.cos(EL)], 1), np.stack([X, yb, (Zc - yb * math.sin(EL)) / math.cos(EL)], 1)])
    a_ = idx[:-1, :-1]; b_ = idx[:-1, 1:]; c_ = idx[1:, 1:]; d_ = idx[1:, :-1]; ok = (a_ >= 0) & (b_ >= 0) & (c_ >= 0) & (d_ >= 0)
    qf = np.stack([a_[ok], d_[ok], c_[ok], b_[ok]], 1); qb = qf[:, ::-1] + n
    from collections import Counter
    ec = Counter(); [ec.update([tuple(sorted((q[k], q[(k + 1) % 4])))]) for q in qf for k in range(4)]
    walls = [[q[(k + 1) % 4], q[k], q[k] + n, q[(k + 1) % 4] + n] for q in qf for k in range(4) if ec[tuple(sorted((q[k], q[(k + 1) % 4])))] == 1]
    faces = np.vstack([qf, qb, np.array(walls, np.int64)])
    me = bpy.data.meshes.new('figure'); me.from_pydata(verts.tolist(), [], faces.tolist()); me.update()
    uv = me.uv_layers.new(name='UV'); U = np.concatenate([px / Ww, px / Ww]); V = np.concatenate([1 - py / Hh, 1 - py / Hh])
    lv = np.zeros(len(me.loops), np.int64); me.loops.foreach_get('vertex_index', lv); uv.data.foreach_set('uv', np.stack([U[lv], V[lv]], 1).ravel())
    for p_ in me.polygons: p_.use_smooth = True
    o = bpy.data.objects.new('figure', me); sc.collection.objects.link(o)
    m = bpy.data.materials.new('figpaint'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; pb = K.principled(m)
    tx = N.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(FIG); tx.interpolation = 'Cubic'; tx.extension = 'EXTEND'
    hs = N.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = 1.25; hs.inputs['Value'].default_value = 1.12
    nt.links.new(tx.outputs['Color'], hs.inputs['Color']); nt.links.new(hs.outputs['Color'], pb.inputs['Base Color'])
    pb.inputs['Roughness'].default_value = 0.42; pb.inputs['Specular IOR Level'].default_value = 0.45
    K.layer_lines(m, 0.00035, 0.25, 0.00008)
    o.data.materials.append(m); return o, m, verts
fig, figm, FV = relief()
LAYER = 0.00035
CUTS = [K.add_clip(figm, LAYER, 0.004, cap_light=float(os.environ.get('CAPL', '0.9')))]

# ---------------- plate under the feet ----------------
pei = K.pei_material('pei', os.path.join(HERE, 'plate.png'), base=(0.035, 0.034, 0.036))   # the same SYMZ plate as the Exploded View
plate_root = bpy.data.objects.new('plate', None); sc.collection.objects.link(plate_root)
K.pei_plate(pei, M['steel'], M['anod'], 256, 256, parent=plate_root)
plate_root.location = ((D['ax'] + 10 - D['w'] / 2) * S, 0.035, 0)

# ---------------- camera: orthographic, lined up with the page's figure canvas ----------------
cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cam.sensor_fit = 'HORIZONTAL'; cam.ortho_scale = (X1d - X0d) * S
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
f = Vector((0, math.cos(EL), -math.sin(EL))); u = Vector((0, math.sin(EL), math.cos(EL))); r = Vector((1, 0, 0))
cx = ((X0d + X1d) / 2 - D['w'] / 2) * S; cy = (D['feet'] - (Y0d + Y1d) / 2) * S
co.location = r * cx + u * cy - f * 1.5
co.rotation_euler = f.to_track_quat('-Z', 'Y').to_euler()
cam.clip_end = 5
def to_canvas(pt):
    v = world_to_camera_view(sc, co, Vector(pt)); return (X0d + v.x * (X1d - X0d), Y0d + (1 - v.y) * (Y1d - Y0d))

# ---------------- light: studio softboxes + the brand's red rim ----------------
T = (cx, 0, 0.08)
K.area('key', (cx + 0.32, -0.55, 0.42), T, 0.45, 16, (1.0, 0.97, 0.94))
K.area('fill', (cx - 0.5, -0.45, 0.18), T, 0.5, 5, (0.92, 0.95, 1.0))
K.area('rim', (cx - 0.3, 0.42, 0.28), T, 0.25, 10, (1.0, 0.12, 0.1))
K.area('top', (cx, 0.05, 0.6), (cx, 0, 0), 0.4, 6)

# ---------------- moving parts ----------------
th, info = K.toolhead(M); beam = K.gantry_beam(M, 700)
MECH = [o for o in K.descendants(th) + K.descendants(beam) if not o.name.startswith('cutter')]
for o in MECH: o.hide_render = True

zmin, zmax = 0.0, float(FV[:, 2].max())
band = (zmax - zmin) / 40
def xext(z):
    sel = FV[np.abs(FV[:, 2] - z) < band]
    if len(sel) == 0: sel = FV[np.abs(FV[:, 2] - FV[np.argmin(np.abs(FV[:, 2] - z)), 2]) < band]
    return float(sel[:, 0].min()), float(sel[:, 0].max())

def feather(path, px=150):
    from PIL import Image
    im = Image.open(path).convert('RGBA'); a = np.asarray(im).copy(); W_ = a.shape[1]
    ramp = np.ones(W_, np.float32); k = np.linspace(0, 1, px); ramp[:px] = k * k * (3 - 2 * k); ramp[-px:] = ramp[:px][::-1]
    a[..., 3] = (a[..., 3].astype(np.float32) * ramp[None, :]).astype(np.uint8); Image.fromarray(a).save(path)

meta = {'region': [X0d, Y0d, X1d - X0d, Y1d - Y0d], 'rs': RS, 'n': NP, 'path': [], 'levels': []}
for i in range(NP):
    p = i / (NP - 1); cz = zmin + (zmax - zmin + 0.002) * p
    K.set_cuts(CUTS, cz if p < 1 else 1000.0); fig.hide_render = p <= 0
    xl, xr = xext(min(cz, zmax)); c = to_canvas((0, 0, cz)); l = to_canvas((xl, 0, cz)); rr = to_canvas((xr, 0, cz))
    meta['path'].append([round(c[1], 1), round(l[0], 1), round(rr[0], 1)])
    fpath = os.path.join(OUT, 'print-%02d.png' % i); sc.render.filepath = fpath; bpy.ops.render.render(write_still=True); feather(fpath)
    print('rendered print', i, flush=True)
K.set_cuts(CUTS, 1000.0)
for lp in (0.12, 0.5, 0.88):
    cz = zmin + (zmax - zmin) * lp
    for o in MECH: o.hide_render = False
    th.location = (0, 0, cz); beam.location = (0, 0, cz); bpy.context.view_layer.update()
    nz = to_canvas((0, 0, cz)); tube = to_canvas(th.matrix_world @ info['tube']); mm = to_canvas((0.010, 0, cz))
    lev = {'p': lp, 'ny': round(nz[1], 1), 'tube': [round(tube[0] - nz[0], 1), round(tube[1] - nz[1], 1)], 'mm': round((mm[0] - nz[0]) / 10, 3)}
    for nm, root in (('head', th), ('beam', beam)):
        restore = K.only_visible([o for o in K.descendants(root) if not o.name.startswith('cutter')])
        fpath = os.path.join(OUT, '%s-%d.png' % (nm, round(lp * 100))); sc.render.filepath = fpath; bpy.ops.render.render(write_still=True); restore()
        if nm == 'beam': feather(fpath)
        x, y, w_, h_ = K.crop_alpha(fpath)
        # crop rect and nozzle anchor, in canvas units
        lev[nm] = [round(X0d + x / RS, 1), round(Y0d + y / RS, 1), round(w_ / RS, 1), round(h_ / RS, 1), round(nz[0], 1), round(nz[1], 1)]
        print('rendered sprite', nm, lp, flush=True)
    for o in MECH: o.hide_render = True
    meta['levels'].append(lev)
json.dump(meta, open(os.path.join(OUT, 'print.json'), 'w'))
print('meta done', flush=True)
