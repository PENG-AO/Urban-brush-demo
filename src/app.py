# app

import tkinter as tk
from tkinter import filedialog
import pickle

from src.grid import Grid
from src.view2d import View2d
from src.view3d import View3d

class App(object):

    CANVAS_H, CANVAS_W = 800, 800
    LOT_ROWS, LOT_COLS = 20, 20
    LOT_SIZE = min(CANVAS_H // LOT_ROWS, CANVAS_W // LOT_COLS)

    BRUSH_TYPE_REPULSE = 0
    BRUSH_TYPE_ATTRACT = 1
    BRUSH_TYPE_DRAG    = 2
    BRUSH_TYPE_BREAK   = 3
    BRUSH_TYPE_CONNECT = 4

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title('urban brush demo')
        self.root.resizable(0, 0)

        self.grid = Grid(App.LOT_ROWS, App.LOT_COLS, 3, 3, App.LOT_SIZE)
        self.view2d = View2d(self)
        self.view3d = View3d(self)

        self.show3d = tk.BooleanVar(value=False)
        self.showLot = tk.BooleanVar(value=True)
        self.showRoad = tk.BooleanVar(value=True)

        self.brushType = tk.IntVar(value=-1)
        self.innerRadius = tk.IntVar(value=3)
        self.outerRadius = tk.IntVar(value=6)
        self.brushAmount = tk.IntVar(value=20)

        self.infoLabel = tk.StringVar('')

        self.createControlPad(self.root)
        self.createCanvas(self.root)
    
    def createControlPad(self, master) -> None:
        controlPad = tk.Frame(master)
        self.createGlobalPad(controlPad)
        self.createDisplayPad(controlPad)
        self.createLayoutPad(controlPad)
        self.createBrushTypePad(controlPad)
        self.createBrushAttrPad(controlPad)
        tk.Label(controlPad, textvariable=self.infoLabel).pack()
        controlPad.pack(anchor='n', side=tk.LEFT, padx=10, pady=10)
    
    def createGlobalPad(self, master) -> None:
        globalPad = tk.LabelFrame(master, text='global')
        tk.Button(globalPad, text='load', command=self.loadButton).pack(fill=tk.X)
        tk.Button(globalPad, text='save', command=self.saveButton).pack(fill=tk.X)
        tk.Button(globalPad, text='rand', command=self.randButton).pack(fill=tk.X)
        globalPad.pack(fill=tk.X, padx=5, pady=5)
    
    def createDisplayPad(self, master) -> None:
        displayPad = tk.LabelFrame(master, text='display')
        tk.Radiobutton(displayPad, text='2d mode', variable=self.show3d, value=False, command=self.renderCanvas).pack(anchor='w')
        tk.Radiobutton(displayPad, text='3d mode', variable=self.show3d, value=True, command=self.renderCanvas).pack(anchor='w')
        displayPad.pack(fill=tk.X, padx=5, pady=5)

    def createLayoutPad(self, master) -> None:
        layoutPad = tk.LabelFrame(master, text='layout')
        tk.Checkbutton(layoutPad, text='lots', variable=self.showLot, command=self.renderCanvas).pack(anchor='w')
        tk.Checkbutton(layoutPad, text='roads', variable=self.showRoad, command=self.renderCanvas).pack(anchor='w')
        layoutPad.pack(fill=tk.X, padx=5, pady=5)
    
    def createBrushTypePad(self, master) -> None:
        brushTypePad = tk.LabelFrame(master, text='brush type')
        tk.Radiobutton(brushTypePad, text='repulse', variable=self.brushType, value=App.BRUSH_TYPE_REPULSE).pack(anchor='w')
        tk.Radiobutton(brushTypePad, text='attract', variable=self.brushType, value=App.BRUSH_TYPE_ATTRACT).pack(anchor='w')
        tk.Radiobutton(brushTypePad, text='drag', variable=self.brushType, value=App.BRUSH_TYPE_DRAG).pack(anchor='w')
        tk.Radiobutton(brushTypePad, text='break', variable=self.brushType, value=App.BRUSH_TYPE_BREAK).pack(anchor='w')
        tk.Radiobutton(brushTypePad, text='connect', variable=self.brushType, value=App.BRUSH_TYPE_CONNECT).pack(anchor='w')
        brushTypePad.pack(fill=tk.X, padx=5, pady=5)
    
    def createBrushAttrPad(self, master) -> None:
        brushAttrPad = tk.LabelFrame(master, text='brush attribute')
        tk.Scale(
            brushAttrPad, label='inner radius', variable=self.innerRadius,
            from_=1, to=max(App.LOT_ROWS, App.LOT_COLS), orient=tk.HORIZONTAL, length=200
        ).pack()
        tk.Scale(
            brushAttrPad, label='outer radius', variable=self.outerRadius,
            from_=1, to=max(App.LOT_ROWS, App.LOT_COLS), orient=tk.HORIZONTAL, length=200
        ).pack()
        tk.Scale(
            brushAttrPad, label='brush amount', variable=self.brushAmount,
            from_=0, to=100, resolution=5, orient=tk.HORIZONTAL, length=200
        ).pack()
        brushAttrPad.pack(fill=tk.X, padx=5, pady=5)

    def createCanvas(self, master) -> None:
        # (3, 3) -- (802, 802)
        size = max(App.CANVAS_H, App.CANVAS_W)
        self.canvas = tk.Canvas(master, bg='white', height=size, width=size)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.view2d.activate()

    def renderCanvas(self) -> None:
        view = self.view3d if self.show3d.get() else self.view2d
        view.activate()
        view.render()
    
    def loadButton(self) -> None:
        if filename := filedialog.askopenfilename(filetypes=[('urban brush file', '.ub')], initialdir='.'):
            with open(filename, 'rb') as f:
                self.grid.load(pickle.load(f))
            self.renderCanvas()

    def saveButton(self) -> None:
        if filename := filedialog.asksaveasfilename(filetypes=[('urban brush file', '.ub')], initialdir='.'):
            with open(filename, 'wb') as f:
                pickle.dump(self.grid.dump(), f)

    def randButton(self) -> None:
        self.grid.randomize()
        self.renderCanvas()

    def run(self) -> None:
        self.root.mainloop()
