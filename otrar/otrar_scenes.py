# -*- coding: utf-8 -*-
"""
Otrar caravan reel: glossy 3D cutaway diorama, built procedurally in Blender.

Run (Windows, Blender 4.3+):
  blender.exe -b -P otrar_scenes.py -- --scene all --out renders
Options:
  --scene  s1..s8 | all          which shot(s) to render
  --out    folder                output folder (mp4 per scene, or png stills)
  --pct    100                   resolution percentage of 1080x1920
  --engine EEVEE | CYCLES
  --samples N                    render samples (EEVEE TAA / Cycles)
  --still  f1,f2,...             render only these frame numbers (local frames) as PNG
  --save   1                     also save the .blend per scene
"""
import bpy, bmesh, math, os, sys, json, random
from mathutils import Vector, Euler, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30

# ------------------------------------------------------------------ args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None):
    if "--" + name in argv:
        return argv[argv.index("--" + name) + 1]
    return default

TIMELINE = json.load(open(os.path.join(HERE, "timeline.json")))

# ------------------------------------------------------------------ helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def lerp(a, b, t):
    return a + (b - a) * t

def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    random.seed(7)

MATS = {}

def mat(name, color, rough=0.45, metal=0.0, emit=None, emit_str=0.0, coat=0.25,
        tex=None, alpha=1.0):
    key = name
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    col = tuple(color) + (1.0,) if len(color) == 3 else tuple(color)
    p.inputs["Base Color"].default_value = col
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    for nm, v in (("Coat Weight", coat), ("Coat Roughness", 0.25)):
        if nm in p.inputs:
            p.inputs[nm].default_value = v
    if emit is not None:
        ec = "Emission Color" if "Emission Color" in p.inputs else "Emission"
        p.inputs[ec].default_value = tuple(emit) + (1.0,)
        p.inputs["Emission Strength"].default_value = emit_str
    if tex == "brick":
        _brick(nt, p, color)
    elif tex == "soil":
        _soil(nt, p)
    elif tex == "sand":
        _noise_tint(nt, p, color, 0.10, 3.0)
    elif tex == "carpet":
        _carpet(nt, p, color)
    elif tex == "tile":
        _tile(nt, p, color)
    elif tex == "noise":
        _noise_tint(nt, p, color, 0.08, 6.0)
    m.diffuse_color = col
    MATS[key] = m
    return m

def _noise_tint(nt, p, color, amt, scale):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[6].default_value = tuple(c * (1 - amt) for c in color) + (1,)
    mix.inputs[7].default_value = tuple(min(1, c * (1 + amt)) for c in color) + (1,)
    nt.links.new(nz.outputs["Fac"], mix.inputs[0])
    nt.links.new(mix.outputs[2], p.inputs["Base Color"])

def _brick(nt, p, color):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = tuple(color) + (1,)
    br.inputs["Color2"].default_value = tuple(c * 0.88 for c in color) + (1,)
    br.inputs["Mortar"].default_value = tuple(min(1, c * 1.12) for c in color) + (1,)
    br.inputs["Scale"].default_value = 1.6
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Brick Width"].default_value = 0.6
    br.inputs["Row Height"].default_value = 0.22
    # project with object coords: use x+y so bricks show on both faces
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    com = nt.nodes.new("ShaderNodeCombineXYZ")
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs[0], add.inputs[0])
    nt.links.new(sep.outputs[1], add.inputs[1])
    nt.links.new(add.outputs[0], com.inputs[0])
    nt.links.new(sep.outputs[2], com.inputs[1])
    nt.links.new(com.outputs[0], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.6

def _soil(nt, p):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.2
    nz.inputs["Detail"].default_value = 6
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "MULTIPLY_ADD"
    add.inputs[1].default_value = 0.35
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], add.inputs[0])
    nt.links.new(sep.outputs[2], add.inputs[2])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.15
    cr.elements[0].color = (0.30, 0.13, 0.07, 1)
    cr.elements[1].position = 0.95
    cr.elements[1].color = (0.36, 0.25, 0.15, 1)
    e = cr.elements.new(0.45); e.color = (0.52, 0.23, 0.11, 1)
    e = cr.elements.new(0.70); e.color = (0.62, 0.36, 0.18, 1)
    e = cr.elements.new(0.86); e.color = (0.45, 0.30, 0.17, 1)
    nt.links.new(add.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.75
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = 0.1

def _carpet(nt, p, color):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ch = nt.nodes.new("ShaderNodeTexChecker")
    ch.inputs["Scale"].default_value = 6
    ch.inputs["Color1"].default_value = tuple(color) + (1,)
    ch.inputs["Color2"].default_value = (0.75, 0.55, 0.15, 1)
    nt.links.new(tc.outputs["UV"], ch.inputs["Vector"])
    nt.links.new(ch.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9

def _tile(nt, p, color):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ch = nt.nodes.new("ShaderNodeTexChecker")
    ch.inputs["Scale"].default_value = 14
    ch.inputs["Color1"].default_value = tuple(color) + (1,)
    ch.inputs["Color2"].default_value = tuple(c * 0.7 for c in color) + (1,)
    nt.links.new(tc.outputs["Generated"], ch.inputs["Vector"])
    nt.links.new(ch.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.2

def outline_mat():
    if "OUTLINE" in MATS:
        return MATS["OUTLINE"]
    m = bpy.data.materials.new("OUTLINE")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.72, 0.18, 1)
    em.inputs["Strength"].default_value = 4.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
    nt.links.new(em.outputs[0], mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    m.use_backface_culling = True
    for attr, val in (("blend_method", "HASHED"), ("surface_render_method", "DITHERED")):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    MATS["OUTLINE"] = m
    return m

COLL = None

def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob

def mesh_obj(name, bm, material, parent=None, bevel=0.0, smooth_shade=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    link(ob)
    if material:
        me.materials.append(material)
    if smooth_shade:
        for poly in me.polygons:
            poly.use_smooth = True
    if bevel > 0:
        md = ob.modifiers.new("bev", "BEVEL")
        md.width = bevel
        md.segments = 2
        md.limit_method = "ANGLE"
    if parent:
        ob.parent = parent
    return ob

def box(name, size, loc, material, parent=None, bevel=0.03, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    ob = mesh_obj(name, bm, material, parent, bevel=min(bevel, min(size) * 0.3))
    ob.location = loc
    ob.rotation_euler = rot
    return ob

def cyl(name, r, h, loc, material, parent=None, seg=24, r2=None, rot=(0, 0, 0),
        bevel=0.0, smooth_shade=True, half=False, cap=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg,
                          radius1=r, radius2=(r if r2 is None else r2), depth=h)
    if half:
        _cut_half(bm)
    ob = mesh_obj(name, bm, material, parent, bevel=bevel, smooth_shade=smooth_shade)
    ob.location = loc
    ob.rotation_euler = rot
    if smooth_shade:
        _autosmooth(ob)
    return ob

def sphere(name, r, loc, material, parent=None, scale=(1, 1, 1), seg=24, half=False,
           hemi=False):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    if hemi:
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context="VERTS")
    if half:
        _cut_half(bm)
    ob = mesh_obj(name, bm, material, parent, smooth_shade=True)
    ob.location = loc
    ob.scale = scale
    return ob

def _cut_half(bm):
    """Remove geometry with y < 0 (front half), fill the cut with a cap."""
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                 plane_co=(0, 0, 0), plane_no=(0, 1, 0),
                                 clear_inner=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    try:
        bmesh.ops.edgeloop_fill(bm, edges=edges)
    except Exception:
        try:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        except Exception:
            pass

def half_tube(name, r, thick, h, loc, material, parent=None, seg=32, r_top=None,
              material_cut=None):
    """Hollow half-cylinder (back half, y>=0) with visible section faces."""
    rt = r if r_top is None else r_top
    bm = bmesh.new()
    rings = []
    for (z, rr) in ((-h / 2, r), (h / 2, rt)):
        outer = [bm.verts.new((math.cos(math.pi * i / seg) * rr, math.sin(math.pi * i / seg) * rr, z))
                 for i in range(seg + 1)]
        inner = [bm.verts.new((math.cos(math.pi * i / seg) * (rr - thick),
                               math.sin(math.pi * i / seg) * (rr - thick), z)) for i in range(seg + 1)]
        rings.append((outer, inner))
    (o0, i0), (o1, i1) = rings
    for k in range(seg):
        bm.faces.new((o0[k], o0[k + 1], o1[k + 1], o1[k]))      # outer
        bm.faces.new((i0[k + 1], i0[k], i1[k], i1[k + 1]))      # inner
        bm.faces.new((o1[k], o1[k + 1], i1[k + 1], i1[k]))      # top
        bm.faces.new((o0[k + 1], o0[k], i0[k], i0[k + 1]))      # bottom
    cut_faces = [bm.faces.new((o0[0], i0[0], i1[0], o1[0])),
                 bm.faces.new((i0[seg], o0[seg], o1[seg], i1[seg]))]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if material_cut is not None:
        for f in cut_faces:
            f.material_index = 1
    ob = mesh_obj(name, bm, material, parent, smooth_shade=True)
    if material_cut is not None:
        ob.data.materials.append(material_cut)
    _autosmooth(ob)
    ob.location = loc
    return ob

def _autosmooth(ob):
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
        ob.select_set(False)
    except Exception:
        pass

def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    link(e)
    e.location = loc
    if parent:
        e.parent = parent
    return e

def add_outline(root, strength=6.0):
    """Soft golden contour: rim emission on every material of this figure."""
    cache = {}
    for ob in [root] + list(root.children_recursive):
        if ob.type != "MESH":
            continue
        for i, m0 in enumerate(ob.data.materials):
            if m0 is None:
                continue
            if m0.name not in cache:
                m = m0.copy()
                m.name = m0.name + "_hero"
                nt = m.node_tree
                p = nt.nodes.get("Principled BSDF")
                lw = nt.nodes.new("ShaderNodeLayerWeight")
                lw.inputs["Blend"].default_value = 0.35
                pw = nt.nodes.new("ShaderNodeMath")
                pw.operation = "POWER"
                pw.inputs[1].default_value = 2.2
                mul = nt.nodes.new("ShaderNodeMath")
                mul.operation = "MULTIPLY"
                mul.inputs[1].default_value = strength
                nt.links.new(lw.outputs["Facing"], pw.inputs[0])
                nt.links.new(pw.outputs[0], mul.inputs[0])
                ec = "Emission Color" if "Emission Color" in p.inputs else "Emission"
                p.inputs[ec].default_value = (1.0, 0.70, 0.15, 1)
                nt.links.new(mul.outputs[0], p.inputs["Emission Strength"])
                cache[m0.name] = m
            ob.data.materials[i] = cache[m0.name]

def text3d(name, body, loc, size, material, parent=None, rot=(math.radians(90), 0, 0),
           extrude=0.02, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    fp = os.path.join(HERE, "fonts", "Montserrat-ExtraBold.ttf")
    if os.path.exists(fp):
        cu.font = bpy.data.fonts.load(fp)
    ob = bpy.data.objects.new(name, cu)
    link(ob)
    cu.materials.append(material)
    ob.location = loc
    ob.rotation_euler = rot
    if parent:
        ob.parent = parent
    return ob

# --------------------------------------------------------- animation (baked)
SCENE_LEN = 0

def key(ob, f, loc=None, rot=None, scale=None):
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=f)
    if rot is not None:
        ob.rotation_euler = rot
        ob.keyframe_insert("rotation_euler", frame=f)
    if scale is not None:
        ob.scale = scale if hasattr(scale, "__len__") else (scale,) * 3
        ob.keyframe_insert("scale", frame=f)

def bake(fn, step=1):
    """fn(f, t) called for every frame; t = seconds since shot start."""
    for f in range(1, SCENE_LEN + 1, step):
        fn(f, (f - 1) / FPS)
    if (SCENE_LEN - 1) % step:
        fn(SCENE_LEN, (SCENE_LEN - 1) / FPS)

def look_rot(cam_loc, target):
    d = Vector(target) - Vector(cam_loc)
    return d.to_track_quat("-Z", "Y").to_euler()

# ----------------------------------------------------------- world & render
def setup_world(top=(0.22, 0.42, 0.85), horizon=(0.72, 0.84, 0.96), strength=0.9):
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = tuple(horizon) + (1,)
    ramp.color_ramp.elements[1].position = 0.35
    ramp.color_ramp.elements[1].color = tuple(top) + (1,)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    # generated coords of world = view direction; use z (-1..1) mapped
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = 0.0
    mp.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs[2], mp.inputs["Value"])
    nt.links.new(mp.outputs[0], ramp.inputs[0])
    # what the camera sees directly: a richer sky; lighting uses the softer ramp
    ramp2 = nt.nodes.new("ShaderNodeValToRGB")
    ramp2.color_ramp.elements[0].position = 0.0
    ramp2.color_ramp.elements[0].color = tuple(min(1, c * 1.15) for c in horizon) + (1,)
    ramp2.color_ramp.elements[1].position = 0.30
    ramp2.color_ramp.elements[1].color = tuple(c * 1.0 for c in top) + (1,)
    nt.links.new(mp.outputs[0], ramp2.inputs[0])
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(ramp.outputs[0], mix.inputs[6])
    sc = nt.nodes.new("ShaderNodeMath")
    sc.operation = "MULTIPLY"
    nt.links.new(ramp2.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength

def sun(rot=(50, 0, 35), energy=4.0, color=(1, 0.90, 0.75), angle=4):
    ld = bpy.data.lights.new("sun", "SUN")
    ld.energy = energy
    ld.color = color
    ld.angle = math.radians(angle)
    ob = bpy.data.objects.new("sun", ld)
    link(ob)
    ob.rotation_euler = [math.radians(a) for a in rot]
    return ob

def point(loc, energy=200, color=(1, 0.6, 0.25), radius=0.15):
    ld = bpy.data.lights.new("pt", "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new("pt", ld)
    link(ob)
    ob.location = loc
    return ob

def camera(lens=50):
    cd = bpy.data.cameras.new("cam")
    cd.lens = lens
    cd.clip_start = 0.1
    cd.clip_end = 1000
    ob = bpy.data.objects.new("cam", cd)
    link(ob)
    bpy.context.scene.camera = ob
    return ob

def setup_render(engine, samples, pct):
    sc = bpy.context.scene
    sc.render.resolution_x = 1080
    sc.render.resolution_y = 1920
    sc.render.resolution_percentage = pct
    sc.render.fps = FPS
    sc.frame_start = 1
    sc.frame_end = SCENE_LEN
    if engine == "CYCLES":
        sc.render.engine = "CYCLES"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for dev in ("OPTIX", "CUDA"):
                try:
                    prefs.compute_device_type = dev
                    prefs.get_devices()
                    if any(d.type == dev for d in prefs.devices):
                        for d in prefs.devices:
                            d.use = d.type == dev
                        sc.cycles.device = "GPU"
                        break
                except Exception:
                    pass
        except Exception:
            pass
        sc.cycles.max_bounces = 6
    else:
        for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = e
                break
            except Exception:
                pass
        ev = sc.eevee
        for attr, val in (("taa_render_samples", samples), ("use_shadows", True),
                          ("shadow_ray_count", 2), ("shadow_step_count", 8),
                          ("use_raytracing", True), ("ray_tracing_method", "SCREEN"),
                          ("use_gtao", True), ("gtao_distance", 1.0),
                          ("use_soft_shadows", True), ("use_bloom", False),
                          ("fast_gi_method", "GLOBAL_ILLUMINATION"),
                          ("use_fast_gi", True)):
            try:
                setattr(ev, attr, val)
            except Exception:
                pass
        try:
            ev.ray_tracing_options.resolution_scale = "1"
        except Exception:
            pass
    vs = sc.view_settings
    vs.view_transform = VIEW
    try:
        vs.look = LOOK
    except Exception:
        pass
    vs.exposure = EXPOSURE
    sc.render.film_transparent = False

VIEW = os.environ.get("OT_VIEW", "Standard")
LOOK = os.environ.get("OT_LOOK", "Medium High Contrast")
EXPOSURE = float(os.environ.get("OT_EXP", "-1.1"))
# ----------------------------------------------------------------- palette
C = dict(
    brick=(0.78, 0.55, 0.34), brick2=(0.66, 0.45, 0.27), section=(0.58, 0.38, 0.23),
    sand=(0.80, 0.62, 0.38), steppe=(0.66, 0.56, 0.30), wood=(0.45, 0.27, 0.13),
    camel=(0.74, 0.55, 0.33), skin=(0.85, 0.62, 0.45), brown=(0.30, 0.15, 0.07),
    cream=(0.93, 0.88, 0.76), green=(0.08, 0.30, 0.18), white=(0.95, 0.95, 0.93),
    black=(0.03, 0.03, 0.03), steel=(0.6, 0.62, 0.66), red=(0.65, 0.08, 0.06),
    blue=(0.10, 0.25, 0.60), teal=(0.05, 0.50, 0.50), gold=(1.0, 0.72, 0.25),
    silver=(0.85, 0.86, 0.88), felt=(0.90, 0.86, 0.78), turq=(0.10, 0.62, 0.72),
)

def M(name):
    presets = {
        "brick": dict(color=C["brick"], tex="brick", rough=0.6),
        "brick2": dict(color=C["brick2"], tex="brick", rough=0.6),
        "section": dict(color=C["section"], tex="noise", rough=0.7),
        "sand": dict(color=C["sand"], tex="sand", rough=0.8, coat=0.05),
        "steppe": dict(color=C["steppe"], tex="sand", rough=0.85, coat=0.05),
        "soil": dict(color=(0.5, 0.3, 0.2), tex="soil"),
        "wood": dict(color=C["wood"], tex="noise", rough=0.5),
        "camel": dict(color=C["camel"], rough=0.55),
        "skin": dict(color=C["skin"], rough=0.45),
        "brown": dict(color=C["brown"], rough=0.5),
        "cream": dict(color=C["cream"], rough=0.5),
        "green": dict(color=C["green"], rough=0.45),
        "white": dict(color=C["white"], rough=0.45),
        "black": dict(color=C["black"], rough=0.35),
        "steel": dict(color=C["steel"], rough=0.25, metal=1.0),
        "red": dict(color=C["red"], rough=0.4),
        "blue": dict(color=C["blue"], rough=0.4),
        "teal": dict(color=C["teal"], rough=0.35),
        "gold": dict(color=C["gold"], rough=0.18, metal=1.0, coat=0.0),
        "silver": dict(color=C["silver"], rough=0.15, metal=1.0, coat=0.0),
        "felt": dict(color=C["felt"], tex="noise", rough=0.85, coat=0.0),
        "turq": dict(color=C["turq"], tex="tile", rough=0.2, coat=0.6),
        "carpet": dict(color=(0.55, 0.06, 0.06), tex="carpet"),
        "fire": dict(color=(1, 0.5, 0.1), emit=(1, 0.45, 0.08), emit_str=12),
        "lamp": dict(color=(1, 0.7, 0.3), emit=(1, 0.6, 0.2), emit_str=8),
        "flag": dict(color=(0.06, 0.06, 0.08), rough=0.6),
        "bubble": dict(color=(0.98, 0.97, 0.94), rough=0.3),
        "darkred": dict(color=(0.45, 0.04, 0.04), rough=0.4),
        "fur": dict(color=(0.30, 0.20, 0.12), tex="noise", rough=0.9, coat=0.0),
        "rope": dict(color=(0.6, 0.5, 0.3), rough=0.8),
        "silk_r": dict(color=(0.75, 0.05, 0.12), rough=0.15, coat=0.8),
        "silk_b": dict(color=(0.10, 0.30, 0.80), rough=0.15, coat=0.8),
        "silk_y": dict(color=(0.95, 0.70, 0.10), rough=0.15, coat=0.8),
        "silk_g": dict(color=(0.05, 0.55, 0.35), rough=0.15, coat=0.8),
        "bale_a": dict(color=(0.55, 0.16, 0.10), tex="noise", rough=0.8),
        "bale_b": dict(color=(0.20, 0.30, 0.45), tex="noise", rough=0.8),
        "bale_c": dict(color=(0.55, 0.45, 0.25), tex="noise", rough=0.8),
        "horse": dict(color=(0.30, 0.17, 0.09), rough=0.5),
        "paper": dict(color=(0.95, 0.88, 0.70), rough=0.6),
        "stone": dict(color=(0.45, 0.42, 0.40), tex="noise", rough=0.7),
    }
    p = presets[name]
    return mat(name, **p)

# ------------------------------------------------------------- diorama base
def diorama_base(x0, x1, y0, y1, depth=3.0, top="sand", name="base"):
    sx, sy = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box(name + "_top", (sx, sy, 0.2), (cx, cy, -0.1), M(top), bevel=0.05)
    box(name + "_soil", (sx, sy, depth), (cx, cy, -0.2 - depth / 2), M("soil"), bevel=0.08)
    # dark plinth under it, like a museum base
    box(name + "_plinth", (sx + 0.4, sy + 0.4, 0.5), (cx, cy, -0.2 - depth - 0.25),
        mat("plinth", (0.08, 0.06, 0.05), rough=0.25, coat=0.8), bevel=0.06)

# ------------------------------------------------------------------ people
class Person:
    def __init__(self, name, robe, hat="turban", hat_mat="white", beard=None,
                 spear=False, outline=False, scale=1.0, sash="gold"):
        self.root = empty(name)
        self.root.scale = (scale,) * 3
        r = self.root
        self.body = empty(name + "_body", (0, 0, 0), r)
        b = self.body
        rm = M(robe) if isinstance(robe, str) else robe
        cyl(name + "_robe", 0.30, 1.05, (0, 0, 0.58), rm, b, r2=0.21, seg=20)
        cyl(name + "_chest", 0.22, 0.32, (0, 0, 1.22), rm, b, r2=0.18, seg=20)
        cyl(name + "_sash", 0.235, 0.09, (0, 0, 1.03), M(sash), b, seg=20)
        self.head = empty(name + "_headpivot", (0, 0, 1.42), b)
        h = self.head
        sphere(name + "_head", 0.17, (0, 0, 0.12), M("skin"), h, scale=(1, 0.95, 1.05))
        sphere(name + "_eyeL", 0.025, (-0.06, -0.155, 0.15), M("black"), h)
        sphere(name + "_eyeR", 0.025, (0.06, -0.155, 0.15), M("black"), h)
        sphere(name + "_nose", 0.03, (0, -0.17, 0.10), M("skin"), h)
        if beard:
            cyl(name + "_beard", 0.11, 0.24, (0, -0.10, -0.04), M(beard), h, r2=0.02,
                rot=(math.radians(200), 0, 0), seg=14)
            box(name + "_moust", (0.14, 0.03, 0.03), (0, -0.165, 0.055), M(beard), h, bevel=0.01)
        if hat == "turban":
            sphere(name + "_turban", 0.20, (0, 0.0, 0.24), M(hat_mat), h, scale=(1, 1, 0.75))
            cyl(name + "_turbanring", 0.19, 0.10, (0, 0, 0.19), M(hat_mat), h, r2=0.20)
        elif hat == "chalma":
            sphere(name + "_turban", 0.185, (0, 0.0, 0.22), M(hat_mat), h, scale=(1, 1, 0.6))
            cyl(name + "_turbanring", 0.18, 0.08, (0, 0, 0.18), M(hat_mat), h)
        elif hat == "helmet":
            sphere(name + "_helm", 0.19, (0, 0, 0.17), M("steel"), h, hemi=True)
            cyl(name + "_spike", 0.05, 0.22, (0, 0, 0.42), M("steel"), h, r2=0.005, seg=10)
            cyl(name + "_rim", 0.20, 0.04, (0, 0, 0.17), M("steel"), h)
        elif hat == "fur":
            cyl(name + "_fur", 0.21, 0.16, (0, 0, 0.22), M("fur"), h, r2=0.20)
            sphere(name + "_furtop", 0.16, (0, 0, 0.30), M("red"), h, scale=(1, 1, 0.6), hemi=True)
        # arms
        self.arms = []
        for sx in (-1, 1):
            sh = empty(name + "_sh%d" % sx, (0.25 * sx, 0, 1.32), b)
            cyl(name + "_arm%d" % sx, 0.075, 0.55, (0, 0, -0.27), rm, sh, r2=0.065, seg=12)
            sphere(name + "_hand%d" % sx, 0.065, (0, 0, -0.57), M("skin"), sh)
            self.arms.append(sh)
        # feet
        self.feet = []
        for sx in (-1, 1):
            ft = empty(name + "_ft%d" % sx, (0.11 * sx, 0, 0.0), r)
            box(name + "_foot%d" % sx, (0.13, 0.24, 0.10), (0, -0.04, 0.05), M("black"), ft, bevel=0.04)
            self.feet.append(ft)
        if spear:
            self.spear = empty(name + "_spearpiv", (0, 0, -0.55), self.arms[1])
            cyl(name + "_shaft", 0.025, 2.4, (0, 0, 0.6), M("wood"), self.spear, seg=8)
            cyl(name + "_tip", 0.06, 0.25, (0, 0, 1.9), M("steel"), self.spear, r2=0.0, seg=8)
        if outline:
            add_outline(self.root)

    def pose(self, f, loc, heading, walk=0.0, phase=0.0, arm_raise=(0, 0), bob=True,
             head_turn=0.0, head_tilt=0.0, sit=False, lean=0.0):
        """heading: angle (rad) the person faces, 0 = -Y (towards camera)."""
        if getattr(self, "riding", False):
            loc, sit, walk = (0, 0, -0.15), True, 0.0
        ph = phase * 2 * math.pi
        dz = abs(math.sin(ph)) * 0.05 * walk if bob else 0
        key(self.root, f, loc=(loc[0], loc[1], loc[2] + dz), rot=(0, 0, heading))
        key(self.body, f, rot=(lean + 0.04 * walk, 0, math.sin(ph) * 0.04 * walk),
            loc=(0, 0, -0.38 if sit else 0))
        for i, sh in enumerate(self.arms):
            s = 1 if i == 0 else -1
            swing = math.sin(ph) * 0.6 * walk * s
            key(sh, f, rot=(swing - arm_raise[i], 0, 0.08 * (1 if i else -1)))
        for i, ft in enumerate(self.feet):
            s = 1 if i == 0 else -1
            fw = math.sin(ph) * 0.28 * walk * s
            up = max(0, math.cos(ph) * s) * 0.10 * walk
            if getattr(self, "riding", False):
                key(ft, f, loc=(0.42 * (-1 if i == 0 else 1), -0.15, 0.05))
            elif sit:
                key(ft, f, loc=(ft.location.x, -0.45, 0.0))
            else:
                key(ft, f, loc=(ft.location.x, -fw, up))
        key(self.head, f, rot=(head_tilt, 0, head_turn))

# ------------------------------------------------------------------ animals
class Quadruped:
    def __init__(self, name, kind="camel", outline_rider=None, bales=None):
        self.root = empty(name)
        r = self.root
        self.body = empty(name + "_body", (0, 0, 0), r)
        b = self.body
        if kind == "camel":
            m = M("camel")
            hb = 1.55
            sphere(name + "_torso", 0.5, (0, 0, hb), m, b, scale=(0.95, 1.9, 0.85))
            sphere(name + "_hump", 0.42, (0, 0.15, hb + 0.38), m, b, scale=(0.9, 1.3, 1.0))
            cyl(name + "_neck", 0.17, 1.0, (0, -0.95, hb + 0.35), m, b, r2=0.13,
                rot=(math.radians(38), 0, 0), seg=14)
            sphere(name + "_head", 0.2, (0, -1.38, hb + 0.82), m, b, scale=(0.8, 1.6, 0.8))
            sphere(name + "_eyeL", 0.03, (-0.14, -1.45, hb + 0.9), M("black"), b)
            sphere(name + "_eyeR", 0.03, (0.14, -1.45, hb + 0.9), M("black"), b)
            leg_len, leg_r, lx, ly = 1.35, 0.09, 0.28, 0.62
            sphere(name + "_bell", 0.07, (0, -0.85, hb + 0.05), M("gold"), b)
        else:  # horse
            m = M("horse")
            hb = 1.25
            sphere(name + "_torso", 0.42, (0, 0, hb), m, b, scale=(0.85, 2.0, 0.85))
            cyl(name + "_neck", 0.15, 0.8, (0, -0.85, hb + 0.35), m, b, r2=0.12,
                rot=(math.radians(32), 0, 0), seg=14)
            sphere(name + "_head", 0.18, (0, -1.15, hb + 0.7), m, b, scale=(0.75, 1.7, 0.8))
            box(name + "_mane", (0.06, 0.6, 0.18), (0, -0.85, hb + 0.5), M("black"), b,
                rot=(math.radians(32), 0, 0))
            cyl(name + "_tail", 0.07, 0.6, (0, 0.85, hb - 0.05), M("black"), b, r2=0.02,
                rot=(math.radians(30), 0, 0))
            leg_len, leg_r, lx, ly = 1.1, 0.07, 0.22, 0.62
        self.hb = hb
        self.legs = []
        for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            hp = empty(name + "_hip%d" % i, (lx * sx, ly * sy, hb - 0.15), b)
            cyl(name + "_leg%d" % i, leg_r, leg_len, (0, 0, -leg_len / 2), m, hp,
                r2=leg_r * 0.75, seg=10)
            sphere(name + "_hoof%d" % i, leg_r * 1.1, (0, 0, -leg_len), M("brown"), hp)
            self.legs.append((hp, sx * sy))
        self.saddle = empty(name + "_saddle", (0, 0.15 if kind == "camel" else 0,
                                               hb + (0.75 if kind == "camel" else 0.42)), b)
        self.bales = []
        if bales:
            for sx in (-1, 1):
                bl = box(name + "_bale%d" % sx, (0.38, 0.75, 0.55),
                         (0.62 * sx, 0.1, hb + 0.05), M(bales), b, bevel=0.08)
                box(name + "_rope%d" % sx, (0.40, 0.06, 0.57), (0.62 * sx, 0.1, hb + 0.05),
                    M("rope"), b, bevel=0.01)
                self.bales.append(bl)

    def pose(self, f, loc, heading, walk=0.0, phase=0.0, gallop=False):
        ph = phase * 2 * math.pi
        dz = abs(math.sin(ph)) * (0.12 if gallop else 0.04) * walk
        key(self.root, f, loc=(loc[0], loc[1], loc[2] + dz), rot=(0, 0, heading))
        key(self.body, f, rot=(math.sin(ph) * (0.08 if gallop else 0.02) * walk, 0, 0))
        for i, (hp, s) in enumerate(self.legs):
            off = (0 if i < 2 else 0.5) if gallop else 0
            a = math.sin(ph + off * 2 * math.pi) * (0.6 if gallop else 0.35) * walk * (1 if gallop else s)
            key(hp, f, rot=(a, 0, 0))

def ride(person, animal):
    person.root.parent = animal.saddle
    person.root.location = (0, 0, -0.15)
    person.riding = True

# ------------------------------------------------------------------ props
def bale_cutaway(name, loc, parent=None, kind=0, side=-1):
    """An opened bale seen in section: shell open on the outer side, layered contents."""
    g = empty(name, loc, parent)
    sh = M(["bale_a", "bale_b", "bale_c"][kind % 3])
    W, D, H = 0.46, 0.85, 0.66   # W across (x), D along camel (y)
    t = 0.04
    box(name + "_inner", (t, D, H), (-side * (W / 2 - t / 2), 0, 0), sh, g, bevel=0.01)
    box(name + "_bot", (W, D, t), (0, 0, -H / 2 + t / 2), sh, g, bevel=0.01)
    box(name + "_top", (W, D, t), (0, 0, H / 2 - t / 2), sh, g, bevel=0.01)
    for sy in (-1, 1):
        box(name + "_end%d" % sy, (W, t, H), (0, sy * (D / 2 - t / 2), 0), sh, g, bevel=0.01)
    z = -H / 2 + t
    # two layers of gold bars
    for layer in range(2):
        for i in range(4):
            for j in range(2):
                box(name + "_gb%d%d%d" % (layer, i, j), (0.08, 0.17, 0.065),
                    (-0.09 + j * 0.18, -0.3 + i * 0.2, z + 0.035), M("gold"), g, bevel=0.015)
        z += 0.075
    # silver coins
    for i in range(5):
        for j in range(2):
            cyl(name + "_sc%d%d" % (i, j), 0.065, 0.06, (-0.09 + j * 0.18, -0.32 + i * 0.16, z + 0.035),
                M("silver"), g, seg=16)
    z += 0.08
    silks = ["silk_r", "silk_b", "silk_y", "silk_g"]
    for i in range(4):
        cyl(name + "_silk%d" % i, 0.08, D - 0.12, (-0.1 + (i % 2) * 0.2, 0, z + 0.085 + (i // 2) * 0.16),
            M(silks[(i + kind) % 4]), g, rot=(math.radians(90), 0, 0), seg=20)
    return g

def torch(loc, parent=None, light=True, energy=60):
    g = empty("torch", loc, parent)
    cyl("torch_stick", 0.03, 0.4, (0, 0, 0), M("wood"), g, seg=8)
    sphere("torch_fire", 0.07, (0, 0, 0.25), M("fire"), g, scale=(1, 1, 1.5))
    if light:
        p = point((0, 0, 0.35), energy=energy)
        p.parent = g
    return g

def flag(name, loc, parent=None, h=3.0, col="flag"):
    g = empty(name, loc, parent)
    cyl(name + "_pole", 0.03, h, (0, 0, h / 2), M("wood"), g, seg=6, smooth_shade=False)
    box(name + "_cloth", (0.03, 0.8, 0.55), (0, 0.4, h - 0.35), M(col), g, bevel=0.0)
    return g

# ------------------------------------------------------------------ Otrar wall
def otrar_wall(x0, x1, y=0.0, h=7.0, t=4.0, gate_x=None, towers=(), night=False,
               rooms_lit=False, name="wall"):
    """Wall along X, centred at y, front half (y<y) removed: rooms visible."""
    B = M("brick")
    B2 = M("brick2")
    S = M("section")
    W = M("wood")
    yb = y + t / 2  # back face
    gw = 3.6  # gate width
    segs = []
    if gate_x is None:
        segs = [(x0, x1)]
    else:
        segs = [(x0, gate_x - gw / 2), (gate_x + gw / 2, x1)]
    objs = {}
    for si, (a, b) in enumerate(segs):
        L = b - a
        cx = (a + b) / 2
        # back slab (outer skin)
        box(f"{name}_back{si}", (L, 0.9, h), (cx, yb - 0.45, h / 2), B, bevel=0.05)
        # floors
        box(f"{name}_f0_{si}", (L, t, 0.3), (cx, y, 0.15), S, bevel=0.03)
        box(f"{name}_f1_{si}", (L, t - 0.9, 0.35), (cx, y - 0.45, h * 0.47), S, bevel=0.03)
        box(f"{name}_top{si}", (L, t, 0.6), (cx, y, h - 0.3), B2, bevel=0.05)
        # merlons on both edges
        n = int(L / 1.1)
        for k in range(n):
            xm = a + (k + 0.5) * L / n
            for yy in (y - t / 2 + 0.25, yb - 0.25):
                box(f"{name}_mer{si}_{k}_{yy:.1f}", (0.6, 0.5, 0.7), (xm, yy, h + 0.35), B, bevel=0.06)
        # partitions -> rooms
        nr = max(1, int(L / 4.2))
        for k in range(nr + 1):
            xp = a + k * L / nr
            xp = min(max(xp, a + 0.25), b - 0.25)
            box(f"{name}_part{si}_{k}", (0.5, t - 0.9, h - 0.6), (xp, y - 0.45, (h - 0.6) / 2),
                S, bevel=0.03)
        # room contents: stairs, lamps, shelves
        for k in range(nr):
            rx0 = a + k * L / nr + 0.3
            rx1 = a + (k + 1) * L / nr - 0.3
            rc = (rx0 + rx1) / 2
            if k % 2 == 0:
                # stair from ground to first floor
                steps = 9
                for s in range(steps):
                    box(f"{name}_st{si}_{k}_{s}", (0.35, 1.2, 0.33 * (s + 1)),
                        (rx0 + 0.25 + s * 0.33, yb - 1.55, 0.165 * (s + 1) + 0.3), B2, bevel=0.02)
            else:
                # guard room: bench + spears on the wall
                box(f"{name}_bench{si}_{k}", (1.6, 0.5, 0.45), (rc, yb - 1.25, 0.52), W, bevel=0.03)
                for s in range(3):
                    cyl(f"{name}_sp{si}_{k}_{s}", 0.025, 2.0, (rc - 0.5 + s * 0.5, yb - 0.98, 1.4),
                        W, seg=6, rot=(math.radians(8), 0, 0))
            # upper floor: storage jars
            for s in range(3):
                cyl(f"{name}_jar{si}_{k}_{s}", 0.22, 0.55, (rc - 0.7 + s * 0.7, yb - 1.4, h * 0.47 + 0.45),
                    mat("jar", (0.62, 0.34, 0.18), rough=0.4), r2=0.12, seg=16)
            # lamp niche
            box(f"{name}_niche{si}_{k}", (0.3, 0.1, 0.3), (rc, yb - 0.93, h * 0.47 + 1.5), M("lamp"), bevel=0.02)
            if rooms_lit:
                point((rc, yb - 1.6, h * 0.47 + 1.6), energy=80 if night else 25)
                point((rc, yb - 1.6, 2.4), energy=80 if night else 25)
        objs[si] = (a, b)
    # gate
    if gate_x is not None:
        gx = gate_x
        box(f"{name}_lintel", (gw + 0.6, t, h - 4.2), (gx, y, 4.2 + (h - 4.2) / 2), B2, bevel=0.05)
        doors = []
        for sx in (-1, 1):
            hinge = empty(f"{name}_hinge{sx}", (gx + sx * gw / 2, yb - 0.6, 0))
            box(f"{name}_door{sx}", (gw / 2, 0.25, 4.0), (-sx * gw / 4, 0, 2.0), W, hinge, bevel=0.04)
            for k in range(3):
                box(f"{name}_band{sx}{k}", (gw / 2, 0.28, 0.12), (-sx * gw / 4, 0, 0.7 + k * 1.3),
                    M("black"), hinge, bevel=0.01)
            doors.append(hinge)
        objs["doors"] = doors
    # towers (half cylinders, hollow with spiral stair)
    for ti, tx in enumerate(towers):
        R = 2.6
        th = h + 2.5
        half_tube(f"{name}_tw{ti}", R, 0.6, th, (tx, y + 0.3, th / 2), B, seg=40, material_cut=S)
        cyl(f"{name}_twfloor{ti}", R - 0.3, 0.3, (tx, y + 0.3, 0.15), S, seg=40, half=True)
        cyl(f"{name}_twcol{ti}", 0.35, th, (tx, y + 0.9, th / 2), S, seg=16)
        # spiral steps on back half
        ns = 30
        for s in range(ns):
            ang = math.pi * 0.05 + (s / ns) * math.pi * 2.6
            # only keep steps behind the cut (y >= 0 in tower space)
            sx = math.cos(ang)
            sy = math.sin(ang)
            ang_back = ang % (2 * math.pi)
            r = 1.2
            stp = box(f"{name}_tws{ti}_{s}", (1.3, 0.55, 0.14),
                      (tx + sx * r, y + 0.9 + abs(sy) * r * 0.9, 0.3 + s * (th - 1.5) / ns), B2,
                      bevel=0.02, rot=(0, 0, ang))
        # crown merlons
        for k in range(9):
            a = math.pi * k / 8
            box(f"{name}_twm{ti}_{k}", (0.6, 0.5, 0.8),
                (tx + math.cos(a) * (R - 0.25), y + 0.3 + math.sin(a) * (R - 0.25), th + 0.4), B,
                bevel=0.06, rot=(0, 0, a + math.pi / 2))
        objs["tower%d" % ti] = (tx, y + 0.9, th)
    return objs

# ------------------------------------------------------------------ yurt / tent
def yurt(name, loc, R=4.0, wall_h=1.8, roof_h=1.6, white=True):
    g = empty(name, loc)
    W = M("wood")
    F = M("felt")
    # floor carpet
    cyl(name + "_floor", R, 0.06, (0, 0, 0.03), M("carpet"), g, seg=48, half=True)
    # felt shell (outer) cut in half
    FC = mat("feltcut", (0.80, 0.70, 0.55), rough=0.9, coat=0.0)
    half_tube(name + "_wall", R + 0.2, 0.15, wall_h, (0, 0, wall_h / 2), F, g, seg=48, material_cut=FC)
    half_tube(name + "_roof", R + 0.35, 0.15, roof_h, (0, 0, wall_h + roof_h / 2), F, g, seg=48,
              r_top=0.95, material_cut=FC)
    # kerege lattice: crossed sticks on back half
    n = 22
    for i in range(n + 1):
        a = math.pi * i / n
        x, y = math.cos(a) * (R - 0.05), math.sin(a) * (R - 0.05)
        for s in (-1, 1):
            cyl(f"{name}_k{i}{s}", 0.025, wall_h * 1.25, (x, y, wall_h / 2), W, g, seg=6,
                rot=(0, s * math.radians(35), a + math.pi / 2), smooth_shade=False)
    # uyk roof poles to shangyrak
    for i in range(n + 1):
        a = math.pi * i / n
        p0 = Vector((math.cos(a) * (R - 0.05), math.sin(a) * (R - 0.05), wall_h))
        p1 = Vector((math.cos(a) * 0.75, math.sin(a) * 0.75, wall_h + roof_h - 0.05))
        mid = (p0 + p1) / 2
        d = p1 - p0
        rot = d.to_track_quat("Z", "Y").to_euler()
        cyl(f"{name}_u{i}", 0.03, d.length, mid, mat("uyk", (0.75, 0.22, 0.10), rough=0.4), g,
            seg=6, rot=rot, smooth_shade=False)
    sh = bpy.data.objects.new(name + "_shan", None)
    half_tube(name + "_shangyrak", 0.85, 0.12, 0.14, (0, 0, wall_h + roof_h), W, g, seg=24)
    # hearth
    for i in range(10):
        a = 2 * math.pi * i / 10
        sphere(f"{name}_stone{i}", 0.12, (math.cos(a) * 0.45, 1.2 + math.sin(a) * 0.45, 0.1), M("stone"), g,
               scale=(1, 1, 0.7))
    fire = sphere(name + "_fire", 0.25, (0, 1.2, 0.3), M("fire"), g, scale=(1, 1, 1.6))
    p = point((0, 1.2, 0.8), energy=150, color=(1, 0.55, 0.2), radius=0.3)
    p.parent = g
    # cushions / chests
    for i, a in enumerate((0.35, 0.65)):
        box(f"{name}_chest{i}", (1.0, 0.5, 0.6), (math.cos(a * math.pi) * (R - 0.8),
            math.sin(a * math.pi) * (R - 0.8), 0.3), M("red"), g, bevel=0.06,
            rot=(0, 0, a * math.pi + math.pi / 2))
    box(name + "_throne", (1.8, 0.9, 0.35), (0, R - 1.4, 0.2), M("darkred"), g, bevel=0.1)
    return g

def palace(name, loc, w=10.0, d=5.0, h=6.0):
    g = empty(name, loc)
    T = M("turq")
    B = mat("palacebrick", (0.90, 0.80, 0.62), tex="brick", rough=0.5)
    # floor tiles
    box(name + "_floor", (w, d, 0.2), (0, d / 2, 0.1), mat("pfloor", (0.85, 0.82, 0.75), tex="tile"), g)
    box(name + "_back", (w, 0.6, h), (0, d - 0.3, h / 2), B, g)
    for sx in (-1, 1):
        box(name + "_side%d" % sx, (0.6, d, h), (sx * (w / 2 - 0.3), d / 2, h / 2), B, g)
    # iwan arch in back wall (turquoise frame)
    box(name + "_iwan", (3.4, 0.2, 4.4), (0, d - 0.65, 2.4), T, g, bevel=0.05)
    cyl(name + "_iwanarch", 1.4, 0.25, (0, d - 0.75, 3.2), mat("niche", (0.12, 0.2, 0.35), rough=0.3), g,
        rot=(math.radians(90), 0, 0), seg=32)
    box(name + "_iwanin", (2.8, 0.25, 3.2), (0, d - 0.75, 1.75), mat("niche", (0.12, 0.2, 0.35)), g)
    # columns
    for i in range(4):
        x = -w / 2 + 1.6 + i * (w - 3.2) / 3
        cyl(f"{name}_col{i}", 0.22, h - 0.4, (x, 1.4, (h - 0.4) / 2 + 0.2), B, g, seg=16)
        box(f"{name}_cap{i}", (0.6, 0.6, 0.3), (x, 1.4, h - 0.2), T, g, bevel=0.05)
    # roof slab and half dome
    box(name + "_roof", (w, d, 0.5), (0, d / 2, h + 0.25), B, g)
    sphere(name + "_dome", 2.8, (0, d / 2 + 0.6, h + 0.5), T, g, hemi=True, half=True, seg=40,
           scale=(1, 1, 1.15))
    cyl(name + "_drum", 2.9, 0.6, (0, d / 2 + 0.6, h + 0.6), B, g, seg=40, half=True)
    for sx in (-1, 1):
        cyl(name + "_min%d" % sx, 0.35, h + 3.5, (sx * (w / 2 - 0.3), d - 0.3, (h + 3.5) / 2), T, g, seg=16)
        sphere(name + "_mintop%d" % sx, 0.45, (sx * (w / 2 - 0.3), d - 0.3, h + 3.6), M("gold"), g)
    # throne platform
    box(name + "_dais", (3.0, 1.6, 0.4), (0, d - 1.6, 0.4), M("darkred"), g, bevel=0.05)
    box(name + "_throne", (1.2, 0.8, 1.6), (0, d - 1.3, 1.2), M("gold"), g, bevel=0.1)
    for i in range(3):
        box(f"{name}_rug{i}", (1.6, 3.0, 0.03), (-3 + i * 3, 2.0, 0.22), M("carpet"), g)
    return g

# =================================================================== SHOTS
def shot_s1():
    """Caravan approaches Otrar, wall cut in half; slow orbit."""
    setup_world()
    sun((55, 0, 30), energy=4.5)
    diorama_base(-22, 22, -16, 10)
    wall = otrar_wall(-20, 20, y=4.0, h=7.5, t=4.2, gate_x=3.0, towers=(-11.0, 14.5))
    # city houses behind the wall (domes, flat roofs)
    for i in range(10):
        x = -18 + i * 4.0
        hh = 3 + (i * 37 % 5) * 0.6
        box(f"house{i}", (3.0, 3.0, hh), (x, 8.0, hh / 2), M("brick"), bevel=0.08)
        if i % 3 == 0:
            sphere(f"hdome{i}", 1.2, (x, 8.0, hh), M("turq"), hemi=True)
    # caravan path
    cam_ = camera(lens=42)
    camels = []
    for i in range(6):
        q = Quadruped(f"camel{i}", bales=["bale_a", "bale_b", "bale_c"][i % 3])
        camels.append(q)
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    ride(hero, camels[1])
    drivers = []
    for i in (0, 3, 5):
        p = Person(f"drv{i}", ["brown", "bale_c", "bale_b"][i % 3], hat="chalma", hat_mat="cream")
        drivers.append((i, p))
    for i in range(6):
        if i in (0, 3, 5):
            continue
    def anim(f, t):
        for i, q in enumerate(camels):
            yy = -8.5 + t * 1.25 - i * 2.7
            q.pose(f, (2.0 + math.sin(i * 1.7) * 0.25, yy, 0), math.pi, walk=1, phase=t * 0.9 + i * 0.3)
        for i, p in drivers:
            yy = -8.5 + t * 1.25 - i * 2.7
            p.pose(f, (3.3, yy - 0.6, 0), math.pi, walk=1, phase=t * 1.4 + i * 0.4)
        hero.pose(f, (0, 0, -0.5), 0, walk=0.0, head_turn=math.sin(t * 1.2) * 0.4)
        # camera slow orbit around the scene centre
        a = math.radians(-38 + t * 6)
        rad = 19
        cl = (2 + math.sin(a) * rad, -7 + -math.cos(a) * rad, 11.5 - t * 0.3)
        key(cam_, f, loc=cl, rot=look_rot(cl, (1.5, -4.5, 2.6)))
    bake(anim)

def shot_s2():
    """Side cut of the caravan: bales opened, gold/silver/silk inside; pan along."""
    setup_world(top=(0.45, 0.62, 0.9), horizon=(0.99, 0.88, 0.72))
    sun((50, 0, -20), energy=4.5)
    diorama_base(-24, 24, -6, 6, top="steppe")
    cam_ = camera(lens=40)
    camels = []
    for i in range(7):
        q = Quadruped(f"camel{i}")
        # side bales replaced by cutaway bales (only the camera-facing side, open)
        for sx in (-1, 1):
            bg_ = bale_cutaway(f"cb{i}{sx}", (0.80 * sx, 0.1, q.hb + 0.0), q.body, kind=i + (sx > 0), side=sx)
            bg_.scale = (1.35, 1.35, 1.35)
        camels.append(q)
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    ride(hero, camels[2])
    for i in range(7):
        if i == 2:
            continue
        p = Person(f"rd{i}", ["bale_c", "bale_b", "brown"][i % 3], hat="chalma", hat_mat="cream")
        ride(p, camels[i])
        camels[i].rider = p
    def anim(f, t):
        for i, q in enumerate(camels):
            x = -18 + i * 4.6 + t * 1.2
            # camels walk along +X, so heading = -90deg (facing +X); bales face the camera (-Y)
            q.pose(f, (x, 0, 0), math.radians(90), walk=1, phase=t * 0.9 + i * 0.27)
            if hasattr(q, "rider"):
                q.rider.pose(f, (0, 0, 0), 0)
        hero.pose(f, (0, 0, 0), 0, head_turn=0.5)
        # camera: side view, slightly above, panning along the caravan
        cx = lerp(-12, 6, smooth(t / (SCENE_LEN / FPS)))
        cl = (cx, -9.6, 3.5)
        key(cam_, f, loc=cl, rot=look_rot(cl, (cx + 0.8, 0, 1.85)))
    bake(anim)

def shot_s3():
    """Gate + tower in section; Inalchuk climbs the spiral stair and looks down."""
    setup_world()
    sun((52, 0, 25), energy=4.2)
    diorama_base(-14, 18, -14, 10)
    wall = otrar_wall(-12, 16, y=4.0, h=7.5, t=4.2, gate_x=3.0, towers=(-1.2,), rooms_lit=False)
    tx, ty, th = wall["tower0"]
    inal = Person("inal", "green", hat="turban", hat_mat="white", beard="black", sash="gold")
    camels = []
    for i in range(4):
        q = Quadruped(f"camel{i}", bales=["bale_a", "bale_b", "bale_c"][i % 3])
        camels.append(q)
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    ride(hero, camels[0])
    cam_ = camera(lens=40)
    T = SCENE_LEN / FPS
    ns = 30
    def stair_pos(u):
        s = u * (ns - 1)
        ang = math.pi * 0.05 + (s / ns) * math.pi * 2.6
        r = 1.2
        return (tx + math.cos(ang) * r, ty + abs(math.sin(ang)) * r * 0.9,
                0.3 + s * (th - 1.5) / ns + 0.07), ang
    def anim(f, t):
        u = clamp(t / (T * 0.72))
        if u < 1:
            (x, y, z), ang = stair_pos(u * 0.98)
            inal.pose(f, (x, y, z), ang + math.pi, walk=1, phase=t * 1.6)
        else:
            # at the top: stands on the battlement and looks down at the caravan
            (x, y, z), ang = stair_pos(1.0)
            k = smooth((t - T * 0.72) / 0.5)
            inal.pose(f, (x, lerp(y, ty - 1.2, k), th - 0.1), lerp(ang + math.pi, 0.25, k),
                      walk=0, head_tilt=0.35 * k, lean=0.1 * k)
        for i, q in enumerate(camels):
            q.pose(f, (5.0 + i * 0.3, -8 - i * 2.6 + t * 0.6, 0), math.pi * 0.95, walk=0.6,
                   phase=t * 0.7 + i * 0.3)
        hero.pose(f, (0, 0, -0.5), 0, head_tilt=-0.25, head_turn=0.2)
        # push in towards the tower section
        k = smooth(t / T)
        cl = vlerp((tx - 9, ty - 20, 14), (tx - 3.5, ty - 10.5, 9.5), k)
        tgt = vlerp((tx + 1, ty, 4.5), (tx, ty, lerp(3, th - 1, k)), k)
        key(cam_, f, loc=cl, rot=look_rot(cl, tgt))
    bake(anim)

def shot_s4():
    """Square at the gate: guards come out of the wall rooms and surround the caravan."""
    setup_world(top=(0.40, 0.55, 0.80), horizon=(0.95, 0.80, 0.62))
    sun((60, 0, 40), energy=4.0)
    diorama_base(-16, 18, -14, 10)
    wall = otrar_wall(-14, 16, y=4.0, h=7.5, t=4.2, gate_x=3.0, towers=(-1.2, 7.4))
    tx, ty, th = wall["tower0"]
    inal = Person("inal", "green", hat="turban", hat_mat="white", beard="black")
    camels = []
    for i in range(4):
        q = Quadruped(f"camel{i}", bales=["bale_a", "bale_b", "bale_c"][i % 3])
        camels.append(q)
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    ride(hero, camels[1])
    centre = Vector((3.0, -4.0, 0))
    camel_spots = [(1.8, -2.5), (4.2, -3.2), (2.0, -5.6), (4.4, -6.2)]
    guards = []
    room_x = [-11, -7, -3, 9, 12, 14.5, -9, 11]
    for i in range(8):
        g = Person(f"guard{i}", "darkred", hat="helmet", spear=True, beard="black" if i % 2 else None)
        guards.append(g)
    # speech bubble above Inalchuk
    bub = empty("bubble", (tx + 0.4, ty - 1.4, th + 2.6))
    sphere("bub_body", 1.0, (0, 0, 0), M("bubble"), bub, scale=(1.9, 0.35, 0.9))
    cyl("bub_tail", 0.35, 0.8, (0.3, 0, -0.95), M("bubble"), bub, r2=0.0, rot=(0, math.radians(-15), 0))
    text3d("bub_text", "Шпионы!", (0, -0.4, -0.05), 0.62, mat("bubtext", (0.75, 0.05, 0.04), rough=0.3), bub)
    cam_ = camera(lens=38)
    T = SCENE_LEN / FPS
    def anim(f, t):
        for i, q in enumerate(camels):
            x, y = camel_spots[i]
            q.pose(f, (x, y, 0), math.pi * 0.98, walk=0, phase=0)
        hero.pose(f, (0, 0, -0.5), 0, head_turn=math.sin(t * 3) * 0.5)
        inal.pose(f, (tx - 0.4, ty - 1.4, th - 0.1), 0.15, arm_raise=(0, 1.6 if t > 0.8 else 0),
                  head_tilt=0.35)
        for i, g in enumerate(guards):
            start = Vector((room_x[i], 4.0 - 0.6, 0.3))
            a = 2 * math.pi * i / len(guards) + 0.3
            end = centre + Vector((math.cos(a) * 4.6, math.sin(a) * 3.8, 0))
            k = smooth((t - 0.2 - i * 0.08) / 2.3)
            p = start.lerp(end, k)
            d = end - start
            head = math.atan2(d.x, -d.y)
            if k >= 0.999:
                face = centre - end
                head = math.atan2(face.x, -face.y)
            g.pose(f, (p.x, p.y, p.z if k < 0.05 else 0), head, walk=1.0 if 0.0 < k < 0.999 else 0,
                   phase=t * 1.8 + i * 0.3, arm_raise=(0, 0.5))
        s = smooth((t - 0.9) / 0.35)
        key(bub, f, scale=(max(0.001, s),) * 3)
        cl = vlerp((-1, -19, 16), (1, -16.5, 13.5), smooth(t / T))
        key(cam_, f, loc=cl, rot=look_rot(cl, (2.0, -1.0, 4.6)))
    bake(anim)

def shot_s5():
    """Night: wall section with a narrow passage; hero runs through and out to the steppe."""
    setup_world(top=(0.02, 0.03, 0.08), horizon=(0.06, 0.08, 0.16), strength=0.6)
    sun((62, 0, -20), energy=3.0, color=(0.55, 0.65, 1.0), angle=2)
    diorama_base(-18, 22, -6, 7, top="steppe")
    B = M("brick")
    S = M("section")
    # solid wall from x=-18..8, corridor inside at y=0..1.2, h 0..2.3
    x0, x1 = -18, 8
    L = x1 - x0
    cx = (x0 + x1) / 2
    box("w_back", (L, 2.5, 7.0), (cx, 2.45, 3.5), B, bevel=0.05)
    box("w_above", (L, 1.6, 4.4), (cx, 0.4, 4.8), S, bevel=0.05)
    box("w_floor", (L, 1.6, 0.25), (cx, 0.4, 0.12), S, bevel=0.03)
    box("w_top", (L, 4.2, 0.5), (cx, 1.5, 7.25), B, bevel=0.05)
    for k in range(int(L / 1.1)):
        box(f"w_mer{k}", (0.6, 0.5, 0.7), (x0 + 0.55 + k * 1.1, -0.35, 7.85), B, bevel=0.06)
    torches = []
    for k in range(5):
        tx = x0 + 3 + k * 5
        torches.append(torch((tx, 1.15, 1.6)))
    # the exit: hole at x1, then steppe; bushes & stars
    for i in range(14):
        sphere(f"bush{i}", 0.35 + (i % 3) * 0.15, (9 + i * 0.95, -3 + (i * 37 % 9) * 0.9, 0.2),
               mat("bush", (0.20, 0.25, 0.12), rough=0.8), scale=(1, 1, 0.6))
    moon = sphere("moon", 2.0, (30, 60, 30), mat("moon", (1, 1, 1), emit=(0.85, 0.9, 1.0), emit_str=6))
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    cam_ = camera(lens=45)
    T = SCENE_LEN / FPS
    def anim(f, t):
        x = lerp(-15, 14, t / T)
        hero.pose(f, (x, 0.45, 0.25 if x < x1 else 0), math.radians(90), walk=1.4,
                  phase=t * 2.6, lean=0.18)
        cl = (x - 1.0, -11.5, 4.2)
        key(cam_, f, loc=cl, rot=look_rot(cl, (x + 1.2, 0.5, 2.8)))
    bake(anim)

def shot_s6():
    """Dawn: Genghis Khan's great tent in section; hero stands before him."""
    setup_world(top=(0.35, 0.45, 0.75), horizon=(1.0, 0.65, 0.40))
    sun((15, 0, 60), energy=3.0, color=(1.0, 0.70, 0.45))
    diorama_base(-12, 12, -10, 10, top="steppe")
    y = yurt("yurt", (0, 0, 0), R=5.0, wall_h=2.0, roof_h=2.2)
    khan = Person("khan", "darkred", hat="fur", beard="black", scale=1.1)
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True)
    guards = [Person(f"g{i}", "darkred", hat="helmet", spear=True) for i in range(2)]
    cam_ = camera(lens=40)
    T = SCENE_LEN / FPS
    def anim(f, t):
        khan.pose(f, (0, 3.5, 0.37), 0, sit=True, head_tilt=0.0, arm_raise=(0.3, 0.3))
        k = smooth(t / 1.4)
        hero.pose(f, (lerp(-2.5, 0, k), lerp(-1.5, 0.6, k), 0), math.pi + lerp(0.6, 0, k),
                  walk=1 if k < 0.99 else 0, phase=t * 1.6, arm_raise=(0.9 * smooth((t - 1.6) / 0.4),) * 2,
                  head_tilt=-0.1)
        for i, g in enumerate(guards):
            g.pose(f, ((-1) ** i * 2.6, 3.4, 0.06), math.pi * (1 + 0.15 * (-1) ** i), arm_raise=(0, 0.4))
        cl = vlerp((0.5, -19, 11), (0.3, -10.5, 5.6), smooth(t / T))
        key(cam_, f, loc=cl, rot=look_rot(cl, (0, 2.0, 1.4)))
    bake(anim)

def shot_s7():
    """Two dioramas: Genghis tent (left) and Khwarezm palace (right). Envoy rides; scroll falls."""
    setup_world(top=(0.40, 0.58, 0.88), horizon=(0.98, 0.86, 0.68))
    sun((55, 0, 20), energy=4.2)
    diorama_base(-17, -3, -7, 7, top="steppe", name="b1")
    diorama_base(3, 19, -7, 7, top="sand", name="b2")
    # little bridge road between them
    box("road", (6.2, 1.6, 0.15), (0, 0, -0.08), M("sand"), bevel=0.04)
    yurt("yurt", (-10, 0, 0), R=4.0)
    khan = Person("khan", "darkred", hat="fur", beard="black")
    palace("pal", (11, -1.5, 0), w=11, d=6.5, h=6)
    shah = Person("shah", "silk_y", hat="turban", hat_mat="white", beard="black")
    guards = [Person(f"pg{i}", "blue", hat="helmet", spear=True) for i in range(2)]
    horse = Quadruped("horse", kind="horse")
    envoy = Person("envoy", "bale_b", hat="fur")
    ride(envoy, horse)
    scroll = empty("scroll", (0, 0, 0))
    cyl("scroll_p", 0.08, 0.5, (0, 0, 0), M("paper"), scroll, rot=(0, math.radians(90), 0), seg=12)
    cyl("scroll_s", 0.09, 0.08, (0.25, 0, 0), M("wood"), scroll, rot=(0, math.radians(90), 0), seg=12)
    cyl("scroll_s2", 0.09, 0.08, (-0.25, 0, 0), M("wood"), scroll, rot=(0, math.radians(90), 0), seg=12)
    cam_ = camera(lens=38)
    T = SCENE_LEN / FPS
    def anim(f, t):
        khan.pose(f, (-10, 2.6, 0.37), 0, sit=True)
        u = smooth(clamp(t / (T * 0.62)))
        hx = lerp(-7.5, 9.0, u)
        horse.pose(f, (hx, -0.5, 0), math.radians(90), walk=1 if u < 0.99 else 0,
                   phase=t * 2.2, gallop=True)
        envoy.pose(f, (0, 0, -0.5), 0, arm_raise=(0, 0.6))
        shah.pose(f, (11, 3.4, 0.6), 0, arm_raise=(0, 1.2 if t < T * 0.7 else 0.3))
        for i, g in enumerate(guards):
            g.pose(f, (11 + (-1) ** i * 2.4, 3.0, 0.2), 0, arm_raise=(0, 0.4))
        # scroll: carried by envoy, handed to shah, then falls to the floor
        if t < T * 0.62:
            p = Vector((hx + 0.3, -0.9, 2.3))
            key(scroll, f, loc=p, rot=(0, 0, 0))
        elif t < T * 0.72:
            k = smooth((t - T * 0.62) / (T * 0.10))
            p = Vector((hx + 0.3, -0.9, 2.3)).lerp(Vector((11.3, 2.7, 2.0)), k)
            key(scroll, f, loc=p, rot=(0, 0, 0))
        else:
            k = clamp((t - T * 0.72) / 0.45)
            z = lerp(2.0, 0.42, k * k)
            key(scroll, f, loc=(11.3 + k * 0.4, 2.5 - k * 0.6, z), rot=(k * 2.5, 0, k * 1.2))
        cx = lerp(-8.5, 10.0, smooth(t / T))
        cl = (cx, -19, 10.5)
        key(cam_, f, loc=cl, rot=look_rot(cl, (cx, 0.5, 1.6)))
    bake(anim)

def shot_s8():
    """Pull-back: whole steppe is one diorama; dark banners march on Otrar; hero on a hill."""
    setup_world(top=(0.30, 0.38, 0.55), horizon=(0.95, 0.62, 0.40))
    sun((25, 0, 120), energy=3.5, color=(1.0, 0.75, 0.5))
    diorama_base(-40, 40, -40, 30, depth=5, top="steppe")
    # Otrar at the far end (north), cut in half
    otrar_wall(-16, 16, y=20.0, h=7.0, t=4.0, gate_x=0.0, towers=(-9, 9))
    for i in range(8):
        x = -14 + i * 4
        box(f"house{i}", (3.0, 3.0, 3.5), (x, 25.0, 1.75), M("brick"), bevel=0.08)
    # hill with the hero
    sphere("hill", 9.0, (-14, -26, -6.0), M("steppe"), scale=(1, 1, 0.9))
    hero = Person("hero", "brown", hat="chalma", hat_mat="cream", outline=True, scale=1.0)
    # banner army: groups parented to moving empties
    groups = []
    rnd = random.Random(3)
    for gi in range(6):
        ge = empty(f"army{gi}", (0, 0, 0))
        for k in range(36):
            x = (k % 9) * 1.3 - 5.2 + rnd.uniform(-0.2, 0.2)
            y = (k // 9) * 1.6 + rnd.uniform(-0.2, 0.2)
            rider = empty(f"r{gi}_{k}", (x, y, 0), ge)
            cyl(f"rb{gi}_{k}", 0.25, 1.0, (0, 0, 0.5), M("horse"), rider, r2=0.15, seg=8)
            sphere(f"rh{gi}_{k}", 0.15, (0, 0, 1.15), M("black"), rider, seg=10)
            flag(f"fl{gi}_{k}", (0.2, 0, 0.4), rider, h=2.6)
        groups.append(ge)
    starts = [(-24, -30), (-8, -34), (8, -34), (24, -30), (-32, -18), (32, -18)]
    cam_ = camera(lens=35)
    T = SCENE_LEN / FPS
    def anim(f, t):
        hero.pose(f, (-14, -26, 1.95), math.radians(160), head_tilt=0.05)
        for gi, ge in enumerate(groups):
            sx, sy = starts[gi]
            tgt = Vector((sx * 0.35, 8.0, 0))
            p = Vector((sx, sy, 0)).lerp(tgt, clamp(t / (T * 1.4)))
            d = tgt - Vector((sx, sy, 0))
            key(ge, f, loc=(p.x, p.y, math.sin(t * 9 + gi) * 0.05), rot=(0, 0, math.atan2(-d.x, d.y)))
        k = smooth(t / (T * 0.85))
        cl = vlerp((-16.5, -31.5, 3.6), (-6, -78, 52), k)
        tgt = vlerp((-13.5, -24.5, 2.6), (0, -2, 0), k)
        key(cam_, f, loc=cl, rot=look_rot(cl, tgt))
    bake(anim, step=1)

SHOTS = dict(s1=shot_s1, s2=shot_s2, s3=shot_s3, s4=shot_s4, s5=shot_s5, s6=shot_s6,
             s7=shot_s7, s8=shot_s8)

# =================================================================== main
def render_shot(name, out, engine, samples, pct, stills=None, save=False):
    global SCENE_LEN, MATS
    MATS = {}
    reset()
    seg = TIMELINE["shots"][name]
    SCENE_LEN = int(round((seg[1] - seg[0]) * FPS))
    SHOTS[name]()
    setup_render(engine, samples, pct)
    sc = bpy.context.scene
    os.makedirs(out, exist_ok=True)
    if save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, name + ".blend"))
    if stills:
        sc.render.image_settings.file_format = "PNG"
        for fr in stills:
            sc.frame_set(min(fr, SCENE_LEN))
            sc.render.filepath = os.path.join(out, f"{name}_{fr:04d}.png")
            bpy.ops.render.render(write_still=True)
        return
    ok = False
    try:
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"
        sc.render.ffmpeg.ffmpeg_preset = "GOOD"
        sc.render.ffmpeg.audio_codec = "NONE"
        sc.render.filepath = os.path.join(out, name + ".mp4")
        ok = True
    except Exception as e:
        print("FFMPEG output not available, falling back to PNG:", e)
    if not ok:
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = os.path.join(out, name, "f_")
    bpy.ops.render.render(animation=True)

def main():
    which = arg("scene", "all")
    out = arg("out", os.path.join(HERE, "renders"))
    engine = arg("engine", "EEVEE").upper()
    samples = int(arg("samples", "64"))
    pct = int(arg("pct", "100"))
    stills = arg("still")
    stills = [int(s) for s in stills.split(",")] if stills else None
    save = arg("save", "0") == "1"
    names = list(SHOTS) if which == "all" else which.split(",")
    for n in names:
        print("=== rendering", n)
        render_shot(n, out, engine, samples, pct, stills, save)

if __name__ == "__main__":
    main()
