import bpy
import bmesh
from mathutils import Vector, Matrix
import random
import sys
import os
import time
from math import radians

from random import randrange

# Delete default cube
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Tree Hyperparameters
height = 20
base_radius = 1
end_radius = base_radius * (0.3 + random.uniform(-0.05, 0.05))
layers = 8
low_polyness = 6
seed = time.time()

random.seed(seed)

# TODO: Follow bezier

def get_center(verts):
    res = Vector((0, 0, 0))
    for vert in verts:
        res += vert.co
    res /= len(verts)
    return res

layer_list = []
for i in range(0, layers+1):
    layer_list.append(i*height/layers)

# Create Trunk
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
    print(get_center(translate_verts), outer_center)
            
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

# Add the mesh to the scene
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)