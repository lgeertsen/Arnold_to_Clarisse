import ix

import os
import json
import ntpath

def createStandardSurface(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + '_mat', "MaterialPhysicalStandard", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createRemap(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureRemap", "Global", path)
    #ix.cmds.SetTexture([str(parent) + ".diffuse_front_color"], str(texture_node))
    return texture_node

def createFile(node, path):
    texture_node = ix.cmds.CreateObject(str(node) + "_tx", "TextureRemap", "Global", path)
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

nodeSwitch = {
    "aiStandardSurface"     : createStandardSurface,
    "remapColor"            : createRemap,
    "file"                  : createFile,
    "bump2d"                : createBump2d,
    "reverse"               : createReverse
}

connectionSwitch = {
    "normalCamera": "normal_input",
    "baseColor": "diffuse_front_color",
    "specularRoughness": "specular_1_roughness",
    "color": "input",
    "inputX": "input",
    "bumpValue": "input"
}

def createNodes(nodes, default_path):
    materialNodes = {}
    toProcess = {}

    for node, value in nodes.items():
        #print(node)
        print(value["type"])
        func = nodeSwitch.get(value["type"], "Invalid type")
        texture = None
        if func != "Invalid type":
            texture = func(node, default_path)

        if texture:
            materialNodes[node] = texture
        else:
            toProcess[node] = value

    for node, value in materialNodes.items():
        print(str(node) + ": " + str(value))

    print("----------------TO PROCESS----------------")
    for node, value in toProcess.items():
        print(str(node) + ": " + str(value))

    return [materialNodes, toProcess]

def linkNodes(connections, nodes):
    for connection in connections:
        print(connection)
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

    connections = data["connections"]
    nodes = data["nodes"]
    #print(connections)
    #print(nodes)

    #standard_mat = ix.cmds.CreateObject("pSphere1" + '_mat', "MaterialPhysicalStandard", "Global", default_path)

    result = createNodes(nodes, default_path)
    materialNodes = result[0]
    toProcess = result[1]

    linkNodes(connections, materialNodes)





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


read_mat_data(file_path='C:\Users\etudiant\Documents\clarisse_alshader_io\pShere1.json', default_path="project://scene")
