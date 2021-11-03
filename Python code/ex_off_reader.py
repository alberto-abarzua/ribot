# coding=utf-8
"""Rendering an OFF file simplified"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.gpu_shape import GPUShape
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def readFaceVertex(faceDescription):

    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex





def readOFF(filename, color):
    vertices = []
    normals= []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line=="OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for i in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]
        
        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        #print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices,3), dtype=np.float32)
        #print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]
            
            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1], vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1], vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]  
            normals[aux[1]][1] += res[1]  
            normals[aux[1]][2] += res[2]  

            normals[aux[2]][0] += res[0]  
            normals[aux[2]][1] += res[1]  
            normals[aux[2]][2] += res[2]  

            normals[aux[3]][0] += res[0]  
            normals[aux[3]][1] += res[1]  
            normals[aux[3]][2] += res[2]  
        #print(faces)
        norms = np.linalg.norm(normals,axis=1)
        normals = normals/norms[:,None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        #print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2],:]
            vertexDataF += vertex.tolist()
            
            indices += [index, index + 1, index + 2]
            index += 3        



        return bs.Shape(vertexDataF, indices)

def createOFFShape(pipeline, filename, r,g, b):
    shape = readOFF(filename, (r, g, b))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

def createScene(pipeline):
    scale_factor = 0.018
    r_orange,g_orange,b_orange = 0.831, 0.462, 0.086
    r_grey,g_grey,b_grey = 0.5,0.5,0.5
    # Base of the robot
    base = sg.SceneGraphNode("base")

    bottom = createOFFShape(pipeline,"obj_files/Base/BOTTOM.off",r_orange,g_orange,b_orange)
    bottomNode = sg.SceneGraphNode("bottom")
    bottomNode.childs += [bottom]
    base.childs +=[bottomNode]
    bottomNode.transform = tr.matmul([tr.uniformScale(scale_factor),tr.rotationX(np.pi/2)])

    top = createOFFShape(pipeline,"obj_files/Base/TOP.off",r_orange,g_orange,b_orange)
    topNode = sg.SceneGraphNode("top")
    topNode.childs+=[top]
    base.childs += [topNode]
    topNode.transform = tr.matmul([tr.uniformScale(scale_factor),tr.rotationX(np.pi/2)])

    #FirstJoint (J1)
    J1 = sg.SceneGraphNode("J1")
    #SecondJoin (J2)
    J2 = sg.SceneGraphNode("J2")
    J1.childs+=[J2]
    
    first_static = createOFFShape(pipeline,"obj_files/First/FIRST_STATIC.off",r_orange,g_orange,b_orange)
    firstStaticNode = sg.SceneGraphNode("first_static")
    firstStaticNode.childs+=[first_static]
    J1.childs += [firstStaticNode]
    firstStaticNode.transform = tr.matmul([tr.uniformScale(scale_factor),tr.rotationX(np.pi/2)])


    first_rotating = createOFFShape(pipeline,"obj_files/First/ROTATING_FIRST.off",r_orange,g_orange,b_orange)
    first_rotatingNode = sg.SceneGraphNode("first_rotating")
    first_rotatingNode.childs+=[first_rotating]
    J2.childs += [first_rotatingNode]
    first_rotatingNode.transform = tr.matmul([tr.translate(0,1.7,3),tr.uniformScale(scale_factor),tr.rotationX(np.pi/2)])

    second_static = createOFFShape(pipeline,"obj_files/Second/SECOND_STATIC.off",r_orange,g_orange,b_orange)
    secondStaticNode = sg.SceneGraphNode("second_static")
    secondStaticNode.childs+=[second_static]
    J2.childs += [secondStaticNode]
    secondStaticNode.transform = tr.matmul([tr.translate(0,1.7,3),tr.uniformScale(scale_factor),tr.rotationX(np.pi/2)])

    scene = sg.SceneGraphNode('system')
    scene.childs += [base]
    scene.childs += [J1]

    J1.transform = tr.rotationZ(np.pi/3)
    J2.transform = tr.matmul([tr.translate(0,1.7,2.5),tr.rotationY(np.pi/2),tr.translate(0,-1.7,-2.5)])
    return scene

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600
    title = "Reading a *.off file"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shader programs
    pipeline = ls.SimpleGouraudShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.5, 0.5, 0.5, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory

    bottom = createScene(pipeline)

    # Setting uniforms that will NOT change on each iteration
    glUseProgram(pipeline.shaderProgram)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -3, 0, 3)
    
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    # Setting up the projection transform
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


    t0 = glfw.get_time()
    camera_theta = -3*np.pi/4

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        # Setting up the view transform
        R = 12
        camX = R * np.sin(camera_theta)
        camY = R * np.cos(camera_theta)
        viewPos = np.array([camX, camY, 7])
        view = tr.lookAt(
            viewPos,
            np.array([0,0,1]),
            np.array([0,0,1])
        )

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.rotationX(np.pi/2))
        
 
        sg.drawSceneGraphNode(bottom,pipeline,"model")

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuPlane.clear()

    glfw.terminate()
