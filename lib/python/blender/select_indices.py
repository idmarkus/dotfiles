# From yhoyo @ SE https://blender.stackexchange.com/questions/28109/how-could-i-select-a-vertex-by-its-id
import bpy
import bmesh

# Indices to select, any iterable
# index = 0, 5, 8
# index = [x for x in range(10)]
index = 0, 1

obj = bpy.context.object
me = obj.data
bm = bmesh.from_edit_mesh(me)

vertices = [e for e in bm.verts]
# oa = bpy.context.active_object

for vert in vertices:
    if vert.index in index:
        vert.select = True
    else:
        vert.select = False

bmesh.update_edit_mesh(me)
