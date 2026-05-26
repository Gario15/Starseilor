import bpy
import random
from math import pi
from mathutils import Vector, Euler, Quaternion, Matrix

INSTANCE_COLLECTION_PREFIX = "Starselor_"
RANDOM_SCALE_RANGE = (0.5, 1.5)
RANDOM_ROTATION_RANGE = (-pi/2, pi/2)

_random_cache = {}

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

def _is_valid_context(context):
    try:
        return (context.object and 
                context.object.type == 'CURVE' and 
                hasattr(context.object, 'main_object') and
                context.object.name in bpy.data.objects)
    except ReferenceError:
        return False

def _safe_place_objects(context):
    if _is_valid_context(context):
        try:
            if not getattr(bpy.app, 'is_undoing', False) and not getattr(bpy.app, 'is_redoing', False):
                bpy.ops.object.place_objects()
        except:
            pass

def _get_random_scale_factors(seed, lock_x=False, lock_y=False, lock_z=False):
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

def _get_random_rotation_factors(seed, lock_x=False, lock_y=False, lock_z=False):
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

def apply_transforms(obj, settings, obj_hash=None):
    if obj_hash is None:
        obj_hash = hash(obj.name) % 10000
    if settings.NormalizationScaleObject:
        base_scale = Vector(settings.ScaleNormalizationObject)
    else:
        base_scale = Vector((settings.ScaleObject,) * 3)
    if settings.RandScaleObject:
        seed = settings.RandScaleObjectSlider + obj_hash
        rand_factors = Vector(_get_random_scale_factors(
            seed,
            lock_x=settings.RandScaleLockX,
            lock_y=settings.RandScaleLockY,
            lock_z=settings.RandScaleLockZ
        ))
        obj.scale = Vector(b * r for b, r in zip(base_scale, rand_factors))
    else:
        obj.scale = base_scale
    user_euler = Euler(settings.NormalizationRotateObject)
    if settings.RandRotateObject:
        seed = settings.RandRoutateObjectSlider + obj_hash
        rand_rot = _get_random_rotation_factors(
            seed,
            lock_x=settings.RandRotLockX,
            lock_y=settings.RandRotLockY,
            lock_z=settings.RandRotLockZ
        )
        user_euler = Euler(b + r for b, r in zip(user_euler, rand_rot))
    user_quat = user_euler.to_quaternion()
    obj.rotation_mode = 'QUATERNION'
    if 'edge' in settings.__class__.__name__.lower():
        obj.rotation_quaternion = obj.rotation_quaternion @ user_quat
    else:
        obj.rotation_quaternion = user_quat

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
