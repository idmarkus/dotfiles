import bpy
from bpy import context as C
from bpy import data as D

import math
import bmesh

import mathutils
from mathutils import Vector, Quaternion, Matrix
import numpy as np

from time import perf_counter


def remove_handler(fn_list, fn):
    fn_name = fn.__name__
    fn_module = fn.__module__
    for i in range(len(fn_list) - 1, -1, -1):
        if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
            del fn_list[i]


def append_function_unique(fn_list, fn):
    """ Appending 'fn' to 'fn_list',
        Remove any functions from with a matching name & module.
    """
    remove_handler(fn_list, fn)
    fn_name = fn.__name__
    fn_module = fn.__module__
    for i in range(len(fn_list) - 1, -1, -1):
        if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
            del fn_list[i]
    fn_list.append(fn)


def my_function(scene):
    print(scene)


def depsgraph_check_linemesh(scene, depsgraph):
    linemesh = D.objects["A_Armature.Pose.py.Shape.LineMesh"]
    for update in depsgraph.updates:
        #        print(update.id.name)
        if update.id.name == linemesh.name:
            print("Linemesh update")
    print("")


def register():
    append_function_unique(bpy.app.handlers.depsgraph_update_post, depsgraph_check_linemesh)


def unregister():
    remove_handler(bpy.app.handlers.depsgraph_update_post, depsgraph_check_linemesh)


if __name__ == "__main__":
    unregister()
