# Blender Import XP Object
Import X-Plane OBJ8 .obj files into Blender 2.90.
Properties and records that are currently supported:
- TEXTURE
- TEXTURE_LIT
- VT
- IDX10/IDX
- TRIS
- Animation commands implemented but NOT tested, i.e. experimental feature at the moment

## Installation

- Download the latest release [v1.1-alpha.zip](https://github.com/FSWindowSeat/BlenderImportXPObj/releases/download/v1.1-alpha/BlenderImportXPObj_1_1_alpha.zip)
  and safe the file to a local directory

- Open Blender (Version 2.90 supported) and go to Edit -> Preferences -> Addons

- (1) Click Install... and (2) select .zip file in local directory and (3) click Install Add-on 

- Remember to check the checkbox next to the new entry to enable the Add-on in Blender! 

- Close Blender Preferences window

<img src="https://fswindowseat.com/images/blenderimportxpobj/blenderimportxpobj_install_addon.png" alt="Installation"/>

## How To

- Open Blender and go to File -> Import -> Import X-Plane obj files

- Select one, or multiple X-Plane .obj files and click Import X-Plane OBJ files

<img src="https://fswindowseat.com/images/blenderimportxpobj/blenderimportxpobj.png" alt="Blender 2.90"/>

## Notes

This tool works primarily for scenery and similar static objects. While I have kept David's code to process animations
also, I haven't tested, nor touched it. So at this point I have listed this as an experimental/legacy feature.

If you encounter any issues with a model's textures, e.g. overly bright night textures, or textures showing a metallic shine,
go to the Shading tab and experiment with the settings and relationships of the various shaders.

If a model doesn't import properly, go to Window -> Toggle System Console and check for any errors. In my testing,
I have encountered plenty of .obj files that referred to non-existing texture files which can cause the importer to fail.

## References

Input file format specification https://developer.x-plane.com/article/obj8-file-format-specification/

Based on XPlaneImport 1.0.1 by David C. Prue <dave.prue@lahar.net> (2017)
