import pymel.core as pm

# These are the color for each shader, you can customize this if you want :)
editModeColor = [0.183656,0.327,0.15696]
garmentColor = [0.107,0.145,0.161]
patternColor = [0.155,0.262,0.315]
retopoColor = [0.228,0.391,0.473]

def createShadingNode(type):
    """ !@Brief
    Create a shader with a predefined color
    @param type: String, There's four type of shader "Edit_Mode", "Garment", "Pattern","Retopo"
    @return: [ShadingNode, SurfaceShader]
    """
    # Determine the right name/color for each type
    shaderName = ""
    shaderColor = []
    if type == "Edit_Mode":
        shaderName = type
        shaderColor = editModeColor
    elif type == "Garment":
        shaderName = type
        shaderColor = garmentColor
    elif type == "Pattern":
        shaderName = type
        shaderColor = patternColor

    else:
        shaderName = type
        shaderColor = retopoColor

    # Create a shader node
    shaderNode = pm.shadingNode('lambert', name=shaderName + "_Shader", asShader=True)
    pm.setAttr(shaderNode.color, shaderColor)
    shaderNodeSG = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name='%s_SG' % (shaderName))
    pm.connectAttr(shaderNode + ".outColor", shaderNodeSG + ".surfaceShader", force=True)

    # Return result
    return [shaderNode,shaderNodeSG]