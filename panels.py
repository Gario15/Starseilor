import bpy
from bpy.utils import register_class, unregister_class
from . import utils

class MainPanel(bpy.types.Panel):
    bl_label = "Starselor"
    bl_idname = "PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'main_object'):
            layout.label(text="Select a curve object", icon='INFO')
            return
        props = obj.main_object
        coll_name = utils.get_collection_name(obj)
        coll = bpy.data.collections.get(coll_name)
        if coll:
            box = layout.box()
            box.label(text=f"Collection: {coll_name}", icon='COLLECTION_COLOR_01')
            box.label(text=f"Objects: {len(coll.objects)}")
        box = layout.box()
        box.label(text="Curve and Objects:", icon='CURVE_DATA')
        box.prop(props, "curv")
        col = box.column(align=True)
        col.prop(props, "ObjectsInPoints")
        col.prop(props, "ObjectsInEdges")
        row = layout.row(align=True)
        row.operator("object.place_objects", text="Place Objects", icon='OBJECT_DATA')
        row.operator("object.clear_instances", text="Clear", icon='X')
        layout.separator()
        layout.operator("object.clear_all_instances", text="Clear All Starselor Collections", icon='TRASH')

class PanelCurveOption(bpy.types.Panel):
    bl_label = "Curve Options"
    bl_idname = "PT_PanelCurveOption"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_operftion'):
            return
        props = obj.curve_operftion
        col = layout.column(align=True)
        col.operator("curve.toggle_handle_type", text="Toggle Handles", icon='MOD_CURVE')
        col.separator()
        col.prop(props, "SubdiveCurveSet")

class PanelDeletePart(bpy.types.Panel):
    bl_label = "Visibility"
    bl_idname = "PT_DeletePart"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_PanelCurveOption'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_operftion'):
            return
        props = obj.curve_operftion
        box = layout.box()
        box.label(text="Hide Objects:", icon='HIDE_OFF')
        col = box.column(align=True)
        col.prop(props, "DelCurvePoints")
        col.prop(props, "DelCurveEdges")

class EqualsPanel(bpy.types.Panel):
    bl_label = "Placement Range"
    bl_idname = "PT_Equals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_equals'):
            return
        props = obj.curve_equals
        box = layout.box()
        box.prop(props, "EqualLengths")
        if props.EqualLengths:
            col = box.column(align=True)
            col.prop(props, "StartEdge")
            col.prop(props, "EndEdge")

class ClipEqualsObj(bpy.types.Panel):
    bl_label = "End Clipping"
    bl_idname = "PT_ClipEquals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_Equals'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_equals'):
            return
        props = obj.curve_equals
        box = layout.box()
        box.prop(props, "ClipOn")
        if props.ClipOn:
            col = box.column()
            col.prop(props, "ClipDistance")

class EdgeSpacingPanel(bpy.types.Panel):
    bl_label = "Edge Spacing"
    bl_idname = "PT_EdgeSpacing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'edge_spacing_props'):
            return
        props = obj.edge_spacing_props
        box = layout.box()
        col = box.column(align=True)
        col.prop(props, "use_distance")
        if props.use_distance:
            col.prop(props, "edge_distance")
        col.separator()
        col.prop(props, "use_count")
        if props.use_count:
            col.prop(props, "edge_count")
        box.separator()
        box.label(text="Offsets (in Blender units):", icon='TRACKING_REFINE_FORWARDS')
        col = box.column(align=True)
        col.prop(props, "offset_start")
        col.prop(props, "offset_end")

class OptionObjectPanel(bpy.types.Panel):
    bl_label = "Object Options"
    bl_idname = "PT_OptionObject"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_option_container'):
            return
        container = obj.curve_option_container
        row = layout.row()
        row.prop(container, "select_target", expand=True)

class ScalePanel(bpy.types.Panel):
    bl_label = "Scale Settings"
    bl_idname = "PT_ScalePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_OptionObject'
    bl_options = {'DEFAULT_CLOSED'}

    def get_active_settings(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'curve_option_container'):
            return None
        container = obj.curve_option_container
        if container.select_target == '2':
            return container.point
        return container.edge

    def draw(self, context):
        layout = self.layout
        settings = self.get_active_settings(context)
        if settings is None:
            return
        box = layout.box()
        box.prop(settings, "ScaleObject")
        box.prop(settings, "NormalizationScaleObject")
        if settings.NormalizationScaleObject:
            col = box.column(align=True)
            col.prop(settings, "ScaleNormalizationObject")
        box.separator()
        box.prop(settings, "RandScaleObject")
        if settings.RandScaleObject:
            col = box.column()
            col.prop(settings, "RandScaleObjectSlider")
            box.separator()
            box.label(text="Lock Random Scale Axes:", icon='LOCKED')
            row = box.row(align=True)
            row.prop(settings, "RandScaleLockX", toggle=True)
            row.prop(settings, "RandScaleLockY", toggle=True)
            row.prop(settings, "RandScaleLockZ", toggle=True)

class RotatePanel(bpy.types.Panel):
    bl_label = "Rotation Settings"
    bl_idname = "PT_RotatePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_OptionObject'
    bl_options = {'DEFAULT_CLOSED'}

    def get_active_settings(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'curve_option_container'):
            return None
        container = obj.curve_option_container
        if container.select_target == '2':
            return container.point
        return container.edge

    def draw(self, context):
        layout = self.layout
        settings = self.get_active_settings(context)
        if settings is None:
            return
        box = layout.box()
        box.prop(settings, "NormalizationRotateObject")
        box.separator()
        box.prop(settings, "RandRotateObject")
        if settings.RandRotateObject:
            col = box.column()
            col.prop(settings, "RandRoutateObjectSlider")
            box.separator()
            box.label(text="Lock Random Rotation Axes:", icon='LOCKED')
            row = box.row(align=True)
            row.prop(settings, "RandRotLockX", toggle=True)
            row.prop(settings, "RandRotLockY", toggle=True)
            row.prop(settings, "RandRotLockZ", toggle=True)

classes = [
    MainPanel,
    PanelCurveOption,
    PanelDeletePart,
    EqualsPanel,
    ClipEqualsObj,
    EdgeSpacingPanel,
    OptionObjectPanel,
    ScalePanel,
    RotatePanel,
]

def register():
    for cl in classes:
        register_class(cl)

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)