import bpy

from .seut_recreateCollections    import SEUT_OT_RecreateCollections
from .seut_export                 import SEUT_OT_Export

class SEUT_OT_ExportLOD(bpy.types.Operator):
    """Exports all LODs"""
    bl_idname = "object.export_lod"
    bl_label = "Export LODs"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the 'LOD' collections"""

        scene = context.scene

        collections = SEUT_OT_RecreateCollections.get_Collections()

        # If no SubtypeId is set, error out.
        if scene.prop_subtypeId == "":
            print("SEUT Error 004: No SubtypeId set.")
            return {'CANCELLED'}

        # If no collections are found, error out.
        if collections['lod1'] == None and collections['lod2'] == None and collections['lod3'] == None:
            print("SEUT Error 003: No 'LOD'-type collections found. Export not possible.")
            return {'CANCELLED'}

        # Export LOD1, if present.
        if collections['lod1'] == None:
            print("SEUT Error 002: Collection 'LOD1' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD1'.")
                SEUT_OT_Export.export_XML(context, collections['lod1'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD1'.")
                SEUT_OT_Export.export_FBX(context, collections['lod1'])
        
        # Export LOD2, if present.
        if collections['lod2'] == None:
            print("SEUT Error 002: Collection 'LOD2' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD2'.")
                SEUT_OT_Export.export_XML(context, collections['lod2'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD2'.")
                SEUT_OT_Export.export_FBX(context, collections['lod2'])

        # Export LOD3, if present.
        if collections['lod3'] == None:
            print("SEUT Error 002: Collection 'LOD3' not found. Export not possible.")
        else:
            if scene.prop_export_xml:
                print("SEUT Info: Exporting XML for 'LOD3'.")
                SEUT_OT_Export.export_XML(context, collections['lod3'])
            if scene.prop_export_fbx:
                print("SEUT Info: Exporting FBX for 'LOD3'.")
                SEUT_OT_Export.export_FBX(context, collections['lod3'])


        return {'FINISHED'}