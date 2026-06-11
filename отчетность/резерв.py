bl_info = {
    "name": "Starselor",
    "author": "Glue",
    "version": (0, 5),
    "blender": (4, 0, 0),
    "location": "View3D > Toolbar > Starselor",
    "description": "Размещение объектов вдоль кривой с настройками (коллекции для каждой кривой)",
    "warning": "Beta version for education",
    "wiki_url": "Git",
    "category": "3D View",
}

import bpy
from bpy.utils import register_class, unregister_class
from math import pi
from bpy.types import Operator
from bpy.props import (
    PointerProperty, BoolProperty, IntProperty, FloatProperty,
    FloatVectorProperty, EnumProperty, StringProperty
)
import mathutils
import random
from mathutils import Vector, Euler, Quaternion, Matrix

# -----------------------------------------------------------------------------
INSTANCE_COLLECTION_PREFIX = "Starselor_"
RANDOM_SCALE_RANGE = (0.5, 1.5)
RANDOM_ROTATION_RANGE = (-pi/2, pi/2)

# -----------------------------------------------------------------------------
def get_collection_name(curve_obj):
    if curve_obj:
        base_name = curve_obj.name.replace(".", "_").replace(" ", "_")
        return f"{INSTANCE_COLLECTION_PREFIX}{base_name}"
    return f"{INSTANCE_COLLECTION_PREFIX}Default"

def get_instance_collection(curve_obj):
    coll_name = get_collection_name(curve_obj)
    
    coll = bpy.data.collections.get(coll_name)
    
    if coll is None:
        coll = bpy.data.collections.new(coll_name)
        if bpy.context.scene:
            bpy.context.scene.collection.children.link(coll)
        coll.hide_viewport = False
        coll.hide_render = False
        
        if curve_obj and hasattr(curve_obj, 'starselor_collection_name'):
            curve_obj.starselor_collection_name = coll_name
    
    return coll

def clear_instances(curve_obj):
    coll_name = get_collection_name(curve_obj)
    coll = bpy.data.collections.get(coll_name)
    
    if coll is None:
        return
    
    objects_to_remove = []
    try:
        objects_to_remove = [obj for obj in coll.objects if obj.name in bpy.data.objects]
    except ReferenceError:
        for obj in bpy.data.objects:
            if any(col.name == coll_name for col in obj.users_collection if col):
                objects_to_remove.append(obj)
    
    if objects_to_remove:
        try:
            bpy.data.batch_remove(objects_to_remove)
        except:
            for obj in objects_to_remove:
                try:
                    if obj.name in bpy.data.objects:
                        bpy.data.objects.remove(obj, do_unlink=True)
                except:
                    pass

def clear_all_instances():
    collections_to_remove = []
    for coll in bpy.data.collections:
        if coll.name.startswith(INSTANCE_COLLECTION_PREFIX):
            objects_to_remove = []
            try:
                objects_to_remove = [obj for obj in coll.objects if obj.name in bpy.data.objects]
            except:
                pass
            
            if objects_to_remove:
                try:
                    bpy.data.batch_remove(objects_to_remove)
                except:
                    for obj in objects_to_remove:
                        try:
                            if obj.name in bpy.data.objects:
                                bpy.data.objects.remove(obj, do_unlink=True)
                        except:
                            pass
            
            collections_to_remove.append(coll)
    
    for coll in collections_to_remove:
        try:
            bpy.data.collections.remove(coll)
        except:
            pass

# -----------------------------------------------------------------------------
def is_valid_context(context):
    try:
        return (context.object and 
                context.object.type == 'CURVE' and 
                hasattr(context.object, 'main_object') and
                context.object.name in bpy.data.objects)
    except ReferenceError:
        return False

def safe_place_objects(context):
    if is_valid_context(context):
        try:
            if not getattr(bpy.app, 'is_undoing', False) and not getattr(bpy.app, 'is_redoing', False):
                bpy.ops.object.place_objects()
        except:
            pass

def update_curve(self, context):
    obj = context.object
    if not obj or obj.type != 'CURVE':
        return
    try:
        new_curve = self.curve
        if new_curve is None:
            self.curve_original_name = ""
            return
        self.curve_original_name = new_curve.name
        if hasattr(obj, 'curve_options'):
            obj.curve_options.subdivide_curve_set = 0
        if obj.data != new_curve:
            clear_instances(obj)
            obj.data = new_curve
            safe_place_objects(context)
    except ReferenceError:
        pass

def update_subdivide(self, context):
    obj = context.object
    if not obj or obj.type != 'CURVE':
        return
    try:
        main_props = obj.main_object
        orig_name = main_props.curve_original_name
        if not orig_name:
            return
        orig_curve = bpy.data.curves.get(orig_name)
        if not orig_curve:
            return
        
        level = self.subdivide_curve_set
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
        
        safe_place_objects(context)
    except ReferenceError:
        pass

def create_update_handler():
    def handler(self, context):
        safe_place_objects(context)
    return handler

update_objects_in_points = create_update_handler()
update_objects_in_edges = create_update_handler()
update_del_curve_points = create_update_handler()
update_del_curve_edges = create_update_handler()
update_clip_settings = create_update_handler()
update_equals_settings = create_update_handler()
update_edge_spacing = create_update_handler()

# -----------------------------------------------------------------------------
_random_cache = {}

def get_random_scale_factors(seed, lock_x=False, lock_y=False, lock_z=False):
    key = f"scale_{seed}"
    if key not in _random_cache:
        random.seed(seed)
        _random_cache[key] = [random.uniform(*RANDOM_SCALE_RANGE) for _ in range(3)]
    
    factors = _random_cache[key].copy()
    if lock_x:
        factors[0] = 1.0
    if lock_y:
        factors[1] = 1.0
    if lock_z:
        factors[2] = 1.0
    
    return factors

def get_random_rotation_factors(seed, lock_x=False, lock_y=False, lock_z=False):
    key = f"rot_{seed}"
    if key not in _random_cache:
        random.seed(seed)
        _random_cache[key] = [random.uniform(*RANDOM_ROTATION_RANGE) for _ in range(3)]
    
    factors = _random_cache[key].copy()
    if lock_x:
        factors[0] = 0.0
    if lock_y:
        factors[1] = 0.0
    if lock_z:
        factors[2] = 0.0
    
    return factors

# -----------------------------------------------------------------------------
def apply_transforms(obj, settings, obj_hash=None):
    if obj_hash is None:
        obj_hash = hash(obj.name) % 10000
    
    if settings.normalization_scale_object:
        base_scale = Vector(settings.scale_normalization_object)
    else:
        base_scale = Vector((settings.scale_object,) * 3)

    if settings.rand_scale_object:
        seed = settings.rand_scale_object_slider + obj_hash
        rand_factors = Vector(get_random_scale_factors(
            seed,
            lock_x=settings.rand_scale_lock_x,
            lock_y=settings.rand_scale_lock_y,
            lock_z=settings.rand_scale_lock_z
        ))
        obj.scale = Vector(b * r for b, r in zip(base_scale, rand_factors))
    else:
        obj.scale = base_scale

    user_euler = Euler(settings.normalization_rotate_object)
    
    if settings.rand_rotate_object:
        seed = settings.rand_rotate_object_slider + obj_hash
        rand_rot = get_random_rotation_factors(
            seed,
            lock_x=settings.rand_rot_lock_x,
            lock_y=settings.rand_rot_lock_y,
            lock_z=settings.rand_rot_lock_z
        )
        user_euler = Euler(b + r for b, r in zip(user_euler, rand_rot))

    user_quat = user_euler.to_quaternion()
    obj.rotation_mode = 'QUATERNION'

    if 'edge' in settings.__class__.__name__.lower():
        obj.rotation_quaternion = obj.rotation_quaternion @ user_quat
    else:
        obj.rotation_quaternion = user_quat

# -----------------------------------------------------------------------------
def get_segment_positions(p0_world, p1_world, distance=None, count=None, 
                         offset_start=0.0, offset_end=0.0):
    segment_vector = p1_world - p0_world
    segment_length = segment_vector.length
    
    if segment_length == 0 or (distance is not None and distance <= 0):
        return [], None
    
    effective_start = offset_start
    effective_end = segment_length - offset_end
    
    if effective_start >= effective_end:
        return [], None
    
    effective_length = effective_end - effective_start
    positions = []
    direction = segment_vector.normalized()
    
    if distance is not None:
        if distance > effective_length:
            mid_point = p0_world + direction * (effective_start + effective_length / 2.0)
            positions = [mid_point]
        else:
            num_objects = max(1, int(effective_length / distance))
            
            if num_objects == 1:
                mid_point = p0_world + direction * (effective_start + effective_length / 2.0)
                positions = [mid_point]
            else:
                step = direction * distance
                remaining_space = effective_length - (distance * (num_objects - 1))
                start_offset = remaining_space / 2.0
                start_point = p0_world + direction * (effective_start + start_offset)
                positions = [start_point + step * i for i in range(num_objects)]
                
    elif count is not None:
        if count <= 0:
            return [], None
            
        if count == 1:
            mid_point = p0_world + direction * (effective_start + effective_length / 2.0)
            positions = [mid_point]
        else:
            step = effective_length / count
            start_point = p0_world + direction * effective_start
            positions = [start_point + direction * (step * (i + 0.5)) for i in range(count)]
    else:
        mid_point = p0_world + direction * (effective_start + effective_length / 2.0)
        positions = [mid_point]
    
    return positions, direction

# -----------------------------------------------------------------------------
class MainObjectProperties(bpy.types.PropertyGroup):
    curve: PointerProperty(
        name='Curve', 
        type=bpy.types.Curve, 
        update=update_curve,
        description="Select curve to use"
    )
    curve_original_name: bpy.props.StringProperty(
        default="",
        description="Original curve name for subdivision tracking"
    )
    objects_in_points: PointerProperty(
        name='Point Object', 
        type=bpy.types.Object, 
        update=update_objects_in_points,
        description="Object to place at curve points"
    )
    objects_in_edges: PointerProperty(
        name='Edge Object', 
        type=bpy.types.Object, 
        update=update_objects_in_edges,
        description="Object to place along curve edges"
    )

class CurveOptionsProperties(bpy.types.PropertyGroup):
    subdivide_curve_set: IntProperty(
        name="Subdivide", 
        default=0, 
        min=0, 
        soft_max=5,
        update=update_subdivide,
        description="Number of subdivision levels"
    )
    del_curve_points: BoolProperty(
        name="Hide Point Objects", 
        default=False, 
        update=update_del_curve_points,
        description="Hide objects placed at points"
    )
    del_curve_edges: BoolProperty(
        name="Hide Edge Objects", 
        default=False, 
        update=update_del_curve_edges,
        description="Hide objects placed along edges"
    )

class SegmentEndsProperties(bpy.types.PropertyGroup):
    equal_lengths: BoolProperty(
        name="Use Range", 
        default=False,
        update=update_equals_settings,
        description="Limit placement to specific range"
    )
    start_edge: FloatProperty(
        name="Start", 
        default=0.0, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR',
        update=update_equals_settings,
        description="Start of placement range"
    )
    end_edge: FloatProperty(
        name="End", 
        default=1.0, 
        min=0.0, 
        max=1.0, 
        subtype='FACTOR',
        update=update_equals_settings,
        description="End of placement range"
    )
    clip_on: BoolProperty(
        name="Enable Clip", 
        default=False,
        update=update_clip_settings,
        description="Enable distance-based clipping from ends"
    )
    clip_distance: FloatProperty(
        name="Distance", 
        default=0.0, 
        min=0.0, 
        soft_max=10.0,
        subtype='DISTANCE',
        update=update_clip_settings,
        description="Distance to clip from each end"
    )

class EdgeSpacingProperties(bpy.types.PropertyGroup):
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

class TransformOptionsBase(bpy.types.PropertyGroup):
    scale_object: FloatProperty(
        name="Uniform Scale", 
        default=1.0, 
        min=0.0,
        description="Uniform scale factor"
    )
    normalization_scale_object: BoolProperty(
        name="Use Custom Scale", 
        default=False,
        description="Enable non-uniform scale"
    )
    scale_normalization_object: FloatVectorProperty(
        name="Custom Scale", 
        size=3, 
        min=0.0, 
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
        description="X, Y, Z scale factors"
    )
    rand_scale_object: BoolProperty(
        name="Random Scale", 
        default=False,
        description="Add random scale variation"
    )
    rand_scale_object_slider: IntProperty(
        name="Seed", 
        default=0, 
        min=0,
        description="Random seed for scale variation"
    )
    rand_scale_lock_x: BoolProperty(
        name="X",
        default=False,
        description="Lock X axis scale randomization",
        update=create_update_handler()
    )
    rand_scale_lock_y: BoolProperty(
        name="Y",
        default=False,
        description="Lock Y axis scale randomization",
        update=create_update_handler()
    )
    rand_scale_lock_z: BoolProperty(
        name="Z",
        default=False,
        description="Lock Z axis scale randomization",
        update=create_update_handler()
    )
    
    normalization_rotate_object: FloatVectorProperty(
        name="Rotation", 
        subtype='EULER', 
        size=3,
        min=-2*pi, 
        max=2*pi, 
        default=(0.0, 0.0, 0.0),
        description="Base rotation in radians"
    )
    rand_rotate_object: BoolProperty(
        name="Random Rotation", 
        default=False,
        description="Add random rotation variation"
    )
    rand_rotate_object_slider: IntProperty(
        name="Seed", 
        default=0, 
        min=0,
        description="Random seed for rotation variation"
    )
    rand_rot_lock_x: BoolProperty(
        name="X",
        default=False,
        description="Lock X axis rotation randomization",
        update=create_update_handler()
    )
    rand_rot_lock_y: BoolProperty(
        name="Y",
        default=False,
        description="Lock Y axis rotation randomization",
        update=create_update_handler()
    )
    rand_rot_lock_z: BoolProperty(
        name="Z",
        default=False,
        description="Lock Z axis rotation randomization",
        update=create_update_handler()
    )

class PointTransformSettings(TransformOptionsBase):
    pass

class EdgeTransformSettings(TransformOptionsBase):
    pass

class TransformOptionsContainer(bpy.types.PropertyGroup):
    select_target: EnumProperty(
        name="Target",
        description="Select which object type to configure",
        items=[
            ("2", "Point Object", "Settings for objects placed at points"),
            ("3", "Edge Object", "Settings for objects placed along edges"),
        ],
        default="2"
    )
    point: PointerProperty(type=PointTransformSettings)
    edge: PointerProperty(type=EdgeTransformSettings)

# -----------------------------------------------------------------------------
class CURVE_OT_toggle_handle_type(bpy.types.Operator):
    bl_idname = "curve.toggle_handle_type"
    bl_label = "Toggle Handle Type"
    bl_description = "Toggle handle type between Automatic and Vector"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or obj.type != 'CURVE':
            self.report({'WARNING'}, "Active object is not a curve")
            return {'CANCELLED'}
        
        curve = obj.data
        if curve is None:
            self.report({'WARNING'}, "No curve data")
            return {'CANCELLED'}
        
        current_type = None
        for spline in curve.splines:
            if spline.type == 'BEZIER' and spline.bezier_points:
                current_type = spline.bezier_points[0].handle_left_type
                break
        
        new_type = 'VECTOR' if current_type == 'AUTO' else 'AUTO'
        
        for spline in curve.splines:
            if spline.type == 'BEZIER':
                for bezier_point in spline.bezier_points:
                    bezier_point.handle_left_type = new_type
                    bezier_point.handle_right_type = new_type
        
        self.report({'INFO'}, f"Handles set to {new_type}")
        return {'FINISHED'}

class OBJECT_OT_place_objects(bpy.types.Operator):
    bl_idname = "object.place_objects"
    bl_label = "Place Objects on Curve"
    bl_description = "Create instances of Point and Edge objects along the curve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'main_object'):
            self.report({'WARNING'}, "Active object must be a curve with main properties")
            return {'CANCELLED'}

        main_props = obj.main_object
        curve_opt = obj.curve_options
        curve_data = obj.data
        
        if not curve_data:
            self.report({'WARNING'}, "Curve has no data")
            return {'CANCELLED'}

        point_template = main_props.objects_in_points
        edge_template = main_props.objects_in_edges
        
        if point_template and point_template.name not in bpy.data.objects:
            point_template = None
        if edge_template and edge_template.name not in bpy.data.objects:
            edge_template = None
        
        point_settings = obj.transform_options_container.point
        edge_settings = obj.transform_options_container.edge
        seg_props = obj.segment_ends_properties
        edge_spacing = obj.edge_spacing_properties
        
        need_points = point_template and not curve_opt.del_curve_points
        need_edges = edge_template and not curve_opt.del_curve_edges
        
        if not (need_points or need_edges):
            self.report({'WARNING'}, "No objects to place. Select Point Object or Edge Object first.")
            return {'CANCELLED'}

        clear_instances(obj)
        
        matrix_world = obj.matrix_world
        coll = get_instance_collection(obj)
        
        start_f = seg_props.start_edge
        end_f = seg_props.end_edge
        if seg_props.equal_lengths and start_f > end_f:
            start_f, end_f = end_f, start_f
        
        clip_distance = seg_props.clip_distance if seg_props.clip_on else 0

        try:
            if need_points:
                self._place_point_objects(
                    curve_data, coll, point_template, point_settings, 
                    matrix_world, start_f, end_f, seg_props.equal_lengths, 
                    clip_distance
                )

            if need_edges:
                self._place_edge_objects(
                    curve_data, coll, edge_template, edge_settings, 
                    matrix_world, start_f, end_f, seg_props.equal_lengths, 
                    clip_distance, edge_spacing
                )
        except Exception as e:
            self.report({'ERROR'}, f"Error placing objects: {str(e)}")
            return {'CANCELLED'}

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        instance_count = len(coll.objects)
        coll_name = get_collection_name(obj)
        self.report({'INFO'}, f"Placed {instance_count} objects in collection '{coll_name}'")
        return {'FINISHED'}
    
    def _place_point_objects(self, curve_data, coll, point_template, point_settings, 
                            matrix_world, start_f, end_f, use_range, clip_distance):
        for spline in curve_data.splines:
            if spline.type not in ('BEZIER', 'POLY'):
                continue
            
            points = spline.bezier_points if spline.type == 'BEZIER' else spline.points
            if not points:
                continue
            
            spline_length = spline.calc_length()
            if spline_length == 0.0 or (clip_distance > 0 and spline_length <= 2 * clip_distance):
                continue
            
            num_points = len(points)
            
            for i, pt in enumerate(points):
                if spline.type == 'BEZIER':
                    coord_local = pt.co.copy()
                else:
                    coord_local = Vector(pt.co.xyz)
                
                rel = 0.5 if num_points == 1 else i / (num_points - 1)
                
                if clip_distance > 0:
                    edge_threshold = clip_distance / spline_length
                    if rel < edge_threshold or rel > (1 - edge_threshold):
                        continue
                
                if use_range and not (start_f <= rel <= end_f):
                    continue
                
                new_obj = point_template.copy()
                if point_template.data:
                    new_obj.data = point_template.data.copy()
                coll.objects.link(new_obj)
                
                new_obj.location = matrix_world @ coord_local
                new_obj.rotation_euler = point_template.rotation_euler.copy()
                new_obj.scale = point_template.scale.copy()
                
                apply_transforms(new_obj, point_settings)
                new_obj.parent = None
    
    def _place_edge_objects(self, curve_data, coll, edge_template, edge_settings, 
                           matrix_world, start_f, end_f, use_range, clip_distance, 
                           edge_spacing):
        for spline in curve_data.splines:
            if spline.type not in ('BEZIER', 'POLY'):
                continue
            
            pts = spline.bezier_points if spline.type == 'BEZIER' else spline.points
            if len(pts) < 2:
                continue
            
            spline_length = spline.calc_length()
            if spline_length == 0.0 or (clip_distance > 0 and spline_length <= 2 * clip_distance):
                continue
            
            num_segments = len(pts) - 1
            use_distance = edge_spacing.use_distance
            use_count = edge_spacing.use_count
            
            for i in range(num_segments):
                if spline.type == 'BEZIER':
                    p0_local = pts[i].co.copy()
                    p1_local = pts[i+1].co.copy()
                else:
                    p0_local = Vector(pts[i].co.xyz)
                    p1_local = Vector(pts[i+1].co.xyz)
                
                mid_rel = (i + 0.5) / num_segments if num_segments > 0 else 0.5
                
                if clip_distance > 0:
                    edge_threshold = clip_distance / spline_length
                    if mid_rel < edge_threshold or mid_rel > (1 - edge_threshold):
                        continue
                
                if use_range and not (start_f <= mid_rel <= end_f):
                    continue
                
                p0_world = matrix_world @ p0_local
                p1_world = matrix_world @ p1_local
                
                if use_distance:
                    positions, direction = get_segment_positions(
                        p0_world, p1_world, 
                        distance=edge_spacing.edge_distance,
                        offset_start=edge_spacing.offset_start,
                        offset_end=edge_spacing.offset_end
                    )
                elif use_count:
                    positions, direction = get_segment_positions(
                        p0_world, p1_world, 
                        count=edge_spacing.edge_count,
                        offset_start=edge_spacing.offset_start,
                        offset_end=edge_spacing.offset_end
                    )
                else:
                    positions, direction = get_segment_positions(
                        p0_world, p1_world,
                        offset_start=edge_spacing.offset_start,
                        offset_end=edge_spacing.offset_end
                    )
                
                if not positions or direction is None:
                    continue
                
                track_quat = direction.to_track_quat('Y', 'Z')
                
                for position in positions:
                    new_obj = edge_template.copy()
                    if edge_template.data:
                        new_obj.data = edge_template.data.copy()
                    coll.objects.link(new_obj)
                    
                    new_obj.location = position
                    new_obj.rotation_mode = 'QUATERNION'
                    new_obj.rotation_quaternion = track_quat
                    new_obj.scale = edge_template.scale.copy()
                    
                    apply_transforms(new_obj, edge_settings)
                    new_obj.parent = None

class OBJECT_OT_clear_instances(bpy.types.Operator):
    bl_idname = "object.clear_instances"
    bl_label = "Clear Instances"
    bl_description = "Remove all created instance objects for this curve"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'main_object'):
            self.report({'WARNING'}, "Select a curve object first")
            return {'CANCELLED'}
        
        coll_name = get_collection_name(obj)
        coll = bpy.data.collections.get(coll_name)
        count = len(coll.objects) if coll else 0
        
        if count > 0:
            clear_instances(obj)
            self.report({'INFO'}, f"Removed {count} instance objects from '{coll_name}'")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, f"No instances to remove in '{coll_name}'")
            return {'CANCELLED'}

class OBJECT_OT_clear_all_instances(bpy.types.Operator):
    bl_idname = "object.clear_all_instances"
    bl_label = "Clear All Instances"
    bl_description = "Remove ALL Starselor collections and objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        total_count = 0
        collections_count = 0
        
        for coll in bpy.data.collections:
            if coll.name.startswith(INSTANCE_COLLECTION_PREFIX):
                total_count += len(coll.objects)
                collections_count += 1
        
        if total_count > 0:
            clear_all_instances()
            self.report({'INFO'}, f"Removed {total_count} objects from {collections_count} collections")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No Starselor instances found")
            return {'CANCELLED'}

# -----------------------------------------------------------------------------
class STARSELOR_PT_main_panel(bpy.types.Panel):
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
        
        coll_name = get_collection_name(obj)
        coll = bpy.data.collections.get(coll_name)
        if coll:
            box = layout.box()
            box.label(text=f"Collection: {coll_name}", icon='COLLECTION_COLOR_01')
            box.label(text=f"Objects: {len(coll.objects)}")
        
        box = layout.box()
        box.label(text="Curve and Objects:", icon='CURVE_DATA')
        box.prop(props, "curve")
        
        col = box.column(align=True)
        col.prop(props, "objects_in_points")
        col.prop(props, "objects_in_edges")
        
        row = layout.row(align=True)
        row.operator("object.place_objects", text="Place Objects", icon='OBJECT_DATA')
        row.operator("object.clear_instances", text="Clear", icon='X')
        
        layout.separator()
        layout.operator("object.clear_all_instances", text="Clear All Starselor Collections", icon='TRASH')

class STARSELOR_PT_curve_options(bpy.types.Panel):
    bl_label = "Curve Options"
    bl_idname = "PT_PanelCurveOption"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'curve_options'):
            return
        
        props = obj.curve_options
        
        col = layout.column(align=True)
        col.operator("curve.toggle_handle_type", text="Toggle Handles", icon='MOD_CURVE')
        col.separator()
        col.prop(props, "subdivide_curve_set")

class STARSELOR_PT_visibility(bpy.types.Panel):
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
        if not obj or not hasattr(obj, 'curve_options'):
            return
        
        props = obj.curve_options
        
        box = layout.box()
        box.label(text="Hide Objects:", icon='HIDE_OFF')
        col = box.column(align=True)
        col.prop(props, "del_curve_points")
        col.prop(props, "del_curve_edges")

class STARSELOR_PT_placement_range(bpy.types.Panel):
    bl_label = "Placement Range"
    bl_idname = "PT_Equals"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'segment_ends_properties'):
            return
        
        props = obj.segment_ends_properties
        
        box = layout.box()
        box.prop(props, "equal_lengths")
        
        if props.equal_lengths:
            col = box.column(align=True)
            col.prop(props, "start_edge")
            col.prop(props, "end_edge")

class STARSELOR_PT_end_clipping(bpy.types.Panel):
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
        if not obj or not hasattr(obj, 'segment_ends_properties'):
            return
        
        props = obj.segment_ends_properties
        
        box = layout.box()
        box.prop(props, "clip_on")
        
        if props.clip_on:
            col = box.column()
            col.prop(props, "clip_distance")

class STARSELOR_PT_edge_spacing(bpy.types.Panel):
    bl_label = "Edge Spacing"
    bl_idname = "PT_EdgeSpacing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'edge_spacing_properties'):
            return
        
        props = obj.edge_spacing_properties
        
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

class STARSELOR_PT_transform_options(bpy.types.Panel):
    bl_label = "Transform Options"
    bl_idname = "PT_OptionObject"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if not obj or not hasattr(obj, 'transform_options_container'):
            return
        
        container = obj.transform_options_container
        
        row = layout.row()
        row.prop(container, "select_target", expand=True)

class STARSELOR_PT_scale(bpy.types.Panel):
    bl_label = "Scale Settings"
    bl_idname = "PT_ScalePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_OptionObject'
    bl_options = {'DEFAULT_CLOSED'}

    def get_active_settings(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'transform_options_container'):
            return None
        container = obj.transform_options_container
        if container.select_target == '2':
            return container.point
        return container.edge

    def draw(self, context):
        layout = self.layout
        settings = self.get_active_settings(context)
        if settings is None:
            return
        
        box = layout.box()
        box.prop(settings, "scale_object")
        box.prop(settings, "normalization_scale_object")
        
        if settings.normalization_scale_object:
            col = box.column(align=True)
            col.prop(settings, "scale_normalization_object")
        
        box.separator()
        box.prop(settings, "rand_scale_object")
        
        if settings.rand_scale_object:
            col = box.column()
            col.prop(settings, "rand_scale_object_slider")
            
            box.separator()
            box.label(text="Lock Random Scale Axes:", icon='LOCKED')
            row = box.row(align=True)
            row.prop(settings, "rand_scale_lock_x", toggle=True)
            row.prop(settings, "rand_scale_lock_y", toggle=True)
            row.prop(settings, "rand_scale_lock_z", toggle=True)

class STARSELOR_PT_rotation(bpy.types.Panel):
    bl_label = "Rotation Settings"
    bl_idname = "PT_RotatePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Starselor'
    bl_parent_id = 'PT_OptionObject'
    bl_options = {'DEFAULT_CLOSED'}

    def get_active_settings(self, context):
        obj = context.object
        if not obj or not hasattr(obj, 'transform_options_container'):
            return None
        container = obj.transform_options_container
        if container.select_target == '2':
            return container.point
        return container.edge

    def draw(self, context):
        layout = self.layout
        settings = self.get_active_settings(context)
        if settings is None:
            return
        
        box = layout.box()
        box.prop(settings, "normalization_rotate_object")
        box.separator()
        box.prop(settings, "rand_rotate_object")
        
        if settings.rand_rotate_object:
            col = box.column()
            col.prop(settings, "rand_rotate_object_slider")
            
            box.separator()
            box.label(text="Lock Random Rotation Axes:", icon='LOCKED')
            row = box.row(align=True)
            row.prop(settings, "rand_rot_lock_x", toggle=True)
            row.prop(settings, "rand_rot_lock_y", toggle=True)
            row.prop(settings, "rand_rot_lock_z", toggle=True)

# -----------------------------------------------------------------------------

classes = [
    MainObjectProperties,
    CurveOptionsProperties,
    SegmentEndsProperties,
    EdgeSpacingProperties,
    TransformOptionsBase,
    PointTransformSettings,
    EdgeTransformSettings,
    TransformOptionsContainer,
    CURVE_OT_toggle_handle_type,
    OBJECT_OT_place_objects,
    OBJECT_OT_clear_instances,
    OBJECT_OT_clear_all_instances,
    STARSELOR_PT_main_panel,
    STARSELOR_PT_curve_options,
    STARSELOR_PT_visibility,
    STARSELOR_PT_placement_range,
    STARSELOR_PT_end_clipping,
    STARSELOR_PT_edge_spacing,
    STARSELOR_PT_transform_options,
    STARSELOR_PT_scale,
    STARSELOR_PT_rotation,
]

def register():
    for cl in classes:
        register_class(cl)

    bpy.types.Scene.curve_container = PointerProperty(type=MainObjectProperties)
    bpy.types.Object.main_object = PointerProperty(type=MainObjectProperties)
    bpy.types.Object.curve_options = PointerProperty(type=CurveOptionsProperties)
    bpy.types.Object.segment_ends_properties = PointerProperty(type=SegmentEndsProperties)
    bpy.types.Object.transform_options_container = PointerProperty(type=TransformOptionsContainer)
    bpy.types.Object.edge_spacing_properties = PointerProperty(type=EdgeSpacingProperties)
    bpy.types.Object.starselor_collection_name = StringProperty(
        default="",
        description="Name of the Starselor collection for this object"
    )

def unregister():
    global _random_cache
    
    _random_cache.clear()
    
    for prop in ['curve_container', 'main_object', 'curve_options', 'segment_ends_properties', 
                 'transform_options_container', 'edge_spacing_properties', 'starselor_collection_name']:
        try:
            if prop in dir(bpy.types.Scene):
                delattr(bpy.types.Scene, prop)
        except:
            pass
        try:
            if prop in dir(bpy.types.Object):
                delattr(bpy.types.Object, prop)
        except:
            pass
    
    clear_all_instances()

    for cl in reversed(classes):
        try:
            unregister_class(cl)
        except:
            pass

if __name__ == "__main__":
    register()
