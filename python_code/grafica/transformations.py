# coding=utf-8
"""Transformation matrices for computer graphics"""

import numpy as np

__author__ = "Daniel Calderon"
__license__ = "MIT"

def identity():
    return np.identity(4, dtype=np.float32)


def uniformScale(s):
    return np.array([
        [s,0,0,0],
        [0,s,0,0],
        [0,0,s,0],
        [0,0,0,1]], dtype = np.float32)


def scale(sx, sy, sz):
    return np.array([
        [sx,0,0,0],
        [0,sy,0,0],
        [0,0,sz,0],
        [0,0,0,1]], dtype = np.float32)


def rotationX(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [1,0,0,0],
        [0,cos_theta,-sin_theta,0],
        [0,sin_theta,cos_theta,0],
        [0,0,0,1]], dtype = np.float32)


def rotationY(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [cos_theta,0,sin_theta,0],
        [0,1,0,0],
        [-sin_theta,0,cos_theta,0],
        [0,0,0,1]], dtype = np.float32)


def rotationZ(theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        [cos_theta,-sin_theta,0,0],
        [sin_theta,cos_theta,0,0],
        [0,0,1,0],
        [0,0,0,1]], dtype = np.float32)


def rotationA(theta, axis):
    s = np.sin(theta)
    c = np.cos(theta)

    assert axis.shape == (3,)

    x = axis[0]
    y = axis[1]
    z = axis[2]

    return np.array([
        # First row
        [c + (1 - c) * x * x,
        (1 - c) * x * y - s * z,
        (1 - c) * x * z + s * y,
        0],
        # Second row
        [(1 - c) * x * y + s * z,
        c + (1 - c) * y * y,
        (1 - c) * y * z - s * x,
        0],
        # Third row
        [(1 - c) * x * z - s * y,
        (1 - c) * y * z + s * x,
        c + (1 - c) * z * z,
        0],
        # Fourth row
        [0,0,0,1]], dtype = np.float32)

def rotationAxis(theta, point1, point2):
    axis = point2-point1
    axis = axis / np.linalg.norm(axis)
    a,b,c = axis
    h = np.sqrt(a**2 + c**2)

    T = translate(-point1[0], -point1[1], -point1[2])
    Tinv = translate(point1[0], point1[1], point1[2])

    Ry = np.array([
        [a/h, 0, c/h, 0],
        [0,1,0,0],
        [-c/h, 0, a/h, 0],
        [0,0,0,1]], dtype=np.float32)
    
    Ryinv = np.array([
        [a/h, 0, -c/h, 0],
        [0,1,0,0],
        [c/h, 0, a/h, 0],
        [0,0,0,1]], dtype=np.float32)
    
    Rz = np.array([
        [h, b, 0, 0],
        [-b, h, 0, 0],
        [0,0,1,0],
        [0,0,0,1]], dtype=np.float32)
    
    Rzinv = np.array([
        [h, -b, 0, 0],
        [b, h, 0, 0],
        [0,0,1,0],
        [0,0,0,1]], dtype=np.float32)
    
    Rx = rotationX(theta)

    return matmul([Tinv,Ryinv,Rzinv,Rx,Rz,Ry,T])
    
def translate(tx, ty, tz):
    return np.array([
        [1,0,0,tx],
        [0,1,0,ty],
        [0,0,1,tz],
        [0,0,0,1]], dtype = np.float32)


def shearing(xy, yx, xz, zx, yz, zy):
    return np.array([
        [ 1, xy, xz, 0],
        [yx,  1, yz, 0],
        [zx, zy,  1, 0],
        [ 0,  0,  0, 1]], dtype = np.float32)


def matmul(mats):
    out = mats[0]
    for i in range(1, len(mats)):
        out = np.matmul(out, mats[i])

    return out


def frustum(left, right, bottom, top, near, far):
    r_l = right - left
    t_b = top - bottom
    f_n = far - near
    return np.array([
        [ 2 * near / r_l,
        0,
        (right + left) / r_l,
        0],
        [ 0,
        2 * near / t_b,
        (top + bottom) / t_b,
        0],
        [ 0,
        0,
        -(far + near) / f_n,
        -2 * near * far / f_n],
        [ 0,
        0,
        -1,
        0]], dtype = np.float32)


def perspective(fovy, aspect, near, far):
    halfHeight = np.tan(np.pi * fovy / 360) * near
    halfWidth = halfHeight * aspect
    return frustum(-halfWidth, halfWidth, -halfHeight, halfHeight, near, far)


def ortho(left, right, bottom, top, near, far):
    r_l = right - left
    t_b = top - bottom
    f_n = far - near
    return np.array([
        [ 2 / r_l,
        0,
        0,
        -(right + left) / r_l],
        [ 0,
        2 / t_b,
        0,
        -(top + bottom) / t_b],
        [ 0,
        0,
        -2 / f_n,
        -(far + near) / f_n],
        [ 0,
        0,
        0,
        1]], dtype = np.float32)


def lookAt(eye, at, up):

    forward = (at - eye)
    forward = forward / np.linalg.norm(forward)

    side = np.cross(forward, up)
    side = side / np.linalg.norm(side)

    newUp = np.cross(side, forward)
    newUp = newUp / np.linalg.norm(newUp)

    return np.array([
            [side[0],       side[1],    side[2], -np.dot(side, eye)],
            [newUp[0],     newUp[1],   newUp[2], -np.dot(newUp, eye)],
            [-forward[0], -forward[1], -forward[2], np.dot(forward, eye)],
            [0,0,0,1]
        ], dtype = np.float32)
