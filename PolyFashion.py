# Details of add-on

bl_info = {
    "name"       : "PolyFashion",
    "author"     : "Keerthan",
    "version"    : (1, 0, 0),
    "blender"    : (3, 3, 1),
    "location"   : "View 3D> UI > PoolyFashion",
    "description": "Easy setup",
    "category"   : "3D View",
}

import bpy

from bpy.types import (
    Panel,
    Operator,
    PropertyGroup
)

from bpy.props import (
    PointerProperty,
    CollectionProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    StringProperty,

)
import importlib.util
from pip._internal import main
import random
import string
import datetime
import os
import ast

light_types = {
    "POINT": ['color', 'energy', 'diffuse_factor', 'specular_factor', 'volume_factor', 'shadow_soft_size'],
    "SUN": ['color', 'energy', 'diffuse_factor', 'specular_factor', 'volume_factor', 'angle'],
    "SPOT": ['color', 'energy', 'diffuse_factor', 'specular_factor', 'volume_factor', 'shadow_soft_size'],
    "AREA": ['color', 'energy', 'diffuse_factor', 'specular_factor', 'volume_factor', 'shape', 'size'],
    }

def append_materials_from_blendfile(blendfile_path):
    with bpy.data.libraries.load(blendfile_path) as (data_from, data_to):
        data_to.materials = data_from.materials
        # print(f"All materials from '{blendfile_path}'.")
        return data_from.materials

blendfile_path = r"D:\Fiver Work\everythingagncy\snPath\PolyFashion\Light_Add-on.blend"
got_materials = append_materials_from_blendfile(blendfile_path)

print(got_materials)

def get_dir(chosen_dir):
    if os.path.exists(chosen_dir):
        return chosen_dir
    
    else: 
        try:
            chosen_dir = chosen_dir.replace("//", "\\")
            file_path = bpy.data.filepath
            file_dir = os.path.dirname(file_path)
            chosen_dir = file_dir + chosen_dir
            if os.path.exists(chosen_dir):
                return chosen_dir
            else:
                file_path = bpy.data.filepath
                file_dir = os.path.dirname(file_path)
                return file_dir
        except:
            file_path = bpy.data.filepath
            file_dir = os.path.dirname(file_path)
            return file_dir

def get_blend_files(self, context):
    scene = context.scene
    pfp = scene.pf_probs
    blend_dir = pfp.blend_dir
    
    blend_files = []
    
    for root, dirs, files in os.walk(blend_dir):
        for file in files:
            if file.endswith(".blend"):
                absolute_path = os.path.abspath(os.path.join(root, file))
                blend_files.append((absolute_path, os.path.splitext(file)[0], ''))
    
    return blend_files

def delete_collection_and_contents(coll_names):
    for collection_name in coll_names:
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            try:
                bpy.context.scene.collection.children.unlink(collection)
            except:
                pass
            if collection_name.startswith("PF_LS_"):
                bpy.data.collections.remove(collection)


def link_collection_as_child(selected_collection_name, child_collection_name):
    selected_collection = bpy.data.collections[selected_collection_name]
    child_collection = bpy.data.collections[child_collection_name]
    selected_collection.children.link(child_collection)
    # print(f"Collection '{child_collection_name}' linked as a child to '{selected_collection_name}' successfully.")


def generate_random_string():
    characters = string.ascii_lowercase + string.digits
    random_chars = ''.join(random.choice(characters) for _ in range(6))
    return random_chars

def modify_string(input_string):
    parts = input_string.split('.')
    modified_string = f"{parts[0]}_{generate_random_string()}"
    return modified_string


def change_object_names_in_collection(collection_name):
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        for obj in collection.objects:
            new_obj_name = modify_string(obj.name)
            obj.name = new_obj_name



def generate_random_collection_name():
    prefix = "PF_LS_"
    suffix_length = 6
    
    ps_lt_coll = []  
    for coll in bpy.data.collections:
        if coll.name.startswith(prefix):
            ps_lt_coll.append(coll.name)

    if len(ps_lt_coll)!=0:
        delete_collection_and_contents(ps_lt_coll)

    characters = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choice(characters) for _ in range(suffix_length))
    collection_name = prefix + suffix

    return collection_name

def create_collection(collection_name):
    if collection_name not in bpy.data.collections:
        pf_ls_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(pf_ls_collection)
        
def set_active_and_selected_collection(collection_name):
    target_collection = bpy.data.collections[collection_name]
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]
    bpy.context.view_layer.active_layer_collection.collection.hide_select = False
    # print(f"Collection '{collection_name}' set as active and selected successfully.")

def get_lights_collections_list(self, context):
    scene = context.scene
    pfp = scene.pf_probs
    blend_path = r"D:\Fiver Work\everythingagncy\snPath\PolyFashion\Light_Add-on.blend"
    
    available_coll = [("None", "None", '')]
    with bpy.data.libraries.load(blend_path) as (data_from, data_to):
        
        for collection_name in data_from.collections:
            available_coll.append((collection_name, collection_name, ''))

    return available_coll

def get_lights_list(self, context):
    scene = context.scene
    pf_internal_p = scene.pf_internal_probs
    available_ligths = [("None", "None", '')]
    collection_name = pf_internal_p.pf_ls_collection_name
    if collection_name:
        if collection_name in bpy.data.collections:
            collection = bpy.data.collections[collection_name]
            for obj in collection.all_objects:
                if obj.type == 'LIGHT':
                    available_ligths.append((obj.name, obj.name, ''))
    return available_ligths


def get_mats_list(self, context):
    available_mats = [("None", "None", '')]
    for mat in got_materials:
        if mat.name != 'Dots Stroke':
            available_mats.append((str([mat]), mat.name, ''))
    return available_mats


def format_property_name(name):
    formatted_name = name.replace('_', ' ').title()
    return formatted_name

def import_light_setup(self, context):
    scene = context.scene
    pf_internal_p = scene.pf_internal_probs
    blend_path = r"D:\Fiver Work\everythingagncy\snPath\PolyFashion\Light_Add-on.blend"

    collection_name = generate_random_collection_name()
    pf_internal_p.pf_ls_collection_name = collection_name
    create_collection(collection_name)

    file_path = blend_path
    inner_path = 'Collection'
    coll_name = self.light_setup
    
    if coll_name != 'None':
        delete_collection_and_contents([coll_name])
        set_active_and_selected_collection(collection_name)
        if not coll_name in bpy.data.collections:
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, coll_name),
                directory=os.path.join(file_path, inner_path),
                filename=coll_name
                )
            
            change_object_names_in_collection(coll_name)

        else:
            link_collection_as_child(collection_name, coll_name)

    available_ligths = get_lights_list(self, context)
    if len(available_ligths) == 1:
            scene.pf_probs.pf_lights = available_ligths[0][0]
            # print(available_ligths[0][0])
    else:
            scene.pf_probs.pf_lights = available_ligths[1][0]
            # print(available_ligths[1][0])

def get_bsdf_node(self, context):
    bsdf_node = []
    def recurive_bsdf(g_node):
        for avilable_node in g_node.node_tree.nodes:
            if avilable_node.type == 'BSDF_PRINCIPLED':
                bsdf_node.append([avilable_node, g_node])
            elif avilable_node.type == 'GROUP':
                g_node = avilable_node
                recurive_bsdf(g_node)

    obj = bpy.context.active_object
    if obj and obj.active_material:
        bsdf = obj.active_material
        # bsdf.use_nodes = True
        for avilable_node in bsdf.node_tree.nodes:
            if avilable_node.type == 'BSDF_PRINCIPLED':
                bsdf_node.append([avilable_node, bsdf])
            elif avilable_node.type == 'GROUP':
                g_node = avilable_node
                recurive_bsdf(g_node)

    available_bsdf_nodes = [("None", "None", '')]
    for bsdf in bsdf_node:
        available_bsdf_nodes.append((str(bsdf), bsdf[0].name, ''))
    return available_bsdf_nodes







class PF_Internal_Properties(PropertyGroup):
    pf_ls_collection_name: bpy.props.StringProperty(name="Collection Name", default='')


class PF_Properties(PropertyGroup):
    blend_dir: StringProperty(
        name="Directory",
        description="Choose the directory",
        subtype='DIR_PATH'
    )
        
    light_setup: EnumProperty(
        name= "Lighting Setup",
        description= "Available lighting setup",
        items=get_lights_collections_list,
        update=import_light_setup,
     )
    
    pf_lights: EnumProperty(
        name= "Lights",
        description= "Available lights",
        items=get_lights_list,
        # update=import_light_setup,
     )
    
    mat_lib: EnumProperty(
        name= "Materials",
        description= "Available materials",
        items=get_mats_list,
        # update=import_light_setup,
     )
    
    bsdf_nodes: EnumProperty(
        name= "BSDF Nodes",
        description= "Available BSDF nodes",
        items=get_bsdf_node,
        # update=import_light_setup,
     )

def find_and_update_principled_bsdf_base_color(context):
    scene = context.scene
    pfp = scene.pf_probs
    bsdf_node = eval(pfp.bsdf_nodes)[0]
    base_color_input = bsdf_node.inputs[0]

    # Check if the input is linked
    if base_color_input.is_linked:
        print(base_color_input.is_linked)
        base_color_input.is_linked = False
        # Disconnect all links from the "Base Color" input
    #     for link in base_color_input.links:
    #         material.node_tree.links.remove(link)
    #         print("Link removed from Base Color input.")
    # else:
    #     print("Base Color input is not linked.")

    # return


# Call the function



class PF_OT_unlink_base_color(Operator):
    """Unlink base color"""
    bl_idname = "pf.unlink_base_color"
    bl_label = "Unlink Base Color"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pfp = scene.pf_probs

        bsdf_node = eval(pfp.bsdf_nodes)
        base_color_input = bsdf_node[0].inputs[0]
        for link in base_color_input.links:
            bsdf_node[1].node_tree.links.remove(link)

        return {'FINISHED'}

class PF_OT_import_scene(Operator):
    """Import scene"""
    bl_idname = "pf.import_scene"
    bl_label = "Import"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pfp = scene.pf_probs
        blend_path = r"D:\Fiver Work\everythingagncy\snPath\Light_Add-on.blend"

        with bpy.data.libraries.load(blend_path) as (data_from, data_to):
        
            for collection_name in data_from.collections:
                print(collection_name)
                collection = bpy.data.collections[collection_name] 

        return {'FINISHED'}


class PF_OT_remove_material(Operator):
    """Remove material"""
    bl_idname = "pf.remove_material"
    bl_label = "Remove Material"
    bl_options = {"REGISTER", "UNDO"}  

    def execute(self, context):
        obj = context.active_object
        active_material = obj.active_material

        if active_material:
            bpy.ops.object.material_slot_remove()

        return {'FINISHED'}  
    
class PF_OT_add_material(Operator):
    """Add material"""
    bl_idname = "pf.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}  

    def execute(self, context):
        scene = context.scene
        pfp = scene.pf_probs

        obj = context.active_object
        selected_material = eval(pfp.mat_lib)[0]
        new_material = selected_material.copy()
        new_material.use_fake_user = False
        obj.data.materials.append(new_material)

        # # Rename the applied material with the prefix "PF"
        # new_material.name = f"PF_{self.material_name}"

        # print(f"Material '{self.material_name}' applied to '{obj.name}' and renamed to 'PF_{self.material_name}'.")

        return {'FINISHED'}  




class PF_PT_panel_lighting_setting(Panel):
    bl_idname = "PF_PT_panel_lighting_setting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PolyFashion"
    bl_label = "Lighting Settings"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pfp = scene.pf_probs

        layout.prop(pfp, 'light_setup', text='Lighting Setup')
        layout.prop(pfp, 'pf_lights', text='Lights')

        pf_light = pfp.pf_lights

        if pf_light != 'None':
            light = bpy.data.objects[pf_light].data

            light_settings = light_types[light.type]

            for ls in light_settings:
                property_name = format_property_name(ls)
                layout.prop(light, ls,
                                    text=property_name)
                




class PF_PT_panel_material(Panel):
    bl_idname = "PF_PT_panel_material"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PolyFashion"
    bl_label = "PolyFashion Materials"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pfp = scene.pf_probs

        layout.prop(pfp, 'mat_lib', text='Materials')
        obj = context.active_object

        # layout.operator("pf.add_material", text = 'Add Material')
        # layout.operator("pf.load", text = 'Load')
        # layout.prop(pfp, 'bsdf_nodes', text='BSDF Nodes')

        if pfp.bsdf_nodes:
            bsdf_node = eval(pfp.bsdf_nodes)
        # print(bsdf_node)


        # active_material = obj.active_material
        material_slots = context.object.material_slots
        # box = self.layout.box()
        # row = box.column(align=True)
        # row.template_preview(slected_mat, show_buttons=False)

        # row1.label(text='Test')

        # for slot in material_slots:
        #     row.template_preview(slot.material, show_buttons=False, preview_id="eevee.smallpreview")
        # #     print(slot.material.name)
        # #     row.template_preview(slot.material, show_buttons=False) #, preview_id="eevee.smallpreview")
        #     row.template_ID_preview(slot, 'material',hide_buttons=False, )  #"active_material"

        # # layout.template_preview(active_material, text="ff", show_buttons=True, preview_id="MATERIAL_PT_MatPreview")     


        if obj and obj.type == 'MESH':
            layout.operator("pf.add_material", text = 'Add Material')
            layout.operator("pf.remove_material", text = 'Remove Material')
            layout.label(text=f"Materials for {obj.name}:")
            mat_list = layout.template_list("MATERIAL_UL_matslots", "", obj, "material_slots", obj, "active_material_index")

            if mat_list:
                # Draw additional UI elements for each material
                for i, slot in enumerate(obj.material_slots):
                    row = layout.row()
                    row.prop_search(slot, "material", bpy.data, "materials", text=f"Material {i + 1}")

            layout.prop(pfp, 'bsdf_nodes', text='BSDF Nodes')

            if bsdf_node != 'None':
                base_color_input = bsdf_node[0].inputs[0]
                if base_color_input.is_linked:
                    layout.operator("pf.unlink_base_color", text = 'Unlink Base Color')
                else:
                    layout.prop(bsdf_node[0].inputs[0], "default_value", text="Base Color")


                layout.prop(bsdf_node[0].inputs[3], "default_value", text="IOR")

        else:
            layout.label(text="Select a mesh object to see material list.")


classes = (
    PF_Internal_Properties,
    PF_Properties,
    PF_PT_panel_lighting_setting,
    PF_PT_panel_material,
    PF_OT_add_material,
    PF_OT_remove_material,
    PF_OT_unlink_base_color,
    PF_OT_import_scene,
)


def register():    
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.pf_internal_probs = PointerProperty(type=PF_Internal_Properties)
    bpy.types.Scene.pf_probs = PointerProperty(type=PF_Properties)



        
def unregister():
    del bpy.types.Scene.pf_internal_probs
    del bpy.types.Scene.pf_probs
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
       
if __name__ == "__main__":
    register()