import ix

import os
import json
import ntpath

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

nodeSwitch = {
    "aiStandardSurface"     : "MaterialPhysicalStandard",
    "remapColor"            : "TextureRemap",
    "file"                  : "TextureMapFile",
    "bump2d"                : "TextureNormalMap",
    "reverse"               : "TextureInvert",
    "remapValue"            : "TextureRescale"
}

connectionSwitch = {
    "normalCamera"          : "normal_input",
    "baseColor"             : "diffuse_front_color",
    "specularRoughness"     : "specular_1_roughness",
    "color"                 : "input",
    "inputX"                : "input",
    "bumpValue"             : "input",
    "inputValue"            : "input"
}

parameterSwitch = {
    "fileTextureName": [ix.cmds.SetValues, "filename[0]"],
    "red": addCurveRed,
    "green": addCurveGreen,
    "blue": addCurveBlue,
    "specularColor": [ix.cmds.SetValues, "specular_1_color"],
    "specularRoughness": [ix.cmds.SetValues, "specular_1_roughness"],
    "specularIOR": [ix.cmds.SetValues, "specular_1_index_of_refraction"],
    "baseColor": [ix.cmds.SetValues, "diffuse_front_color"],
    "base": [ix.cmds.SetValues, "diffuse_front_strength"],
    "alphaIsLuminance": [ix.cmds.SetValues, "single_channel_file_behavior"]
}

def createNodes(nodes, default_path, material):
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
            texture = createMaterial(node, type, default_path, material)
            mat = texture
            #node = material
            #print(material)
            #texture = "project://scene/" + str(material)
        elif type:
            texture = createNode(node, type, default_path)

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
    for node, values in parameterNodes.items():
#        #print(str(node) + ": " + str(values))
        addNodeValues(node, values)

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

        ix.cmds.SetTexture([str(parent) + "." + str(connector)], str(child))





def attributeMaterials(selected, mat, objects):
    if not mat:
        return
    print(mat)
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

            #standard_mat = ix.cmds.CreateObject("pSphere1" + '_mat', "MaterialPhysicalStandard", "Global", default_path)

        result = createNodes(nodes, default_path, material)
        materialNodes = result[0]
        toProcess = result[1]
        mat = result[2]

        linkNodes(connections, materialNodes, material)

        attributeMaterials(selected, mat, objects)
#    if(selected):
#        for j in range(selected.get_attribute_count()): # item.get_attribute_count() gives us the number of attributes for this item
#            attr = selected.get_attribute(j) # This is our attribute, we get it like we could get it inside of a python list
#            print("    "+str(attr))



        #sphere = ix.cmds.CreateObject("sphere", "GeometrySphere")
        #sphere.attrs.override_material = "project://scene/METAL_tx"

    #ix.cmds.SetValue(str(sphere) + ".materials[0]", ["project://scene/CONCRETE_tx"])



        #if value["type"] == "remapColor":
        #   texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureRemap", "Global", default_path)
        #   ix.cmds.SetTexture([str(standard_mat) + ".diffuse_front_color"], str(texture_node))


#    for shader in dataA:
#        if shader:
#            shader_name = shader['name']

#            # Create Physical Material
#            if shader_name:
#                standard_mat = ix.cmds.CreateObject(str(shader_name) + '_mat', "MaterialPhysicalStandard", "Global",
#                                                    default_path)

#            # Get the attributes
#            if standard_mat:
#                attributes_data = shader.get('data')

#                if attributes_data:
#                    for i in attributes_data:
#                        if i:

#                            if isinstance(i, dict):
#                                for clar_id, val in i.iteritems():

#                                    if isinstance(val, list) and len(val) == 3:
#                                        ix.cmds.SetValues([standard_mat.get_full_name() + "." + str(clar_id)],
#                                                          [str(val[0]), str(val[1]), str(val[2])])

#                                    # Everything that is a string is considered as a file path
#                                    elif isinstance(val, basestring):
#                                        texture_node = ix.cmds.CreateObject(str(ntpath.basename(val)) + "_tx",
#                                                                            "TextureStreamedMapFile", "Global",
#                                                                            default_path)

#                                        if texture_node:
#                                            ix.cmds.SetValues([texture_node.get_full_name() + ".filename[0]"],
#                                                              [str(val)])

#                                            # TODO Bump still needs to be implemented as an override

#                                            ix.cmds.SetTexture([standard_mat.get_full_name() + "." + str(clar_id)],
#                                                               texture_node.get_full_name())

#                                    else:
#                                        # Set the attribute
#                                        ix.cmds.SetValues([standard_mat.get_full_name() + "." + str(clar_id)],
#                                                          [str(val)])


read_mat_data(file_path='C:\Users\etudiant\Documents\clarisse_alshader_io\\batiment.json', default_path="project://scene")
