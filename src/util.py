# utils

import numpy as np

def distance(u: tuple, v: tuple) -> float:
    return sum((a - b) ** 2 for a, b in zip(u, v)) ** 0.5

def flatten(multiList: list) -> list:
    if not multiList: return []
    if isinstance(multiList[0], list):
        flattened = flatten(multiList[0])
    else:
        flattened = multiList[:1]
    return flattened + flatten(multiList[1:])

def extend2homo(posList: list) -> list:
    if not posList: return []
    if isinstance(posList[0], list):
        extended = [extend2homo(posList[0])]
    else:
        extended = [np.array((*posList[0], 1))]
    return extended + extend2homo(posList[1:])

def buildRotationMat4(deg: float) -> np.ndarray:
    return np.array([
        [np.cos(deg), -np.sin(deg), 0, 0],
        [np.sin(deg), np.cos(deg), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

def buildTranslationMat4(x: int, y: int, z: int) -> np.ndarray:
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ])

def buildProjectionMat4(n: int, f: int, b: int, t: int, l: int, r: int) -> np.ndarray:
    return np.array([
        [2 * n / (r - l), 0, (r + l) / (l - r), 0],
        [0, 2 * n / (t - b), (t + b) / (b - t), 0],
        [0, 0, (f + n) / (f - n), -2 * n * f / (f - n)],
        [0, 0, 1, 0]
    ])
