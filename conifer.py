import bpy
import bmesh
from mathutils import Vector, Matrix
from math import radians
import random
import sys
import os
import time

from random import randrange

# Delete everything on screen
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Tree Hyperparameters
height = 20
base_radius = 5
layers = 10
low_polyness = 10
seed = time.time()
drop_off = 0.5
tilt = 0.2
trunk_scale = 0.2
color_hex = "4EB036"
color = [int(color_hex[0:2], 16)/255,
         int(color_hex[2:4], 16)/255,
         int(color_hex[4:6], 16)/255,
         1]

random.seed(seed)

# TODO: Non Linear function
# TODO: Follow path instead of straight

layer_list = []
for i in range(0, layers+1):
    layer_list.append(i*height/layers)

for i in range(1, layers):
    layer_list[i] += random.uniform(-0.2, 0.2)*height/layers

# Create Tree
bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

bm.verts.ensure_lookup_table()
last_edges = bm.edges
prev_radius = base_radius
to_pull_down = []
should_terminate = False
angle = radians(random.uniform(-5, 5))

rot_matrix = Matrix.Rotation(angle, 4, "Z")
bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rot_matrix, verts=bm.verts)

# Bottom pull down
for j in range(len(bm.verts)):
        even_odd = random.choice([0, 1])
        if j%2 == even_odd:
            to_pull_down.append((bm.verts[j], 1))

for i in range(1, layers+1):
    outer_radius = (((height - layer_list[i]) / height) ** drop_off) * base_radius
    
    if outer_radius < 0.1:
        outer_radius = 0
        should_terminate = True
    
    # Extrude up
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    
    # Move extruded geometry
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    
    
    up = Vector((random.uniform(-0.1, 0.1)*base_radius/i, 
                 random.uniform(-0.1, 0.1)*base_radius/i, 
                 layer_list[i]-layer_list[i-1]))
    bmesh.ops.translate(bm, vec=up, verts=translate_verts)
    
    # Scale down
    dr = 1 - random.uniform(0.15, 0.20)
    scale_factor = dr * outer_radius / prev_radius
    scale = Vector((scale_factor, scale_factor, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    
#    rot_matrix = Matrix.Rotation(angle, 4, "Z")
#    bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rot_matrix, verts=translate_verts)
#    
    angle = radians(random.uniform(-45, 45))
    if i != layers:
        # Extrude out
        last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
        extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
        translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
        
        # Scale up
        scale_factor = 1/dr
        scale = Vector((scale_factor, scale_factor, 1))
        bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
       
        rot_matrix = Matrix.Rotation(angle, 4, "Z")
        bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rot_matrix, verts=translate_verts)
            
        # Choose to bring down
        for j in range(len(translate_verts)):
            even_odd = random.choice([0, 1])
            if j%2 == even_odd:
                to_pull_down.append((translate_verts[j], i))
                
        last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
        prev_radius = outer_radius
    
    
    if should_terminate:
        break

# Actually bring down
for vert in to_pull_down:
    exp = 2*(1+vert[1])/layers
    dz = (random.uniform(0.1, 0.15)**exp) * (height / layers)
    down = Vector((0, 0, -dz))
    bmesh.ops.translate(bm, vec=down, verts=[vert[0]])


# Remove doubles
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

# Move the mesh up
bmesh.ops.translate(bm, vec=Vector((0, 0, height*trunk_scale)), verts=bm.verts)
    
# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Assign color
tree_mat = bpy.data.materials.new("tree_mat")
tree_mat.diffuse_color = color
me.materials.append(tree_mat)


# Add the mesh to the scene
obj = bpy.data.objects.new("Tree", me)
bpy.context.collection.objects.link(obj)

# Trunk Hyperparameters
height *= trunk_scale
base_radius *= 0.2
layers = 3
low_polyness = 8
max_growth = 1.5
color_hex = "A52A2A"
color = [int(color_hex[0:2], 16)/255,
         int(color_hex[2:4], 16)/255,
         int(color_hex[4:6], 16)/255,
         1]


# Create trunk
bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

layer_list = []
for i in range(0, layers+1):
    layer_list.append(-i*height/layers)
    
last_edges = bm.edges
prev_radius = base_radius
for i in range(1, layers+1):
    # Extrude down
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    
    # Move extruded geometry
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    down = Vector((random.uniform(-0.3*base_radius, 0.3*base_radius), 
                   random.uniform(-0.3*base_radius, 0.3*base_radius), 
                   layer_list[i]-layer_list[i-1]))
    bmesh.ops.translate(bm, vec=down, verts=translate_verts)
    
    # Scale up
    dr = 1 + random.uniform(0.10, 0.15)
    if prev_radius/base_radius > max_growth:
        dr = 1
    scale = Vector((dr, dr, 1))
    prev_radius *= dr
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]

# Fill bottom
bmesh.ops.edgeloop_fill(bm, edges=last_edges)

# Remove doubles
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

# Move the mesh up
bmesh.ops.translate(bm, vec=Vector((0, 0, height)), verts=bm.verts)
    
# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()



# Assing color
trunk_mat = bpy.data.materials.new("trunk_mat")
trunk_mat.diffuse_color = color
me.materials.append(trunk_mat)

    
# Add the mesh to the scene
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)