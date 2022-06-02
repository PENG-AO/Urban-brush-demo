# 3d view

from math import degrees
import numpy as np
import tkinter as tk

from src.util import buildProjectionMat4, buildTranslationMat4, distance

class View3d(object):

    CANVAS_H, CANVAS_W = 800, 800
    NEAR_LEN, FAR_LEN = 3200, 4000
    BOTTOM_LEN, TOP_LEN = 600, 1400
    LEFT_LEN, RIGHT_LEN = -520, 520
    VIEW_ANGLE = 5.58 # 320 degrees

    def __init__(self, master) -> None:
        self.master = master
        self.leftClickPos = None
        self.rightClickPos = None
    
    def activate(self) -> None:
        self.master.canvas.bind('<Motion>', self.mouseMove)
        self.master.canvas.bind('<Button-1>', self.leftButtonClick)
        self.master.canvas.bind('<ButtonRelease-1>', self.leftButtonRelease)
        self.master.canvas.bind('<Button-2>', lambda _:_)
    
    def render(self) -> None:
        # prepare canvas
        canvas = self.master.canvas
        canvas.delete('all')
        # calculate matrixes
        switchYZ = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])
        trans = buildTranslationMat4(
            -View3d.CANVAS_W // 2,
            -View3d.TOP_LEN * 0.618,
            -(View3d.NEAR_LEN + View3d.CANVAS_H))
        project = buildProjectionMat4(
            View3d.NEAR_LEN, View3d.FAR_LEN,
            View3d.BOTTOM_LEN, View3d.TOP_LEN,
            View3d.LEFT_LEN, View3d.RIGHT_LEN
        )
        # iterate lots
        meshes = list()
        rows, cols = self.master.LOT_ROWS, self.master.LOT_COLS
        for row, col in ((i, j) for i in range(rows) for j in range(cols)):
            lot = self.master.grid.lots[row][col]
            bodyMesh = [[
                project.dot(trans.dot(switchYZ.dot(v))) for v in surface
            ] for surface in lot.bodyMesh(
                View3d.VIEW_ANGLE,
                (View3d.CANVAS_W // 2, View3d.CANVAS_H // 2)
            )]
            # project back to canvas
            meshes.extend([(
                [(
                    -x / w * (View3d.CANVAS_W // 2) + View3d.CANVAS_W // 2,
                    y / w * (View3d.CANVAS_H // 2) + View3d.BOTTOM_LEN
                ) for (x, y, _, w) in surface],
                sum(z / w for (_, _, z, w) in surface) / len(surface),
                lot.population, lot.color
            ) for surface in bodyMesh])
        # render
        meshes.sort(key=lambda x: x[1])
        for (v1, v2, v3, v4), _, population, color in meshes:
            canvas.create_polygon(
                *v1, *v2, *v3, *v4,
                fill=color, width=1,
                outline='black' if population < lot.POPULATION_MAX * 0.618 else 'grey'
            )

    def mouseMove(self, event: tk.Event) -> None:
        self.master.infoLabel.set(f'mouse at {event.x}, {event.y}\nview angle is {degrees(View3d.VIEW_ANGLE):.2f}')
    
    def leftButtonClick(self, event: tk.Event) -> None:
        self.leftClickPos = (event.x, event.y)

    def leftButtonRelease(self, event: tk.Event) -> None:
        prevX, prevY = self.leftClickPos
        currX, currY = event.x, event.y
        # update view angle basing on horizontal distance
        absRadian = distance((prevX, 0), (currX, 0)) / (View3d.CANVAS_W // 2)
        signX = 1 if currX > prevX else -1
        View3d.VIEW_ANGLE = (View3d.VIEW_ANGLE + signX * absRadian) % 6.28
        # update focus basing on vertical distance
        absDis = distance((0, prevY), (0, currY))
        signY = 1 if currY > prevY else -1
        View3d.NEAR_LEN = min(max(View3d.NEAR_LEN + 5 * signY * absDis, 1600), 8000)
        View3d.FAR_LEN = View3d.NEAR_LEN + max(View3d.CANVAS_W, View3d.CANVAS_H)
        # update info
        self.master.infoLabel.set(f'mouse at {currX}, {currY}\nview angle is {degrees(View3d.VIEW_ANGLE):.2f}')
        # rerender canvas
        self.render()
