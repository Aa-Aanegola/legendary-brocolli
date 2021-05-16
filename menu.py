import bpy


class VIEW3D_MT_lowpoly_add(bpy.types.Menu):
    bl_label = "Low Poly"

    def draw(self, context):
        layout = self.layout

        layout.menu("VIEW3D_MT_tree_add", text="Trees")


class VIEW3D_MT_tree_add(bpy.types.Menu):
    bl_label = "Tree"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.primitive_plane_add",
                        text="Conifer", icon="PLUGIN")
        layout.operator("mesh.primitive_plane_add",
                        text="Palm", icon="PLUGIN")
        layout.operator("mesh.primitive_plane_add",
                        text="Deciduous", icon="PLUGIN")


def menu_draw(self, context):
    '''
    Adds low poly menu
    '''
    self.layout.menu("VIEW3D_MT_lowpoly_add")


classes = (
    VIEW3D_MT_lowpoly_add,
    VIEW3D_MT_tree_add
)
