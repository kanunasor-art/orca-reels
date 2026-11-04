"""ORCA balloon hook (Blender). Args: <mode> where mode = test | anim | wire
test: renders frames 30 and 170 at low res; anim: frames 1..FREEZE to frames/; wire: wireframe still."""
import math
import sys

import bpy
from mathutils import Vector

MODE = sys.argv[-1]
FREEZE = 180          # last rendered frame (needle 2 frames from popping)
CUT = 54              # wide -> macro cut
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 6 if MODE == 'test' else 12
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = (360, 640) if MODE == 'test' else (720, 1280)
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, FREEZE
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - High Contrast'

w = bpy.data.worlds.new('w')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0, 0, 0, 1)


def principled(name, col, rough, metal=0.0, coat=0.0, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Subsurface Weight'].default_value = sss
    b.inputs['Subsurface Radius'].default_value = (1.0, 0.4, 0.2)
    b.inputs['Subsurface Scale'].default_value = 0.15
    return m


# ---------------------------------------------------------------- balloon
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=96, radius=1.0, location=(0, 0, 0))
bal = bpy.context.object
bal.scale = (1.0, 1.0, 1.08)
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.shade_smooth()
bal.data.materials.append(principled('bal', (0.85, 0.09, 0.005), 0.18, coat=1.0, sss=0.35))
# knot
bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.12, depth=0.14, location=(0, 0, -1.12))
bpy.context.object.data.materials.append(bal.data.materials[0])

# dent shape key: vertices near the top pole pushed down (gaussian)
TOPZ = max(v.co.z for v in bal.data.vertices)
bal.shape_key_add(name='Basis')
sk = bal.shape_key_add(name='dent')
DEPTH, SIG = 0.32, 0.22
for i, v in enumerate(bal.data.vertices):
    r = math.hypot(v.co.x, v.co.y)
    if v.co.z > 0:
        k = math.exp(-(r * r) / (2 * SIG * SIG))
        sk.data[i].co = v.co + Vector((0, 0, -DEPTH * k))

# ---------------------------------------------------------------- needle
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.013, depth=4.0, location=(0, 0, 2.0))
shaft = bpy.context.object
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.013, radius2=0.0, depth=0.16, location=(0, 0, -0.045),
                                rotation=(math.pi, 0, 0))
tip = bpy.context.object
steel = principled('steel', (0.55, 0.56, 0.6), 0.32, metal=1.0)
for o in (shaft, tip):
    o.data.materials.append(steel)
needle = bpy.data.objects.new('needle', None)
sc.collection.objects.link(needle)
shaft.parent = needle
tip.parent = needle
# needle tip z: high above -> touching -> pushing the dent
keys = [(1, TOPZ + 1.6), (CUT, TOPZ + 0.35), (120, TOPZ + 0.02), (FREEZE, TOPZ - DEPTH * 0.92)]
for f, z in keys:
    needle.location = (0, 0, z)
    needle.keyframe_insert('location', frame=f)
for f, val in [(1, 0.0), (118, 0.0), (FREEZE, 0.92)]:
    sk.value = val
    sk.keyframe_insert('value', frame=f)

# ---------------------------------------------------------------- lights
def area(loc, rot, energy, size, col=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc, rotation=rot)
    L = bpy.context.object
    L.data.energy, L.data.size, L.data.color = energy, size, col
    return L


area((-2.5, -2.5, 3.0), (math.radians(55), 0, math.radians(-45)), 380, 2.5)
area((2.8, 2.5, 1.0), (math.radians(75), 0, math.radians(135)), 260, 2.0, (1.0, 0.6, 0.4))
area((0, -1.5, 4.0), (math.radians(20), 0, 0), 150, 1.0)


# ---------------------------------------------------------------- cameras (fixed aim, cut between them)
def camera(name, loc, look, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.location = loc
    c.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    c.data.dof.use_dof = True
    c.data.dof.focus_distance = (Vector(look) - Vector(loc)).length
    c.data.dof.aperture_fstop = 2.8 if lens < 80 else 4.0
    return c


wide = camera('wide', (0, -6.4, 0.9), (0, 0, 0.55), 50)
macro = camera('macro', (0, -1.5, TOPZ + 0.42), (0, 0, TOPZ - 0.12), 85)
# slow push-in on the macro camera along its line of sight
d = (Vector((0, 0, TOPZ - 0.12)) - macro.location).normalized()
macro.keyframe_insert('location', frame=CUT)
macro.location = macro.location + d * 0.35
macro.keyframe_insert('location', frame=FREEZE)
m1 = sc.timeline_markers.new('w', frame=1)
m1.camera = wide
m2 = sc.timeline_markers.new('m', frame=CUT)
m2.camera = macro
sc.camera = wide

for a in bpy.data.actions:
    for fc in getattr(a, 'fcurves', []):
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'

sc.render.image_settings.file_format = 'PNG'
if MODE == 'test':
    for f in (30, 150, FREEZE):
        sc.frame_set(f)
        sc.camera = wide if f < CUT else macro
        sc.render.filepath = f'/home/claude/b3d/bt{f}.png'
        bpy.ops.render.render(write_still=True)
elif MODE == 'wire':
    sc.frame_set(FREEZE)
    sc.camera = macro
    wm = bal.modifiers.new('wf', 'WIREFRAME')
    wm.thickness = 0.004
    em = bpy.data.materials.new('wire')
    em.use_nodes = True
    nt = em.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = (1.0, 0.35, 0.08, 1)
    e.inputs[1].default_value = 3.0
    nt.links.new(e.outputs[0], nt.nodes['Material Output'].inputs[0])
    bal.data.materials[0] = em
    sc.render.filepath = '/home/claude/b3d/wire.png'
    bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = '/home/claude/b3d/frames/b'
    bpy.ops.render.render(animation=True)
