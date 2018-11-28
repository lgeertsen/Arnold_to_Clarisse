import ix

import os
import json
import ntpath

path="project://scene"

nodeTrees = []



class NodeTree(object):
    def __init__(self, name, nodes, connections, objects, object):
        self.name = name
        self.jsonNodes = nodes
        self.jsonConnections = connections
        self.jsonObjects = objects
        self.object = object
        self.material = None
        self.nodes = {}

    def createNodes(self):
        for node, value in self.jsonNodes.items():
            type = nodeLibrary.get(value["type"])
            #texture = None
            if type:
                if type[0] == "Material":
                    #texture = createMaterial(node, type, default_path, material)
                    mat = Material(self.name, value["type"], type[1], value["data"])
                    self.material = mat
                    self.nodes[node] = mat
                    #mat = texture
                    #node = material
                    #print(texture.name)
                    #texture = "project://scene/" + str(material)
                elif type:
                    #texture = createNode(node, type, default_path)
                    if(isinstance(type[1], dict)):
                        if(type[1]["key"] in value["data"]):
                            n = Node(node, value["type"], type[1][str(value["data"][type[1]["key"]])], value["data"])
                            self.nodes[n.name] = n
                        else:
                            n = Node(node, value["type"], type[1]["default"], value["data"])
                            self.nodes[n.name] = n
                    else:
                        n = Node(node, value["type"], type[1], value["data"])
                        self.nodes[n.name] = n

                    #print(texture.name)

#                if texture:
#                    materialNodes[node] = texture
#                    parameterNodes[node] = {}
#                    parameterNodes[node]["type"] = texture
#                    parameterNodes[node]["data"] = value["data"]
#                else:
#                    toProcess[node] = value
        #print(self.material)
        #print(self.nodes)
        self.linkNodes()

    def linkNodes(self):
        for connection in self.jsonConnections:
            #print(connection)
            child = self.nodes.get(connection["from"])
            if not child:
                continue

            parent = self.nodes.get(connection["to"])
            if not parent:
                continue

            connector = connectionLibrary.get(connection["toAttribute"])
            if not connector:
                continue

            parent.input.append(child)
            child.output.append({"to": parent, "connection": connector})

            #if(isinstance(connector, list)):
            for c in connector:
                ix.cmds.SetTexture([str(parent.path) + "." + str(c)], str(child.path))
            #else:
                #ix.cmds.SetTexture([str(parent) + "." + str(connector)], str(child))
        self.replaceTriplanars()


    def replaceTriplanars(self):
        for name, node in self.nodes.items():
            if(node.typeM == "aiTriplanar"):
                #print("Triplanar")
                #print(node.name)
                files = []
                for input in node.input:
                    for output in node.output:
                        for c in output["connection"]:
                            ix.cmds.SetTexture([str(output["to"].path) + "." + str(c)], str(input.path))

                node.output = []
                files = self.getLinkedFiles(node.input)

                index = 1

                for file in files:
                    #print(file.output)
                    doDuplicate = True

                    for output in file.output:
                        if output["to"].typeM == "aiTriplanar":
                            #print(output["to"].typeM)
                            doDuplicate = False

                    if not doDuplicate:
                        continue

                    duplicate = self.duplicateTriplanar(node)
                    duplicate.name = duplicate.name + str(index)
                    index += 1
                    duplicate.output = file.output
                    duplicate.input.append(file)
                    connection = ["right", "left", "top", "bottom", "front", "back"]
                    file.output = [{"to": duplicate, "connection": connection}]
                    self.nodes[duplicate.name] = duplicate
                    for c in connection:
                        ix.cmds.SetTexture([str(duplicate.path) + "." + str(c)], str(file.path))
                    for output in duplicate.output:
                        for c in output["connection"]:
                            ix.cmds.SetTexture([str(output["to"].path) + "." + str(c)], str(duplicate.path))

        self.addNodeValues()


    def getLinkedFiles(self, n):
        if not n:
            return []

        nodes = n
        files = []
        while nodes:
            node = nodes.pop(0)
            if(node.typeM == "file" or node.typeM == "aiNoise" or node.typeM == "noise"):
                files.append(node)
            if node.input:
                nodes.extend(node.input)
        return files

    def duplicateTriplanar(self, node):
        duplicate = Node(node.name, node.typeM, node.typeC, node.data)
        return duplicate

    def addNodeValues(self):
        for name, node in self.nodes.items():
            if(node.typeM == "remapHsv"):
                ix.cmds.SetValues([str(node.path) + ".output_color_model"], ["1"])
                continue
            elif(node.typeM == "aiNoise"):
                ix.cmds.SetValues([str(node.path) + ".color1"], ["0.0", "0.0", "0.0"])
                ix.cmds.SetValues([str(node.path) + ".color2"], ["1", "1", "1"])

            for parameter, value in node.data.items():
    #    print("----------------" + node + "ADD NODE VALUES----------------")
        #print(str(data["type"]) + ": " + str(data["data"]))
        #for parameter, value in data["data"].items():
    #        print(str(parameter) + ": " + str(value))
                type = parameterLibrary.get(parameter)

                if not type:
                    continue

        #        if(isinstance(type, list) and isinstance(type[0], str)):
        #            type[1](data, value, type[2])
        #            continue
                if(isinstance(type, dict)):
                    if(node.typeM == "aiTriplanar" and value["type"] == "float3"):
                        type["aiTriplanar"](node, value["value"])
                        continue
                    if(node.typeM == "aiNoise"):
                        type["aiNoise"][0]([str(node.path) + "." + str(type["aiNoise"][1])], [str(value["value"][0][0]), str(value["value"][0][1]), str(value["value"][0][2])])
                        continue
                elif(isinstance(type, list)):
                    if(value["type"] == "string"):
                        type[0]([str(node.path) + "." + str(type[1])], [str(value["value"])])
                        #ix.cmds.SetValues([str(data["type"]) + "." + str(type)], [str(value["value"])])
                        continue
                    elif(value["type"] == "float" or value["type"] == "long"):
                        type[0]([str(node.path) + "." + str(type[1])], [str(value["value"])])
                        continue
                    elif(value["type"] == "float3" and parameter != "scale"):
                        type[0]([str(node.path) + "." + str(type[1])], [str(value["value"][0][0]), str(value["value"][0][1]), str(value["value"][0][2])])
                        continue
                    elif(value["type"] == "bool"):
                        if(value["value"]):
                            type[0]([str(node.path) + "." + str(type[1])], ["1"])
                        continue
                elif(value["type"] == "TdataCompound" and node.typeC == "TextureRemap"):
                    type(node.path, value["value"])
                    continue
                elif(value["type"] == "string" or value["type"] == "float"):
                    type(node, value["value"])


        self.attributeMaterials()

    def attributeMaterials(self):
        if not self.material:
            return
        #print(mat)
        for object in self.jsonObjects:
            #print self.material
            ix.cmds.SetValues([str(self.object) + "/" + str(object) + ".materials[0]"], [str(self.material.path)])






class MaterialNode(object):
    def __init__(self, name, typeM, typeC, data):
        self.name = name
        self.typeM = typeM
        self.typeC = typeC
        self.data = data
        self.input = []




class Material(MaterialNode):
    def __init__(self, name, typeM, typeC, data):
        super(Material, self).__init__(name, typeM, typeC, data)
        self.path = self.createMaterial()

    def createMaterial(self):
        material = ix.cmds.CreateObject(str(self.name), str(self.typeC), "Global", path)
        return material




class Node(MaterialNode):
    def __init__(self, name, typeM, typeC, data):
        super(Node, self).__init__(name, typeM, typeC, data)
        self.path = self.createNode()
        self.output = []


    def createNode(self):
        node = ix.cmds.CreateObject(str(self.name), str(self.typeC), "Global", path)
        return node




materials = {}

def createStandardSurface(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + '_mat', "MaterialPhysicalStandard", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createRemap(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureRemap", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createFile(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureMapFile", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createBump2d(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureNormalMap", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createReverse(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureInvert", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node



def addCurveRed(node, data):
#    print("############# Add Curve Red #############")
#    print(node)
#    print(data)
#    print(str(node) + ".output")
    ix.cmds.RemoveCurveValue([str(node) + ".output"], [2, 1, 2, 0, 0, 0])
    for point in data:
#        print(point)
        ix.cmds.AddCurveValue([str(node) + ".output"], [
                1.0,
                0.0, point[0], point[1],
                0.0,
                0.0,
                0.0
            ])
    #ix.cmds.RemoveCurveValue(["project://scene/remapColor1_tx.output"], [2, 1, 2, 0, 0, 0])

def addCurveGreen(node, data):
#    print("############# Add Curve Green #############")
#    print(node)
#    print(data)
#    print(str(node) + ".output")
    ix.cmds.RemoveCurveValue([str(node) + ".output"], [0, 2, 1, 2, 0, 0])
    for point in data:
#        print(point)
        ix.cmds.AddCurveValue([str(node) + ".output"], [
                0.0,
                1.0,
                0.0, point[0], point[1],
                0.0,
                0.0
            ])

def addCurveBlue(node, data):
#    print("############# Add Curve Blue #############")
#    print(node)
#    print(data)
#    print(str(node) + ".output")
    ix.cmds.RemoveCurveValue([str(node) + ".output"], [0, 0, 2, 1, 2, 0])
    for point in data:
#        print(point)
        ix.cmds.AddCurveValue([str(node) + ".output"], [
                0.0,
                0.0,
                1.0,
                0.0, point[0], point[1],
                0.0
            ])

def addAllCurves(node, data):
#    print("############# Add All Curves #############")
#    print(node)
#    print(data)
#    print(str(node) + ".output")
    try:
        ix.cmds.RemoveCurveValue([str(node) + ".output"], [2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2])
        for point in data:
    #        print(point)
            ix.cmds.AddCurveValue([str(node) + ".output"], [
                    1.0,
                    0.0, point[0], point[1],
                    1.0,
                    0.0, point[0], point[1],
                    1.0,
                    0.0, point[0], point[1],
                    1.0,
                    0.0, point[0], point[1],
                ])
    except:
        pass

def triplanarScaleToFile(node, data):
    #print("triplanarScaleToFile")
    #print(node.path)
    if node.input:

        #print(node.input[0].path)
        #print(data)
        ix.cmds.SetValues([str(node.input[0].path) + ".uv_scale"], [str(data[0][0]), str(data[0][1]), str(data[0][2])])

def setFileColorSpace(node, data):
    if(data == "Raw"):
        ix.cmds.SetValues([str(node.path) + ".use_raw_data"], ["1"])

def setFrequency(node, data):
    ix.cmds.SetValues([str(node.path) + ".frequency"], [str(data / 100)])



nodeLibrary = {
    "aiStandardSurface"     : ["Material", "MaterialPhysicalStandard"],
    "remapColor"            : ["Node", "TextureRemap"],
    "file"                  : ["Node", "TextureMapFile"],
    "bump2d"                : ["Node", {"key": "bumpInterp", "1": "TextureNormalMap", "default": "TextureBumpMap"}],
    "reverse"               : ["Node", "TextureInvert"],
    "remapValue"            : ["Node", "TextureRemap"],
    "aiTriplanar"           : ["Node", "TextureTriplanar"],
    "blendColors"           : ["Node", "TextureBlend"],
    "remapHsv"              : ["Node", "TextureColorModel"],
    "aiNoise"               : ["Node", "TextureFractalNoise"],
    "noise"                 : ["Node", "TexturePerlinNoise"]
}

connectionLibrary = {
    "normalCamera"          : ["normal_input"],
    "baseColor"             : ["diffuse_front_color"],
    "specularRoughness"     : ["specular_1_roughness"],
    "color"                 : ["input"],
    "inputX"                : ["input"],
    "bumpValue"             : ["input"],
    "inputValue"            : ["input"],
    "inputR"                : ["right", "left", "top", "bottom", "front", "back"],
    "color1"                : ["input1"],
    "color2"                : ["input2"],
    "blender"               : ["mix"]
}

parameterLibrary = {
    "fileTextureName": [ix.cmds.SetValues, "filename[0]"],
    "red": addCurveRed,
    "green": addCurveGreen,
    "blue": addCurveBlue,
    "value": addAllCurves,
    "specularColor": [ix.cmds.SetValues, "specular_1_color"],
    "specularRoughness": [ix.cmds.SetValues, "specular_1_roughness"],
    "specularIOR": [ix.cmds.SetValues, "specular_1_index_of_refraction"],
    "baseColor": [ix.cmds.SetValues, "diffuse_front_color"],
    "base": [ix.cmds.SetValues, "diffuse_front_strength"],
    "alphaIsLuminance": [ix.cmds.SetValues, "single_channel_file_behavior"],
    "scale": {"aiTriplanar": triplanarScaleToFile, "aiNoise": [ix.cmds.SetValues, "uv_scale"]},
    "octaves": [ix.cmds.SetValues, "octaves"],
    "lacunarity": [ix.cmds.SetValues, "lacunarity"],
    "colorSpace": setFileColorSpace,
    "frequency": setFrequency
}








def createMaterial(node, type, path, material):
#    try:
#        ix.cmds.DeleteItem("project://scene/" + str(material))
#    except:
#        pass
    texture_node = ix.cmds.CreateObject(str(material), str(type), "Global", path)
#    index = None
#    for i in range(len(shading_groups)):
#        print(shading_groups[i] + " " + material)
#        if(shading_groups[i] == material):
#            index = i
#    print(str(shading_groups[index]))
#    print(str(selected))
#    ix.cmds.SetValues([str(selected) + ".materials[" + str(index) + "]"], [texture_node])
    #print(texture_node.attrs)
    return texture_node

def createNode(node, type, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", str(type), "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def setSpecular(data, value, type):
    print("#################################################################################")
    print(type)
    print("#################################################################################")
    #ix.cmds.SetValues([str(data["type"]) + ".specular_1_strength"], ["1"])
    #ix.cmds.SetValues([str(data["type"]) + "." + str(type)], [str(value["value"])])
    pass




def createNodes(nodes, default_path, material):
    print(material)
    print(nodes)
    materialNodes = {}
    toProcess = {}

    parameterNodes = {}

    mat = None

    for node, value in nodes.items():
        #print(node)
        #print(value["type"])
        #print(value["data"])
#        func = nodeSwitch.get(value["type"])
#        texture = None
#        if not func:
#            continue

#        texture = func(node, default_path)

        type = nodeSwitch.get(value["type"])
        texture = None
        if type == "MaterialPhysicalStandard":
            #texture = createMaterial(node, type, default_path, material)
            texture = Material(material, value["type"], type)
            mat = texture
            #node = material
            #print(texture.name)
            #texture = "project://scene/" + str(material)
        elif type:
            #texture = createNode(node, type, default_path)
            texture = Node(node, value["type"], type)
            #print(texture.name)

        if texture:
            materialNodes[node] = texture
            parameterNodes[node] = {}
            parameterNodes[node]["type"] = texture
            parameterNodes[node]["data"] = value["data"]
        else:
            toProcess[node] = value

#    print("----------------MATERIAL NODES----------------")
#    for node, values in materialNodes.items():
#        print(str(node) + ": " + str(values))

#    print("----------------PARAMETER NODES----------------")
    #for node, values in parameterNodes.items():
#        #print(str(node) + ": " + str(values))
        #addNodeValues(node, values)

    #print("----------------TO PROCESS----------------")
    #for node, value in toProcess.items():
        #print(str(node) + ": " + str(value))

    return [materialNodes, toProcess, mat]

def addNodeValues(node, data):
#    print("----------------" + node + "ADD NODE VALUES----------------")
    #print(str(data["type"]) + ": " + str(data["data"]))
    for parameter, value in data["data"].items():
#        print(str(parameter) + ": " + str(value))
        type = parameterSwitch.get(parameter)

#        if(parameter == "red"):
#            print(data["type"])
#            #ix.cmds.SetCurve(["project://scene/remapColor1_tx.output"], [0.0])
#            ix.cmds.RemoveCurveValue(["project://scene/remapColor1_tx.output"], [2, 1, 2, 0, 0, 0])
#            #ix.cmds.RemoveCurveValue(["project://scene/remapColor1_tx.output"], [1, 2, 0, 0, 0])
#            #ix.cmds.RemoveCurveValue(["project://scene/remapColor1_tx.output"], [0, 0, 1, 2, 0])
#            ix.cmds.AddCurveValue(["project://scene/remapColor1_tx.output"], [
#                2.0,
#                0.0, 0.5, 0.2,
#                0.0, 0.8, 0.4,
#                0.0,
#                0.0,
#                0.0
#            ])

        if not type:
            continue

#        if(isinstance(type, list) and isinstance(type[0], str)):
#            type[1](data, value, type[2])
#            continue
        if(value["type"] == "string"):
            type[0]([str(data["type"]) + "." + str(type[1])], [str(value["value"])])
            #ix.cmds.SetValues([str(data["type"]) + "." + str(type)], [str(value["value"])])
            continue
        if(value["type"] == "float"):
            type[0]([str(data["type"]) + "." + str(type[1])], [str(value["value"])])
            continue
        if(value["type"] == "float3"):
            type[0]([str(data["type"]) + "." + str(type[1])], [str(value["value"][0][0]), str(value["value"][0][1]), str(value["value"][0][2])])
            continue
        if(value["type"] == "bool"):
            if(value["value"]):
                type[0]([str(data["type"]) + "." + str(type[1])], ["1"])
            continue
        if(value["type"] == "TdataCompound"):
            type(data["type"], value["value"])







def linkNodes(connections, nodes, material):
    for connection in connections:
        #print(connection)
        child = nodes.get(connection["from"])
        if not child:
            continue

        parent = nodes.get(connection["to"])
        if not parent:
            continue

        connector = connectionSwitch.get(connection["toAttribute"])
        if not connector:
            continue

        if(isinstance(connector, list)):
            for c in connector:
                ix.cmds.SetTexture([str(parent) + "." + str(c)], str(child))
        else:
            ix.cmds.SetTexture([str(parent) + "." + str(connector)], str(child))





def attributeMaterials(selected, mat, objects):
    if not mat:
        return
    #print(mat)
    for object in objects:
        ix.cmds.SetValues([str(selected) + "/" + str(object) + ".materials[0]"], [str(mat)])


def read_mat_data(file_path=None, default_path="project://scene"):
    """

    Reads the material data from the json file

    Example: read_mat_data(file_path='c:/test_mat.json')

    :param file_path: str, full path to the json file
    :param default_path: str, context path where the materials and texture nodes will be created
    :return:
    """

    if not file_path:
        return


    if not os.path.exists(file_path):
        return

    # Open the json file and read the data
    with open(file_path, 'r') as fp:
        data = json.load(fp)


    if not data:
        return

    selected = None
    try:
        selected = ix.selection[0]
        print(selected)
    except:
        print("Nothing selected")

    if not selected:
        return

#    shading_groups = selected.attrs.shading_groups
#    print(shading_groups)


    for material, values in data.items():
        connections = values["connections"]
        nodes = values["nodes"]
        objects = values["objects"]
        nodeTree = NodeTree(material, nodes, connections, objects, selected)
        nodeTrees.append(nodeTree)

        nodeTree.createNodes()

        #nodeTree.linkNodes(connections)

            #standard_mat = ix.cmds.CreateObject("pSphere1" + '_mat', "MaterialPhysicalStandard", "Global", default_path)

#        result = createNodes(nodes, default_path, material)
#        materialNodes = result[0]
#        toProcess = result[1]
#        mat = result[2]

        #linkNodes(connections, materialNodes, material)

        #attributeMaterials(selected, mat, objects)




#    if(selected):
#        for j in range(selected.get_attribute_count()): # item.get_attribute_count() gives us the number of attributes for this item
#            attr = selected.get_attribute(j) # This is our attribute, we get it like we could get it inside of a python list
#            print("    "+str(attr))


read_mat_data(file_path='C:\Users\etudiant\Documents\clarisse_alshader_io\\batiment.json', default_path="project://scene")
