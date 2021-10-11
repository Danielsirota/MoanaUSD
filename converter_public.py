import json
import os
from pxr import Usd, UsdGeom, Gf


class Mesh:
    "Mesh Data Class"

    def __init__(self, meshname):
        """Constructor.
        Args:
            meshname (str): mesh name
        """
        self.Name = meshname
        self.index = []
        self.faceCount = []


class OBJ:
    "OBJ File Reader"
    def __init__(self, filename):
        """Constructor.
        Args:
            filename (str): obj file to read
        """
        self.vertices = []
        self.meshs = Mesh(filename)
        try:
            f = open(filename)
            for line in f:
                ltype = line.split(" ")
                if ltype[0] == "v":
                    tokens = line.split(" ")
                    vertex = (float(tokens[1]), float(
                        tokens[2]), float(tokens[3]))
                    self.vertices.append(vertex)

                elif ltype[0] == "f":
                    tokens = line.split(" ")
                    tokens.pop(0)
                    index = []
                    for t in tokens:
                        index.append(t.split("/")[0])
                    self.meshs.faceCount.append(len(tokens))
                    for i in range(len(tokens)):
                        self.meshs.index.append(int(index[i])-1)
            f.close()
        except IOError:
            print("OBJ file not found.")


def JSONtoUsd(filename, root):
    """Converts JSON Files To USD
    Args:
        filename (string): JSON file to convert
        root (string): Moana dataset root location
    """
    with open(filename) as read_file:
        _data = json.load(read_file)
        _stage = Usd.Stage.CreateNew(_data['name'] + '.usda')
        # print(stage)
        _a = OBJ(root + _data['geomObjFile'])
        UsdGeom.Mesh.Define(_stage, "/" + _data['name'])
        _m = _a.meshs
        _mesh = _stage.GetPrimAtPath("/"+_data['name'])
        _stage.SetDefaultPrim(_mesh)
        _pointsAttr = _mesh.GetAttribute('points')
        _pointsAttr.Set(_a.vertices)
        _vcAttr = _mesh.GetAttribute('faceVertexCounts')
        _vcAttr.Set(_m.faceCount)
        _viAttr = _mesh.GetAttribute('faceVertexIndices')
        _viAttr.Set(_m.index)
        _mesh.SetInstanceable()
        _stage.GetRootLayer().Save()

        _refStage = Usd.Stage.CreateNew(_data['name'] + '_scene.usda')
        _refPrim = _refStage.OverridePrim("/"+_data['name'])

        _refPrim.GetReferences().AddReference('./' + _data['name'] + '.usda')

        _transform = _data['transformMatrix']
        _trans = UsdGeom.Xform(_refPrim).AddTransformOp()
        _trans.Set(Gf.Matrix4d(_transform[0], _transform[1], _transform[2], _transform[3],
                               _transform[4], _transform[5], _transform[6], _transform[7],
                               _transform[8], _transform[9], _transform[10], _transform[11],
                               _transform[12], _transform[13], _transform[14], _transform[15]))

        if 'instancedCopies' in _data:
            _instances = _data['instancedCopies']
            for i in _instances:
                _refPrim = _refStage.OverridePrim("/"+i)
                _refPrim.GetReferences().AddReference(
                    './' + _data['name'] + '.usda')
                _transform = _data['instancedCopies'][i]['transformMatrix']
                _trans = UsdGeom.Xform(_refPrim).AddTransformOp()
                _trans.Set(Gf.Matrix4d(_transform[0], _transform[1], _transform[2], _transform[3],
                                       _transform[4], _transform[5], _transform[6], _transform[7],
                                       _transform[8], _transform[9], _transform[10], _transform[11],
                                       _transform[12], _transform[13], _transform[14], _transform[15]))

        _refStage.GetRootLayer().Save()


def convertMoanaToUSD(root):
    """Converts Moana Island dataset To USD
    Args:
        root (string): Moana dataset root location
    """
    for f in os.listdir(root + "\\json"):
        if ("cameras" not in f):
            if ("lights" not in f):
                if ("osOcean" not in f):
                    for j in os.listdir(root + "\\json\\"+f):
                        if ("_" not in j):
                            if ("materials" not in j):
                                if ("Ironwood" not in j):
                                    print("Converting: " + root +
                                          "\\json\\"+f+"\\"+j)
                                    JSONtoUsd(root + "\\json\\" +
                                              f+"\\"+j, root + "\\")

    Stage = Usd.Stage.CreateNew('Scene.usda')
    rootLayer = Stage.GetRootLayer()
    for f in os.listdir(os.getcwd()):
        if ("_scene" in f):
            if ("usd" in f):
                if ("usda" in f):
                    print(f)
                    rootLayer.subLayerPaths.append('./' + f)
    Stage.GetRootLayer().Save()


convertMoanaToUSD("E:\\Disney_island")
