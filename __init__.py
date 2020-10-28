# ---------------------------------------------------------------------------
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
from . import ImportXPObj

bl_info = {
    "name": "Import X-Plane OBJ Files",
    "author": "FSWindowSeat",
    "version": (1,0,0),
    "blender": (2,90,0),
    "location": "File > Import/Export > XPlane",
    "description": "Import X-Plane obj files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export"
}


def menu_func(self, context):
    self.layout.operator(ImportXPObj.XPlaneImport.bl_idname, text="X-Plane Objects (.obj)")


def register():
    bpy.utils.register_class(ImportXPObj.XPlaneImport)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_class(ImportXPObj.XPlaneImport)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()