# app

import tkinter as tk
from tkinter import ttk
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
        self.showAnimation = tk.BooleanVar(value=False)

        self.brushType = tk.IntVar(value=-1)
        self.innerRadius = tk.IntVar(value=3)
        self.outerRadius = tk.IntVar(value=6)
        self.brushAmount = tk.IntVar(value=20)

        self.infoLabel = tk.StringVar(value='')
        self.innerRadiusLabel = tk.StringVar(value=f'inner radius: {self.innerRadius.get()}')
        self.outerRadiusLabel = tk.StringVar(value=f'outer radius: {self.outerRadius.get()}')
        self.brushAmountLabel = tk.StringVar(value=f'brush amount: {self.brushAmount.get()}%')

        self.createControlPad(self.root)
        self.createCanvas(self.root)
    
    def createControlPad(self, master) -> None:
        controlPad = ttk.Frame(master)
        self.createGlobalPad(controlPad)
        self.createDisplayPad(controlPad)
        self.createBrushPad(controlPad)
        ttk.Label(controlPad, textvariable=self.infoLabel).pack()
        controlPad.pack(anchor='n', side=tk.LEFT, padx=10, pady=10)
    
    def createGlobalPad(self, master) -> None:
        globalPad = ttk.Labelframe(master, text='global')
        ttk.Button(globalPad, text='load', command=self.loadButton).pack(fill=tk.X)
        ttk.Button(globalPad, text='save', command=self.saveButton).pack(fill=tk.X)
        ttk.Button(globalPad, text='rand', command=self.randButton).pack(fill=tk.X)
        globalPad.pack(fill=tk.X, padx=5, pady=5)
    
    def createDisplayPad(self, master) -> None:
        displayPad = ttk.Labelframe(master, text='display')
        ttk.Radiobutton(displayPad, text='2d mode', variable=self.show3d, value=False, command=self.renderCanvas).pack(anchor=tk.W)
        ttk.Radiobutton(displayPad, text='3d mode', variable=self.show3d, value=True, command=self.renderCanvas).pack(anchor=tk.W)
        ttk.Separator(displayPad, orient=tk.HORIZONTAL).pack(fill=tk.BOTH, padx=5, pady=5)
        ttk.Checkbutton(displayPad, text='lots', variable=self.showLot, command=self.renderCanvas).pack(anchor=tk.W)
        ttk.Checkbutton(displayPad, text='roads', variable=self.showRoad, command=self.renderCanvas).pack(anchor=tk.W)
        ttk.Separator(displayPad, orient=tk.HORIZONTAL).pack(fill=tk.BOTH, padx=5, pady=5)
        ttk.Checkbutton(displayPad, text='animated', variable=self.showAnimation).pack(anchor=tk.W)
        displayPad.pack(fill=tk.X, padx=5, pady=5)
    
    def createBrushPad(self, master) -> None:
        brushPad = ttk.Labelframe(master, text='brushes')
        ttk.Radiobutton(brushPad, text='none', variable=self.brushType, value=-1).pack(anchor=tk.W)
        ttk.Radiobutton(brushPad, text='repulse', variable=self.brushType, value=App.BRUSH_TYPE_REPULSE).pack(anchor=tk.W)
        ttk.Radiobutton(brushPad, text='attract', variable=self.brushType, value=App.BRUSH_TYPE_ATTRACT).pack(anchor=tk.W)
        ttk.Radiobutton(brushPad, text='drag', variable=self.brushType, value=App.BRUSH_TYPE_DRAG).pack(anchor=tk.W)
        ttk.Radiobutton(brushPad, text='break', variable=self.brushType, value=App.BRUSH_TYPE_BREAK).pack(anchor=tk.W)
        ttk.Radiobutton(brushPad, text='connect', variable=self.brushType, value=App.BRUSH_TYPE_CONNECT).pack(anchor=tk.W)
        ttk.Separator(brushPad, orient=tk.HORIZONTAL).pack(fill=tk.BOTH, padx=5, pady=5)
        ttk.Label(brushPad, textvariable=self.innerRadiusLabel).pack(anchor=tk.W)
        ttk.Scale(
            brushPad, variable=self.innerRadius, from_=1, to=max(App.LOT_ROWS, App.LOT_COLS), orient=tk.HORIZONTAL, length=200,
            command=lambda _: self.innerRadiusLabel.set(f'inner radius: {self.innerRadius.get()}')
        ).pack(padx=5)
        ttk.Label(brushPad, textvariable=self.outerRadiusLabel).pack(anchor=tk.W)
        ttk.Scale(
            brushPad, variable=self.outerRadius, from_=1, to=max(App.LOT_ROWS, App.LOT_COLS), orient=tk.HORIZONTAL, length=200,
            command=lambda _: self.outerRadiusLabel.set(f'outer radius: {self.outerRadius.get()}')
        ).pack(padx=5)
        ttk.Label(brushPad, textvariable=self.brushAmountLabel).pack(anchor=tk.W)
        ttk.Scale(
            brushPad, variable=self.brushAmount, from_=0, to=100, orient=tk.HORIZONTAL, length=200,
            command=lambda _: self.brushAmountLabel.set(f'brush amount: {self.brushAmount.get()}%')
        ).pack(padx=5)
        brushPad.pack(fill=tk.X, padx=5, pady=5)
    
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
