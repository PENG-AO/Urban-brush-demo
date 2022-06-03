# 2d view

import tkinter as tk

class View2d(object):

    def __init__(self, master) -> None:
        self.master = master
        self.leftClickPos = None
        self.rightClickPos = None
        self.roadBuffer = list()

    def activate(self) -> None:
        self.master.canvas.bind('<Motion>', self.mouseMove)
        self.master.canvas.bind('<Button-1>', self.leftClick)
        self.master.canvas.bind('<ButtonRelease-1>', lambda _:_)
        self.master.canvas.bind('<Button-2>', self.rightClick)

    def render(self) -> None:
        canvas = self.master.canvas
        canvas.delete('all')
        rows, cols = self.master.LOT_ROWS, self.master.LOT_COLS
        for row, col in ((i, j) for i in range(rows) for j in range(cols)):
            lot = self.master.grid.lots[row][col]
            if self.master.showLot.get():
                canvas.create_rectangle(lot.bodyRect, fill=lot.color, width=0)
            if self.master.showRoad.get():
                for roadRect, focused in lot.roadRect:
                    canvas.create_rectangle(roadRect, fill='magenta' if focused else 'black', width=0)
    
    def mouseMove(self, event: tk.Event) -> None:
        self.master.infoLabel.set(f'mouse at {event.x}, {event.y}')
        brushType = self.master.brushType.get()
        canvas = self.master.canvas
        if brushType < 0: return
        # plot the inner circle
        canvas.delete('innerCircle')
        innerRadius = self.master.innerRadius.get() * self.master.LOT_SIZE
        x, y = self.rightClickPos if brushType == self.master.BRUSH_TYPE_DRAG and self.rightClickPos else (event.x, event.y)
        canvas.create_oval(x - innerRadius, y - innerRadius, x + innerRadius, y + innerRadius, outline='#3583f7', width=3, dash=(3, 6), tags='innerCircle')
        # plot the outer circle
        canvas.delete('outerCircle')
        if brushType == self.master.BRUSH_TYPE_BREAK: return
        outerRadius = self.master.outerRadius.get() * self.master.LOT_SIZE
        x, y = (event.x, event.y)
        canvas.create_oval(x - outerRadius, y - outerRadius, x + outerRadius, y + outerRadius, outline='#3583f7', width=3, dash=(3, 9), tags='outerCircle')
    
    def leftClick(self, event: tk.Event) -> None:
        self.leftClickPos = (event.x, event.y)
        brushType = self.master.brushType.get()
        if brushType == self.master.BRUSH_TYPE_REPULSE:
            self.master.grid.repulseLots(
                self.leftClickPos,
                self.master.innerRadius.get() * self.master.LOT_SIZE,
                self.master.outerRadius.get() * self.master.LOT_SIZE,
                self.master.brushAmount.get()
            )
        elif brushType == self.master.BRUSH_TYPE_ATTRACT:
            self.master.grid.attractLots(
                self.leftClickPos,
                self.master.innerRadius.get() * self.master.LOT_SIZE,
                self.master.outerRadius.get() * self.master.LOT_SIZE,
                self.master.brushAmount.get()
            )
        elif brushType == self.master.BRUSH_TYPE_DRAG:
            if self.rightClickPos:
                self.master.grid.dragLots(
                    self.rightClickPos,
                    self.leftClickPos,
                    self.master.innerRadius.get() * self.master.LOT_SIZE,
                    self.master.outerRadius.get() * self.master.LOT_SIZE,
                    self.master.brushAmount.get()
                )
        elif brushType == self.master.BRUSH_TYPE_BREAK:
            self.master.grid.breakRoads(
                self.leftClickPos,
                self.master.innerRadius.get() * self.master.LOT_SIZE,
                self.roadBuffer
            )
        elif brushType == self.master.BRUSH_TYPE_CONNECT:
            self.master.grid.connectRoads(
                self.leftClickPos,
                self.master.innerRadius.get() * self.master.LOT_SIZE,
                self.master.outerRadius.get() * self.master.LOT_SIZE,
                self.roadBuffer
            )
        self.roadBuffer.clear()
        self.render()
        self.rightClickPos = None

    def rightClick(self, event: tk.Event) -> None:
        self.rightClickPos = (event.x, event.y)
        brushType = self.master.brushType.get()
        if brushType in (self.master.BRUSH_TYPE_BREAK, self.master.BRUSH_TYPE_CONNECT):
            self.roadBuffer.extend(self.master.grid.markRoads(self.rightClickPos))
        else:
            lot = self.master.grid.getNearestLot(self.rightClickPos)
            self.master.infoLabel.set(f'population of Lot{lot.info.id} is {lot.population}')
        self.render()
