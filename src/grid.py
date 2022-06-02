# grid

from random import randint, choice
from collections import deque

from src.util import distance, flatten
from src.sec import Sec
from src.lot import Lot

class Grid(object):

    def __init__(self, rows: int, cols: int, baseX: int, baseY: int, size: int) -> None:
        self.shape = (rows, cols)
        self.basePos = (baseX, baseY)
        # init lots
        Lot.LOT_SIZE = size
        self.lots = [[
            Lot(self, (row, col), baseX + col * size, baseY + row * size) for col in range(cols)
        ] for row in range(rows)]
        # init secs
        self.secs = [[
            Sec((row, col), baseX + col * size, baseY + row * size) for col in range(cols + 1)
        ] for row in range(rows + 1)]
    
    def getSecsByDistance(self, base: tuple, dis: float) -> list:
        return [sec for sec in flatten(self.secs) if distance(base, sec.pos) < dis]
    
    def getLotsByDistance(self, base: tuple, minDis: float, maxDis: float) -> deque:
        lotList = [(lot, d) for lot in flatten(self.lots) if minDis < (d := distance(base, lot.center)) < maxDis]
        lotList.sort(key=lambda x: x[1])
        return deque([x[0] for x in lotList])
    
    def getNearestLot(self, base: tuple) -> Lot:
        return min([(lot, distance(base, lot.center)) for lot in flatten(self.lots)], key=lambda x: x[1])[0]
    
    def getRoadsByDistance(self, base: tuple, dis: float) -> list:
        secList = [sec for sec in flatten(self.secs) if distance(base, sec.pos) < dis]
        return [(secA, secB) for secA in secList for secB in secList]

    def keepSecsConsistent(self) -> None:
        rows, cols = self.shape
        for row, col in ((i, j) for i in range(1, rows) for j in range(1, cols)):
            sec = self.secs[row][col]
            if sec.e: Sec.set2(sec, self.secs[row][col + 1], Sec.ACTIVE, connection=Sec.HOR_CONNECTED)
            if sec.n: Sec.set2(self.secs[row - 1][col], sec, Sec.ACTIVE, connection=Sec.VER_CONNECTED)
            if sec.w: Sec.set2(self.secs[row][col - 1], sec, Sec.ACTIVE, connection=Sec.HOR_CONNECTED)
            if sec.s: Sec.set2(sec, self.secs[row + 1][col], Sec.ACTIVE, connection=Sec.VER_CONNECTED)

    def keepRoadsConsistent(self) -> None:
        valid = True
        rows, cols = self.shape
        # restore intersections on the border
        for row in range(rows):
            Sec.set2(self.secs[row][0], self.secs[row + 1][0], Sec.ACTIVE, connection=Sec.VER_CONNECTED)
            Sec.set2(self.secs[row][-1], self.secs[row + 1][-1], Sec.ACTIVE, connection=Sec.VER_CONNECTED)
        for col in range(cols):
            Sec.set2(self.secs[0][col], self.secs[0][col + 1], Sec.ACTIVE, connection=Sec.HOR_CONNECTED)
            Sec.set2(self.secs[-1][col], self.secs[-1][col + 1], Sec.ACTIVE, connection=Sec.HOR_CONNECTED)
        # check inner intersections
        for row, col in ((i, j) for i in range(1, rows) for j in range(1, cols)):
            sec = self.secs[row][col]
            if int(sec) != 1: continue
            # check every direction
            if sec.e: Sec.set2(sec, self.secs[row][col + 1], Sec.BLOCKED, connection=Sec.HOR_CONNECTED)
            if sec.n: Sec.set2(self.secs[row - 1][col], sec, Sec.BLOCKED, connection=Sec.VER_CONNECTED)
            if sec.w: Sec.set2(self.secs[row][col - 1], sec, Sec.BLOCKED, connection=Sec.HOR_CONNECTED)
            if sec.s: Sec.set2(sec, self.secs[row + 1][col], Sec.BLOCKED, connection=Sec.VER_CONNECTED)
            # set flag to invalid
            valid = False
        # loop until all valid
        if not valid: self.keepRoadsConsistent()
    
    def repulseLots(self, base: tuple, innerRadius: int, outerRadius: int, amount: int) -> None:
        innerLots = self.getLotsByDistance(base, 0, innerRadius)
        outerLots = self.getLotsByDistance(base, innerRadius, outerRadius)
        # prepare buffer
        for lot in innerLots: lot.prepareBuffer(amount)
        # transfer population
        while len(innerLots) and len(outerLots):
            srcLot, tarLot = innerLots.popleft(), outerLots.popleft()
            srcDone, tarDone = Lot.transfer(srcLot, tarLot)
            if not srcDone: innerLots.append(srcLot)
            if not tarDone: outerLots.append(tarLot)
        # restore buffer
        for lot in innerLots: lot.restoreBuffer()

    def attractLots(self, base: tuple, innerRadius: int, outerRadius: int, amount: int) -> None:
        innerLots = self.getLotsByDistance(base, 0, innerRadius)
        outerLots = self.getLotsByDistance(base, innerRadius, outerRadius)
        # prepare buffer
        for lot in outerLots: lot.prepareBuffer(amount)
        # transfer population
        while len(innerLots) and len(outerLots):
            srcLot, tarLot = outerLots.popleft(), innerLots.popleft()
            srcDone, tarDone = Lot.transfer(srcLot, tarLot)
            if not srcDone: outerLots.append(srcLot)
            if not tarDone: innerLots.append(tarLot)
        # restore buffer
        for lot in outerLots: lot.restoreBuffer()
    
    def dragLots(self, innerBase: tuple, outerBase: tuple, innerRadius: int, outerRadius: int, amount: int) -> None:
        innerLots = self.getLotsByDistance(innerBase, 0, innerRadius)
        outerLots = self.getLotsByDistance(outerBase, 0, outerRadius)
        # prepare buffer
        for lot in innerLots: lot.prepareBuffer(amount)
        # transfer population
        while len(innerLots) and len(outerLots):
            srcLot, tarLot = innerLots.popleft(), outerLots.popleft()
            srcDone, tarDone = Lot.transfer(srcLot, tarLot)
            if not srcDone: innerLots.append(srcLot)
            if not tarDone: outerLots.append(tarLot)
        # restore buffer
        for lot in innerLots: lot.restoreBuffer()

    def markRoads(self, base: tuple) -> list:
        secPairs = self.getRoadsByDistance(base, Lot.LOT_SIZE / 1.414)
        for secA, secB in secPairs:
            Sec.set2(secA, secB, Sec.FOCUSED)
        return secPairs
    
    def breakRoads(self, base: tuple, radius: int, roadList: list) -> None:
        roadList = roadList or self.getRoadsByDistance(base, radius)
        for secA, secB in roadList:
            Sec.set2(secA, secB, Sec.BLOCKED)
        self.keepRoadsConsistent()

    def connectRoads(self, base: tuple, innerRadius: int, outerRadius: int, roadList: list) -> None:
        if roadList:
            # connect
            for secA, secB in roadList:
                Sec.set2(secA, secB, Sec.ACTIVE)
        else:
            # rebuild
            styleList = [sec.get() for sec in self.getSecsByDistance(base, outerRadius)]
            for sec in self.getSecsByDistance(base, innerRadius):
                sec.set(*choice(styleList))
            self.keepSecsConsistent()
        self.keepRoadsConsistent()

    def load(self, infoDict: dict) -> None:
        # set lots
        for row, info in enumerate(infoDict['lots']):
            for col, population in enumerate(info):
                self.lots[row][col].population = population
        # set secs
        for row, info in enumerate(infoDict['secs']):
            for col, dir in enumerate(info):
                self.secs[row][col].set(*dir)

    def dump(self) -> None:
        infoDict = dict()
        infoDict['lots'] = [[col.population for col in row] for row in self.lots]
        infoDict['secs'] = [[col.get() for col in row] for row in self.secs]
        return infoDict

    def randomize(self) -> None:
        rows, cols = self.shape
        # randomize population
        for row, col in ((i, j) for i in range(rows) for j in range(cols)):
            self.lots[row][col].population = randint(0, Lot.POPULATION_MAX)
        # set all intersections back to all-connected
        for row, col in ((i, j) for i in range(rows + 1) for j in range(cols + 1)):
            self.secs[row][col].set(Sec.ACTIVE, Sec.ACTIVE, Sec.ACTIVE, Sec.ACTIVE)
        # randomize horizontal roads
        for row, col in ((i, j) for i in range(1, rows) for j in range(cols)):
            if not bool(randint(0, 100) > 30):
                Sec.set2(self.secs[row][col], self.secs[row][col + 1], Sec.BLOCKED, connection=Sec.HOR_CONNECTED)
        # randomize vertical roads
        for row, col in ((i, j) for i in range(rows) for j in range(1, cols)):
            if not bool(randint(0, 100) > 30):
                Sec.set2(self.secs[row][col], self.secs[row + 1][col], Sec.BLOCKED, connection=Sec.VER_CONNECTED)
        # keep consistency
        self.keepRoadsConsistent()
    
    def isRoad(self, lotId: tuple, direction: str) -> int:
        row, col = lotId
        if direction == 'e':
            return Sec.get2(self.secs[row][col + 1], self.secs[row + 1][col + 1], connection=Sec.VER_CONNECTED)
        if direction == 'n':
            return Sec.get2(self.secs[row][col], self.secs[row][col + 1], connection=Sec.HOR_CONNECTED)
        if direction == 'w':
            return Sec.get2(self.secs[row][col], self.secs[row + 1][col], connection=Sec.VER_CONNECTED)
        if direction == 's':
            return Sec.get2(self.secs[row + 1][col], self.secs[row + 1][col + 1], connection=Sec.HOR_CONNECTED)
        return Sec.BLOCKED
