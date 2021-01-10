# --------------------------------------------------------------------------
#
# Import X-Plane OBJ8 .obj files into Blender 2.90.
# Properties and records that are currently supported:
# - TEXTURE
# - TEXTURE_LIT
# - TEXTURE_NORMAL
# - VT
# - IDX10/IDX
# - TRIS
# - Animation commands implemented but NOT tested, i.e. experimental feature at the moment
#
# Input file format specification https://developer.x-plane.com/article/obj8-file-format-specification/
#
# Based on XPlaneImport 1.0.1 by David C. Prue <dave.prue@lahar.net> (2017)
#
# MIT License
#
# Copyright 2020 FSWindowSeat <muppetlabs@FSWindowSeat.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# XPlaneImport 1.0.1 for Blender by David C. Prue <dave.prue@lahar.net> 20-July-2017
# https://github.com/daveprue/XPlaneImport/releases
#
# ---------------------------------------------------------------------------

import bpy
import os
import pathlib
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )


class XPlaneImport(bpy.types.Operator, ImportHelper):
    # Import from X-Plane Object file format (.obj)
    bl_label = "Import X-Plane OBJ files"
    bl_idname = "import.xplane_obj"

    # Filter and only show .obj files in import dialog
    filename_ext = ".obj"
    file_no = 1

    filter_glob: StringProperty(
        default="*.obj",
        options={'HIDDEN'},
    )

    # Allow to select multiple files
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        # Get the folder
        folder = (os.path.dirname(self.filepath))

        # Iterate through all of the selected files
        for j, i in enumerate(self.files):
            # Create new collection
            obj_collection = bpy.data.collections.new('%d %s' % (self.file_no, i.name))
            bpy.context.scene.collection.children.link(obj_collection)

            # Generate full path and process specific file
            obj_filepath = (os.path.join(folder, i.name))
            self.process_file(obj_filepath, obj_collection)
            self.file_no += 1

            print("Imported %s" % i.name)

        return {"FINISHED"}

    def process_file(self, filepath, obj_collection):
        """
        This function reads the X-Plane .obj file, parses through its information line by line and re-creates the
        object in Blender. Input file format specification,
        https://developer.x-plane.com/article/obj8-file-format-specification/

        :param filepath: Path and filename to .obj file
        :param obj_collection: Reference to Blender collection
        :return: void
        """

        # Local Vars
        verts = []
        vert_normals = []
        vert_uvs = []
        faces = []
        origin_temp = Vector((0, 0, 0))
        anim_nesting = 0
        a_trans = [origin_temp]
        trans_available = False
        objects = []

        # Create and add a material
        material = bpy.data.materials.new(name='Material')
        material.use_nodes = True
        material_nodes = material.node_tree.nodes
        material_links = material.node_tree.links

        # Get Material and Principled Bidirectional Scattering Distribution Function (BSDF) nodes
        material_output = material_nodes.get('Material Output')
        bsdf = material_nodes.get('Principled BSDF')
        bsdf.inputs['Roughness'].default_value = 0.5
        bsdf.location = Vector((0, 0))

        # Parse .obj file
        f = open(filepath, 'r')
        lines = f.readlines()
        f.close()

        # Loop through .obj file line by line
        for line_str in lines:
            # Split line items
            line_items = line_str.split()
            if len(line_items) < 2:
                continue

            # Process default texture
            if line_items[0] == 'TEXTURE':
                # Create Base Color node
                def_tex = material_nodes.new('ShaderNodeTexImage')
                def_tex.label = 'DEFAULT TEXTURE'
                def_tex.location = Vector((-310, -185))

                # Load and assign base texture file
                #tex_file_name = line_items[1]
                #dir_path = pathlib.PureWindowsPath(os.path.dirname(filepath))
                #texture_path = pathlib.PureWindowsPath(tex_file_name)
                
                # Load and assign base texture file and link Color and Alpha channels between Base Color and BSDF nodes
                texture = self.load_texture(filepath, line_items[1])
                if texture is not None:
                    def_tex.image = texture
                    material_links.new(bsdf.inputs['Base Color'], def_tex.outputs['Color'])
                    material_links.new(bsdf.inputs['Alpha'], def_tex.outputs['Alpha'])

            # Process draped texture. Note: Supported in XP-11. Carbon copy of default texture processing as it appears
            #                               that draped textures aren't supported in FS2020.
            if line_items[0] == 'TEXTURE_DRAPED':
                # Create Base Color node
                def_tex = material_nodes.new('ShaderNodeTexImage')
                def_tex.label = 'DRAPED TEXTURE'
                def_tex.location = Vector((-310, -185))

                # Load and assign base texture file and link Color and Alpha channels between Base Color and BSDF nodes
                texture = self.load_texture(filepath, line_items[1])
                if texture is not None:
                    def_tex.image = texture
                    material_links.new(bsdf.inputs['Base Color'], def_tex.outputs['Color'])
                    material_links.new(bsdf.inputs['Alpha'], def_tex.outputs['Alpha'])


            # Process lighted/emissive texture
            if line_items[0] == 'TEXTURE_LIT':
                # Create and link Mix Shader
                mix_shader = material_nodes.new('ShaderNodeMixShader')
                mix_shader.label = 'MIX SHADER'
                mix_shader.location = Vector((310, 68))
                material_output.location = Vector((515, 93))
                material_links.new(bsdf.outputs[0], mix_shader.inputs[2])
                material_links.new(mix_shader.outputs[0], material_output.inputs[0])

                # Create and link Emissive node
                emissive = material_nodes.new('ShaderNodeEmission')
                emissive.label = 'EMISSIVE'
                emissive.location = Vector((0, 140))
                emissive.inputs['Color'].default_value = Vector((0.05, 0.05, 0.05, 0.0))
                material_links.new(emissive.outputs['Emission'],mix_shader.inputs[1])

                # Create Emissive texture
                emissive_tex = material_nodes.new('ShaderNodeTexImage')
                emissive_tex.label = 'EMISSIVE TEXTURE'
                emissive_tex.location = Vector((-310, 115))

                # Load and assign base texture file and link Color channel of Emissive Texture node to Emission channel of BSDF node
                texture = self.load_texture(filepath, line_items[1])
                if texture is not None:
                    emissive_tex.image = texture
                    material_links.new(emissive.inputs['Color'], emissive_tex.outputs['Color'])

            # Process specular + normal map
            if line_items[0] == 'TEXTURE_NORMAL':
                # Create and link Normal Map
                norm_map = material_nodes.new('ShaderNodeNormalMap')
                norm_map.label = 'NORMAL MAP'
                norm_map.uv_map = 'UVMap'
                norm_map.location = Vector((-310, -481))
                material_links.new(norm_map.outputs['Normal'], bsdf.inputs['Normal'])

                # Create Normal Map texture
                norm_map_tex = material_nodes.new('ShaderNodeTexImage')
                norm_map_tex.label = 'NORMAL MAP TEXTURE'
                norm_map_tex.location = Vector((-610, -580))

                # Load and assign base texture file and link Color channel of Normal Map Texture node to Color channel of Normal Map nod
                texture = self.load_texture(filepath, line_items[1])
                if texture is not None:
                    norm_map_tex.image = texture
                    material_links.new(norm_map.inputs['Color'], norm_map_tex.outputs['Color'])

            # Process triangle vertex table entries (VT). The eight numbers represent a triplet coordinate (x,y,z)
            # a triplet normal coordinate (x,y,z), and a corresponding texture coordinate (u,v / x,y)
            if line_items[0] == 'VT':
                vx = float(line_items[1])
                vy = float(line_items[3]) * -1
                vz = float(line_items[2])
                verts.append((vx, vy, vz))

                vnx = float(line_items[4])
                vny = float(line_items[6]) * -1
                vnz = float(line_items[5])
                vert_normals.append((vnx, vny, vnz))

                uvx = float(line_items[7])
                uvy = float(line_items[8])
                vert_uvs.append((uvx, uvy))

            # Process index table entries (IDX10/IDX). The table is used to refer to vertices in the vertex table (VT)
            # arranged in blocks of ten (IDX10), or one (IDX)
            if line_items[0] == 'IDX10' or line_items[0] == 'IDX':
                faces.extend(map(int, line_items[1:]))

            # Process triangular elements (TRIS) to create mesh structure
            if line_items[0] == 'TRIS':
                obj_origin = Vector((0, 0, 0))
                tris_offset, tris_count = int(line_items[1]), int(line_items[2])
                obj_lst = faces[tris_offset:tris_offset+tris_count]

                if trans_available:
                    obj_origin = origin_temp

                objects.append((obj_origin, obj_lst))

            # Process animations. NOTE: NOT tested. Experimental
            if line_items[0] == 'ANIM_begin':
                anim_nesting += 1
                a_trans.append(Vector((0, 0, 0)))

            if line_items[0] == 'ANIM_trans':
                trans_x = float(line_items[1])
                trans_y = (float(line_items[2]))
                trans_z = float(line_items[3])
                o_t = Vector((trans_x, trans_y, trans_z))
                a_trans[anim_nesting] = o_t
                origin_temp = origin_temp + o_t
                trans_available = True

            if line_items[0] == 'ANIM_end':
                anim_nesting -= 1
                origin_temp = origin_temp - a_trans.pop()
                if anim_nesting == 0:
                    trans_available = False

        # Iterate through objects, create mesh and assign to the collection in Blender
        obj_no = 1
        for orig, obj in objects:
            faces = tuple(zip(*[iter(obj)]*3))
            obj_mesh = self.create_mesh('OBJ %d.%d' % (self.file_no, obj_no), orig, verts, vert_normals, vert_uvs, faces, material)

            # Link object to object collection and make active
            obj_collection.objects.link(obj_mesh)
            bpy.context.view_layer.objects.active = obj_mesh

            obj_no += 1

        return

    def create_mesh(self, name, origin, verts, vert_normals, vert_uvs, faces, material):
        """
        This function processes the information collected from the .obj file to create a corresponding
        mesh and assigns it to the Blender collection

        :param name: Name of object, i.e. "OBJ" + running integer counter
        :param origin: Origin coordinates/vector 0,0,0 by default
        :param verts: Collection of triplet coordinates
        :param vert_normals: Collection of triplet normal coordinates
        :param vert_uvs: Collection of texture coordinates
        :param faces: Collection of faces read from .obj file
        :param material: Reference to Blender material node
        :return: object
        """

        # Create mesh and object
        me = bpy.data.meshes.new(name+'Mesh')
        obj = bpy.data.objects.new(name, me)
        obj.location = origin
        obj.show_name = False

        # Create mesh from given vertices and faces
        me.from_pydata(verts, [], faces)

        # Assign the Material to the object
        me.materials.append(material)

        # Assign the UV coordinates to each vertex
        me.uv_layers.new(name="UVMap")
        me.uv_layers[-1].data.foreach_set("uv", [uv for pair in [vert_uvs[l.vertex_index] for l in me.loops] for uv in pair])

        # Assign the normals for each vertex
        vindex = 0
        for vertex in me.vertices:
            vertex.normal = vert_normals[vindex]
            vindex += 1

        # Update mesh with new data
        me.flip_normals()
        me.update(calc_edges=True)

        return obj


    def load_texture(self, filepath, tex_file_name):
        """
        This function loads the texture file from disk. In case the texture cannot be found,
        it attemps to load the file with alterantive extensions, e.g. .dds instead of .png.

        :param filepath: Path texture file folder
        :param tex_file_name: Name texture file
        :return: texture/image
        """

        # Concatenate file path and name
        dir_path = pathlib.PureWindowsPath(os.path.dirname(filepath))
        texture_path = pathlib.PureWindowsPath(tex_file_name)
        
        # 1st attempt to load texture file
        try:
            texture = bpy.data.images.load(os.path.normpath(os.path.join(dir_path, texture_path)))
        except:
            texture = None

        # In case the 1st attempt failed, attempt to load filed with an alternate extension, i.e. .dds -> .png and vice versa
        # Note: For some reason it is fairly common that the file extensions listed in the .obj file are incorrect
        if(texture is None):
            file_name, file_extension = os.path.splitext(tex_file_name)

            if(file_extension == '.png'):
                texture_path = pathlib.PureWindowsPath(file_name + ".dds")
            
            elif(file_extension == '.dds'):
                texture_path = pathlib.PureWindowsPath(file_name + ".png")

            # 2nd attempt to texture load file
            try:
                texture = bpy.data.images.load(os.path.normpath(os.path.join(dir_path, texture_path)))
            except:
                texture = None

        return texture
