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
    
    bm = bmesh.new()
    
    # Add the left vertex
    bmesh.ops.create_vert(bm, co=Vector((0, 0, 0)))
    
    # Create all intermediate vertices in pairs
    for i in range(1, s+1):
        if l*i <= s * c:
            y = l*i/s
            pos = Vector(((w/2)*sin(radians(90*y/c)), 
                          y, 
                          (c**2/(l-c)**2)*d*(sin(radians(90*y/c))))) 
        else:
            y = l*i/s
            pos = Vector(((w/2)*(sin(radians(90)-radians(90*(y-c)/(l-c)))),
                          y,
                          (c**2/(l-c)**2)*d-d*(1-cos(radians(90*(y-c)/(l-c))))))
        bmesh.ops.create_vert(bm, co=pos)
        pos.x *= -1
        bmesh.ops.create_vert(bm, co=pos)
     
    #bmesh.ops.contextual_create(bm, geom=bm.verts)
    
    # Add the terminal edges    
    bm.verts.ensure_lookup_table()
    bm.edges.new((bm.verts[0], bm.verts[1]))
    bm.edges.new((bm.verts[0], bm.verts[2]))
    bm.edges.new((bm.verts[-1], bm.verts[-2]))
    bm.edges.new((bm.verts[-1], bm.verts[-3]))
   
    for i in range(1, len(bm.verts)-3):
        bm.verts.ensure_lookup_table()
        # If odd add the vertical edge to distinguish segment
        if i%2 == 1:
            bm.edges.new((bm.verts[i], bm.verts[i+1]))
        
        # Add the lateral edge
        bm.edges.new((bm.verts[i], bm.verts[i+2]))
      
    rot = Matrix.Rotation(-radians(angle), 4, "X")
    bmesh.ops.rotate(bm, cent=Vector((0.0, 0.0, 0.0)), matrix=rot, verts=bm.verts)         
    
    return bm


bm = create_leaf({"length" : 10,
                   "width" : 3,
                   "center" : 4.5,
                   "segments" : 9,
                   "dropoff" : 6,
                   "angle" : 10})

# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Add the mesh to the scene
obj = bpy.data.objects.new("Leaf", me)
bpy.context.collection.objects.link(obj)