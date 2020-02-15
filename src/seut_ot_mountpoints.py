import bpy

from math           import pi
from bpy.types      import Operator

from .seut_ot_recreateCollections   import SEUT_OT_RecreateCollections
from .seut_errors                   import errorCollection, isCollectionExcluded
from .seut_utils                    import getParentCollection

class SEUT_OT_Mountpoints(Operator):
    """Handles everything related to mountpoint functionality"""
    bl_idname = "scene.mountpoints"
    bl_label = "Mountpoints"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):

        scene = context.scene

        if scene.seut.mountpointToggle == 'on':
            if scene.seut.mirroringToggle == 'on':
                scene.seut.mirroringToggle = 'off'
            result = SEUT_OT_Mountpoints.mountpointSetup(self, context)

        elif scene.seut.mountpointToggle == 'off':
            result = SEUT_OT_Mountpoints.cleanMountpointSetup(self, context)

        return result
    

    def mountpointSetup(self, context):
        """Sets up mountpoint utilities"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.getCollections(scene)
        allCurrentViewLayerCollections = context.window.view_layer.layer_collection.children

        if collections['seut'] is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' not found. Action not possible. (002)")
            scene.seut.mountpointToggle = 'off'
            return {'CANCELLED'}

        isExcluded = isCollectionExcluded(collections['seut'].name, allCurrentViewLayerCollections)
        if isExcluded or isExcluded is None:
            print("SEUT Warning: Collection 'SEUT " + scene.name + "' excluded from view layer. Action not possible. (019)")
            scene.seut.mountpointToggle = 'off'
            return {'CANCELLED'}

        mpMat = None
        for mat in bpy.data.materials:
            if mat.name == 'SMAT_Mountpoint':
                mpMat = mat
        
        if mpMat is None:
            print("SEUT: Cannot find mountpoint material. Re-link 'MatLib_Presets.blend'! (027)")
            scene.seut.mountpointToggle = 'off'
            return {'CANCELLED'}
            
        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        # Create collection if it doesn't exist already
        if not 'Mountpoints' + tag in bpy.data.collections:
            collection = bpy.data.collections.new('Mountpoints' + tag)
            collections['seut'].children.link(collection)
        else:
            collection = bpy.data.collections['Mountpoints' + tag]
            try:
                collections['seut'].children.link(collection)
            except:
                pass

        # Create empty tree for sides
        if scene.seut.gridScale == 'small':
            scale = 0.5
        else:
            scale = 2.5

        bboxX = scene.seut.bBox_X * scale
        bboxY = scene.seut.bBox_Y * scale
        bboxZ = scene.seut.bBox_Z * scale

        # Create and position side empties
        emptyFront = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints front', collection, None)
        emptyFront.empty_display_type = 'SINGLE_ARROW'
        emptyFront.rotation_euler.x = pi * -90 / 180
        emptyFront.rotation_euler.z = pi * -180 / 180
        emptyFront.location.y = -(bboxY / 2 * 1.05)
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint front', scale, scene.seut.bBox_X, scene.seut.bBox_Z, collection, emptyFront)
        area.active_material = mpMat

        emptyBack = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints back', collection, None)
        emptyBack.empty_display_type = 'SINGLE_ARROW'
        emptyBack.rotation_euler.x = pi * -90 / 180
        emptyBack.location.y = bboxY / 2 * 1.05
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint back', scale, scene.seut.bBox_X, scene.seut.bBox_Z, collection, emptyBack)
        area.active_material = mpMat

        emptyLeft = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints left', collection, None)
        emptyLeft.empty_display_type = 'SINGLE_ARROW'
        emptyLeft.rotation_euler.x = pi * -90 / 180
        emptyLeft.rotation_euler.z = pi * -270 / 180
        emptyLeft.location.x = -(bboxX / 2 * 1.05)
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint left', scale, scene.seut.bBox_Y, scene.seut.bBox_Z, collection, emptyLeft)
        area.active_material = mpMat

        emptyRight = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints right', collection, None)
        emptyRight.empty_display_type = 'SINGLE_ARROW'
        emptyRight.rotation_euler.x = pi * -90 / 180
        emptyRight.rotation_euler.z = pi * 270 / 180
        emptyRight.location.x = bboxX / 2 * 1.05
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint right', scale, scene.seut.bBox_Y, scene.seut.bBox_Z, collection, emptyRight)
        area.active_material = mpMat

        emptyTop = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints top', collection, None)
        emptyTop.empty_display_type = 'SINGLE_ARROW'
        emptyTop.location.z = bboxZ / 2 * 1.05
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint top', scale, scene.seut.bBox_X, scene.seut.bBox_Y, collection, emptyTop)
        area.active_material = mpMat

        emptyBottom = SEUT_OT_Mountpoints.createEmpty(context, 'Mountpoints bottom', collection, None)
        emptyBottom.empty_display_type = 'SINGLE_ARROW'
        emptyBottom.rotation_euler.x = pi * 180 / 180
        emptyBottom.location.z = -(bboxZ / 2 * 1.05)
        area = SEUT_OT_Mountpoints.createArea(context, 'Mountpoint bottom', scale, scene.seut.bBox_X, scene.seut.bBox_Y, collection, emptyBottom)
        area.active_material = mpMat

        area.select_set(state=False, view_layer=context.window.view_layer)

        return {'FINISHED'}
    

    def createEmpty(context, name, collection, parent):
        """Creates empty with given name, links it to specified collection and assigns it to a parent, if available"""

        scene = context.scene

        bpy.ops.object.add(type='EMPTY')
        empty = bpy.context.view_layer.objects.active
        empty.name = name

        parentCollection = getParentCollection(context, empty)
        if parentCollection != collection:
            collection.objects.link(empty)

            if parentCollection is None:
                scene.collection.objects.unlink(empty)
            else:
                parentCollection.objects.unlink(empty)
        
        if parent is not None:
            empty.parent = parent

        return empty
    

    def createArea(context, name, size, x, y, collection, parent):

        scene = context.scene

        bpy.ops.mesh.primitive_plane_add(size=size, calc_uvs=True, enter_editmode=False, align='WORLD')
        area = bpy.context.view_layer.objects.active
        area.name = name

        area.scale.x = x
        area.scale.y = y

        parentCollection = getParentCollection(context, area)
        if parentCollection != collection:
            collection.objects.link(area)

            if parentCollection is None:
                scene.collection.objects.unlink(area)
            else:
                parentCollection.objects.unlink(area)
        
        if parent is not None:
            area.parent = parent

        return area
    

    def saveMountpointData(context, collection):

        scene = context.scene

        areas = scene.seut.mountpointAreas
        areas.clear()

        for empty in collection.objects:

            if empty is None:
                continue

            elif empty.type == 'EMPTY' and empty.name.find('Mountpoints ') != -1 and empty.children is not None:
                side = empty.name[12:]

                for child in empty.children:
                    context.window.view_layer.objects.active = child
                    bpy.ops.object.transform_apply(location=True, scale=True)
                    
                    item = areas.add()
                    item.side = side
                    item.x = child.location.x
                    item.y = child.location.y
                    item.xDim = child.dimensions.x
                    item.yDim = child.dimensions.y
        
        print("areas ------------------------------------")
        for area in areas:
            print(area.side + " x: " + str(area.x) + " y: " + str(area.y) + " xDim: " + str(area.xDim) + " yDim: " + str(area.yDim))

        return

    def cleanMountpointSetup(self, context):
        """Cleans up mountpoint utilities"""

        scene = context.scene

        if scene.seut.subtypeId == "":
            scene.seut.subtypeId = scene.name
        tag = ' (' + scene.seut.subtypeId + ')'

        SEUT_OT_Mountpoints.saveMountpointData(context, bpy.data.collections['Mountpoints' + tag])

        # Save empty rotation values to properties, delete children instances, remove empty
        for obj in scene.objects:
            if obj is not None and obj.type == 'EMPTY':
                if obj.name == 'Mountpoints front' or obj.name == 'Mountpoints back' or obj.name == 'Mountpoints left' or obj.name == 'Mountpoints right' or obj.name == 'Mountpoints top' or obj.name == 'Mountpoints bottom':
                    for child in obj.children:
                        bpy.data.objects.remove(child)
                    obj.select_set(state=False, view_layer=context.window.view_layer)
                    bpy.data.objects.remove(obj)
    
        # Delete collection
        if 'Mountpoints' + tag in bpy.data.collections:
            bpy.data.collections.remove(bpy.data.collections['Mountpoints' + tag])

        return {'FINISHED'}
    