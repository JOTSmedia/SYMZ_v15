"""Web version of the Meshy model: decimated mesh + smaller textures, plain GLB (no Draco) for three.js r128.
usage (Blender's Python): python3 web_glb.py SYMZavatar.glb models/symz.glb 0.1   (0.1 = keep 10% of the triangles)"""
import bpy, os, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else 'SYMZavatar.glb'
DST = sys.argv[2] if len(sys.argv) > 2 else 'models/symz.glb'
RATIO = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]
bpy.context.view_layer.objects.active = o; o.select_set(True)
md = o.modifiers.new('dec', 'DECIMATE'); md.decimate_type = 'COLLAPSE'; md.ratio = RATIO; md.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier='dec')
print('tris after', sum(len(p.vertices) - 2 for p in o.data.polygons))
sizes = {'Image_0': 2048, 'Image_1': 1024, 'Image_2': 1024}
for im in bpy.data.images:
    if im.name in sizes: im.scale(sizes[im.name], sizes[im.name])
bpy.ops.export_scene.gltf(filepath=DST, export_format='GLB', use_selection=False,
    export_image_format='JPEG', export_jpeg_quality=86, export_apply=True, export_yup=True, export_draco_mesh_compression_enable=False)
print('size', os.path.getsize(DST) // 1024, 'KB')
