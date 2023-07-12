import bpy
from bpy import context as C
from bpy import data as D

import math
import bmesh

import mathutils
from mathutils import Vector, Quaternion, Matrix
import numpy as np

from time import perf_counter


# from temp_sel import temp_sel

class temp_sel():
    def __init__(self, ob, **keywords):
        self.keywords = {
            'object': ob,
            'active_object': ob,
            'selected_objects': [ob],
            'selected_editable_objects': [ob]
        }

        if keywords:
            for k, v in keywords.items():
                self.keywords[k] = v

        self.prev_view_active = C.view_layer.objects.active
        self.ob = ob

    def __enter__(self):
        try:
            C.view_layer.objects.active = self.ob
            yield C.temp_override(**self.keywords)
        except Exception as e:
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        C.view_layer.objects.active = self.prev_view_active


class Shaperig():
    skel_ob = None
    body_ob = None
    shaperig_ob = None
    line_ob = None

    def __init__(self, memo=False):
        # Push undo
        bpy.ops.ed.undo_push()

        self.memo = memo

        try:
            self._typecheck_selection()
        except Exception as e:
            if self._try_update():
                return
            else:
                raise e

        self._remake_collection()
        self._reset_shapekeys()
        # self._mk_bone_empties()
        # self._mk_bone_mesh()
        self._mk_shape_rig()
        self._add_handler()

    def _typecheck_selection(self):
        sel_objs = C.selected_objects

        n_sel = len(sel_objs)
        if n_sel < 2:
            raise TypeError("Too few objects selected, need exactly 2: (rig + mesh)")
        elif n_sel > 2:
            raise TypeError("Too many objects selected, need exactly 2: (rig + mesh)")

        skel_ob = body_ob = None

        for obj in sel_objs:
            if obj.type == "ARMATURE":
                skel_ob = obj
            elif obj.type == "MESH":
                body_ob = obj
            else:  # Error or ignore
                raise TypeError(f"Selected objects must be ARMATURE and MESH: not {obj.type}")

        if skel_ob is None: raise TypeError("No rig selected.")
        if body_ob is None: raise TypeError("No mesh selected.")

        self.skel_ob = skel_ob
        self.body_ob = body_ob

    def _try_update(self):
        for col in D.collections[:]:
            if col.name[:9] == "SHAPERIG.":
                objs = col.objects[:]
                if not objs:
                    D.collections.remove(col)
                    continue
                for obj in objs:
                    if obj.type == 'ARMATURE':
                        self.shaperig_ob = obj
                    elif obj.type == 'MESH':
                        self.line_ob = obj
                    else:
                        continue  # raise TypeError(f"Unknown object type ({obj.type})in SHAPERIG collection: {col.name}")
                if not self.shaperig_ob or not self.line_ob:
                    continue  # raise TypeError(f"SHAPERIG collection missing rig or linemesh: {col.name}")

                try:
                    self.skel_ob = D.objects[self.shaperig_ob.name[9:]]
                    self.body_ob = D.objects[self.line_ob.name[9:-5]]
                except:
                    raise TypeError(f"Can't find mesh or rig belonging to SHAPERIG: {col.name}")

                def __reconstruct_inds():
                    ind = 0
                    _inds = dict()
                    for bone in self.shaperig_ob.data.bones:
                        _inds[bone.name] = (ind, ind + 1)
                        ind += 2
                    self.linemesh_inds = _inds

                def __reconstruct_z_axes():
                    rig_ob = self.skel_ob
                    self.z_axes = dict()
                    with C.temp_override(active_object=rig_ob, selected_objects=[rig_ob],
                                         selected_editable_objects=[rig_ob]):
                        # Set edit mode
                        prev_view_active = C.view_layer.objects.active
                        prev_mode = C.object.mode
                        C.view_layer.objects.active = C.active_object
                        bpy.ops.object.mode_set(mode="EDIT")

                        for bone in rig_ob.data.edit_bones:
                            self.z_axes[bone.name] = bone.z_axis

                        bpy.ops.object.mode_set(mode=prev_mode)
                        C.view_layer.objects.active = prev_view_active

                __reconstruct_inds()
                __reconstruct_z_axes()
                self._add_handler()
                return True
        return False

    def _remake_collection(self, _rm=True):
        skel_ob = self.skel_ob
        cparent = skel_ob.users_collection[0]
        cname = "SHAPERIG." + skel_ob.name
        if cname in cparent.children:
            col = D.collections[cname]
            while _rm and col.objects:
                D.objects.remove(col.objects[0])
        else:
            col = D.collections.new(cname)
            cparent.children.link(col)
        self.col = col

    def _reset_shapekeys(self):
        if self.memo: store = dict()
        for block in self.body_ob.data.shape_keys.key_blocks:
            if self.memo: store[block.name] = block.value
            block.value = 0.0
        if self.memo: self._shapekey_store = store

    def _get_vgroups_vertices(self, minw=0.0001):
        deform_names = [bone.name for bone in self.skel_ob.data.bones if bone.use_deform]
        selections = {self.body_ob.vertex_groups[bname].index: [] for bname in deform_names}

        _check = [(i in selections.keys()) for i in range(max(selections.keys()) + 1)]
        for v in self.body_ob.data.vertices:
            high_w = minw
            high_i = -1
            for vg in v.groups:
                if vg.weight > high_w and vg.group < len(_check) and _check[vg.group]:
                    high_w = vg.weight
                    high_i = vg.group
            if high_w == minw or high_i == -1:
                print(f"INFO: Vertex without deform weights: {v.index}")
            else:
                selections[high_i].append(v.index)

        return {deform_names[i]: v for i, v in enumerate(selections.values())}

    def _mk_bone_mesh(self, skel):
        mat = skel.matrix_world.copy()
        vertices = []
        edges = []
        _inds = dict()
        for bone in skel.data.bones:
            if not bone.use_deform: continue

            phead = mat @ bone.head_local
            ptail = mat @ bone.tail_local

            ind = len(vertices)
            vertices += [phead, ptail]
            edges += [(ind, ind + 1)]
            _inds[bone.name] = (ind, ind + 1)

        # Construct mesh
        mesh_name = "SHAPERIG." + self.body_ob.name + ".Line"
        try:  # Purge mesh data block if updating
            old_mesh_data = D.meshes[mesh_name + "Data"]
            D.meshes.remove(old_mesh_data)
        except:
            pass

        mesh_data = D.meshes.new(mesh_name + "Data")
        mesh_data.from_pydata(vertices, edges, [])

        corrections = mesh_data.validate(verbose=True, clean_customdata=True)

        mesh_ob = D.objects.new(mesh_name, mesh_data)
        self.col.objects.link(mesh_ob)

        self.linemesh_inds = _inds

        #        # Make vertex groups
        #        for k, v in _inds.items():
        #            vg_head = mesh_ob.vertex_groups.new(name=k+".Head")
        #            vg_tail = mesh_ob.vertex_groups.new(name=k+".Tail")
        #            vg_head.add([v[0]], 1.0, 'ADD')
        #            vg_tail.add([v[1]], 1.0, 'ADD')
        #
        # Bind a surface deform modifier
        mod = mesh_ob.modifiers.new("SurfaceDeform", type="SURFACE_DEFORM")
        mod.target = self.body_ob
        with C.temp_override(object=mesh_ob, active_object=mesh_ob):
            bpy.ops.object.surfacedeform_bind(modifier=mod.name)

        # Evaluate surface deform shapekeys
        depsgraph = C.evaluated_depsgraph_get()
        for block in self.body_ob.data.shape_keys.key_blocks:
            if block.name == 'Basis': continue
            block.value = 1.0
            line_eval = mesh_ob.evaluated_get(depsgraph)
            with C.temp_override(object=mesh_ob, active_object=mesh_ob, selected_objects=[mesh_ob]):
                bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier="SurfaceDeform")
                mesh_ob.data.shape_keys.key_blocks["SurfaceDeform"].name = block.name
            block.value = 0.0

            # Add driver
            relpath = f'key_blocks["{block.name}"].value'
            k = mesh_ob.data.shape_keys.key_blocks[block.name]
            d = k.driver_add("value").driver
            v = d.variables.new()
            v.name = "value"
            v.targets[0].id_type = "KEY"
            v.targets[0].id = self.body_ob.data.shape_keys
            v.targets[0].data_path = relpath
            d.expression = v.name

        # Remove surface deform modifier    
        mesh_ob.modifiers.remove(mod)

        # Parent linemesh to rig
        mat.invert()
        mesh_ob.matrix_world = mat
        mesh_ob.parent = skel
        mesh_ob.show_in_front = True
        self.line_ob = mesh_ob

    def _mk_shape_rig(self, CONNECT_LIMIT=0.01):
        skel = self.skel_ob

        def __cpy(arm, name):
            try:  # Purge old data
                old_data = D.armatures[name + "Data"]
                D.armatures.remove(old_data)
            except:
                pass
            data = arm.data.copy()
            data.name = name + "Data"
            ob = D.objects.new(name, data)
            self.col.objects.link(ob)
            ob.matrix_world = arm.matrix_world.copy()
            return ob

        def __sel_only(ob):
            for selob in C.selected_objects:
                selob.select_set(False)
            ob.select_set(True)
            C.view_layer.objects.active = ob

        shape_ob = __cpy(skel, "SHAPERIG." + skel.name)

        # Move deform bones to bone layer 1
        for bone in shape_ob.data.bones:
            if bone.use_deform:
                bone.layers[0] = True
                for i in range(1, len(bone.layers)):
                    if bone.layers[i]: bone.layers[i] = False

        # Connect close bones and remove non-deform bones
        # with temp_sel(shape_ob):
        __sel_only(shape_ob)
        bpy.ops.object.mode_set(mode="EDIT")

        self.z_axes = dict()
        for bone in shape_ob.data.edit_bones[:]:
            if not bone.use_deform:
                shape_ob.data.edit_bones.remove(bone)
                continue
            elif bone.parent:
                phead = bone.head
                ptail = bone.parent.tail
                if math.fabs((phead - ptail).magnitude) < CONNECT_LIMIT:
                    bone.use_connect = True
            self.z_axes[bone.name] = bone.z_axis

        bpy.ops.object.mode_set(mode="OBJECT")
        __sel_only(self.skel_ob)
        self.body_ob.select_set(True)

        # Make bone line mesh
        self._mk_bone_mesh(shape_ob)

        # Copy animation data
        shape_ob.animation_data_create()
        shape_ob.animation_data.action = skel.animation_data.action.copy()

        self.shaperig_ob = shape_ob

        # Assign shaperig to body armature mod
        for mod in self.body_ob.modifiers:
            if mod.type == 'ARMATURE':
                if not mod.object or mod.object == self.skel_ob:
                    mod.object = shape_ob
                    break
        else:
            mod = self.body_ob.modifiers.new("ShaperigArmature", type="ARMATURE")
            mod.object = shape_ob

        # Add shape bone constraints

    #        __target_space = "LOCAL_WITH_PARENT" # "LOCAL_WITH_PARENT"
    #        __owner_space = "LOCAL_WITH_PARENT"
    #        for bone in shape_ob.pose.bones:
    #            if bone.name[-5:] == ".Hook":
    #                #continue
    #                root_name = bone.name[:-5]
    #                cloc = bone.constraints.new(type="COPY_LOCATION")
    #                cloc.target = self.line_ob
    #                cloc.subtarget = root_name + ".Head"
    #
    #                #cstretch = bone.constraints.new(type="STRETCH_TO")
    #                #cstretch.target = self.line_ob
    #                #cstretch.subtarget = root_name + ".Tail"
    #                #cstretch.rest_length = bone.length
    #                #cstretch.volume = 'VOLUME_X'#'NO_VOLUME' #'VOLUME_XZX' # 'NO_VOLUME'
    #
    #                #climit = bone.constraints.new(type="LIMIT_ROTATION")
    #                #climit.owner_space = __owner_space
    #                #climit.use_limit_y = True
    #            else: # Inverse
    #                hook_name = bone.name + ".Hook"
    #
    #                cloc = bone.constraints.new(type="COPY_LOCATION")
    #                cloc.target = shape_ob
    #                cloc.subtarget = hook_name#bone.name + ".Head"
    #                cloc.invert_x = True
    #                cloc.invert_y = True
    #                cloc.invert_z = True
    #                cloc.target_space = __target_space
    #                cloc.owner_space = __owner_space
    #
    ##                crot = bone.constraints.new(type="COPY_ROTATION")
    ##                crot.target = shape_ob
    ##                crot.subtarget = hook_name
    ##                crot.invert_x = True
    ##                crot.invert_y = True
    ##                crot.invert_z = True
    ##                crot.target_space = __target_space
    ##                crot.owner_space = __owner_space
    ##                crot.influence = 0.5
    #
    ##                climit = bone.constraints.new(type="LIMIT_ROTATION")
    ##                climit.owner_space = __owner_space
    ##                climit.use_limit_y = True
    #
    ##                cscale = bone.constraints.new(type="COPY_SCALE")
    ##                cscale.target = shape_ob
    ##                cscale.subtarget = hook_name
    ##                cscale.power = -1
    ##                cscale.target_space = __target_space
    ##                cscale.owner_space = __owner_space

    #        # Add pose armature bone constraints
    #        for bone in pose_ob.pose.bones:
    #            #hook_name = bone.name + ".Hook"
    #            cloc = bone.constraints.new(type="COPY_LOCATION")
    #            cloc.target = self.line_ob
    #            cloc.subtarget = bone.name + ".Head"
    #            #cloc.target_space = __target_space
    #            #cloc.owner_space = __owner_space
    #
    #            cstretch = bone.constraints.new(type="STRETCH_TO")
    #            cstretch.target = self.line_ob
    #            cstretch.subtarget = bone.name + ".Tail"
    #            cstretch.rest_length = bone.length
    #            cstretch.volume = 'NO_VOLUME'
    #
    #            crot = bone.constraints.new(type="COPY_ROTATION")
    #            crot.target = self.skel_ob
    #            crot.subtarget = bone.name
    #            crot.target_space = __target_space
    #            crot.owner_space = __owner_space
    #
    #            ploc = bone.constraints.new(type="COPY_LOCATION")
    #            ploc.target = self.skel_ob
    #            ploc.subtarget = bone.name
    #            ploc.target_space = __target_space
    #            ploc.owner_space = __owner_space
    #            ploc.use_offset = True
    #
    #            pscale = bone.constraints.new(type="COPY_SCALE")
    #            pscale.target = self.skel_ob
    #            pscale.subtarget = bone.name
    #            pscale.target_space = __target_space
    #            pscale.owner_space = __owner_space
    #            pscale.use_offset = True
    #
    ##            crot = bone.constraints.new(type="COPY_ROTATION")
    ##            crot.target = shape_ob
    ##            crot.subtarget = hook_name
    ##            crot.mix_mode = "BEFORE"
    ##            crot.target_space = __target_space
    ##            crot.owner_space = __owner_space
    #
    ##            cscale = bone.constraints.new(type="COPY_SCALE")
    ##            cscale.target = shape_ob
    ##            cscale.subtarget = hook_name
    ##            cscale.power = 1
    ##            cscale.target_space = __target_space
    ##            cscale.owner_space = __owner_space

    def _add_handler(self):
        rig_ob = self.shaperig_ob
        line_ob = self.line_ob

        def __append_function_unique(fn_list, fn, append=True):
            """ Appending 'fn' to 'fn_list',
                Remove any functions from with a matching name & module.
            """
            fn_name = fn.__name__
            fn_module = fn.__module__
            for i in range(len(fn_list) - 1, -1, -1):
                if fn_list[i].__name__ == fn_name and fn_list[i].__module__ == fn_module:
                    del fn_list[i]
            if append: fn_list.append(fn)

        self.in_update = False

        def __shaperig_depsgraph_post(scene, depsgraph):
            if self.in_update: return
            self.in_update = True
            try:
                for update in depsgraph.updates:
                    if update.id.name == line_ob.name:
                        if update.is_updated_geometry:
                            with C.temp_override(active_object=rig_ob, selected_objects=[rig_ob],
                                                 selected_editable_objects=[rig_ob]):
                                # Set edit mode
                                prev_view_active = C.view_layer.objects.active
                                prev_mode = C.object.mode
                                C.view_layer.objects.active = C.active_object
                                bpy.ops.object.mode_set(mode="EDIT")

                                # Update edit_bones locations
                                line_eval = self.line_ob.evaluated_get(depsgraph)
                                rig_mat = rig_ob.matrix_world.copy()
                                rig_mat.invert()
                                cos = [v.co for v in line_eval.data.vertices]

                                for bone in rig_ob.data.edit_bones:
                                    ind_head, ind_tail = self.linemesh_inds[bone.name]
                                    bone.head = rig_mat @ cos[ind_head]
                                    bone.tail = rig_mat @ cos[ind_tail]
                                    bone.align_roll(self.z_axes[bone.name])

                                # Return context
                                bpy.ops.object.mode_set(mode=prev_mode)
                                C.view_layer.objects.active = prev_view_active
                        break
            except:
                pass

            self.in_update = False

        def __shaperig_frame_change_post(scene):
            depsgraph = C.evaluated_depsgraph_get()
            #            line_eval = line_ob.evaluated_get(depsgraph)
            #            rig_eval = rig_ob.evaluated_get(depsgraph)
            with C.temp_override(active_object=rig_ob, selected_objects=[rig_ob], selected_editable_objects=[rig_ob]):
                # Set edit mode
                prev_view_active = C.view_layer.objects.active
                prev_mode = C.object.mode
                C.view_layer.objects.active = C.active_object
                bpy.ops.object.mode_set(mode="EDIT")

                # Update edit_bones locations
                line_eval = self.line_ob.evaluated_get(depsgraph)
                rig_mat = rig_ob.matrix_world.copy()
                rig_mat.invert()
                cos = [v.co for v in line_eval.data.vertices]

                for bone in rig_ob.data.edit_bones:
                    ind_head, ind_tail = self.linemesh_inds[bone.name]
                    bone.head = rig_mat @ cos[ind_head]
                    bone.tail = rig_mat @ cos[ind_tail]
                    bone.align_roll(self.z_axes[bone.name])

                # Return context
                bpy.ops.object.mode_set(mode=prev_mode)
                C.view_layer.objects.active = prev_view_active

        __append_function_unique(bpy.app.handlers.depsgraph_update_post, __shaperig_depsgraph_post, append=True)
        __append_function_unique(bpy.app.handlers.frame_change_post, __shaperig_frame_change_post)

    def _mk_bone_empties(self):
        skel_ob = self.skel_ob
        mat = skel_ob.matrix_world
        col = self.col
        _vertices = self._get_vgroups_vertices()

        print(_vertices["Arm.L"])
        for bone in skel_ob.data.bones:
            if not bone.use_deform: continue

            phead = mat @ bone.head_local
            ptail = mat @ bone.tail_local

            rot = bone.matrix_local.to_euler()

            # Make head empty
            head = D.objects.new("Head." + bone.name, None)
            head.empty_display_size = bone.length * 0.4
            head.empty_display_type = "SPHERE"

            head.location = phead
            head.rotation_euler = rot
            #            head.parent = self.body_ob
            #            head.parent_type = "VERTEX"
            #            head.parent_vertices = _vertices[bone.name]
            col.objects.link(head)

            tail = D.objects.new("Tail." + bone.name, None)
            tail.empty_display_size = bone.length * 0.3
            tail.empty_display_type = "ARROWS"

            tail.location = ptail
            tail.rotation_euler = rot
            #            tail.parent = self.body_ob
            #            tail.parent_type = "VERTEX"
            #            tail.parent_vertices = _vertices[bone.name]
            col.objects.link(tail)


# def _mk_bone_empties(skel):
# skel_ob, body_ob = _typecheck_selection()
# sr_col = _remake_collection(skel_ob)
# _reset_shapekeys(body_ob)

rig = Shaperig(memo=True)
