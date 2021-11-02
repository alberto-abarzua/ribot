import numpy as np
import math

#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# PHYSICAL PARAMETERS [mm]

#J1
a1x = 0
a1y = 0
a1z = 0
#J2
a2x = 0
a2y = 0
a2z = 134.0
#J3
a3x=0
a3y = 0
a3z = 144
#J4
a4x= 62
a4y = 0
a4z = 0
#J5
a5x = 89
a5y = 0
a5z = 0
#J6
a6x = 28
a6z = 0
a6y = 0

L1 = a3z
L2 = a4z
'''
#J1
a1x = 0
a1y = 0
a1z = 650
#J2
a2x = 400
a2y = 0
a2z = 680
#J3
a3x = 0
a3y = 0
a3z = 1100
#J4
a4x = 766
a4y = 0
a4z = 230
#J5
a5x = 345
a5y = 0
a5z = 0
#J6
a6x = 244
a6z = 0
a6y = 0
'''
#-----------------------------------------------------------
#-----------------------------------------------------------------------------------
# ROTATION AND TRANSLATION MATRIXES
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def rad2degree(angle):
    return (180/np.pi)*angle
def degree2rad(angle):
    return (np.pi/180)*angle
def xmatrix(angle):
    R = np.array([
        [1,0,0],
        [0,math.cos(angle),-math.sin(angle)],
        [0,math.sin(angle),math.cos(angle)]
    ])
    return R
def ymatrix(angle):
    R = np.array([
        [math.cos(angle),0,math.sin(angle)],
        [0,1,0],
        [-math.sin(angle),0,math.cos(angle)]
    ])
    return R

def zmatrix(angle):
    R  = np.array([
        [math.cos(angle),-math.sin(angle),0],
        [math.sin(angle),math.cos(angle),0],
        [0,0,1]
    ])
    return R
def tmatrix(R,D):
    T = np.block([
        [R,D],
        [0,0,0,1]
    ])
    return T


def rotationMatrixToEulerAngles(R):
    if (R[2,0] !=1 and R[2,0] !=-1):
        B1 = -math.asin(R[2,0])
        B2 = np.pi + B1
        A1 = math.atan2(R[2,1]/math.cos(B1),R[2,2]/math.cos(B1))
        A2 = math.atan2(R[2,1]/math.cos(B2),R[2,2]/math.cos(B2))
        C1 = math.atan2(R[1,0]/math.cos(B1),R[0,0]/math.cos(B1))
        C2 =math.atan2(R[1,0]/math.cos(B2),R[0,0]/math.cos(B2))
        return [float(A1),float(B1),float(C1)]
    else:
        C = 0
        if (R[2,0] ==-1):
            B = np.pi/2.0
            A = C+ math.atan2(R[0,1],R[0,2])
        else:
            B = -np.pi/2.0
            A = -C + math.atan2(-R[0,1],-R[0,2])
        return [float(A),float(B),float(C)]

def eulerAnglesToRotMatrix(A,B,C):
    return zmatrix(C)@ymatrix(B)@xmatrix(A)


#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# FORWARD KINEMATCIS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def directKinematics(l):

    J1 = degree2rad(l[0])
    J2 = degree2rad(l[1])
    J3 = degree2rad(l[2])
    J4 = degree2rad(l[3])
    J5 = degree2rad(l[4]) 
    J6 = degree2rad(l[5])
    ## BASE --> J1
    R1 = zmatrix(J1)
    D1 = np.array([
        [a1x],
        [a1y],
        [a1z]
    ])
    T1 = tmatrix(R1,D1)
    ## J1 -->  J2
    R2 = ymatrix(J2)
    D2 = np.array([
        [a2x],
        [a2y],
        [a2z]
    ])
    T2 = tmatrix(R2,D2)
    ## J2 -->  J3
    R3 = ymatrix(J3)
    D3 = np.array([
        [a3x],
        [a3y],
        [a3z]
    ])
    T3 = tmatrix(R3,D3)
    ## J3 -->  J4

    R4= xmatrix(J4)
    D4 = np.array([
        [a4x],
        [a4y],
        [a4z]
    ])
    T4 = tmatrix(R4,D4)
    ## J4 -->  J5
    R5= ymatrix(J5)
    D5 = np.array([
        [a5x],
        [a5y],
        [a5z]
    ])
    T5 = tmatrix(R5,D5)
    ## J5 -->  J6
    R6= xmatrix(J6)
    D6 = np.array([
        [a6x],
        [a6y],
        [a6z]
    ])
    T6 = tmatrix(R6,D6)
    ## Base--> TCP
    position = T1@T2@T3@T4@T5@T6@np.array([[0],[0],[0],[1]])
    rotation = R1@R2@R3@R4@R5@R6
    anglesinrad = rotationMatrixToEulerAngles(rotation)
    for i in range(len(anglesinrad)):
        anglesinrad[i] = rad2degree(anglesinrad[i])
    return list(position[:3,0])+anglesinrad
#-----------------------------------------------------------------------------------
# INVERSE KINEMATICS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
def inverseKinematics(l):
    x = l[0]
    y = l[1]
    z = l[2]
    a = l[3]
    b = l[4]
    c = l[5]
    A = degree2rad(a)
    B = degree2rad(b)
    C = degree2rad(c)
    TCP = np.array([
        [x],
        [y],
        [z]
    ])
    zdirection = eulerAnglesToRotMatrix(A,B,C) @ np.array([[0],[0],[1]])
    xdirection = eulerAnglesToRotMatrix(A,B,C) @ np.array([[1],[0],[0]])
    WP = TCP - a6x*xdirection
    # Finding J1,J2,J3
    J1 = math.atan2(WP[1,0],WP[0,0])  ## Singularity, if Wx = Wy =0 dejar J1 como pos actual.
    WPxy = math.sqrt(WP[0,0]**2 + WP[1,0]**2)
    L = WPxy - a2x
    H = WP[2,0] - a1z-a2z
    P = math.sqrt(H**2 + L**2)
    b4x = math.sqrt(a4z**2+(a4x + a5x)**2)
    if (P<=a3z + b4x) and abs(a3z-b4x)<P:
        alfa = math.atan2(H,L)
        cosbeta =( P**2 + a3z**2 - b4x**2)/(2*P*a3z)
        beta = math.atan2(math.sqrt(1-cosbeta**2),cosbeta)
        cosgamma = (a3z**2  + b4x**2 - P**2)/(2*a3z*b4x)
        gamma = math.atan2(math.sqrt(1-cosgamma**2),cosgamma)
        lamb2 = math.atan2(a3x,a3z)
        delta = math.atan2(a4x+a5x,a4z)
        J2 = np.pi/2.0 - alfa  - beta
        J3 = np.pi - gamma - delta
        # Finding Wrist Orientation
        R1 = zmatrix(J1)
        R2 = ymatrix(J2)
        R3 = ymatrix(J3)
        Rarm = R1@R2@R3
        Rarmt = Rarm.transpose()
        R = eulerAnglesToRotMatrix(A,B,C)
        Rwrist=Rarmt@R
        #Finding J4
        J5 = math.atan2(math.sqrt(1-Rwrist[0,0]**2),Rwrist[0,0] )
        if J5 == 0:
            J6 = 0
            J4 = math.atan2(Rwrist[2,1],Rwrist[2,2])
        else:
            J4 = math.atan2(Rwrist[1,0],-Rwrist[2,0])
            J6 = math.atan2(Rwrist[0,1],Rwrist[0,2])
        preangle = [J1,J2,J3,J4,J5,J6]
        for i in range(len(preangle)):
            preangle[i] = round(rad2degree(preangle[i]),4)
        return preangle
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------
# TESTS
#-----------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------

def test(x,y,z,A,B,C):
    inverse = inverseKinematics(x,y,z,A,B,C)
    print(inverse)
    print("-----------------------------------------------------------------------")
    print()
    direct =directKinematics(inverse[0],inverse[1],inverse[2],inverse[3])
    angles = np.array([
        [int(x)],
        [int(y)],
        [int(z)],
        [int(A)],
        [int(B)],
        [int(C)]
    ])
    print("These are the positions entered to InverseKInematics\n",angles)
    print()
    print("These are the angles from inverse kinematics:\n", inverse)
    print()
    for i in range(len(direct[0])):
        direct[0][1] = int(direct[0][1])
    print("These are the positions from theese angles:\n" ,direct[0])
    print()
    print("These are the euler angles from this Joint angles:\n",direct[1])
    print()
    print()

#print(test(12.5,0,373.06,0,0,0))
#print(directKinematics(inverseKinematics([120, 0, 200, 0, 0, 0])))


#target =  [245,65,191,0,89,15]
#print(test(257,40,150,0,87,9))
#print(inverseKinematics(600,-1000,3300,250,0,-90))






