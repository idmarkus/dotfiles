import bpy
from bpy import context as C


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
            yield C.temp_override(**ctx)
        except Exception as e:
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        C.view_layer.objects.active = self.prev_view_active


if __name__ == "__main__":
    from bpy import data as D

    rig_ob = D.objects["A_Armature.Pose.py.Shape"]
    with temp_selonly(rig_ob, mode="EDIT"):
        bpy.ops.object.mode_set(mode="EDIT")
        print(C.active_object.data.is_editmode)
        bpy.ops.object.mode_set(mode="OBJECT")
