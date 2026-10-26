"""Loading screen: a photoreal enclosed CoreXY printer printing Symz (the Meshy model), rendered in Cycles.
The print hovers halfway between the bed and the top of the frame (a deliberate exception to how printers work).
Writes:
  frame-NN.png     the printer with the print up to layer NN; the flying gantry (X beam + Y rails) rides at that height
  head-K.png       the toolhead alone (transparent) at three heights; the page slides it along the beam between frames
  loader.json      per frame: the nozzle's screen position at the left/right edge of that layer and the sprite scale there
env: OUT, W, H, SAMPLES, FRAMES (default 49), MODEL (the .glb), ROTZ (deg), HS (print height, m)
Site frames: OUT=out W=800 H=500 SAMPLES=24 FRAMES=49 MODEL=../../models/symz.glb python3 loader_printer.py
then convert out/frame-NN.png to assets/loader/pNN.webp and out/head-K.png to assets/loader/head-K.webp."""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get('OUT', 'out'); os.makedirs(OUT, exist_ok=True)
RW, RH = int(os.environ.get('W', '800')), int(os.environ.get('H', '500'))
SAMPLES = int(os.environ.get('SAMPLES', '24')); NF = int(os.environ.get('FRAMES', '49'))
MODEL = os.environ.get('MODEL', os.path.join(HERE, '..', '..', 'models', 'symz.glb'))
HS = float(os.environ.get('HS', '0.24'))
ONLY = [int(v) for v in os.environ.get('ONLY', '').split(',') if v != '']

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sys.path.insert(0, HERE); import printkit as K; K.sc = sc
from printkit import MM, box, cyl, extrusion, mat, micro, area
K.setup_cycles(SAMPLES, RW, RH, transparent=False)
sc.cycles.adaptive_threshold = 0.03
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.0036, 0.004, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1
M = K.kit_materials()

def glass(name, tint=(0.62, 0.62, 0.64), rough=0.02):
    """smoked glass that still lets light through for shadows (no caustics)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); g = N.new('ShaderNodeBsdfGlass'); g.inputs['Color'].default_value = (*tint, 1); g.inputs['Roughness'].default_value = rough; g.inputs['IOR'].default_value = 1.5
    tr = N.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value = (*tint, 1)
    lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader')
    L.new(lp.outputs['Is Shadow Ray'], mx.inputs[0]); L.new(g.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs['Surface'])
    return m
GLASS = glass('glass')
DGLASS = glass('doorglass', (0.4, 0.4, 0.42))
SHEET = micro(mat('sheet', (0.016, 0.016, 0.018), 0.35, 0.5, spec=0.45), 2600, 0.12, 0.00012, rough_var=0.05)   # powder-coated steel
DESK = micro(mat('desk', (0.03, 0.028, 0.027), 0.0, 0.42), 40, 0.05, 0.0006, rough_var=0.12)
WALL = mat('wall', (0.012, 0.011, 0.011), 0.0, 0.85)
LED = mat('led', (1, 1, 1), 0, 0.5, emit=(0.9, 0.95, 1.0), es=18)

# ---------------- room ----------------
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.0); K.from_bm('desk', bm, DESK)
K.box('wall', -2000, 2000, 900, 920, -10, 2000, WALL)
for i, (x, z, c, s) in enumerate([(-0.75, 0.62, (1.0, 0.55, 0.25), 1.2), (0.55, 0.9, (1.0, 0.45, 0.2), 0.8), (1.1, 0.35, (1.0, 0.12, 0.08), 1.6), (-1.25, 1.1, (0.9, 0.9, 1.0), 0.6)]):
    K.cyl('bokeh%d' % i, 14, 880, 884, mat('bk%d' % i, c, 0, 0.5, emit=c, es=30 * s), None, 24, loc=(x * 1000, z * 1000), axis='Y')

# ---------------- the enclosure (outer 500 x 480 x 580 mm) ----------------
X2, Y2, ZB, ZT = 250.0, 240.0, 100.0, 610.0
box('chassis', -X2, X2, -Y2, Y2, 8, ZB, SHEET, bev=3.0)
for x in (-X2 + 30, X2 - 30):
    for y in (-Y2 + 30, Y2 - 30): cyl('foot', 14, 0, 8, M['rubber'], None, 32, loc=(x, y))
box('bezel', -X2 + 12, X2 - 12, -Y2 - 1.5, -Y2 + 2, 14, ZB - 8, M['shell'], bev=1.5)
# touchscreen with a simple status UI
def screen_image():
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (400, 240), (8, 10, 14)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 14, 386, 226), 14, outline=(40, 46, 58), width=2)
    d.ellipse((40, 60, 160, 180), outline=(60, 64, 76), width=10); d.arc((40, 60, 160, 180), -90, 140, fill=(227, 20, 27), width=10)
    for i, y in enumerate((70, 104, 138, 172)): d.rounded_rectangle((190, y, 360 - i * 30, y + 14), 6, fill=(70, 76, 90) if i else (200, 205, 215))
    d.rectangle((14, 14, 386, 40), fill=(20, 24, 32)); p = os.path.join(OUT, '_screen.png'); im.save(p); return p
scr = mat('screen', (0.01, 0.01, 0.012), 0, 0.08, spec=0.9); nt = scr.node_tree; tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(screen_image())
nt.links.new(tx.outputs['Color'], K.principled(scr).inputs['Emission Color']); K.principled(scr).inputs['Emission Strength'].default_value = 1.4
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5); uvl = bm.loops.layers.uv.new()
for f in bm.faces:
    for l in f.loops: l[uvl].uv = (l.vert.co.x + 0.5, l.vert.co.y + 0.5)
so = K.from_bm('screen', bm, scr); so.scale = (0.096 * 2, 0.056 * 2, 1); so.rotation_euler = (math.pi / 2, 0, 0); so.location = (0.13, -Y2 * MM - 0.0022, 0.054)
# posts, top frame, vertical rails
for x in (-X2 + 10, X2 - 10):
    for y in (-Y2 + 10, Y2 - 10):
        p = extrusion('post', ZT - ZB, M['anod'], None, 1); p.rotation_euler = (0, math.pi / 2, 0); p.location = (x * MM, y * MM, (ZB + ZT) / 2 * MM)
for y in (-Y2 + 10, Y2 - 10): extrusion('topx', 2 * X2 - 40, M['anod'], None, 1, loc=(0, y, ZT - 10))
for x in (-X2 + 10, X2 - 10):
    e = extrusion('topy', 2 * Y2 - 40, M['anod'], None, 1); e.rotation_euler = (0, 0, math.pi / 2); e.location = (x * MM, 0, (ZT - 10) * MM)
for y in (-Y2 + 10, Y2 - 10): extrusion('botx', 2 * X2 - 40, M['anod'], None, 1, loc=(0, y, ZB + 10))
for x in (-X2 + 10, X2 - 10):
    for y in (-Y2 + 10, Y2 - 10):
        xi = x + (10 if x < 0 else -10)                   # rails on the inner faces of the posts
        box('zrail', *((xi, xi + 8) if x < 0 else (xi - 8, xi)), y - 6, y + 6, ZB + 30, ZT - 30, M['steel'], bev=0.4)
# panels: smoked glass sides and lid, powder-coated back with a vent
box('glassL', -X2 + 1, -X2 + 5, -Y2 + 20, Y2 - 20, ZB + 20, ZT - 20, GLASS)
box('glassR', X2 - 5, X2 - 1, -Y2 + 20, Y2 - 20, ZB + 20, ZT - 20, GLASS)
box('back', -X2 + 20, X2 - 20, Y2 - 4, Y2 - 1, ZB + 20, ZT - 20, SHEET)
for i in range(7): box('vent', -60, 60, Y2 - 5, Y2 - 4, ZB + 250 + i * 14, ZB + 256 + i * 14, M['fan'], bev=2.5)
box('lid', -X2 + 2, X2 - 2, -Y2 + 2, Y2 - 2, ZT, ZT + 5, GLASS)
for (a, b, c, d) in ((-X2, X2, -Y2, -Y2 + 22), (-X2, X2, Y2 - 22, Y2), (-X2, -X2 + 22, -Y2, Y2), (X2 - 22, X2, -Y2, Y2)):
    box('lidframe', a, b, c, d, ZT + 5, ZT + 9, M['shell'], bev=1.2)
box('handle_lid', -60, 60, -Y2 - 6, -Y2 + 8, ZT + 2, ZT + 12, M['shell2'], bev=2.5)
# front door: glass in a black frame, swung open on its left hinge
door = bpy.data.objects.new('door', None); sc.collection.objects.link(door); door.location = (-X2 * MM, -Y2 * MM, 0)
DW = 2 * X2 - 4
for o in (box('door_glass', 6, DW - 6, -3, 1, ZB + 6, ZT - 6, DGLASS), box('door_frameT', 0, DW, -6, 2, ZT - 16, ZT - 2, M['shell'], bev=1.5),
          box('door_frameB', 0, DW, -6, 2, ZB + 2, ZB + 16, M['shell'], bev=1.5), box('door_frameL', 0, 14, -6, 2, ZB + 2, ZT - 2, M['shell'], bev=1.5),
          box('door_frameR', DW - 14, DW, -6, 2, ZB + 2, ZT - 2, M['shell'], bev=1.5), box('door_handle', DW - 30, DW - 18, -26, -6, 280, 420, M['shell2'], bev=3)):
    o.parent = door
door.rotation_euler = (0, 0, math.radians(90))    # swung all the way round, folded against the outside of the left side
# interior light bar under the top front rail
box('ledbar', -X2 + 40, X2 - 40, -Y2 + 22, -Y2 + 30, ZT - 26, ZT - 22, LED)
area('ledlight', (0, -0.2, (ZT - 30) * MM), (0, 0.02, 0.2), 0.38, 9, (0.92, 0.96, 1.0), 0.02)

# ---------------- bed ----------------
BEDZ = 0.142
bedroot = bpy.data.objects.new('bed', None); sc.collection.objects.link(bedroot); bedroot.location = (0, 0.01, BEDZ)
pei = K.pei_material('pei', None, base=(0.2, 0.115, 0.035))
K.pei_plate(pei, M['steel'], M['anod'], 330, 330, parent=bedroot)
for x in (-140, 140):
    for y in (-140, 140): cyl('standoff', 7, -0.142 / MM + ZB, -4, M['alu'], bedroot, 24, loc=(x, y))

# ---------------- the print: Symz, hovering halfway between the bed and the top of the frame ----------------
def import_model(path, height, base_z):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]; meshes = [o for o in new if o.type == 'MESH']
    root = bpy.data.objects.new('model', None); sc.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    root.rotation_euler = (0, 0, math.radians(float(os.environ.get('ROTZ', '0'))))
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    k = height / (mx.z - mn.z); root.scale = (k, k, k)
    root.location = (-(mn.x + mx.x) / 2 * k, -(mn.y + mx.y) / 2 * k, base_z - mn.z * k)
    bpy.context.view_layer.update()
    for o in meshes:
        for p_ in o.data.polygons: p_.use_smooth = True
    return meshes
TOPZ = (ZT - 10) * MM
PZ0 = (BEDZ + TOPZ) / 2 - HS / 2 - 0.012
parts = import_model(MODEL, HS, PZ0)
LAYER = 0.0012
CUTS, seen = [], set()
for o in parts:
    for slot in o.material_slots:
        m = slot.material
        if m and m.use_nodes and m.name not in seen:
            seen.add(m.name); K.layer_lines(m, LAYER, 0.35, 0.00025); CUTS.append(K.add_clip(m, LAYER, 0.007, cap_light=float(os.environ.get('CAPL', '0.5'))))
dg = bpy.context.evaluated_depsgraph_get(); V = []
for o in parts:
    ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world; V += [mw @ v.co for v in me.vertices]; ev.to_mesh_clear()
zmin, zmax = min(v.z for v in V), max(v.z for v in V); band = (zmax - zmin) / 40
def xext(z):
    xs = [v.x for v in V if abs(v.z - z) < band and abs(v.y) < 0.05]
    if not xs: xs = [v.x for v in V if abs(v.z - z) < band * 2] or [0.0]
    return min(xs), max(xs)

# ---------------- flying gantry: X beam + Y rails + A/B motors, rides at the layer height ----------------
gantry = K.gantry_beam(M, 2 * X2 - 70, 'gantry')
for x in (-X2 + 36, X2 - 36):
    e = extrusion('yrail', 2 * Y2 - 60, M['anod'], gantry, 1); e.rotation_euler = (0, 0, math.pi / 2); e.location = (x * MM, 0, (64 + K.LIFT) * MM)
    box('ycar', x - 14, x + 14, 20, 60, 50 + K.LIFT, 80 + K.LIFT, M['steel'], gantry, bev=0.8)
for x in (-X2 + 50, X2 - 50):
    box('motor', x - 21, x + 21, Y2 - 80, Y2 - 38, 44 + K.LIFT, 84 + K.LIFT, M['shell'], gantry, bev=1.5)
    box('motorcap', x - 21.2, x + 21.2, Y2 - 80.2, Y2 - 37.8, 76 + K.LIFT, 84 + K.LIFT, M['alu'], gantry, bev=0.8)
th, info = K.toolhead(M)
HEAD = [o for o in K.descendants(th) if not o.name.startswith('cutter')]
for o in HEAD: o.hide_render = True

# ---------------- light ----------------
T = (0, 0, 0.33)
area('key', (-0.65, -0.95, 1.0), T, 0.9, 120, (1.0, 0.96, 0.92), 0.6)
area('fill', (1.1, -0.7, 0.45), T, 0.8, 30, (0.9, 0.94, 1.0))
area('rim', (0.7, 0.75, 0.75), T, 0.5, 70, (1.0, 0.1, 0.07))
area('kick', (-0.9, 0.6, 0.4), T, 0.4, 25, (1.0, 0.18, 0.12))

# ---------------- camera ----------------
cam = bpy.data.cameras.new('cam'); cam.lens = 40; cam.dof.use_dof = True; cam.dof.aperture_fstop = 4.0
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
co.location = (0.6, -1.44, 0.5); tgt = Vector((0.0, 0.0, 0.305))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.dof.focus_distance = (Vector((0, -0.03, (zmin + zmax) / 2)) - co.location).length
bpy.context.view_layer.update()
def scr(pt):
    v = world_to_camera_view(sc, co, Vector(pt)); return (v.x, 1 - v.y, v.z)

# ---------------- frames ----------------
meta = {'w': RW, 'h': RH, 'n': NF, 'path': [], 'levels': []}
for i in range(NF):
    p = i / (NF - 1); cz = zmin + (zmax - zmin + 0.001) * p
    K.set_cuts(CUTS, cz if p < 1 else 1000.0)
    for o in parts: o.hide_render = p <= 0
    nz = min(cz, zmax) + 0.0004 if p < 1 else zmax + 0.012          # parks just above the finished print
    gantry.location = (0, 0, nz)
    xl, xr = xext(min(cz, zmax)); a = scr((0, 0, nz)); l = scr((xl, 0, nz)); r = scr((xr, 0, nz))
    meta['path'].append([round(l[0], 4), round(l[1], 4), round(a[2] / l[2], 4), round(r[0], 4), round(r[1], 4), round(a[2] / r[2], 4), round(a[0], 4), round(a[1], 4)])
    if ONLY and i not in ONLY: continue
    sc.render.filepath = os.path.join(OUT, 'frame-%02d.png' % i); bpy.ops.render.render(write_still=True); print('rendered', i, round(p, 3), flush=True)
# toolhead sprites at three heights (rendered alone; the page places them on the beam)
if os.environ.get('SPRITES', '1') == '1':
    sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'
    for lp in (0.12, 0.5, 0.88):
        cz = zmin + (zmax - zmin) * lp; th.location = (0, 0, cz); gantry.location = (0, 0, cz); bpy.context.view_layer.update()
        for o in HEAD: o.hide_render = False
        restore = K.only_visible(HEAD)
        f = os.path.join(OUT, 'head-%d.png' % round(lp * 100)); sc.render.filepath = f; bpy.ops.render.render(write_still=True); restore()
        for o in HEAD: o.hide_render = True
        x, y, w_, h_ = K.crop_alpha(f); nz = scr((0, 0, cz)); tb = scr(th.matrix_world @ info['tube'])
        meta['levels'].append({'p': lp, 'head': [x, y, w_, h_, round(nz[0] * RW, 1), round(nz[1] * RH, 1)], 'tube': [round((tb[0] - nz[0]) * RW, 1), round((tb[1] - nz[1]) * RH, 1)]})
        print('rendered head', lp, flush=True)
    lid = scr((0.02, 0.0, ZT * MM)); meta['lid'] = [round(lid[0], 4), round(lid[1], 4)]
json.dump(meta, open(os.path.join(OUT, 'loader.json'), 'w'))
print('meta done', flush=True)
