import bpy
from bpy import context as C
from bpy import data as D

import math
import bmesh

import mathutils
from mathutils import Vector, Quaternion, Matrix
import numpy as np

from time import perf_counter

# Push undo
bpy.ops.ed.undo_push()


def mknames():
    testbody = D.objects["Base_Mean.MirrorTopo.Shapekeyed"]
    testskel = D.objects["A_Armature.001"]

    str = "name_map = {\n"
    for bone in testskel.data.bones:
        name = bone.name[10:]
        if "Left" in name:
            name = name.replace("Left", "") + ".L"
        elif "Right" in name:
            name = name.replace("Right", "") + ".R"

        str += f'    "{bone.name}": "{name}",\n'

    print(str[:-2] + "\n}")


names = {
    "mixamorig:Hips": "Hips",
    "mixamorig:Spine": "Spine",
    "mixamorig:Spine1": "Spine1",
    "mixamorig:Spine2": "Spine2",
    "mixamorig:Neck": "Neck",
    "mixamorig:Head": "Head",
    "mixamorig:LeftShoulder": "Shoulder.L",
    "mixamorig:LeftArm": "Arm.L",
    "mixamorig:LeftForeArm": "ForeArm.L",
    "mixamorig:LeftHand": "Hand.L",
    "mixamorig:LeftHandThumb1": "HandThumb1.L",
    "mixamorig:LeftHandThumb2": "HandThumb2.L",
    "mixamorig:LeftHandThumb3": "HandThumb3.L",
    "mixamorig:LeftHandIndex1": "HandIndex1.L",
    "mixamorig:LeftHandIndex2": "HandIndex2.L",
    "mixamorig:LeftHandIndex3": "HandIndex3.L",
    "mixamorig:LeftHandMiddle1": "HandMiddle1.L",
    "mixamorig:LeftHandMiddle2": "HandMiddle2.L",
    "mixamorig:LeftHandMiddle3": "HandMiddle3.L",
    "mixamorig:LeftHandRing1": "HandRing1.L",
    "mixamorig:LeftHandRing2": "HandRing2.L",
    "mixamorig:LeftHandRing3": "HandRing3.L",
    "mixamorig:LeftHandPinky1": "HandPinky1.L",
    "mixamorig:LeftHandPinky2": "HandPinky2.L",
    "mixamorig:LeftHandPinky3": "HandPinky3.L",
    "mixamorig:RightShoulder": "Shoulder.R",
    "mixamorig:RightArm": "Arm.R",
    "mixamorig:RightForeArm": "ForeArm.R",
    "mixamorig:RightHand": "Hand.R",
    "mixamorig:RightHandThumb1": "HandThumb1.R",
    "mixamorig:RightHandThumb2": "HandThumb2.R",
    "mixamorig:RightHandThumb3": "HandThumb3.R",
    "mixamorig:RightHandIndex1": "HandIndex1.R",
    "mixamorig:RightHandIndex2": "HandIndex2.R",
    "mixamorig:RightHandIndex3": "HandIndex3.R",
    "mixamorig:RightHandMiddle1": "HandMiddle1.R",
    "mixamorig:RightHandMiddle2": "HandMiddle2.R",
    "mixamorig:RightHandMiddle3": "HandMiddle3.R",
    "mixamorig:RightHandRing1": "HandRing1.R",
    "mixamorig:RightHandRing2": "HandRing2.R",
    "mixamorig:RightHandRing3": "HandRing3.R",
    "mixamorig:RightHandPinky1": "HandPinky1.R",
    "mixamorig:RightHandPinky2": "HandPinky2.R",
    "mixamorig:RightHandPinky3": "HandPinky3.R",
    "mixamorig:LeftUpLeg": "UpLeg.L",
    "mixamorig:LeftLeg": "Leg.L",
    "mixamorig:LeftFoot": "Foot.L",
    "mixamorig:LeftToeBase": "ToeBase.L",
    "mixamorig:RightUpLeg": "UpLeg.R",
    "mixamorig:RightLeg": "Leg.R",
    "mixamorig:RightFoot": "Foot.R",
    "mixamorig:RightToeBase": "ToeBase.R"
}

names_inv = {v: k for (k, v) in names.items()}

sel = C.selected_objects


def _newname(name):
    if name[:9] == "mixamorig":
        return names[name]
    else:
        return names_inv[name]


for obj in sel:
    if obj.type == "ARMATURE":
        for bone in obj.data.bones:
            bone.name = _newname(bone.name)

    elif obj.type == "MESH":
        for vg in obj.vertex_groups:
            vg.name = _newname(vg.name)
