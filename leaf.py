import bpy
import bmesh
from mathutils import Vector, Matrix
from math import radians, sin, cos
import random
import sys
import os
import time

from random import randrange

# Delete everything on screen
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

def create_leaf(params):
    l = params["length"]
    w = params["width"]
    c = params["center"]
    s = params["segments"]
    d = params["dropoff"]
    angle = params["angle"]
    thickness = params["thickness"]
    
    bm = bmesh.new()
    
    # Add the left vertex
    bmesh.ops.create_vert(bm, co=Vector((0, 0, 0)))
    
    # Create all intermediate vertices in pairs
    for i in range(1, s+1):
        y = l*i/s
        if l*i <= s * c:
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

    # Add the mesh to the scene
    obj = bpy.data.objects.new("Leaf", me)
    mod = obj.modifiers.new(f"{obj.name}", "SOLIDIFY")
    mod.thickness = thickness
    
    return obj


obj = create_leaf({"length" : 10,
                   "width" : 3,
                   "center" : 4,
                   "segments" : 7,
                   "dropoff" : 3,
                   "angle" : 0,
                   "thickness": 0.1
                   })



bpy.context.collection.objects.link(obj)
