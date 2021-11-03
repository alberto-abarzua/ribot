# coding=utf-8
"""Face based data structure for a triangle mesh"""

__author__ = "Daniel Calderon"
__license__ = "MIT"

class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return "Triangle(" +\
            str(self.a) + ", " +\
            str(self.b) + ", " +\
            str(self.c) + ")"

class TriangleFaceMesh:
    def __init__(self, data):
        self.data = data
        self.ab = None
        self.bc = None
        self.ca = None

    def __str__(self):
        output = "TriangleFaceMesh{\n"
        output += "\tdata :" + str(self.data) + "\n"
        
        def getIndexIfNotNone(side, quadFaceMesh):
            if quadFaceMesh != None:
                return "\t" + side + ": " +\
                    str(quadFaceMesh.data) + "\n"
            return ""
        
        output += getIndexIfNotNone("ab", self.ab)
        output += getIndexIfNotNone("bc", self.bc)
        output += getIndexIfNotNone("ca", self.ca)
        output += "}\n"
        
        return output


class TriangleFaceMeshBuilder:
    def __init__(self):
        self.triangleMeshes = []

        # Helper dictionary to search for previously inserted edges,
        # so 2 triangles can be connected over each edge
        self.previousEdges = {}


    def connectToPreviousTriangle(self, tail, head, side, triangleFaceMeshIndex):
        
        triangleFaceMesh = self.triangleMeshes[triangleFaceMeshIndex]

        # We have only 2 possibilities of connection: tail->head and head->tail
        
        # Once we have the connection we do not need to keep the edge on memory
        # This is assuming the user will provide valid data.
        if (tail, head) in self.previousEdges:
            previousTriangleMesh, previousSide = self.previousEdges[(tail, head)]
            del self.previousEdges[(tail, head)]

        elif (head, tail) in self.previousEdges:
            previousTriangleMesh, previousSide = self.previousEdges[(head, tail)]
            del self.previousEdges[(head, tail)]

        else:
            # If the edge is new, this triangle does not need to be connected via this edge
            # We just need to store the edge for a future query
            self.previousEdges[(tail, head)] = (triangleFaceMesh, side)
            return

        # At this step, we already have a triangle with that edge, we need to connect the
        # new and the old triangle.

        # Connections are done using the 'side' specified
        if previousSide == "ab":
            previousTriangleMesh.ab = triangleFaceMesh
        elif previousSide == "bc":
            previousTriangleMesh.bc = triangleFaceMesh
        else:
            assert(previousSide == "ca")
            previousTriangleMesh.ca = triangleFaceMesh

        if side == "ab":
            triangleFaceMesh.ab = previousTriangleMesh
        elif side == "bc":
            triangleFaceMesh.bc = previousTriangleMesh
        else:
            assert(side == "ca")
            triangleFaceMesh.ca = previousTriangleMesh

        
    def addTriangle(self, newTriangle):

        triangleFaceMeshIndex = len(self.triangleMeshes)
        triangleFaceMesh = TriangleFaceMesh(newTriangle)
        self.triangleMeshes += [triangleFaceMesh]

        self.connectToPreviousTriangle(newTriangle.a, newTriangle.b, "ab", triangleFaceMeshIndex)
        self.connectToPreviousTriangle(newTriangle.b, newTriangle.c, "bc", triangleFaceMeshIndex)
        self.connectToPreviousTriangle(newTriangle.c, newTriangle.a, "ca", triangleFaceMeshIndex)

    
    def getTriangleFaceMeshes(self):
        return self.triangleMeshes

        

        
