import bpy
import bmesh
from mathutils import Vector, Matrix
import random
import sys
import os
import time
from math import radians, sin, cos

from random import randrange

# Delete default cube
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

seed = time.time()
random.seed(seed)

# TODO: Follow bezier

def get_center(verts):
    res = Vector((0, 0, 0))
    for vert in verts:
        res += vert.co
    res /= len(verts)
    return res

def create_leaf(params):
    l = params["length"]
    w = params["width"]
    c = params["center"]
    s = params["segments"]
    d = params["dropoff"]
    angle = params["angle"]
    thickness = params["thickness"]
    mat = params["material"]
    
    bm = bmesh.new()
    
    # Add the left vertex
    bmesh.ops.create_vert(bm, co=Vector((0, 0, 0)))
    
    # Create all intermediate vertices in pairs
    for i in range(1, s+1):
        y = l*i/s
        if l*i <= s*c:
            x = (w/2)*sin(radians(90*y/c))
            z = (c**2/(l-c)**2)*d*(sin(radians(90*y/c)))
            
            pos = Vector((x, y, z))
        else:
            x = (w/2)*(sin(radians(90)-radians(90*(y-c)/(l-c))))
            z = (c**2/(l-c)**2)*d-d*(1-cos(radians(90*(y-c)/(l-c))))
            
            pos = Vector((x, y, z))
        
        p = random.uniform(0.90, 1.1)
        pos.x *= p
        bmesh.ops.create_vert(bm, co=pos)
        pos.x *= -1/p
        pos.x *= random.uniform(0.90, 1.1)
        bmesh.ops.create_vert(bm, co=pos)    
        pos.z += pos.x/w
        pos.x = 0
        bmesh.ops.create_vert(bm, co=pos)
    
    bmesh.ops.remove_doubles(bm, dist=0.001, verts = bm.verts)
      
    # Create faces
    bm.verts.ensure_lookup_table()
    for i in range(3, len(bm.verts) - 4, 3):
        bm.faces.new((bm.verts[i], bm.verts[i-2], bm.verts[i+1], bm.verts[i+3]))
        bm.faces.new((bm.verts[i], bm.verts[i+3], bm.verts[i+2], bm.verts[i-1]))
        
    # Terminal faces
    bm.faces.new((bm.verts[0], bm.verts[1], bm.verts[3]))
    bm.faces.new((bm.verts[0], bm.verts[3], bm.verts[2]))
    bm.faces.new((bm.verts[-1], bm.verts[-3], bm.verts[-2]))
    bm.faces.new((bm.verts[-1], bm.verts[-2], bm.verts[-4]))
      
    rot = Matrix.Rotation(radians(angle), 4, "X")
    bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rot, verts=bm.verts)         
    
    # Finish up, write the bmesh into a new mesh
    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()

    # Assign the material
    me.materials.append(mat)
    
    # Add the mesh to the scene
    obj = bpy.data.objects.new("Leaf", me)
    mod = obj.modifiers.new(f"{obj.name}", "SOLIDIFY")
    mod.thickness = thickness
    
    return obj

# Create Trunk
# Tree Hyperparameters
height = 20
base_radius = 1
end_radius = base_radius * (0.3 + random.uniform(-0.05, 0.05))
layers = 8
low_polyness = 6
leaf_length = 8
leaf_width = 1.5
leaf_dropoff = 1.75
leaf_count = 11
leaf_elev_layers = 2 # Can be 1 to 3
leaf_center = 2
leaf_segments = 6
leaf_thickness = 0.1

trunk_color_hex = "A52A2A"
trunk_color = [int(trunk_color_hex[0:2], 16)/255,
         int(trunk_color_hex[2:4], 16)/255,
         int(trunk_color_hex[4:6], 16)/255,
         1]


leaf_color_hex = "4EB036"
leaf_color = [int(leaf_color_hex[0:2], 16)/255,
         int(leaf_color_hex[2:4], 16)/255,
         int(leaf_color_hex[4:6], 16)/255,
         1]

layer_list = []
for i in range(0, layers+1):
    layer_list.append(i*height/layers)

bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

bm.verts.ensure_lookup_table()
prev_radius = base_radius
last_edges = bm.edges
prev_normal = Vector((0, 0, 1))
to_pull_down = []

for i in range(1, layers+1):
    radius = end_radius + ((height - layer_list[i]) * (base_radius - end_radius)) / height
    
    # Extrude up
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    
    # Move extruded geometry
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    up = (layer_list[i]-layer_list[i-1]) * prev_normal
    bmesh.ops.translate(bm, vec=up, verts=translate_verts)
   
    
    # Scale Up
    dr = 1 + random.uniform(0.05, 0.07)
    scale_factor = dr * radius / prev_radius
    scale = Vector((scale_factor, scale_factor, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    outer_center = get_center(translate_verts)
    
    # Extrude in
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    
    # Scale in
    scale_factor = 1 / dr
    scale = Vector((scale_factor, scale_factor, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    
    # Rotate
    center = get_center(translate_verts)
    mat_y = Matrix.Rotation(radians(random.uniform(-7,7)), 3, 'Y')
    bmesh.ops.rotate(bm, verts=translate_verts, cent=center, matrix=mat_y)
    
    # Translate to fix 'x' and 'z'
    center = get_center(translate_verts)
    bmesh.ops.translate(bm, vec=outer_center-center, verts=translate_verts)
    
    # Get normal
    face = bmesh.ops.edgeloop_fill(bm, edges=last_edges)["faces"][0]
    prev_normal = Vector(face.normal)
    if prev_normal.z < 0:
        prev_normal *= -1
    bmesh.ops.delete(bm, geom=[face], context='FACES')
            
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
    prev_radius = radius
    
   
# Remove doubles
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

# Fill Top
bmesh.ops.edgeloop_fill(bm, edges=last_edges)


# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Create the material for the trunk
trunk_mat = bpy.data.materials.new("tree_mat")
trunk_mat.diffuse_color = trunk_color
me.materials.append(trunk_mat)

# Add the mesh to the scene
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)

# Create a material for the leaves
leaf_mat = bpy.data.materials.new("tree_mat")
leaf_mat.diffuse_color = leaf_color

# Create leafs
for i in range(leaf_count):
    theta = (i * 360 / leaf_count) + (360/leaf_count) * random.uniform(-0.1, 0.1)
    if i % 2:
        angle = random.uniform(-10, 0)
    else:
        angle = random.uniform(0, 10)
    leaf = create_leaf({
        "length": leaf_length*random.uniform(0.9, 1.1),
        "center": leaf_center*random.uniform(0.8, 1.1),
        "width": leaf_width*random.uniform(0.9, 1.1),
        "segments": leaf_segments,
        "dropoff": leaf_dropoff*random.uniform(0.95, 1.05),
        "thickness": leaf_thickness,
        "angle": angle,
        "material": leaf_mat
    })
    leaf.rotation_euler = (0, 0, radians(theta))
    
    # Translate leaf to top of trunk
    leaf.location = center
    
    # Rotate it to match angle of the trunk
    leaf.delta_rotation_euler = prev_normal
    
    bpy.context.collection.objects.link(leaf)