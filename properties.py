import bpy
from bpy.props import (
    PointerProperty, BoolProperty, IntProperty, FloatProperty,
    FloatVectorProperty, EnumProperty, StringProperty
)
from bpy.utils import register_class, unregister_class
from math import pi
from . import utils

# Update handlers -------------------------------------------------------------
def _create_update_handler():
    def handler(self, context):
        utils._safe_place_objects(context)
    return handler

update_ObjectsInPoints = _create_update_handler()
update_ObjectsInEdges = _create_update_handler()
update_DelCurvePoints = _create_update_handler()
update_DelCurveEdges = _create_update_handler()
update_clip_settings = _create_update_handler()
update_equals_settings = _create_update_handler()
update_edge_spacing = _create_update_handler()

def update_curve(self, context):
    obj = context.object
    if not obj or obj.type != 'CURVE':
        return
    try:
        new_curve = self.curv
        if new_curve is None:
            self.curv_original_name = ""
            return
        self.curv_original_name = new_curve.name
        if hasattr(obj, 'curve_operftion'):
            obj.curve_operftion.SubdiveCurveSet = 0
        if obj.data != new_curve:
            utils.clear_instances(obj)
            obj.data = new_curve
            utils._safe_place_objects(context)
    except ReferenceError:
        pass

def update_subdivide(self, context):
    obj = context.object
    if not obj or obj.type != 'CURVE':
        return
    try:
        main_props = obj.main_object
        orig_name = main_props.curv_original_name
        if not orig_name:
            return
        orig_curve = bpy.data.curves.get(orig_name)
        if not orig_curve:
            return
        level = self.SubdiveCurveSet
        current_curve = obj.data
        prev_active = context.view_layer.objects.active
        prev_mode = context.mode if context.active_object else 'OBJECT'
        if current_curve and current_curve.name != orig_name and current_curve.name.startswith(orig_name + "_subdiv"):
            obj.data = orig_curve
            if current_curve.users == 0:
                bpy.data.curves.remove(current_curve)
        if level == 0:
            obj.data = orig_curve
        else:
            temp = orig_curve.copy()
            temp.name = f"{orig_name}_subdiv"
            obj.data = temp
            if obj.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.curve.select_all(action='SELECT')
            if level > 0:
                bpy.ops.curve.subdivide(number_cuts=level)
            bpy.ops.object.mode_set(mode='OBJECT')
        if prev_active:
            context.view_layer.objects.active = prev_active
            if prev_mode == 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
        utils._safe_place_objects(context)
    except ReferenceError:
        pass

# Property Groups ------------------------------------------------------------
class MainObject(bpy.types.PropertyGroup):
    curv: PointerProperty(
        name='Curve',
        type=bpy.types.Curve,
        update=update_curve,
        description="Select curve to use"
    )
    curv_original_name: StringProperty(
        default="",
        description="Original curve name for subdivision tracking"
    )
    ObjectsInPoints: PointerProperty(
        name='Point Object',
        type=bpy.types.Object,
        update=update_ObjectsInPoints,
        description="Object to place at curve points"
    )
    ObjectsInEdges: PointerProperty(
        name='Edge Object',
        type=bpy.types.Object,
        update=update_ObjectsInEdges,
        description="Object to place along curve edges"
    )

class CurveOption(bpy.types.PropertyGroup):
    SubdiveCurveSet: IntProperty(
        name="Subdivide",
        default=0,
        min=0,
        soft_max=5,
        update=update_subdivide,
        description="Number of subdivision levels"
    )
    DelCurvePoints: BoolProperty(
        name="Hide Point Objects",
        default=False,
        update=update_DelCurvePoints,
        description="Hide objects placed at points"
    )
    DelCurveEdges: BoolProperty(
        name="Hide Edge Objects",
        default=False,
        update=update_DelCurveEdges,
        description="Hide objects placed along edges"
    )

class SegmentEnds(bpy.types.PropertyGroup):
    EqualLengths: BoolProperty(
        name="Use Range",
        default=False,
        update=update_equals_settings,
        description="Limit placement to specific range"
    )
    StartEdge: FloatProperty(
        name="Start",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=update_equals_settings,
        description="Start of placement range"
    )
    EndEdge: FloatProperty(
        name="End",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        update=update_equals_settings,
        description="End of placement range"
    )
    ClipOn: BoolProperty(
        name="Enable Clip",
        default=False,
        update=update_clip_settings,
        description="Enable distance-based clipping from ends"
    )
    ClipDistance: FloatProperty(
        name="Distance",
        default=0.0,
        min=0.0,
        soft_max=10.0,
        subtype='DISTANCE',
        update=update_clip_settings,
        description="Distance to clip from each end"
    )

class EdgeSpacingProps(bpy.types.PropertyGroup):
    use_distance: BoolProperty(
        name="Use Distance",
        default=False,
        update=update_edge_spacing,
        description="Place objects at specified distance intervals"
    )
    use_count: BoolProperty(
        name="Use Count",
        default=False,
        update=update_edge_spacing,
        description="Place specified number of objects per segment"
    )
    edge_distance: FloatProperty(
        name="Distance",
        default=1.0,
        min=0.001,
        soft_max=100.0,
        subtype='DISTANCE',
        update=update_edge_spacing,
        description="Distance between edge objects"
    )
    edge_count: IntProperty(
        name="Count",
        default=1,
        min=1,
        soft_max=100,
        update=update_edge_spacing,
        description="Number of objects per segment"
    )
    offset_start: FloatProperty(
        name="Offset Start",
        default=0.0,
        min=0.0,
        soft_max=10.0,
        subtype='DISTANCE',
        update=update_edge_spacing,
        description="Offset from segment start"
    )
    offset_end: FloatProperty(
        name="Offset End",
        default=0.0,
        min=0.0,
        soft_max=10.0,
        subtype='DISTANCE',
        update=update_edge_spacing,
        description="Offset from segment end"
    )

class OptionBase(bpy.types.PropertyGroup):
    ScaleObject: FloatProperty(name="Uniform Scale", default=1.0, min=0.0)
    NormalizationScaleObject: BoolProperty(name="Use Custom Scale", default=False)
    ScaleNormalizationObject: FloatVectorProperty(
        name="Custom Scale", size=3, min=0.0, default=(1.0, 1.0, 1.0), subtype='XYZ'
    )
    RandScaleObject: BoolProperty(name="Random Scale", default=False)
    RandScaleObjectSlider: IntProperty(name="Seed", default=0, min=0)
    RandScaleLockX: BoolProperty(name="X", default=False, update=_create_update_handler())
    RandScaleLockY: BoolProperty(name="Y", default=False, update=_create_update_handler())
    RandScaleLockZ: BoolProperty(name="Z", default=False, update=_create_update_handler())
    NormalizationRotateObject: FloatVectorProperty(
        name="Rotation", subtype='EULER', size=3, min=-2*pi, max=2*pi, default=(0.0, 0.0, 0.0)
    )
    RandRotateObject: BoolProperty(name="Random Rotation", default=False)
    RandRoutateObjectSlider: IntProperty(name="Seed", default=0, min=0)
    RandRotLockX: BoolProperty(name="X", default=False, update=_create_update_handler())
    RandRotLockY: BoolProperty(name="Y", default=False, update=_create_update_handler())
    RandRotLockZ: BoolProperty(name="Z", default=False, update=_create_update_handler())

class PointOptionSettings(OptionBase):
    pass

class EdgeOptionSettings(OptionBase):
    pass

class OptionContainerGroup(bpy.types.PropertyGroup):
    select_target: EnumProperty(
        name="Target",
        description="Select which object type to configure",
        items=[
            ("2", "Point Object", "Settings for objects placed at points"),
            ("3", "Edge Object", "Settings for objects placed along edges"),
        ],
        default="2"
    )
    point: PointerProperty(type=PointOptionSettings)
    edge: PointerProperty(type=EdgeOptionSettings)

classes = [
    MainObject,
    CurveOption,
    SegmentEnds,
    EdgeSpacingProps,
    OptionBase,
    PointOptionSettings,
    EdgeOptionSettings,
    OptionContainerGroup,
]

def register():
    for cl in classes:
        register_class(cl)
    bpy.types.Object.main_object = PointerProperty(type=MainObject)
    bpy.types.Object.curve_operftion = PointerProperty(type=CurveOption)
    bpy.types.Object.curve_equals = PointerProperty(type=SegmentEnds)
    bpy.types.Object.curve_option_container = PointerProperty(type=OptionContainerGroup)
    bpy.types.Object.edge_spacing_props = PointerProperty(type=EdgeSpacingProps)
    bpy.types.Object.starselor_collection_name = StringProperty(default="")

def unregister():
    for prop in ['main_object', 'curve_operftion', 'curve_equals',
                 'curve_option_container', 'edge_spacing_props', 'starselor_collection_name']:
        try:
            delattr(bpy.types.Object, prop)
        except:
            pass
    for cl in reversed(classes):
        try:
            unregister_class(cl)
        except:
            pass