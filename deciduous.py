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

# Hyperparameters
low_polyness = 8
base_radius = 1
length_scaler = 0.8
radius_threshold = 0.1
base_length = 6
radius_scaler = 0.6
length_threshold = 0.05
max_branches = 4
min_angle = 30
depth = 4
seed = time.time()
linear_dropoff = False
random.seed(seed)

def get_center(verts):
    res = Vector((0, 0, 0))
    for vert in verts:
        res += vert
    res /= len(verts)
    return res
     

leaf_positions = []
def create_branches(bm, face, curr_dep, min_branch=2, max_branch=3):
    if curr_dep == depth:
        return face.calc_center_bounds()
    
    if curr_dep == 0:
        branches = 1
    else:
        branches = max(random.randint(min_branch, max_branch), min(3, curr_dep))
        
    # Extrude
    extruded = bmesh.ops.extrude_edge_only(bm, edges=face.edges)
    
    verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
    
    center = get_center([vert.co for vert in verts])
                
    # Rotate
    old_normal = face.normal
    normals = []
    centers = []
    for i in range(branches):
        for j in range(100):
            new_normal = old_normal.copy()
            if curr_dep != 0:
                mat_y = Matrix.Rotation(radians(random.uniform(-30,30)), 3, 'Y')
                new_normal.rotate(mat_y)
                mat_x = Matrix.Rotation(radians(random.uniform(-30,30)), 3, 'X')
                new_normal.rotate(mat_x)
            else:
                mat_y = Matrix.Rotation(radians(0), 3, 'Y')
                mat_x = Matrix.Rotation(radians(0), 3, 'X')
                
            valid = True
            for normal in normals:
                if new_normal.angle(normal) < radians(min_angle):
                    valid = False
                    break
                
            if valid:
                new_extruded = bmesh.ops.extrude_edge_only(bm, edges=edges)
                new_verts = [v for v in new_extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
                new_edges = [e for e in new_extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
                
                for vert in new_verts:
                    delta = (vert.co - center)
                    if linear_dropoff:
                        new_delta = delta*base_radius/delta.length
                        if new_delta.length*radius_scaler - delta.length < radius_threshold*base_radius:
                            vert.co += new_delta * -radius_scaler
                    elif delta.length >= radius_threshold*base_radius:
                        vert.co -= delta * (radius_scaler ** 2)
                    
                
                bmesh.ops.rotate(bm, verts=new_verts, cent=center, matrix=mat_y)
                bmesh.ops.rotate(bm, verts=new_verts, cent=center, matrix=mat_x)
                normals.append(new_normal)
                
                
                l = base_length * (length_scaler ** curr_dep) * random.uniform(0.9, 1.7)
                bmesh.ops.translate(bm, verts=new_verts, vec=l*new_normal)
                new_face = bm.faces.new(new_verts)
                
                cent = create_branches(bm, new_face, curr_dep+1)
                if curr_dep == depth - 1:
                    centers.append(cent)
                break
    
    if curr_dep == depth -1:
        leaf_positions.append((get_center(centers), face.calc_center_bounds()))
        
def create_leaf(center, radius, wonkiness, subdiv=2, ):
    bm = bmesh.new()
    
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, diameter=2*radius*random.uniform(0.9, 1.1))
    
    # Translate
    bmesh.ops.translate(bm, verts=bm.verts, vec=center[0])
    vec = center[0]-center[1]
    # len = vec.length()
    vec = vec.normalized()
    print(radius*vec)
    bmesh.ops.translate(bm, verts=bm.verts, vec=radius*vec)
    
    bm.faces.ensure_lookup_table()
    for face in bm.faces:
        verts = face.verts
        norm = face.normal
        dn = random.uniform(-wonkiness, wonkiness) * norm
        bmesh.ops.translate(bm, verts=verts, vec=dn)
        
    # Finish up, write the bmesh into a new mesh
    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()
    
    # Add the mesh to the scene
    obj = bpy.data.objects.new("Leaf", me)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
    return obj
     
bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

bm.faces.ensure_lookup_table()
create_branches(bm, bm.faces[0], 0, 2, 3)

for leaf_position in leaf_positions:
    create_leaf(leaf_position, 2, 0.3, 2)

# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Add the mesh to the scene
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)