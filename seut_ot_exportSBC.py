import bpy
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

from .seut_ot_recreateCollections    import SEUT_OT_RecreateCollections

class SEUT_OT_ExportSBC(bpy.types.Operator):
    """Exports to SBC"""
    bl_idname = "object.export_sbc"
    bl_label = "Export SBC"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        """Exports the SBC file for a defined collection"""

        scene = context.scene
        collections = SEUT_OT_RecreateCollections.get_Collections()
        preferences = bpy.context.preferences.addons.get(__package__).preferences

        if preferences.pref_looseFilesExportFolder == '1' and scene.prop_export_exportPath == "":
            self.report({'ERROR'}, "SEUT: No export folder defined. (003)")
            return {'CANCELLED'}

        if scene.prop_subtypeId == "":
            self.report({'ERROR'}, "SEUT: No SubtypeId set. (004)")
            return {'CANCELLED'}

        if not scene.prop_export_sbc:
            self.report({'WARNING'}, "SEUT: 'SBC' is toggled off. SBC export skipped.")
            return {'CANCELLED'}

        # Create XML tree and add initial parameters.
        definitions = ET.Element('Definitions')
        definitions.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        definitions.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')

        cubeBlocks = ET.SubElement(definitions, 'CubeBlocks')
        def_definition = ET.SubElement(cubeBlocks, 'Definition')
        
        def_Id = ET.SubElement(def_definition, 'Id')
        def_TypeId = ET.SubElement(def_Id, 'TypeId')
        def_TypeId.text = 'PLACEHOLDER'
        def_SubtypeId = ET.SubElement(def_Id, 'SubtypeId')
        def_SubtypeId.text = scene.prop_subtypeId

        def_DisplayName = ET.SubElement(def_definition, 'DisplayName')
        def_DisplayName.text = 'DisplayName_' + scene.prop_subtypeId
        def_Description = ET.SubElement(def_definition, 'Description')
        def_Description.text = 'Description_' + scene.prop_subtypeId
        
        def_Icon = ET.SubElement(def_definition, 'Icon')
        def_Icon.text = 'PLACEHOLDER'
        
        def_CubeSize = ET.SubElement(def_definition, 'CubeSize')
        if scene.prop_gridScale == '0': 
            def_CubeSize.text = 'Large'
        else:
            def_CubeSize.text = 'Small'
        
        def_BlockTopology = ET.SubElement(def_definition, 'BlockTopology')
        def_BlockTopology.text = 'TriangleMesh'

        def_Size = ET.SubElement(def_definition, 'Size')
        def_Size.set('x', str(scene.prop_bBox_X))
        def_Size.set('y', str(scene.prop_bBox_Y))
        def_Size.set('z', str(scene.prop_bBox_Z))

        def_ModelOffset = ET.SubElement(def_definition, 'ModelOffset')
        def_ModelOffset.set('x', '0')
        def_ModelOffset.set('y', '0')
        def_ModelOffset.set('z', '0')

        # Dependant on main collection existing
        def_Model = ET.SubElement(def_definition, 'Model')
        def_Model.text = scene.prop_subtypeId + '.mwm'
        
        """
        def_Mountpoints = ET.SubElement(def_definition, 'Mountpoints')
        def_Mountpoint = ET.SubElement(def_Mountpoints, 'Mountpoint')
        def_Mountpoint.set('Side', 'PLACEHOLDER')
        def_Mountpoint.set('StartX', 'PLACEHOLDER')
        def_Mountpoint.set('StartY', 'PLACEHOLDER')
        def_Mountpoint.set('EndX', 'PLACEHOLDER')
        def_Mountpoint.set('EndY', 'PLACEHOLDER')
        def_Mountpoint.set('Default', 'PLACEHOLDER')
        """
        
        # Dependant on bs collections existing
        def_BuildProgressModels = ET.SubElement(def_definition, 'BuildProgressModels')
        def_BS_Model = ET.SubElement(def_BuildProgressModels, 'Model')
        def_BS_Model.set('BuildPercentUpperBound', 'PLACEHOLDER')
        def_BS_Model.set('File', scene.prop_subtypeId + '_BS1.mwm')

        # Write to file, place in export folder
        xmlString = xml.dom.minidom.parseString(ET.tostring(definitions))
        xmlFormatted = xmlString.toprettyxml()

        filename = scene.prop_subtypeId

        path = ""

        # If file is still startup file (hasn't been saved yet), it's not possible to derive a path from it.
        if not bpy.data.is_saved and preferences.pref_looseFilesExportFolder == '0':
            self.report({'ERROR'}, "SEUT: BLEND file must be saved before SBC can be exported to its directory. (008)")
            return
        else:
            if preferences.pref_looseFilesExportFolder == '0':
                path = os.path.dirname(bpy.data.filepath) + "\\"

            elif preferences.pref_looseFilesExportFolder == '1':
                path = bpy.path.abspath(scene.prop_export_exportPath)

        exportedXML = open(path + filename + ".sbc", "w")
        exportedXML.write(xmlFormatted)
        self.report({'INFO'}, "SEUT: '%s.sbc' has been created." % (path + filename))

        return {'FINISHED'}