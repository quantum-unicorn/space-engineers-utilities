import bpy
import os

from math   import pi

from .seut_collections              import get_collections
from .seut_errors                   import check_collection, seut_report

def linkSubpartScene(self, originScene, empty, targetCollection, collectionType = 'main'):
    """Link instances of subpart scene objects as children to empty"""

    context = bpy.context
    parentCollections = get_collections(originScene)

    currentScene = bpy.context.window.scene
    subpartScene = empty.seut.linkedScene

    subpartCollections = get_collections(subpartScene)
    # Checks whether collection exists, is excluded or is empty
    result = check_collection(self, context, subpartScene, subpartCollections[collectionType], False)
    if not result == {'CONTINUE'}:
        empty.seut.linkedScene = None
        empty['file'] = None
        return result
    
    # This prevents instancing loops.
    for o in subpartCollections[collectionType].objects:
        if o is not None and o.type == 'EMPTY' and o.seut.linkedScene == originScene:
            seut_report(self, context, 'ERROR', False, 'E005', subpartScene.name, currentScene.name)
            empty.seut.linkedScene = None
            empty['file'] = None
            return {'CANCEL'}
    
    # Switch to subpartScene to get collections
    context.window.scene = subpartScene
    current_area = prep_context(context)

    objectsToIterate = set(subpartCollections[collectionType].objects)

    for obj in objectsToIterate:

        # The following is done only on a first-level subpart as
        # further-nested subparts already have empties as parents.
        # Needs to account for empties being parents that aren't subpart empties.
        if obj is not None and (obj.parent is None or obj.parent.type != 'EMPTY' or not 'file' in obj.parent) and obj.name.find("(L)") == -1:

            obj.hide_viewport = False

            existingObjects = set(subpartCollections[collectionType].objects)
            
            # Create instance of object
            try:
                context.window.view_layer.objects.active.select_set(state=False, view_layer=context.window.view_layer)
            except AttributeError:
                pass
            context.window.view_layer.objects.active = obj
            obj.select_set(state=True, view_layer=context.window.view_layer)

            bpy.ops.object.duplicate(linked=True)
        
            newObjects = set(subpartCollections[collectionType].objects)
            createdObjects = newObjects.copy()
            deleteObjects = set()

            for obj1 in newObjects:
                for obj2 in existingObjects:
                    if obj1 == obj2:
                        createdObjects.remove(obj1)
                if obj1 in createdObjects and obj1.name.find("(L)") != -1:
                    createdObjects.remove(obj1)
                    deleteObjects.add(obj1)
            
            for delObj in deleteObjects:
                bpy.data.objects.remove(delObj, do_unlink=True)
            
            # Rename instance
            linkedObject = None
            for createdObj in createdObjects:
                createdObj.name = obj.name + " (L)"
                linkedObject = createdObj

            if linkedObject is not None:
                # Link instance to empty
                try:
                    if targetCollection is None:
                        parentCollections[collectionType].objects.link(linkedObject)
                    else:
                        targetCollection.objects.link(linkedObject)
                except RuntimeError:
                    pass
                subpartCollections[collectionType].objects.unlink(linkedObject)
                linkedObject.parent = empty

                if linkedObject.type == 'EMPTY' and linkedObject.seut.linkedScene is not None and linkedObject.seut.linkedScene.name in bpy.data.scenes and originScene.seut.linkSubpartInstances:
                    linkSubpartScene(self, originScene, linkedObject, targetCollection)
        
    # Switch back to previous scene
    context.area.type = current_area
    context.window.scene = currentScene
    
    return {'CONTINUE'}


def unlinkSubpartScene(empty):
    """Unlinks all subpart instances from an empty"""

    for obj in empty.children:
        unlinkObjectsInHierarchy(obj)

    return {'CONTINUE'}


def unlinkObjectsInHierarchy(obj):
    """Unlinks all objects in hierarchy of an object"""

    for child in obj.children:
        unlinkObjectsInHierarchy(child)

    bpy.data.objects.remove(obj, do_unlink=True)


def get_parent_collection(context, child):
    scene = context.scene

    collections = get_collections(scene)
    
    for key, value in collections.items():
        if value is not None:
            for obj in value.objects:
                if obj is not None and obj == child:
                    return value
    
    return None

def to_radians(number):
    """Converts degrees to radians"""

    return pi * number / 180


def get_preferences():
    """Returns the preferences of the addon"""

    if __package__.find(".") == -1:
        addon = __package__
    else:
        addon = __package__[:__package__.find(".")]

    return bpy.context.preferences.addons.get(addon).preferences


def prep_context(context):
    """Prep context for doing larger alterations"""

    try:
        current_area = context.area.type
        context.area.type = 'VIEW_3D'
    except AttributeError:
        context.area.type = 'VIEW_3D'
        current_area = context.area.type

    clear_selection(context)
    
    return current_area


def clear_selection(context):
    """Deselects object and sets active object to None."""

    if context.object is not None:
        context.object.select_set(False)
        context.view_layer.objects.active = None


def toggle_scene_modes(context, mirroring, mountpoints, icon_render):
    """Sets modes in all scenes."""

    original_scene = context.scene

    for scn in bpy.data.scenes:
        context.window.scene = scn

        if scn == original_scene:
            if scn.seut.mirroringToggle != mirroring:
                scn.seut.mirroringToggle = mirroring
            if scn.seut.mountpointToggle != mountpoints:
                scn.seut.mountpointToggle = mountpoints
            if scn.seut.renderToggle != icon_render:
                scn.seut.renderToggle = icon_render

        else:
            if scn.seut.mirroringToggle == 'on':
                scn.seut.mirroringToggle = 'off'
            if scn.seut.mountpointToggle == 'on':
                scn.seut.mountpointToggle = 'off'
            if scn.seut.renderToggle == 'on':
                scn.seut.renderToggle = 'off'

    context.window.scene = original_scene

def create_seut_collection(seut_collection, name: str):
    """Creates a new SEUT collection if it doesn't exist yet, else returns the existing one."""

    if not name in bpy.data.collections:
        collection = bpy.data.collections.new(name)
        seut_collection.children.link(collection)

    else:
        collection = bpy.data.collections[name]
        try:
            seut_collection.children.link(collection)
        except:
            pass
    
    return collection