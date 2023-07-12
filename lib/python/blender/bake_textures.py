import bpy
from pathlib import Path

root_d = Path("")

names_f = ["Female 01", "Female 02", "Female 03", "Female 04", "Female 06"]
names_m = ["Male 01", "Male 02", "Male 03", "Male 05", "Male 06"]

names = ["Female/" + fn for fn in names_f] + ["Male/" + mn for mn in names_m]
names_d = [root_d / n / "Textures" / "JPG" for n in names]

body_texture_names = ["Body_Colour", "Body_Normal", "Body_Roughness", "Body_Spec"]
eye_texture_names = ["Eyes_Diffuse", "Eyes_Normals", "Eyes_parallax", "Eyes_roughness", "Eyes_spec", "Eyes_SSS"]


# tex_fnames = [fn + ".jpg" for fn in body_texture_names + eye_texture_names]

# texture_ps = [n_d / tn for n_d in names_d for tn in tex_fnames]
# for tp in texture_ps:
#     assert(tp.exists())

def get_paths(texture_name):
    fname = texture_name + ".jpg"
    return [n_d / fname for n_d in names_d]


# print(get_paths(body_texture_names[0]))

# out_d = Path("B:/RESOURCE/MESH/CrowdCrush/Bake_out")
# out_d.mkdir(exist_ok=True)


bake_in_tex = bpy.data.images["bake_input"]
mat = bpy.data.materials["bake"]


def bake_one(name):
    paths = get_paths(name)
    colspace = "sRGB" if ("Colour" in name or "Normal" in name) else "Raw"
    if colspace == "sRGB": return
    for i, im_p in enumerate(paths):
        #        if i > 1: break

        #        bake_out_tex = bpy.data.images["bake_out"]
        bake_in = bpy.data.images.load(str(im_p))
        bake_in.colorspace_settings.name = colspace

        #        bake_in_tex.filepath = str(im_p)
        #        bake_in_tex.colorspace_settings.name = colspace

        node_in = mat.node_tree.nodes["Image Texture.001"]
        node_in.image = bake_in
        #        node_in.image.
        #

        base_out = bpy.data.images["bake_out.004"]
        node_out = mat.node_tree.nodes["Image Texture"]
        bake_out = base_out.copy()
        bake_out.colorspace_settings.name = colspace
        node_out.image = bake_out

        #        node_out.image = bpy.data.images.new("bake_out", 2048, 2048)
        #        node_out.image.colorspace_settings.name = colspace

        #    bake_in_tex.reload()
        #        bake_in_tex.update()
        oname = im_p.parent.parent.parent.name.replace("emale", "").replace("ale", "").replace(" ", "")
        oname += "_" + im_p.name[:-4] + ".png"
        out_p = out_d / oname

        bpy.ops.object.bake(type='EMIT',
                            use_clear=False)  # , width=2048, height=2048, margin=256, save_mode="EXTERNAL", filepath=str(out_p), uv_layer="UVMap")

        #        bpy.ops.image.save_as(copy=True, filepath=str(out_p))

        #        image_out = bake_out.copy()
        #        image_out.update()

        #        image_out.file_format = "PNG"
        #        image_out.filepath_raw = str(out_p)
        #        image_out.save()

        bpy.data.images.remove(bake_in)
        #        bpy.data.images.remove(image_out)

        #        bake_out_tex = bpy.data.images["bake_out"]

        bake_out.file_format = "PNG"
        bake_out.filepath_raw = str(out_p)
        bake_out.save()

        bpy.data.images.remove(bake_out)


#        bpy.data.images.remove(node_in.image)
#        bpy.data.images.remove(node_out.image)


#        bake_out_tex.file_format = "PNG"
##        bake_out_tex.filepath_raw = str(out_p)
#        bake_out_tex.colorspace_settings.name = colspace
#        bake_out_tex.save(filepath=str(out_p))

# bake_one(body_texture_names[0])
# for n in body_texture_names:
#    bake_one(n)

# for n in eye_texture_names:
#    bake_one(n)    
# bake_one(body_texture_names[0])

de_namemap = {"C": "Body_Colour", "N": "Body_Normal", "S": "Body_Spec"}

out_d = Path("")
out_d.mkdir(exist_ok=True)


def debake_one(path):
    name = path.name[:-4]
    b = name[:3]
    if b == "F01" or b == "F02" or b == "F04" or name == "F06_C": return
    out_p = out_d / (name + ".jpg")

    if out_p.exists(): return
    print(name)
    de_d = "Female/" if name[0] == "F" else "Male/"

    de_d += name[:3].replace("F", "Female ").replace("M", "Male ")
    de_d += "/Textures/JPG/"
    de_d += "/" + de_namemap[name[-1]] + ".jpg"

    de_d = root_d / de_d

    colspace = "Raw" if "_S" in name else "sRGB"
    bake_in = bpy.data.images.load(str(path))
    bake_in.colorspace_settings.name = colspace

    node_in = mat.node_tree.nodes["Image Texture.001"]
    node_in.image = bake_in

    #    base_out = bpy.data.images.load(str(de_d))
    node_out = mat.node_tree.nodes["Image Texture"]
    bake_out = bpy.data.images.load(str(de_d))  # base_out.copy()
    bake_out.scale(8192, 8192)
    bake_out.colorspace_settings.name = colspace
    bake_out.update()
    node_out.image = bake_out

    bpy.ops.object.bake(type='EMIT', use_clear=False)

    bpy.data.images.remove(bake_in)

    #    out_p = out_d / (name + ".jpg")
    bake_out.file_format = "JPEG"
    bake_out.filepath_raw = str(out_p)
    bake_out.save()
    #

    bpy.data.images.remove(bake_out)


#    bpy.data.images.remove(base_in)

debake_d = Path("")
# print(debake_d.exists())
debake_ps = list(debake_d.glob("*.jpg"))

for i, p in enumerate(debake_ps):
    debake_one(p)

# print(debake_ps[0])
# debake_one(debake_ps[0])
