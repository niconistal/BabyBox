"""
Blender Python script — Photorealistic BabyBox product render.
Run headless: /Applications/Blender.app/Contents/MacOS/Blender --background --python render_scene.py
"""

import bpy
import math
import os
import bmesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Cleanup ──────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── Render settings ──────────────────────────────────────
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '16'
scene.render.filepath = os.path.join(SCRIPT_DIR, 'babybox_render.png')

# Color management
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium Contrast'

# ── Helper: Create material ──────────────────────────────
def make_material(name, color, roughness=0.35, subsurface=0.0, metallic=0.0, alpha=1.0, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    # Subsurface (Blender 4.x uses 'Subsurface Weight')
    try:
        bsdf.inputs['Subsurface Weight'].default_value = subsurface
    except KeyError:
        try:
            bsdf.inputs['Subsurface'].default_value = subsurface
        except KeyError:
            pass

    if emission_strength > 0:
        try:
            bsdf.inputs['Emission Color'].default_value = (*color, 1.0)
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        except KeyError:
            try:
                bsdf.inputs['Emission'].default_value = (*color, 1.0)
            except KeyError:
                pass

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


# ── Materials ────────────────────────────────────────────
# PETG-like matte plastic for enclosure (soft white)
mat_case = make_material('Case', (0.92, 0.90, 0.87), roughness=0.4, subsurface=0.05)

# Figurine coral red
mat_figurine = make_material('Figurine', (1.0, 0.42, 0.42), roughness=0.35, subsurface=0.08)

# LED teal glow
mat_led_teal = make_material('LED_Teal', (0.306, 0.804, 0.769), roughness=0.1, emission_strength=15.0)
mat_led_purple = make_material('LED_Purple', (0.424, 0.388, 1.0), roughness=0.1, emission_strength=12.0)
mat_led_coral = make_material('LED_Coral', (1.0, 0.42, 0.42), roughness=0.1, emission_strength=10.0)
mat_led_yellow = make_material('LED_Yellow', (1.0, 0.9, 0.427), roughness=0.1, emission_strength=10.0)

# Dark plastic for LED strip housing
mat_dark = make_material('Dark', (0.08, 0.08, 0.08), roughness=0.5)

# Floor/backdrop
mat_backdrop = make_material('Backdrop', (0.95, 0.93, 0.90), roughness=0.6)

# Second figurine (purple)
mat_figurine2 = make_material('Figurine2', (0.424, 0.388, 1.0), roughness=0.35, subsurface=0.08)

# Third figurine (teal)
mat_figurine3 = make_material('Figurine3', (0.306, 0.804, 0.769), roughness=0.35, subsurface=0.08)


# ── Import STLs ──────────────────────────────────────────
def import_stl(filepath, name):
    bpy.ops.wm.stl_import(filepath=filepath)
    obj = bpy.context.active_object
    obj.name = name
    # OpenSCAD exports in mm, Blender default is meters.
    # STL importer may auto-scale; we want mm scale (0.001 factor).
    # Reset scale and apply at mm
    obj.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(scale=True)
    return obj


body_path = os.path.join(SCRIPT_DIR, 'body.stl')
lid_path = os.path.join(SCRIPT_DIR, 'lid.stl')
figurine_path = os.path.join(SCRIPT_DIR, 'figurine.stl')

body_obj = None
lid_obj = None
fig_obj = None

if os.path.exists(body_path):
    body_obj = import_stl(body_path, 'Body')
    body_obj.data.materials.append(mat_case)

if os.path.exists(lid_path):
    lid_obj = import_stl(lid_path, 'Lid')
    # Position lid on top of body (body_h = 63mm = 0.063m)
    lid_obj.location.z = 0.063
    lid_obj.data.materials.append(mat_case)

if os.path.exists(figurine_path):
    fig_obj = import_stl(figurine_path, 'Figurine')
    # Position figurine on top of lid (body_h + lid_h = 75mm = 0.075m)
    # Center on lid (box is 150x110, center = 75, 55)
    fig_obj.location = (0.075, 0.055, 0.075)
    fig_obj.data.materials.append(mat_figurine)

    # Create second figurine (standing nearby)
    fig2 = fig_obj.copy()
    fig2.data = fig_obj.data.copy()
    fig2.name = 'Figurine2'
    fig2.location = (0.22, 0.06, 0.0)
    fig2.rotation_euler = (0, 0, math.radians(25))
    fig2.data.materials.clear()
    fig2.data.materials.append(mat_figurine2)
    bpy.context.collection.objects.link(fig2)

    # Create third figurine (standing nearby other side)
    fig3 = fig_obj.copy()
    fig3.data = fig_obj.data.copy()
    fig3.name = 'Figurine3'
    fig3.location = (-0.06, 0.08, 0.0)
    fig3.rotation_euler = (0, 0, math.radians(-15))
    fig3.data.materials.clear()
    fig3.data.materials.append(mat_figurine3)
    bpy.context.collection.objects.link(fig3)


# ── LED Strip (individual glowing dots on front face) ────
# LED window is on front wall (Y=0), centered at X=75mm, Z≈31.5mm
# 8 LEDs spaced about 6.4mm apart across 51mm
led_colors = [mat_led_teal, mat_led_purple, mat_led_coral, mat_led_yellow,
              mat_led_teal, mat_led_purple, mat_led_coral, mat_led_yellow]

for i in range(8):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.0025,
        location=(0.075 - 0.0255 + i * 0.00728, -0.001, 0.0315),
        segments=16, ring_count=8
    )
    led = bpy.context.active_object
    led.name = f'LED_{i}'
    led.data.materials.append(led_colors[i])

# LED glow backdrop (subtle rectangle behind LEDs)
bpy.ops.mesh.primitive_plane_add(
    size=0.06,
    location=(0.075, 0.001, 0.0315)
)
glow_plane = bpy.context.active_object
glow_plane.name = 'LED_Glow'
glow_plane.scale = (1.0, 0.2, 1.0)
bpy.ops.object.transform_apply(scale=True)
glow_plane.rotation_euler = (math.radians(90), 0, 0)
mat_glow = make_material('Glow', (0.306, 0.804, 0.769), roughness=0.1, emission_strength=3.0)
glow_plane.data.materials.append(mat_glow)


# ── Backdrop / Floor ─────────────────────────────────────
# Large curved backdrop (infinite sweep feel)
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0.075, 0.055, 0.0))
floor = bpy.context.active_object
floor.name = 'Floor'
floor.data.materials.append(mat_backdrop)

# Back wall (curved up)
bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0.075, 1.5, 1.5))
back = bpy.context.active_object
back.name = 'BackWall'
back.rotation_euler = (math.radians(90), 0, 0)
back.data.materials.append(mat_backdrop)


# ── Smooth shading ───────────────────────────────────────
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)


# ── Camera ───────────────────────────────────────────────
bpy.ops.object.camera_add(
    location=(0.30, -0.22, 0.15)
)
cam = bpy.context.active_object
cam.name = 'Camera'
scene.camera = cam

# Point camera at the center of the box using a Track To constraint
target_empty = bpy.data.objects.new('CameraTarget', None)
bpy.context.collection.objects.link(target_empty)
target_empty.location = (0.075, 0.055, 0.04)

track = cam.constraints.new(type='TRACK_TO')
track.target = target_empty
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# Bake the constraint so it applies before render
bpy.context.view_layer.update()

cam.data.lens = 50
cam.data.dof.use_dof = True
try:
    cam.data.dof.aperture_fsize = 2.8
except AttributeError:
    cam.data.dof.aperture_fstop = 2.8
cam.data.dof.focus_distance = 0.38


# ── Lighting ─────────────────────────────────────────────
# Key light (warm, from upper right front)
bpy.ops.object.light_add(type='AREA', location=(0.35, -0.3, 0.4))
key = bpy.context.active_object
key.name = 'KeyLight'
key.data.energy = 8.0
key.data.size = 0.4
key.data.color = (1.0, 0.95, 0.88)
key.rotation_euler = (math.radians(55), math.radians(15), math.radians(-35))

# Fill light (cool, from upper left)
bpy.ops.object.light_add(type='AREA', location=(-0.25, -0.15, 0.3))
fill = bpy.context.active_object
fill.name = 'FillLight'
fill.data.energy = 3.0
fill.data.size = 0.5
fill.data.color = (0.88, 0.92, 1.0)
fill.rotation_euler = (math.radians(50), math.radians(-20), math.radians(30))

# Rim/back light (accent)
bpy.ops.object.light_add(type='AREA', location=(0.0, 0.25, 0.25))
rim = bpy.context.active_object
rim.name = 'RimLight'
rim.data.energy = 5.0
rim.data.size = 0.3
rim.data.color = (0.9, 0.88, 1.0)
rim.rotation_euler = (math.radians(-45), 0, 0)

# Overhead soft fill
bpy.ops.object.light_add(type='AREA', location=(0.075, 0.055, 0.5))
top = bpy.context.active_object
top.name = 'TopLight'
top.data.energy = 2.0
top.data.size = 0.8
top.data.color = (1.0, 0.98, 0.95)
top.rotation_euler = (0, 0, 0)

# World background (very subtle warm gradient)
world = bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
wnodes.clear()

bg = wnodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.96, 0.94, 0.91, 1.0)
bg.inputs['Strength'].default_value = 0.3

out = wnodes.new('ShaderNodeOutputWorld')
wlinks.new(bg.outputs['Background'], out.inputs['Surface'])


# ── Render ───────────────────────────────────────────────
print(f"\n>>> Rendering to: {scene.render.filepath}")
print(f">>> Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f">>> Samples: {scene.cycles.samples}")
print(">>> Starting render...\n")

bpy.ops.render.render(write_still=True)

print(f"\n>>> Done! Image saved to: {scene.render.filepath}")
