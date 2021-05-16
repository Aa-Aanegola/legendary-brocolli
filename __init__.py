import sys
import os
import pathlib

# Check if this add-on is being reloaded
if "bpy" in locals():
    # Reloading .py files
    import importlib

    from . import menu  # addon_props.py (properties are created here)
    importlib.reload(menu)
# Or if this is the first load of this add-on
else:
    import bpy
    from . import menu

bl_info = {
    "name": "Low Poly Trees",
    "author": "Aakash Aenegola and Ishaan Shah",
    "version": 0.1,
    "blender": (2, 90, 0),
    "location": "View 3D > Add > Low Poly",
    "category": "Development"
}

classes = [*menu.classes]


def register():
    for _class in classes:
        bpy.utils.register_class(_class)

    bpy.types.VIEW3D_MT_add.append(menu.menu_draw)


def unregister():
    for _class in classes:
        bpy.utils.unregister_class(_class)

    bpy.types.VIEW3D_MT_add.remove(menu.menu_draw)


if __name__ == "__main__":
    register()
