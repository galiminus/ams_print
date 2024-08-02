from xml.dom.minidom import getDOMImplementation
from zipfile import ZipFile
import random

COLOR_CODES =  ['4', '8', '0C', '1C', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'AC', 'BC', 'CC', 'DC']

class ThreeMF:
    def __init__(self):
        self.model_document = self._create_model_document()
        self.settings_document = self._create_model_settings_document()

        self.object_id = 1

    def _create_model_document(self):
        document = getDOMImplementation().createDocument(None, "model", None)

        document.documentElement.setAttribute("unit", "millimeter")
        document.documentElement.setAttribute("xml:lang", "en-US")
        document.documentElement.setAttribute("xmlns", "http://schemas.microsoft.com/3dmanufacturing/core/2015/02")

        return document
    
    def _create_model_settings_document(self):
        document = getDOMImplementation().createDocument(None, "config", None)

        return document

    def add_object(self, object, name):
        object.build_geometry()

        self.add_object_to_model_document(object)
        self.add_object_to_model_settings_document(name)

        self.object_id += 1

    def add_object_to_model_settings_document(self, name):
        document = self.settings_document

        metadata_element = document.createElement("metadata")
        metadata_element.setAttribute("key", "name")
        metadata_element.setAttribute("value", name)

        item_element = document.createElement("object")
        item_element.setAttribute("id", str(self.object_id))
        item_element.appendChild(metadata_element)

        document.documentElement.appendChild(item_element)

    def add_object_to_model_document(self, object):
        document = self.model_document

        # Make sure the required nodes are present
        try:
            resources_element = document.getElementsByTagName("resources")[0]
        except IndexError:
            resources_element = document.createElement("resources")
            document.documentElement.appendChild(resources_element)

        try:
            build_element = document.getElementsByTagName("build")[0]
        except IndexError:
            build_element = document.createElement("build")
            document.documentElement.appendChild(build_element)

        object_element = document.createElement("object")
        object_element.setAttribute("id", str(self.object_id))
        object_element.setAttribute("type", "model")
        resources_element.appendChild(object_element)

        mesh_element = document.createElement("mesh")
        object_element.appendChild(mesh_element)

        vertices_element = document.createElement("vertices")
        mesh_element.appendChild(vertices_element)

        triangles_element = document.createElement("triangles")
        mesh_element.appendChild(triangles_element)

        item_element = document.createElement("item")
        item_element.setAttribute("objectid", str(self.object_id))
        item_element.setAttribute("transform", "1 0 0 0 1 0 0 0 1 90 90 0")
        item_element.setAttribute("printable", "1")
        build_element.appendChild(item_element)

        for vertex in object.vertices.keys():
            x, y, z = vertex.split('x')

            vertice = document.createElement("vertex")
            vertice.setAttribute("x", x)
            vertice.setAttribute("y", y)
            vertice.setAttribute("z", z)
            vertices_element.appendChild(vertice)

        for face in object.triangles:
            v1_index, v2_index, v3_index = face

            triangle_element = document.createElement("triangle")
            triangle_element.setAttribute("v1", str(v1_index))
            triangle_element.setAttribute("v2", str(v2_index))
            triangle_element.setAttribute("v3", str(v3_index))
            # triangle_element.setAttribute("paint_color", COLOR_CODES[self.object_id - 1])
            triangles_element.appendChild(triangle_element)
        
    def save(self, path):
        # Remove file if it already exists
        with ZipFile(path, 'w') as output_zip:
            output_zip.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>''')

            output_zip.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>''')

            output_zip.writestr('3D/3dmodel.model', self.model_document.toprettyxml(encoding="utf-8"))
            output_zip.writestr('Metadata/model_settings.config', self.settings_document.toprettyxml(encoding="utf-8"))
