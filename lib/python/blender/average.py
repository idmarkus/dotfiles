import bpy
from bpy import context as C
from bpy import data as D

import math
import bmesh

import mathutils
from mathutils import Vector, Quaternion, Matrix

# Push undo
bpy.ops.ed.undo_push()

col = D.collections["AnimationReady"]

objs = col.objects  # [:2]
nobjs = len(objs)
nverts = len(objs[0].data.vertices)

mean_verts = [Vector([0.0, 0.0, 0.0]) for i in range(nverts)]
# median_verts = []

# Calc mean
for obj in objs:
    for i, v in enumerate(obj.data.vertices):
        mean_verts[i] += obj.matrix_world @ v.co

for i in range(len(mean_verts)):
    mean_verts[i] /= nobjs


# Calc median
# for i in range(nverts):
#    xs = []
#    ys = []
#    zs = []
#    for obj in objs:
#        vco = obj.matrix_world @ obj.data.vertices[i].co
#        xs.append(vco.x)
#        ys.append(vco.y)
#        zs.append(vco.z)
#    xs.sort()
#    ys.sort()
#    zs.sort()
#    idx = nobjs//2
#    
#        #print(idx, len(xs), xs[idx], ys[idx], zs[idx], mean_verts[i], xs[0], xs[-1])
#    median_verts.append( Vector( [xs[idx], ys[idx], zs[idx]] ) )
#    
# for i in range(nverts):
#    vcos = []
#    for obj in objs:
#        vco = obj.matrix_world @ obj.data.vertices[i].co
#        vcos.append(vco)

#    vcos.sort(key=lambda x: x.length)
#    idx = len(vcos)//2
#    median_verts.append(vcos[idx])

def mkmesh(_name, _col, _vertices, _edges, _faces):
    m_data = D.meshes.new(_name)
    m_data.from_pydata(_vertices, _edges, _faces)
    m_obj = D.objects.new(m_data.name, m_data)
    _col.objects.link(m_obj)
    return m_obj


def cpy_uv(source, target):
    import numpy as np
    uvs = np.empty((2 * len(source.data.uv_layers[0].data), 1), "f")
    target_layers = target.data.uv_layers
    while target_layers:
        target.data.uv_layers.remove(target.data.uv_layers[0])
    for l in source.data.uv_layers:
        l.data.foreach_get('uv', uvs)
        target_layer = target_layers.new(name=l.name, do_init=False)
        target_layer.data.foreach_set('uv', uvs)
        target_layer.active_clone = l.active_clone
        target_layer.active_render = l.active_render
        target_layer.active = l.active


# mesh_name = "Average_Animation_Ready"
# mesh_data = D.meshes.new(mesh_name)
edges = [(e.vertices[0], e.vertices[1]) for e in objs[0].data.edges]
faces = [tuple(p.vertices) for p in objs[0].data.polygons]

mean_obj = mkmesh("Base_Mean", col, mean_verts, edges, faces)
# median_obj = mkmesh("Base_Median", col, median_verts, edges, faces)

cpy_uv(objs[0], mean_obj)
# cpy_uv(objs[0], median_obj)


# faces = objs[0].data.polygons
# mesh_data.from_pydata(avg_verts, edges, faces)
# mesh_obj = D.objects.new(mesh_data.name, mesh_data)
# col.objects.link(mesh_obj)
