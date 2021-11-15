import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.text_renderer as tx
import arm_utils.robotarm as ra
import arm_control.controller as ac
from arm_utils.armTransforms import Angle
from grafica.assets_path import getAssetPath
from grafica.gpu_shape import GPUShape
import grafica.performance_monitor as pm
import grafica.lighting_shaders as ls
import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.basic_shapes as bs
import grafica.transformations as tr
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

__author__ = "Alberto Abarzua"


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

    if key == glfw.KEY_LEFT_ALT:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def readFaceVertex(faceDescription):

    aux = faceDescription.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    faceVertex = [int(aux[0]), None, None]

    assert len(
        aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        faceVertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        faceVertex[2] = int(aux[2])

    return faceVertex


def readOFF(filename, color):
    """Reads a mesh stored in an .off file.

    Args:
        filename (string): location of the .off file
        color (list[int]): r,g,b color of the object

    Returns:
        Shape: shape containing the vertex and index data.
    """
    vertices = []
    normals = []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line == "OFF"

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

        normals = np.zeros((numVertices, 3), dtype=np.float32)
        #print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]

            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]]
                    [1] - vertices[aux[1]][1], vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]]
                    [1] - vertices[aux[2]][1], vertices[aux[3]][2] - vertices[aux[2]][2]]

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
        # print(faces)
        norms = np.linalg.norm(normals, axis=1)
        normals = normals/norms[:, None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        # print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1], :]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2], :]
            vertexDataF += vertex.tolist()

            indices += [index, index + 1, index + 2]
            index += 3

        return bs.Shape(vertexDataF, indices)


def createOFFShape(pipeline, filename, r, g, b):
    """Creates gpuShape from .off file

    Args:
        pipeline (Pipeline): Pipeline for the gpuShape
        filename (str): directory of file
        r (int): red component of object's colour
        g (int): green component of object's colour
        b (int): blue component of object's colour

    Returns:
        GPUShape: gpuShape created from .off file
    """
    shape = readOFF(filename, (r, g, b))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape


def createScene(pipeline):
    """Creates the scene and the loads all the off files to recreate the robot arm.

    Args:
        pipeline (Pipeline): Pipeline that manages 3d models.

    Returns:
        SceneGraphNode: SceneGraphNode containing the scene
    """
    scale_factor = 0.018
    r_orange, g_orange, b_orange = 0.831, 0.462, 0.086
    r_grey, g_grey, b_grey = 0.2, 0.2, 0.2
    # Base of the robot
    base = sg.SceneGraphNode("base")

    bottom = createOFFShape(
        pipeline, "arm_off_files/Base/BOTTOM.off", r_orange, g_orange, b_orange)
    bottomNode = sg.SceneGraphNode("bottom")
    bottomNode.childs += [bottom]
    base.childs += [bottomNode]
    bottomNode.transform = tr.matmul(
        [tr.uniformScale(scale_factor), tr.rotationZ(np.pi), tr.rotationX(np.pi/2)])

    top = createOFFShape(pipeline, "arm_off_files/Base/TOP.off",
                         r_orange, g_orange, b_orange)
    topNode = sg.SceneGraphNode("top")
    topNode.childs += [top]
    base.childs += [topNode]
    topNode.transform = tr.matmul(
        [tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])

    #FirstJoint (J1)
    J1 = sg.SceneGraphNode("J1")
    #SecondJoin (J2)
    J2 = sg.SceneGraphNode("J2")
    J1.childs += [J2]

    first_static = createOFFShape(
        pipeline, "arm_off_files/First/FIRST_STATIC.off", r_grey, g_grey, b_grey)
    firstStaticNode = sg.SceneGraphNode("first_static")
    firstStaticNode.childs += [first_static]
    J1.childs += [firstStaticNode]
    firstStaticNode.transform = tr.matmul(
        [tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])

    first_rotating = createOFFShape(
        pipeline, "arm_off_files/First/ROTATING_FIRST.off", r_orange, g_orange, b_orange)
    first_rotatingNode = sg.SceneGraphNode("first_rotating")
    first_rotatingNode.childs += [first_rotating]
    J2.childs += [first_rotatingNode]
    first_rotatingNode.transform = tr.matmul(
        [tr.translate(0, 1.7, 3), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])

    second_static = createOFFShape(
        pipeline, "arm_off_files/Second/SECOND_STATIC.off", r_orange, g_orange, b_orange)
    secondStaticNode = sg.SceneGraphNode("second_static")
    secondStaticNode.childs += [second_static]
    J2.childs += [secondStaticNode]
    secondStaticNode.transform = tr.matmul(
        [tr.translate(0, 1.7, 3), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])

    second_static = createOFFShape(
        pipeline, "arm_off_files/Second/SECOND_STATIC.off", r_grey, g_grey, b_grey)
    secondStaticNode = sg.SceneGraphNode("second_static")
    secondStaticNode.childs += [second_static]
    J2.childs += [secondStaticNode]
    secondStaticNode.transform = tr.matmul(
        [tr.translate(0, 1.7, 3), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])

    J3 = sg.SceneGraphNode("J3")
    J2.childs += [J3]

    second_rotating = createOFFShape(
        pipeline, "arm_off_files/Second/SECOND_ROTATION.off", r_grey, g_grey, b_grey)
    secondRotatingNode = sg.SceneGraphNode("second_rotating")
    secondRotatingNode.childs += [second_rotating]
    secondRotatingNode.transform = tr.matmul(
        [tr.translate(0, 1.7, 3), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])
    J3.childs += [secondRotatingNode]

    J4 = sg.SceneGraphNode("J4")
    J3.childs += [J4]

    third_static = createOFFShape(
        pipeline, "arm_off_files/Third/THIRD_STATIC.off", r_grey, g_grey, b_grey)
    thirdStaticNode = sg.SceneGraphNode("third_static")
    thirdStaticNode.childs += [third_static]
    thirdStaticNode.transform = tr.matmul(
        [tr.translate(0, 0, 6), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])
    J4.childs += [thirdStaticNode]

    J5 = sg.SceneGraphNode("J5")
    J4.childs += [J5]

    third_rotating = createOFFShape(
        pipeline, "arm_off_files/Third/THIRD_ROTATING.off", r_grey, g_grey, b_grey)
    thirdRotatingNode = sg.SceneGraphNode("third_rotating")
    thirdRotatingNode.childs += [third_rotating]
    thirdRotatingNode.transform = tr.matmul(
        [tr.translate(0, 0, 6), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])
    J5.childs += [thirdRotatingNode]

    J6 = sg.SceneGraphNode("J6")
    J5.childs += [J6]

    tcp = createOFFShape(pipeline, "arm_off_files/TCP/TCP.off",
                         r_orange, g_orange, b_orange)
    tcpNode = sg.SceneGraphNode("tcp")
    tcpNode.childs += [tcp]
    tcpNode.transform = tr.matmul(
        [tr.translate(-0.1, 0.9, 8), tr.uniformScale(scale_factor), tr.rotationX(np.pi/2)])
    J6.childs += [tcpNode]

    scene = sg.SceneGraphNode('system')
    scene.childs += [base]
    scene.childs += [J1]
    return scene


def setJoints(scene, joints):
    """Used to update the joints angles in real time.

    Args:
        scene (SceneGraphNode): Node that contains the whole robot arm.
        joints (list[Angle]): List of angles
    """
    J1_val, J2_val, J3_val, J4_val, J5_val, J6_val = [j.rad for j in joints]
    J1, J2, J3, J4, J5, J6 = [sg.findNode(scene, f"J{i+1}") for i in range(6)]
    J3_val += np.pi/2  # J1 offset
    J1.transform = tr.rotationZ(J1_val)
    J2.transform = tr.matmul(
        [tr.translate(0, 1.7, 2.5), tr.rotationY(J2_val), tr.translate(0, -1.7, -2.5)])
    J3.transform = tr.matmul([tr.translate(
        0, 1.7*2, 2.5*2), tr.rotationY(J3_val), tr.translate(0, -1.7*2, -2.5*2)])
    J4.transform = tr.matmul(
        [tr.translate(0, 0, 6), tr.rotationZ(J4_val), tr.translate(0, 0, -6)])
    J5.transform = tr.matmul(
        [tr.translate(0, 0, 8), tr.rotationY(J5_val), tr.translate(0, 0, -8)])
    J6.transform = tr.matmul(
        [tr.translate(0, 0, 8), tr.rotationZ(J6_val), tr.translate(0, 0, -8)])


def drawText(textPipeline, string, size, pos):
    """Creates and draws text on the screen

    Args:
        textPipeline (Pipeline): Pipeline that manages text.
        string (str): String to be displayed in text
        size (int): display size of the string
        pos (list[int]): list of x,y,z (position of the text on the screen)
    """
    color = [1, 1, 1]

    shape_text = tx.textToShape(string, size, size)
    gpu_text = es.GPUShape().initBuffers()
    textPipeline.setupVAO(gpu_text)
    gpu_text.fillBuffers(shape_text.vertices,
                         shape_text.indices, GL_STATIC_DRAW)
    gpu_text.texture = gpuText3DTexture
    glUseProgram(textPipeline.shaderProgram)
    glUniform4f(glGetUniformLocation(textPipeline.shaderProgram,
                "fontColor"), color[0], color[1], color[2], 1)
    glUniform4f(glGetUniformLocation(textPipeline.shaderProgram,
                "backColor"), 1-color[0], 1-color[1], 1-color[2], 0.5)
    glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
                       tr.translate(pos[0], pos[1], pos[2]))

    textPipeline.drawCall(gpu_text)
    return gpu_text


if __name__ == "__main__":
    # Creation of robot arm
    robot_controller = ac.Controller()
    robot = robot_controller.robot

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1200
    height = 1200
    title = "6DOF Robot Arm simulation"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shader programs
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()
    pipeline = ls.SimpleGouraudShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    textBitsTexture = tx.generateTextBitsTexture()
    # Axis setup
    glUseProgram(axisPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    axisPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(
        axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.5, 0.5, 0.5, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory

    bottom = createScene(pipeline)
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    # Setting uniforms that will NOT change on each iteration
    glUseProgram(pipeline.shaderProgram)
    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(
        pipeline.shaderProgram, "lightPosition"), 0, 0, 7)

    glUniform1ui(glGetUniformLocation(
        pipeline.shaderProgram, "shininess"), 20)
    glUniform1f(glGetUniformLocation(
        pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(
        pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(
        pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    # Setting up the projection transform
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(
        pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    color = [1.0, 1.0, 1.0]

    t0 = glfw.get_time()
    camera_theta = 3*np.pi/4

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    R = 17
    robot.direct_kinematics()  # We update the euler angles and xyz
    x, y, z = robot.xyz
    A, B, C = robot.euler_angles

    (x_disp, y_disp, z_disp) = robot.xyz
    A_disp, B_disp, C_disp = robot.euler_angles
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

        # Camera controlls
        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2 * dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            R -= 5 * dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            R += 5 * dt

        # Arm controlls
        movement_step = 30
        if (glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
            x += movement_step * dt

        if (glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
            x -= movement_step * dt

        if (glfw.get_key(window, glfw.KEY_A) == glfw.PRESS):
            y += movement_step * dt

        if (glfw.get_key(window, glfw.KEY_D) == glfw.PRESS):
            y -= movement_step * dt

        if (glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS):
            z += movement_step * dt

        if (glfw.get_key(window, glfw.KEY_E) == glfw.PRESS):
            z -= movement_step * dt

        angle_step_positive = Angle(0.5*dt, "rad")
        angle_step_negative = Angle(-0.5*dt, "rad")
        if (glfw.get_key(window, glfw.KEY_J) == glfw.PRESS):
            A.add(angle_step_positive)

        if (glfw.get_key(window, glfw.KEY_L) == glfw.PRESS):
            A.add(angle_step_negative)

        if (glfw.get_key(window, glfw.KEY_I) == glfw.PRESS):
            B.add(angle_step_positive)

        if (glfw.get_key(window, glfw.KEY_K) == glfw.PRESS):
            B.add(angle_step_negative)

        if (glfw.get_key(window, glfw.KEY_U) == glfw.PRESS):
            C.add(angle_step_positive)

        if (glfw.get_key(window, glfw.KEY_O) == glfw.PRESS):
            C.add(angle_step_negative)

        # Setting up the view transform

        camX = R * np.sin(camera_theta)
        camY = R * np.cos(camera_theta)
        viewPos = np.array([camX, camY, 10])
        view = tr.lookAt(
            viewPos,
            np.array([0, 0, 1.2]),
            np.array([0, 0, 1.2])
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(axisPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(
            axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUseProgram(axisPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(
            axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        axisPipeline.drawCall(gpuAxis, GL_LINES)
        # Clearing the screen in both, color and depth

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing shapes
        glUseProgram(pipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram,
                    "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(
            pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(
            pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.rotationX(np.pi/2))

        
        if (robot_controller.move_to_point([x, y, z], [A, B, C]) != "Angles out of reach"):
            setJoints(bottom, robot_controller.get_arduino_angles())
            pos, angles = robot.direct_kinematics()
            # Text to display
            (x_disp, y_disp, z_disp) = pos
            A_disp, B_disp, C_disp = angles

        sg.drawSceneGraphNode(bottom, pipeline, "model")
        cords_text = drawText(
            textPipeline, f"x = {x_disp:.2f} y = {y_disp:.2f} z = {z_disp:.2f}", 0.03, [-0.95, -0.8, 0])
        angles_text = drawText(
            textPipeline, f"A = {A_disp.deg:.2f} B = {B_disp.deg:.2f} C = {C_disp.deg:.2f}", 0.03, [-0.95, -0.9, 0])
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    bottom.clear()
    cords_text.clear()
    angles_text.clear()
    glfw.terminate()
    gpuAxis.clear()
