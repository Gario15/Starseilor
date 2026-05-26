bl_info = {
    "name": "Starselor",
    "author": "Glue",
    "version": (1, 5),
    "blender": (4, 0, 0),
    "location": "View3D > Toolbar > Starselor",
    "description": "Размещение объектов вдоль кривой с настройками (коллекции для каждой кривой)",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

from . import utils
from . import properties
from . import operators
from . import panels

def register():
    properties.register()
    operators.register()
    panels.register()

def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    utils.clear_all_instances()

if __name__ == "__main__":
    register()