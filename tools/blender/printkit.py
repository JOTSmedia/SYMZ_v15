"""Photoreal 3D-printing kit shared by the site's Blender renders (loader_printer.py, lab_models.py, p2f_print.py).

  toolhead()      a modern CoreXY toolhead: rounded housing, front fan grille, side blower, ring duct,
                  red silicone sock and a brass nozzle. Origin = nozzle tip, front faces -Y (the camera).
  gantry_beam()   2040 aluminium extrusion with an MGN12 rail and two GT2 belts, built around the same origin.
  pei_plate()     textured-PEI spring-steel sheet (optional printed graphic) on a magnetic heated bed, with a tab.
  layer_lines()   printed layer lines (world height) on any material, real or imported.
  add_clip()      prints any mesh layer by layer: everything above CUT is gone, the open top shows the top
                  layer with its infill pattern, and the freshest layer has the wet sheen of molten plastic.
All sizes are in metres, so 0.001 = 1 mm."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

MM = 0.001
LIFT = 5.0          # housing height above the stock layout (mm)
sc = bpy.context.scene

# ---------------------------------------------------------------- materials
def principled(m):
    return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)

def mat(name, color, metal=0.0, rough=0.5, coat=0.0, trans=0.0, emit=None, es=0.0, spec=None, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = principled(m)
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Metallic'].default_value = metal; p.inputs['Roughness'].default_value = rough
    if coat: p.inputs['Coat Weight'].default_value = coat
    if trans: p.inputs['Transmission Weight'].default_value = trans
    if spec is not None: p.inputs['Specular IOR Level'].default_value = spec
    if sss: p.inputs['Subsurface Weight'].default_value = sss
    if emit: p.inputs['Emission Color'].default_value = (*emit, 1); p.inputs['Emission Strength'].default_value = es
    return m

def _bump_into(m, height_socket, strength, dist):
    """route a height signal into the principled normal, keeping any normal map already there"""
    nt = m.node_tree; p = principled(m)
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = strength; b.inputs['Distance'].default_value = dist
    if p.inputs['Normal'].links:
        nt.links.new(p.inputs['Normal'].links[0].from_socket, b.inputs['Normal'])
    nt.links.new(height_socket, b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    return b

def micro(m, scale=2500.0, strength=0.08, dist=0.0002, rough_var=0.0, stretch=None, coord='Object'):
    """fine surface texture: moulded plastic (round noise) or brushed/extruded metal (noise stretched along an axis)"""
    nt = m.node_tree; N = nt.nodes; L = nt.links; p = principled(m)
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 8
    mp = N.new('ShaderNodeMapping')
    s = [scale, scale, scale]
    if stretch is not None: s['XYZ'.index(stretch)] = scale * 0.015
    mp.inputs['Scale'].default_value = s
    L.new(tc.outputs[coord], mp.inputs['Vector']); L.new(mp.outputs['Vector'], nz.inputs['Vector'])
    _bump_into(m, nz.outputs['Fac'], strength, dist)
    if rough_var and not p.inputs['Roughness'].links:
        r0 = p.inputs['Roughness'].default_value
        mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.0, r0 - rough_var); mr.inputs['To Max'].default_value = r0 + rough_var
        L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs['Result'], p.inputs['Roughness'])
    return m

def kit_materials():
    M = {}
    M['shell'] = micro(mat('th_shell', (0.016, 0.016, 0.018), 0.0, 0.46, spec=0.45), 4200, 0.12, 0.00012, rough_var=0.06)
    M['shell2'] = micro(mat('th_cover', (0.024, 0.024, 0.027), 0.0, 0.38, spec=0.5), 4200, 0.08, 0.0001, rough_var=0.05)
    M['fan'] = mat('th_fan', (0.006, 0.006, 0.007), 0.0, 0.42)
    M['blade'] = mat('th_blade', (0.035, 0.035, 0.038), 0.0, 0.35)
    M['red'] = micro(mat('th_red', (0.5, 0.012, 0.016), 0.0, 0.36, coat=0.2), 4200, 0.06, 0.0001)
    M['anod'] = micro(mat('anod', (0.028, 0.028, 0.032), 1.0, 0.34), 1500, 0.06, 0.00015, rough_var=0.07, stretch='X')
    M['alu'] = micro(mat('alu', (0.8, 0.81, 0.83), 1.0, 0.26), 1500, 0.06, 0.00015, rough_var=0.05, stretch='X')
    M['steel'] = micro(mat('steel', (0.86, 0.86, 0.88), 1.0, 0.17), 2500, 0.03, 0.0001, rough_var=0.04, stretch='X')
    M['brass'] = mat('brass', (0.95, 0.68, 0.33), 1.0, 0.24)
    # burnt filament on the very tip of the nozzle
    nt = M['brass'].node_tree; N = nt.nodes; tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0012; mr.inputs['From Max'].default_value = 0.0028; nt.links.new(sp.outputs['Z'], mr.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; nt.links.new(mr.outputs['Result'], mx.inputs['Factor'])
    mx.inputs[6].default_value = (0.09, 0.05, 0.025, 1); mx.inputs[7].default_value = (0.95, 0.68, 0.33, 1); nt.links.new(mx.outputs[2], principled(M['brass']).inputs['Base Color'])
    M['sock'] = micro(mat('sock', (0.42, 0.03, 0.025), 0.0, 0.62, sss=0.04), 1800, 0.18, 0.0002, rough_var=0.08)
    M['rubber'] = micro(mat('belt', (0.012, 0.012, 0.013), 0.0, 0.72), 9000, 0.25, 0.00008, stretch='X')
    M['pom'] = mat('fitting', (0.02, 0.02, 0.022), 0.0, 0.3)
    M['label'] = mat('label', (0.62, 0.62, 0.6), 0.0, 0.5)
    return M

def pei_material(name='pei', graphic=None, base=(0.22, 0.13, 0.04), cell=2800.0):
    """textured PEI powder coat: fine sparkle, satin, with an optional printed graphic (image: colour + where it is printed)"""
    m = mat(name, base, 0.3, 0.52, spec=0.6); nt = m.node_tree; N = nt.nodes; L = nt.links; p = principled(m)
    tc = N.new('ShaderNodeTexCoord')
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = cell; L.new(tc.outputs['Object'], vo.inputs['Vector'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = cell * 0.5; nz.inputs['Detail'].default_value = 4; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    h = N.new('ShaderNodeMath'); h.operation = 'ADD'; L.new(vo.outputs['Distance'], h.inputs[0]); L.new(nz.outputs['Fac'], h.inputs[1])
    _bump_into(m, h.outputs[0], 0.5, 0.00012)
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.34; rr.inputs['To Max'].default_value = 0.66; L.new(nz.outputs['Fac'], rr.inputs['Value']); L.new(rr.outputs['Result'], p.inputs['Roughness'])
    var = N.new('ShaderNodeMix'); var.data_type = 'RGBA'; var.blend_type = 'MULTIPLY'; var.inputs['Factor'].default_value = 0.35
    L.new(vo.outputs['Distance'], var.inputs[7]); var.inputs[6].default_value = (*base, 1)
    col = var.outputs[2]
    if graphic:
        tx = N.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(graphic); tx.interpolation = 'Cubic'
        uv = N.new('ShaderNodeUVMap'); L.new(uv.outputs['UV'], tx.inputs['Vector'])
        g2 = N.new('ShaderNodeMix'); g2.data_type = 'RGBA'; g2.blend_type = 'MULTIPLY'; g2.inputs['Factor'].default_value = 0.25
        L.new(tx.outputs['Color'], g2.inputs[6]); L.new(vo.outputs['Distance'], g2.inputs[7]); col = g2.outputs[2]
    L.new(col, p.inputs['Base Color'])
    return m

def layer_lines(m, period, strength=0.3, dist=0.0001, axis='Z'):
    """printed layer lines: a sine of world height, plus a faint per-layer roughness change"""
    nt = m.node_tree; N = nt.nodes; L = nt.links
    g = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(g.outputs['Position'], sp.inputs[0])
    mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = math.pi / period; L.new(sp.outputs[axis], mu.inputs[0])
    sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; L.new(mu.outputs[0], sn.inputs[0])
    ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(sn.outputs[0], ab.inputs[0])   # rounded beads, sharp valleys
    _bump_into(m, ab.outputs[0], strength, dist)
    return m

# ---------------------------------------------------------------- geometry helpers
def _link(o, m=None, parent=None):
    sc.collection.objects.link(o)
    if m is not None: o.data.materials.append(m)
    if parent is not None: o.parent = parent
    return o

def from_bm(name, bm, m=None, parent=None, smooth=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth is not None:
        for poly in me.polygons: poly.use_smooth = smooth(poly)
    return _link(bpy.data.objects.new(name, me), m, parent)

def bevel(o, w, seg=3, harden=True):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'; md.harden_normals = False
    for p in o.data.polygons: p.use_smooth = True
    try:
        o.data.set_sharp_from_angle(angle=math.radians(35))
    except Exception:
        pass
    return o

def box(name, x0, x1, y0, y1, z0, z1, m, parent=None, bev=0.0, seg=3):
    """axis-aligned box from mm extents"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM), verts=bm.verts)
    o = from_bm(name, bm, m, parent); o.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM)
    return bevel(o, bev * MM, seg) if bev else o

def cyl(name, r, z0, z1, m, parent=None, seg=48, r2=None, loc=(0, 0), axis='Z', bev=0.0):
    """cylinder / cone along an axis, mm; for axis Y the 'z' range runs along Y"""
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r * MM, radius2=(r if r2 is None else r2) * MM, depth=(z1 - z0) * MM)
    o = from_bm(name, bm, m, parent, smooth=lambda p: abs(p.normal.z) < 0.9)
    c = (z0 + z1) / 2 * MM
    if axis == 'Z': o.location = (loc[0] * MM, loc[1] * MM, c)
    elif axis == 'Y': o.rotation_euler = (math.pi / 2, 0, 0); o.location = (loc[0] * MM, c, loc[1] * MM)
    else: o.rotation_euler = (0, math.pi / 2, 0); o.location = (c, loc[0] * MM, loc[1] * MM)
    return bevel(o, bev * MM, 2) if bev else o

def torus(name, R, r, m, parent=None, loc=(0, 0, 0), axis='Z', seg=64, rseg=16, sy=1.0):
    bm = bmesh.new()
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(rseg):
            b = 2 * math.pi * j / rseg
            rr = R + r * math.cos(b)
            bm.verts.new((rr * math.cos(a) * MM, rr * math.sin(a) * sy * MM, r * math.sin(b) * MM))
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(rseg):
            a = i * rseg + j; b = ((i + 1) % seg) * rseg + j; c = ((i + 1) % seg) * rseg + (j + 1) % rseg; d = i * rseg + (j + 1) % rseg
            bm.faces.new((bm.verts[a], bm.verts[b], bm.verts[c], bm.verts[d]))
    o = from_bm(name, bm, m, parent, smooth=lambda p: True)
    o.location = tuple(v * MM for v in loc)
    if axis == 'Y': o.rotation_euler = (math.pi / 2, 0, 0)
    elif axis == 'X': o.rotation_euler = (0, math.pi / 2, 0)
    return o

def boolean_cut(o, cutter):
    md = o.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cutter
    try: md.solver = 'EXACT'
    except Exception: pass
    bpy.context.view_layer.objects.active = o
    for mm in list(o.modifiers):
        if mm.name == 'cut':
            o.select_set(True); bpy.ops.object.modifier_apply(modifier='cut')
    bpy.data.objects.remove(cutter)

def extrusion(name, length, m, parent=None, rows=1, loc=(0, 0, 0)):
    """20x20 (rows=1) or 20x40 (rows=2, stacked in Z) slotted aluminium extrusion running along X, mm"""
    def profile(cz):
        h = 10.0; s = 3.1; d = 4.4   # half size, slot half-width, slot depth
        pts = []
        for k in range(4):
            a = k * math.pi / 2; c, sn = math.cos(a), math.sin(a)
            side = [(-h, -h), (-s - 1.2, -h), (-s, -h + 1.0), (-s, -h + d), (s, -h + d), (s, -h + 1.0), (s + 1.2, -h)]
            pts += [(x * c - y * sn, x * sn + y * c + cz) for (x, y) in side]
        return pts
    bm = bmesh.new()
    for r in range(rows):
        cz = (r - (rows - 1) / 2) * 20.0
        pts = profile(cz)
        vs = [bm.verts.new((-length / 2 * MM, y * MM, z * MM)) for (y, z) in pts]
        f = bm.faces.new(vs)
        ex = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [e for e in ex['geom'] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(length * MM, 0, 0), verts=top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = from_bm(name, bm, m, parent); o.location = tuple(v * MM for v in loc)
    return bevel(o, 0.35 * MM, 1)

# ---------------------------------------------------------------- the toolhead
def toolhead(M, name='toolhead'):
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root)
    R = root
    # brass nozzle: tip, cone, hex
    cyl('nz_tip', 0.55, 0.0, 0.35, M['brass'], R, 32)
    cyl('nz_cone', 0.55, 0.3, 3.6, M['brass'], R, 48, r2=3.4)
    cyl('nz_hex', 4.0, 3.5, 7.2, M['brass'], R, 6, bev=0.35)
    # silicone sock over the heater block
    box('sock', -10.5, 10.5, -8.5, 8.5, 6.4, 19.5, M['sock'], R, bev=3.6, seg=5)
    first = set(bpy.data.objects)                              # everything from here up sits 5 mm higher, so nozzle and sock show below the duct
    # ring duct around the nozzle, carried on two posts
    torus('duct', 17.5, 3.0, M['shell'], R, loc=(0, -1.0, 11.5), sy=0.86)
    for x in (-17.5, 17.5): box('duct_post', x - 2.6, x + 2.6, -4.5, 3.0, 11.5, 17.0, M['shell'], R, bev=1.2)
    # main housing
    box('body', -24.0, 24.0, -19.5, 14.0, 15.5, 72.0, M['shell'], R, bev=5.5, seg=5)
    # front cover with a recessed fan
    cover = box('cover', -22.2, 22.2, -22.4, -19.2, 19.0, 69.5, M['shell2'], R, bev=2.6, seg=4)
    bpy.context.view_layer.update()
    cut = cyl('cutter', 13.6, -40, 0, None, R, 64, loc=(0, 46.0), axis='Y')
    md = cover.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = cut
    try: md.solver = 'EXACT'
    except Exception: pass
    cut.hide_render = True; cut.hide_viewport = True
    cyl('fan_well', 13.7, -20.2, -19.4, M['fan'], R, 64, loc=(0, 46.0), axis='Y')
    hub = cyl('fan_hub', 5.2, -21.2, -20.0, M['blade'], R, 48, loc=(0, 46.0), axis='Y')
    for i in range(9):                                          # blades seen through the grille
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(3.4 * MM, 0.6 * MM, 7.4 * MM), verts=bm.verts)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(34), 3, 'Z'))
        bmesh.ops.translate(bm, vec=(0, 0, 9.2 * MM), verts=bm.verts)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(2 * math.pi * i / 9, 3, 'Y'))
        o = from_bm('fan_blade', bm, M['blade'], R); o.location = (0, -20.7 * MM, 46.0 * MM)
    for rr in (5.6, 9.2, 12.8): torus('grille', rr, 0.42, M['shell2'], R, loc=(0, -22.3, 46.0), axis='Y', rseg=10)
    for a in (90, 210, 330):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.9 * MM, 0.6 * MM, 13.0 * MM), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0, 0, 6.5 * MM), verts=bm.verts)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(a), 3, 'Y'))
        o = from_bm('spoke', bm, M['shell2'], R); o.location = (0, -22.3 * MM, 46.0 * MM)
    cyl('hub_cap', 4.6, -22.9, -22.1, M['shell2'], R, 48, loc=(0, 46.0), axis='Y', bev=0.3)
    torus('fan_ring', 14.3, 0.7, M['red'], R, loc=(0, -22.55, 46.0), axis='Y', rseg=12)   # the one red accent
    # side blower (part cooling) on the left
    box('blower', -33.0, -23.0, -16.0, 11.0, 22.0, 56.0, M['shell'], R, bev=3.2)
    torus('blower_in', 7.8, 0.9, M['shell2'], R, loc=(-33.3, -2.5, 40.0), axis='X', rseg=10)
    cyl('blower_well', 7.4, -33.6, -32.6, M['fan'], R, 48, loc=(-2.5, 40.0), axis='X')
    # cable connector on the right, PTFE fitting on top
    box('conn', 23.0, 28.0, -6.0, 8.0, 52.0, 64.0, M['shell2'], R, bev=1.2)
    cyl('fit_hex', 5.2, 71.0, 77.0, M['pom'], R, 6, loc=(0, -3.0), bev=0.4)
    cyl('fit_collet', 4.4, 77.0, 79.4, M['red'], R, 40, loc=(0, -3.0), bev=0.5)
    # linear-rail carriage behind the housing
    box('carriage', -22.5, 22.5, 14.0, 26.0, 52.0, 79.0, M['steel'], R, bev=0.8)
    box('car_cap_l', -24.5, -22.5, 14.5, 25.5, 53.0, 78.0, M['pom'], R, bev=0.5)
    box('car_cap_r', 22.5, 24.5, 14.5, 25.5, 53.0, 78.0, M['pom'], R, bev=0.5)
    for o in bpy.data.objects:
        if o not in first and o.parent == R: o.location.z += LIFT * MM
    info = {'tube': Vector((0, -3.0 * MM, (79.4 + LIFT) * MM)), 'top': (79.4 + LIFT) * MM}
    return root, info

def gantry_beam(M, length_mm, name='gantry'):
    """X beam behind the toolhead (same origin as the toolhead's nozzle tip)"""
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root)
    extrusion('xbeam', length_mm, M['anod'], root, rows=2, loc=(0, 40.0, 64.0))
    box('rail', -length_mm / 2 + 4, length_mm / 2 - 4, 23.0, 30.0, 58.0, 70.0, M['steel'], root, bev=0.5)
    for i in range(int(length_mm // 25)):                     # rail screws
        x = -length_mm / 2 + 12 + i * 25
        cyl('screw', 2.3, 22.6, 23.2, M['anod'], root, 16, loc=(x, 64.0), axis='Y')
    for z0 in (84.6, 41.9):                                   # GT2 belts above and below the beam
        box('belt', -length_mm / 2, length_mm / 2, 32.0, 38.0, z0, z0 + 1.5, M['rubber'], root)
    for o in root.children: o.location.z += LIFT * MM
    return root

def pei_plate(m_pei, m_edge, m_base, size_x, size_y, parent=None, thick=0.6, base_thick=3.0, tab=True):
    """spring-steel sheet (top face textured PEI, uv 0..1 over the sheet) on a magnetic heated bed; top surface at z=0 (mm)"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(size_x * MM, size_y * MM, thick * MM), verts=bm.verts)
    uvl = bm.loops.layers.uv.new()
    for f in bm.faces:
        for l in f.loops: l[uvl].uv = (l.vert.co.x / (size_x * MM) + 0.5, l.vert.co.y / (size_y * MM) + 0.5)
    sheet = from_bm('pei', bm, m_pei, parent); sheet.data.materials.append(m_edge)
    for p in sheet.data.polygons: p.material_index = 0 if p.normal.z > 0.9 else 1
    sheet.location = (0, 0, -thick / 2 * MM); bevel(sheet, 0.25 * MM, 2)
    if tab:
        t = box('pei_tab', -18, 18, -size_y / 2 - 9, -size_y / 2 + 1, -thick, 0, m_edge, parent, bev=0.25)
    b = box('heatbed', -size_x / 2 - 4, size_x / 2 + 4, -size_y / 2 - 4, size_y / 2 + 4, -thick - base_thick, -thick, m_base, parent, bev=0.6)
    for x in (-size_x / 2 + 30, size_x / 2 - 30):
        cyl('bed_pin', 2.0, -thick, 1.6, m_edge, parent, 24, loc=(x, size_y / 2 + 2.0))
    return sheet

# ---------------------------------------------------------------- printing layer by layer
def add_clip(m, layer, infill=None, cap_tint=0.82, cap_light=0.6):
    """shader clip: hides everything above CUT (a Value node named CUT); the open top reads as the top layer
    (infill strands + darker gaps, shaded flat as if it were the cut plane) and the newest layer is glossy-wet.
    layer = layer height (m); infill = strand spacing (m)."""
    infill = infill or layer * 9
    nt = m.node_tree; N = nt.nodes; L = nt.links
    outs = [n for n in N if n.type == 'OUTPUT_MATERIAL']; out = next((n for n in outs if n.is_active_output), outs[0])
    lk = out.inputs['Surface'].links[0]; src = lk.from_socket
    geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sep.inputs[0])
    cutv = N.new('ShaderNodeValue'); cutv.name = 'CUT'; cutv.label = 'CUT'; cutv.outputs[0].default_value = 1000.0
    above = N.new('ShaderNodeMath'); above.operation = 'GREATER_THAN'; L.new(sep.outputs['Z'], above.inputs[0]); L.new(cutv.outputs[0], above.inputs[1])
    # --- the cap: where the view ray crosses the cut plane
    inc = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Incoming'], inc.inputs[0])
    dz = N.new('ShaderNodeMath'); dz.operation = 'SUBTRACT'; L.new(cutv.outputs[0], dz.inputs[0]); L.new(sep.outputs['Z'], dz.inputs[1])
    iz = N.new('ShaderNodeMath'); iz.operation = 'MAXIMUM'; L.new(inc.outputs['Z'], iz.inputs[0]); iz.inputs[1].default_value = 0.05
    t = N.new('ShaderNodeMath'); t.operation = 'DIVIDE'; L.new(dz.outputs[0], t.inputs[0]); L.new(iz.outputs[0], t.inputs[1])
    sv = N.new('ShaderNodeVectorMath'); sv.operation = 'SCALE'; L.new(geo.outputs['Incoming'], sv.inputs[0]); L.new(t.outputs[0], sv.inputs['Scale'])
    pc = N.new('ShaderNodeVectorMath'); pc.operation = 'ADD'; L.new(geo.outputs['Position'], pc.inputs[0]); L.new(sv.outputs[0], pc.inputs[1])
    pcs = N.new('ShaderNodeSeparateXYZ'); L.new(pc.outputs[0], pcs.inputs[0])
    def strand(sign):
        a = N.new('ShaderNodeMath'); a.operation = 'ADD' if sign > 0 else 'SUBTRACT'; L.new(pcs.outputs['X'], a.inputs[0]); L.new(pcs.outputs['Y'], a.inputs[1])
        d = N.new('ShaderNodeMath'); d.operation = 'DIVIDE'; L.new(a.outputs[0], d.inputs[0]); d.inputs[1].default_value = infill * 1.4142
        f = N.new('ShaderNodeMath'); f.operation = 'FRACT'; L.new(d.outputs[0], f.inputs[0])
        c = N.new('ShaderNodeMath'); c.operation = 'SUBTRACT'; L.new(f.outputs[0], c.inputs[0]); c.inputs[1].default_value = 0.5
        ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(c.outputs[0], ab.inputs[0])
        sm = N.new('ShaderNodeMapRange'); sm.interpolation_type = 'SMOOTHSTEP'; sm.inputs['From Min'].default_value = 0.36; sm.inputs['From Max'].default_value = 0.26
        L.new(ab.outputs[0], sm.inputs['Value']); return sm.outputs['Result']
    s1, s2 = strand(1), strand(-1)
    mxs = N.new('ShaderNodeMath'); mxs.operation = 'MAXIMUM'; L.new(s1, mxs.inputs[0]); L.new(s2, mxs.inputs[1])
    pb = principled(m)
    base = None
    if pb is not None and pb.inputs['Base Color'].links: base = pb.inputs['Base Color'].links[0].from_socket
    tint = N.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'; tint.inputs['Factor'].default_value = 1.0
    if base is not None: L.new(base, tint.inputs[6])
    else: tint.inputs[6].default_value = tuple(pb.inputs['Base Color'].default_value) if pb else (0.5, 0.5, 0.5, 1)
    shade = N.new('ShaderNodeMapRange'); shade.inputs['To Min'].default_value = 0.22; shade.inputs['To Max'].default_value = cap_tint
    L.new(mxs.outputs[0], shade.inputs['Value'])
    comb = N.new('ShaderNodeCombineColor'); [L.new(shade.outputs['Result'], comb.inputs[i]) for i in range(3)]
    L.new(comb.outputs[0], tint.inputs[7])
    cap = N.new('ShaderNodeBsdfPrincipled'); L.new(tint.outputs[2], cap.inputs['Base Color']); cap.inputs['Roughness'].default_value = 0.42
    up = N.new('ShaderNodeCombineXYZ'); up.inputs[2].default_value = 1.0; L.new(up.outputs[0], cap.inputs['Normal'])
    # the walls below shade the inside of the mesh, so the cap's light is faked: it reads as an evenly top-lit surface
    em = N.new('ShaderNodeEmission'); L.new(tint.outputs[2], em.inputs['Color']); em.inputs['Strength'].default_value = cap_light
    capmix = N.new('ShaderNodeAddShader'); L.new(cap.outputs[0], capmix.inputs[0]); L.new(em.outputs[0], capmix.inputs[1])
    act = N.new('ShaderNodeMath'); act.operation = 'LESS_THAN'; L.new(cutv.outputs[0], act.inputs[0]); act.inputs[1].default_value = 100.0   # only while printing
    capon = N.new('ShaderNodeMath'); capon.operation = 'MULTIPLY'; L.new(geo.outputs['Backfacing'], capon.inputs[0]); L.new(act.outputs[0], capon.inputs[1])
    mixcap = N.new('ShaderNodeMixShader'); L.new(capon.outputs[0], mixcap.inputs[0]); L.new(src, mixcap.inputs[1]); L.new(capmix.outputs[0], mixcap.inputs[2])
    # --- freshly laid layer: wet, glossy plastic (no glow: real PLA isn't hot enough to shine)
    lo = N.new('ShaderNodeMath'); lo.operation = 'SUBTRACT'; L.new(cutv.outputs[0], lo.inputs[0]); lo.inputs[1].default_value = layer * 1.6
    inb = N.new('ShaderNodeMath'); inb.operation = 'GREATER_THAN'; L.new(sep.outputs['Z'], inb.inputs[0]); L.new(lo.outputs[0], inb.inputs[1])
    band = N.new('ShaderNodeMath'); band.operation = 'SUBTRACT'; L.new(inb.outputs[0], band.inputs[0]); L.new(above.outputs[0], band.inputs[1])
    bw = N.new('ShaderNodeMath'); bw.operation = 'MULTIPLY'; L.new(band.outputs[0], bw.inputs[0]); bw.inputs[1].default_value = 0.45
    wet = N.new('ShaderNodeBsdfPrincipled'); wet.inputs['Roughness'].default_value = 0.08; wet.inputs['Specular IOR Level'].default_value = 0.8
    if base is not None: L.new(base, wet.inputs['Base Color'])
    elif pb is not None: wet.inputs['Base Color'].default_value = tuple(pb.inputs['Base Color'].default_value)
    mixwet = N.new('ShaderNodeMixShader'); L.new(bw.outputs[0], mixwet.inputs[0]); L.new(mixcap.outputs[0], mixwet.inputs[1]); L.new(wet.outputs[0], mixwet.inputs[2])
    tr = N.new('ShaderNodeBsdfTransparent'); mixcut = N.new('ShaderNodeMixShader')
    L.new(above.outputs[0], mixcut.inputs[0]); L.new(mixwet.outputs[0], mixcut.inputs[1]); L.new(tr.outputs[0], mixcut.inputs[2])
    nt.links.remove(lk); L.new(mixcut.outputs[0], out.inputs['Surface'])
    return cutv

def set_cuts(cuts, value):
    for c in cuts: c.outputs[0].default_value = value

# ---------------------------------------------------------------- render helpers
def setup_cycles(samples, w, h, transparent=False):
    cy = sc.cycles; sc.render.engine = 'CYCLES'
    cy.device = 'CPU'; cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.025
    cy.use_denoising = True
    try: cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    cy.max_bounces = 8; cy.diffuse_bounces = 3; cy.glossy_bounces = 4; cy.transmission_bounces = 6; cy.transparent_max_bounces = 24
    cy.sample_clamp_indirect = 4
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    for vt in ('AgX', 'Filmic'):
        try: sc.view_settings.view_transform = vt; break
        except Exception: pass
    for lk in ('AgX - Medium High Contrast', 'Medium High Contrast', 'None'):
        try: sc.view_settings.look = lk; break
        except Exception: pass

def area(name, loc, target, size, power, color=(1, 1, 1), sy=None):
    Lg = bpy.data.lights.new(name, 'AREA'); Lg.shape = 'RECTANGLE'; Lg.size = size; Lg.size_y = sy or size; Lg.energy = power; Lg.color = color
    o = bpy.data.objects.new(name, Lg); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o

def descendants(root):
    return [root] + list(root.children_recursive)

def only_visible(objs):
    """render only these objects (lights stay); returns a function that restores the previous state"""
    keep = set(objs); state = {o.name: o.hide_render for o in sc.objects}
    for o in sc.objects:
        if o.type in ('LIGHT', 'CAMERA'): continue
        if o not in keep: o.hide_render = True
    def restore():
        for n, v in state.items(): sc.objects[n].hide_render = v
    return restore

def crop_alpha(path, pad=2):
    """crop a transparent render to its content; returns (x, y, w, h) of the crop in the full frame"""
    from PIL import Image
    im = Image.open(path); bb = im.getchannel('A').point(lambda a: 255 if a > 3 else 0).getbbox()
    if not bb: return (0, 0, 0, 0)
    x0, y0, x1, y1 = max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)
    im.crop((x0, y0, x1, y1)).save(path); return (x0, y0, x1 - x0, y1 - y0)
