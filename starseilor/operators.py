import bpy
from bpy.utils import register_class, unregister_class
from mathutils import Vector
from . import utils
from .properties import (
    MainObject, CurveOption, SegmentEnds, EdgeSpacingProps,
    PointOptionSettings, EdgeOptionSettings, OptionContainerGroup
)

class CURVE_OT_toggle_handle_type(bpy.types.Operator):
    bl_idname = "curve.toggle_handle_type"
    bl_label = "Toggle Handle Type"
    bl_description = "Переключить тип ручек между Automatic и Vector"
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
        curve_opt = obj.curve_operftion
        curve_data = obj.data
        if not curve_data:
            self.report({'WARNING'}, "Curve has no data")
            return {'CANCELLED'}
        point_template = main_props.ObjectsInPoints
        edge_template = main_props.ObjectsInEdges
        if point_template and point_template.name not in bpy.data.objects:
            point_template = None
        if edge_template and edge_template.name not in bpy.data.objects:
            edge_template = None
        point_settings = obj.curve_option_container.point
        edge_settings = obj.curve_option_container.edge
        seg_props = obj.curve_equals
        edge_spacing = obj.edge_spacing_props
        need_points = point_template and not curve_opt.DelCurvePoints
        need_edges = edge_template and not curve_opt.DelCurveEdges
        if not (need_points or need_edges):
            self.report({'WARNING'}, "No objects to place. Select Point Object or Edge Object first.")
            return {'CANCELLED'}
        utils.clear_instances(obj)
        matrix_world = obj.matrix_world
        coll = utils.get_instance_collection(obj)
        start_f = seg_props.StartEdge
        end_f = seg_props.EndEdge
        if seg_props.EqualLengths and start_f > end_f:
            start_f, end_f = end_f, start_f
        clip_distance = seg_props.ClipDistance if seg_props.ClipOn else 0
        try:
            if need_points:
                self._place_point_objects(
                    curve_data, coll, point_template, point_settings,
                    matrix_world, start_f, end_f, seg_props.EqualLengths,
                    clip_distance
                )
            if need_edges:
                self._place_edge_objects(
                    curve_data, coll, edge_template, edge_settings,
                    matrix_world, start_f, end_f, seg_props.EqualLengths,
                    clip_distance, edge_spacing
                )
        except Exception as e:
            self.report({'ERROR'}, f"Error placing objects: {str(e)}")
            return {'CANCELLED'}
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        instance_count = len(coll.objects)
        coll_name = utils.get_collection_name(obj)
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
                utils.apply_transforms(new_obj, point_settings)
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
                    positions, direction = utils.get_segment_positions(
                        p0_world, p1_world,
                        distance=edge_spacing.edge_distance,
                        offset_start=edge_spacing.offset_start,
                        offset_end=edge_spacing.offset_end
                    )
                elif use_count:
                    positions, direction = utils.get_segment_positions(
                        p0_world, p1_world,
                        count=edge_spacing.edge_count,
                        offset_start=edge_spacing.offset_start,
                        offset_end=edge_spacing.offset_end
                    )
                else:
                    positions, direction = utils.get_segment_positions(
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
                    utils.apply_transforms(new_obj, edge_settings)
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
        coll_name = utils.get_collection_name(obj)
        coll = bpy.data.collections.get(coll_name)
        count = len(coll.objects) if coll else 0
        if count > 0:
            utils.clear_instances(obj)
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
            if coll.name.startswith(utils.INSTANCE_COLLECTION_PREFIX):
                total_count += len(coll.objects)
                collections_count += 1
        if total_count > 0:
            utils.clear_all_instances()
            self.report({'INFO'}, f"Removed {total_count} objects from {collections_count} collections")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, "No Starselor instances found")
            return {'CANCELLED'}

classes = [
    CURVE_OT_toggle_handle_type,
    OBJECT_OT_place_objects,
    OBJECT_OT_clear_instances,
    OBJECT_OT_clear_all_instances,
]

def register():
    for cl in classes:
        register_class(cl)

def unregister():
    for cl in reversed(classes):
        unregister_class(cl)
