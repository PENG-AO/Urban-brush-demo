# lot

from collections import namedtuple

from src.sec import Sec
from src.util import buildRotationMat4, buildTranslationMat4, extend2homo

class Lot(object):

    LOT_MARGIN = 5
    LOT_SIZE = 0
    Info = namedtuple('Info', ['id', 'x', 'y'])
    POPULATION_MAX = 255

    def __init__(self, grid, id: tuple, x: int, y: int) -> None:
        self.grid = grid
        self.info = Lot.Info(id, x, y)
        self.population = 0
        self.buffer = 0
    
    def prepareBuffer(self, amount: int) -> None:
        delta = self.population * amount // 100
        self.population -= delta
        self.buffer += delta
    
    def restoreBuffer(self) -> None:
        self.population += self.buffer
        self.buffer = 0

    @staticmethod
    def transfer(srcLot, tarLot) -> tuple:
        delta = min(srcLot.buffer, Lot.POPULATION_MAX - tarLot.population)
        srcLot.buffer -= delta
        tarLot.population += delta
        return (srcLot.buffer == 0, tarLot.population == Lot.POPULATION_MAX)

    @property
    def bodyRect(self) -> tuple:
        nwx = self.info.x + Lot.LOT_MARGIN,
        nwy = self.info.y + Lot.LOT_MARGIN,
        sex = self.info.x + Lot.LOT_SIZE - Lot.LOT_MARGIN - 1,
        sey = self.info.y + Lot.LOT_SIZE - Lot.LOT_MARGIN - 1
        return (nwx, nwy, sex, sey)
    
    @property
    def roadRect(self) -> list:
        # fetch info
        id = self.info.id
        x, y = self.info.x, self.info.y
        size = Lot.LOT_SIZE
        # build list
        roadList = list()
        if state := self.grid.isRoad(id, 'e'):
            roadList.append(((x + size - 1, y, x + size - 1, y + size - 1), state == Sec.FOCUSED))
        if state := self.grid.isRoad(id, 'n'):
            roadList.append(((x, y, x + size - 1, y), state == Sec.FOCUSED))
        if state := self.grid.isRoad(id, 'w'):
            roadList.append(((x, y, x, y + size - 1), state == Sec.FOCUSED))
        if state := self.grid.isRoad(id, 's'):
            roadList.append(((x, y + size - 1, x + size - 1, y + size - 1), state == Sec.FOCUSED))
        return roadList

    @property
    def buildingHeight(self) -> int:
        return 2 * Lot.LOT_SIZE * self.population // Lot.POPULATION_MAX

    @property
    def topMesh(self) -> list:
        x, y = self.info.x, self.info.y
        margin, size = Lot.LOT_MARGIN, Lot.LOT_SIZE
        return [
            (x + margin, y + margin, self.buildingHeight),
            (x + size - margin - 1, y + margin, self.buildingHeight),
            (x + size - margin - 1, y + size - margin - 1, self.buildingHeight),
            (x + margin, y + size - margin - 1, self.buildingHeight)
        ]
    
    @property
    def frontMesh(self) -> list:
        x, y = self.info.x, self.info.y
        margin, size = Lot.LOT_MARGIN, Lot.LOT_SIZE
        return [
            (x + margin, y + size - margin - 1, 0),
            (x + size - margin - 1, y + size - margin - 1, 0),
            (x + size - margin - 1, y + size - margin - 1, self.buildingHeight),
            (x + margin, y + size - margin - 1, self.buildingHeight)
        ]
    
    @property
    def backMesh(self) -> list:
        x, y = self.info.x, self.info.y
        margin, size = Lot.LOT_MARGIN, Lot.LOT_SIZE
        return [
            (x + margin, y + margin, 0),
            (x + size - margin - 1, y + margin, 0),
            (x + size - margin - 1, y + margin, self.buildingHeight),
            (x + margin, y + margin, self.buildingHeight)
        ]
    
    @property
    def leftMesh(self) -> list:
        x, y = self.info.x, self.info.y
        margin, size = Lot.LOT_MARGIN, Lot.LOT_SIZE
        return [
            (x + margin, y + margin, 0),
            (x + margin, y + size - margin -1, 0),
            (x + margin, y + size - margin -1, self.buildingHeight),
            (x + margin, y + margin, self.buildingHeight)
        ]
    
    @property
    def rightMesh(self) -> list:
        x, y = self.info.x, self.info.y
        margin, size = Lot.LOT_MARGIN, Lot.LOT_SIZE
        return [
            (x + size - margin - 1, y + margin, 0),
            (x + size - margin - 1, y + size - margin - 1, 0),
            (x + size - margin - 1, y + size - margin - 1, self.buildingHeight),
            (x + size - margin - 1, y + margin, self.buildingHeight)
        ]

    def mesh(self, viewAngle: float, center: tuple, showLot: bool, showRoad: bool) -> list:
        # build mesh lists
        meshes = list()
        if showLot: meshes.extend([self.leftMesh, self.rightMesh, self.frontMesh, self.backMesh, self.topMesh])
        if showRoad: meshes.extend([[
            (x1, y1, 0), (x1, y1, 0), (x2, y2, 0), (x2, y2, 0)
        ] for (x1, y1, x2, y2), _ in self.roadRect])
        # rotate around center
        transAway = buildTranslationMat4(-center[0], -center[1], 0)
        rotate = buildRotationMat4(-viewAngle)
        transBack = buildTranslationMat4(center[0], center[1], 0)
        return [[
            transBack.dot(rotate.dot(transAway.dot(v))) for v in surface
        ] for surface in extend2homo(meshes)]

    @property
    def center(self) -> tuple:
        return (self.info.x + Lot.LOT_SIZE // 2, self.info.y + Lot.LOT_SIZE // 2)

    @property
    def color(self) -> str:
        grey = hex(255 - self.population)[2:].zfill(2)
        return f'#{grey}{grey}{grey}'
