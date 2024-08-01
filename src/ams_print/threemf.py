from xml.dom.minidom import getDOMImplementation
from zipfile import ZipFile

class ThreeMF:
    def __init__(self):
        self.model_document = self._create_model_document()

    def _create_model_document(self):
        document = getDOMImplementation().createDocument(None, "model", None)

        document.documentElement.setAttribute("unit", "millimeter")
        document.documentElement.setAttribute("xml:lang", "en-US")
        document.documentElement.setAttribute("xmlns", "http://schemas.microsoft.com/3dmanufacturing/core/2015/02")

        return document

    def add_object(self, object, id, paint_color):
        document = self.model_document

        object.build_geometry()

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
        object_element.setAttribute("id", id)
        object_element.setAttribute("type", "model")
        resources_element.appendChild(object_element)

        mesh_element = document.createElement("mesh")
        object_element.appendChild(mesh_element)

        vertices_element = document.createElement("vertices")
        mesh_element.appendChild(vertices_element)

        triangles_element = document.createElement("triangles")
        mesh_element.appendChild(triangles_element)

        item_element = document.createElement("item")
        item_element.setAttribute("objectid", id)
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
            # triangle_element.setAttribute("paint_color", paint_color)
            triangles_element.appendChild(triangle_element)
    
    def save(self, path):
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
