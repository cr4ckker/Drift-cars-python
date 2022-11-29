from math import sqrt
import numpy as np
import numba

@numba.njit(cache=True)
def rotate(angle, point_x, point_y, offset_x, offset_y, center_x, center_y):
    return [(center_x - point_x) * np.math.cos(np.math.radians(angle))  -  (center_y - point_y) * np.math.sin(np.math.radians(angle))  +  offset_x, 
        (center_x - point_x) * np.math.sin(np.math.radians(angle))  +  (center_y - point_y) * np.math.cos(np.math.radians(angle))  +  offset_y]


def hyp(vec):
    return sqrt(vec[0]**2 + vec[1]**2)

@numba.njit
def GetLines(obj):
    return [[obj[i-1], obj[i]] for i in range(-1, len(obj)-1)]

@numba.njit
def GetCenter(obj):
    return sum(map(lambda x: np.array(x), obj))/len(obj)

def Normalize(Vec):
    if Vec[0] == 0 and Vec[1] == 0:
        Vec[1] = 1
    Magnitude = np.math.sqrt(Vec[0]**2 + Vec[1]**2)
    Vec[0] /= Magnitude
    Vec[1] /= Magnitude
    return Vec