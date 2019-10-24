import pymel.core as pm
import re
import os

class coutureDataNode():
    def __init__(self,existingNode = None):
        """ !@Brief
        This class manage creation,interaction and loading of the couture node which allow user to save their progression in Couture
        @param existingNode: CoutureNode, If there's an existing couture node in the see, the node will be provided to the class through this variable
        """

        if existingNode == None:

            ### Create Attributes
            self.coutureDataNode = pm.createNode('partition', name="CoutureDataNode")
            pm.addAttr(self.coutureDataNode,longName='exportPath',dt= "string")
            pm.addAttr(self.coutureDataNode, longName='Garment', dt="string")
            pm.addAttr(self.coutureDataNode, longName='Pattern', dt="string")
            pm.addAttr(self.coutureDataNode, longName='Retopo', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolLoadGarment', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolSoloGarment', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolFlattenGarment', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolDefineRetopo', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolPairFlatten', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolErrorPair', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolCreateBs', dt="string")
            pm.addAttr(self.coutureDataNode, longName='boolCreateWrap', dt="string")
            pm.addAttr(self.coutureDataNode, longName='ScaleFactor', dt="string")
            pm.addAttr(self.coutureDataNode, longName='TranslateX', dt="string")
            pm.addAttr(self.coutureDataNode, longName='BlendshapeNodes', dt="string")
            pm.addAttr(self.coutureDataNode, longName='EditSelection', dt="string")

            ### Set default attributes
            pm.setAttr(self.coutureDataNode.name() + '.boolLoadGarment', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolSoloGarment', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolFlattenGarment', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolDefineRetopo', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolPairFlatten', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolErrorPair', "False", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolCreateBs', "True", type="string")
            pm.setAttr(self.coutureDataNode.name() + '.boolCreateWrap', "True", type="string")



        else :
            ### Set an existing couture node
            self.coutureDataNode = pm.PyNode(existingNode)

    ### Series of function to edit and acces attributes
    def addExportPath(self,path):
        pm.setAttr(self.coutureDataNode.name() + '.exportPath', path, type="string")

    def getExportPath(self):
        path = pm.getAttr(self.coutureDataNode.name()+'.exportPath')
        return path

    def addGarmentList(self,list):
        pm.setAttr(self.coutureDataNode.name() + '.Garment', "%s"%list, type="string")

    def getGarmentList(self):
        list = pm.getAttr(self.coutureDataNode.name() + '.Garment')
        return list

    def addPatternList(self,list):
        pm.setAttr(self.coutureDataNode.name() + '.Pattern', "%s"%list, type="string")

    def getPatternList(self):
        list = pm.getAttr(self.coutureDataNode.name() + '.Pattern')
        return list

    def changeBoolLoadGarment(self,status):
        pm.setAttr(self.coutureDataNode.name() + '.boolLoadGarment', "%s"%status, type="string")

    def getBoolLoadGarment(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolLoadGarment')
        return status

    def changeBoolSoloGarment(self,status):
        pm.setAttr(self.coutureDataNode.name() + '.boolSoloGarment', "%s"%status, type="string")

    def getBoolSoloGarment(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolSoloGarment')
        return status

    def changeBoolFlattenGarment(self,status):
        pm.setAttr(self.coutureDataNode.name() + '.boolFlattenGarment', "%s"%status, type="string")

    def getBoolFlattenGarment(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolFlattenGarment')
        return status

    def changeBoolDefineRetopo(self, status):
        pm.setAttr(self.coutureDataNode.name() + '.boolDefineRetopo', "%s" % status, type="string")

    def getBoolDefineRetopo(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolDefineRetopo')
        return status

    def changeBoolPairFlatten(self, status):
        pm.setAttr(self.coutureDataNode.name() + '.boolPairFlatten', "%s" % status, type="string")

    def getBoolPairFlatten(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolPairFlatten')
        return status

    def changeBoolErrorPair(self, status):
        pm.setAttr(self.coutureDataNode.name() + '.boolErrorPair', "%s" % status, type="string")

    def getBoolErrorPair(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolErrorPair')
        return status

    def changeBoolCreateBs(self, status):
        pm.setAttr(self.coutureDataNode.name() + '.boolCreateBs', "%s" % status, type="string")

    def getBoolCreateBs(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolCreateBs')
        return status

    def changeBoolCreateWrap(self, status):
        pm.setAttr(self.coutureDataNode.name() + '.boolCreateWrap', "%s" % status, type="string")

    def getBoolCreateWrap(self):
        status = pm.getAttr(self.coutureDataNode.name() + '.boolCreateWrap')
        return status

    def addRetopoList(self,list):
        pm.setAttr(self.coutureDataNode.name() + '.Retopo', "%s"%list, type="string")

    def getRetopoList(self):
        list = pm.getAttr(self.coutureDataNode.name() + '.Retopo')
        return list

    def addScaleFactor(self,value):
        pm.setAttr(self.coutureDataNode.name() + '.ScaleFactor', "%s"%value, type="string")

    def getScaleFactor(self):
        value = pm.getAttr(self.coutureDataNode.name() + '.ScaleFactor')
        return value

    def addTranslateX(self,value):
        pm.setAttr(self.coutureDataNode.name() + '.TranslateX', "%s"%value, type="string")

    def getTranslateX(self):
        value = pm.getAttr(self.coutureDataNode.name() + '.TranslateX')
        return value

    def addBsNodeList(self,list):
        pm.setAttr(self.coutureDataNode.name() + '.BlendshapeNodes', "%s"%list, type="string")

    def getBsNodeList(self):
        list = pm.getAttr(self.coutureDataNode.name() + '.BlendshapeNodes')
        return list

    def addEditSelectionDic(self,list):
        pm.setAttr(self.coutureDataNode.name() + '.EditSelection', "%s"%list, type="string")

    def getEditSelectionDic(self):
        list = pm.getAttr(self.coutureDataNode.name() + '.EditSelection')
        return list

    def resetNode(self):
        ### Restart to a default Couture Node
        pm.setAttr(self.coutureDataNode.name() + '.exportPath', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.Garment', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.Pattern', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.Retopo', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.ScaleFactor', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.TranslateX', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.BlendshapeNodes', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.EditSelection', "", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolLoadGarment', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolSoloGarment', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolFlattenGarment', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolDefineRetopo', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolPairFlatten', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolErrorPair', "False", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolCreateBs', "True", type="string")
        pm.setAttr(self.coutureDataNode.name() + '.boolCreateWrap', "True", type="string")


def testGeo(objectList):
    """ !@Brief
    This function checks if selected object are a geometry
    @param objectList: List, a list of selected  pm node
    """

    polygonMesh = []
    nonPolygonMesh = []
    for object in objectList:

        if pm.nodeType(object.getShape(), api=True) == "mesh":
            polygonMesh.append(object)

        else:
            nonPolygonMesh.append(object)

    return polygonMesh,nonPolygonMesh


def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text)]

def humanSorting(list):

    list.sort(key=natural_keys)
    return list

def removeNamespace(namespaceSelected):
    """ !@Brief
    Remove Namespace to selected garments, namespace will generate error otherwise
    @param namespaceSelected: List, a list of namespace
    """

    namespacesInScene = []
    for ns in pm.listNamespaces(recursive=True, internal=False):
        namespacesInScene.append(ns)

    namespaces = []

    for namespace in namespaceSelected:
        if namespace in namespacesInScene:
            namespaces.append(namespace)

    for ns in reversed(namespaces):
        currentSpace = ns
        pm.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)

def goToWeb(url,coutureMessage):
    """ !@Brief
    Acces a webpage in default web brower
    @param url: String, web url
    @param coutureMessage: coutureMessage instance, close the window
    """
    os.startfile(url)
    if coutureMessage != None:
        coutureMessage.killWindow()

def longNameEdit (type,longName,source,target):
    """ !@Brief
    This function handle the renaming of longName through differente state of couture
    @param type: String, get one of the three types : 'garment' 'pattern' 'retopo'
    @param longName: String, longName of a couture mesh
    @param source: String, input to search
    @param target: String, input to replace
    @return longNameEdited: String
    """

    if type == "garment":

        longNameEdited = longName[:19] + target+"_" + longName[19:]
        longNameEdited = longNameEdited.replace(source,target)

        return longNameEdited
    elif type == "pattern":
        if target == "garment":
            longName = longName.replace(source+'_','')
        longNameEdited = longName.replace(source, target)

        return longNameEdited

    elif type == "retopo":
        if target == "garment":
            longName = longName.replace(source+'_','')
        longNameEdited = longName.replace(source, target)

        return longNameEdited
def twoDigitStr(int):
    """ !@Brief
    This function convert a int number lower than 10 in a string starting by 0
    @param int: int, The desired number to convert
    @return result: String
    """

    if len("%s" % int) < 2:
        result = "0%s" % int
    else:
        result = "%s" % int
    return result

def strLineReturn (Dic):
    """ !@Brief
    Return a dictionnary in a string whose each key entry is separated by a line break
    @param Dic: Dictionnary, The desired Dictionnary to convert
    @return list: String
    """

    list = ""
    for garment, type in Dic.items():
        if type == "two":
            list = list + longNameEdit("garment", garment, "garment", "pattern")+"\n"
    return list
def extract_name_nb(a):
    """ !@Brief
    This function will find if there is a digit suffix in a string, return None if there's no digit suffix in the string
    @param a: str, given string by the user
    @return: list, [core string, string digit suffix]
    """

    name_len = len(a.rstrip("0123456789"))
    nb_len = len(a) - name_len
    nb = None
    if nb_len:
        nb = int(a[-nb_len:])
    return a[:name_len], nb