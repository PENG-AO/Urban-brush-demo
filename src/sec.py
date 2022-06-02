# intersection

from collections import namedtuple

class Sec(object):

    BLOCKED, ACTIVE, FOCUSED = 0, 1, 2
    NOT_CONNECTED, HOR_CONNECTED, VER_CONNECTED = 0, 1, 2
    Info = namedtuple('Info', ['id', 'x', 'y'])

    def __init__(self, id: tuple, x: int, y: int) -> None:
        self.set(Sec.ACTIVE, Sec.ACTIVE, Sec.ACTIVE, Sec.ACTIVE)
        self.info = Sec.Info(id, x, y)
    
    def set(self, e: int, n: int, w: int, s: int) -> None:
        self.e, self.n, self.w, self.s = e, n, w, s
    
    def get(self) -> tuple:
        return (self.e, self.n, self.w, self.s)
    
    @staticmethod
    def comb(secA, secB) -> tuple:
        hor = secA.info.id[1] - secB.info.id[1]
        ver = secA.info.id[0] - secB.info.id[0]
        # horizontally connected and A on the left
        if hor == -1 and ver == 0:
            return (secA, secB, Sec.HOR_CONNECTED)
        # horizontally connected and A on the right
        if hor == 1 and ver == 0:
            return (secB, secA, Sec.HOR_CONNECTED)
        # vertically connected and A on the top
        if hor == 0 and ver == -1:
            return (secA, secB, Sec.VER_CONNECTED)
        # vertically connected and A on the bottom
        if hor == 0 and ver == 1:
            return (secB, secA, Sec.VER_CONNECTED)
        # not connected
        return (secA, secB, Sec.NOT_CONNECTED)
    
    @staticmethod
    def set2(secA, secB, state: int, connection: int=None) -> None:
        # comb the secs and get the connection
        if connection is None:
            secA, secB, connection = Sec.comb(secA, secB)
        # set the 2 secs with the given state
        if connection == Sec.HOR_CONNECTED:
            secA.e = secB.w = state
        elif connection == Sec.VER_CONNECTED:
            secA.s = secB.n = state

    @staticmethod
    def get2(secA, secB, connection: int=None) -> int:
        # comb the secs and get the connection
        if connection is None:
            secA, secB, connection = Sec.comb(secA, secB)
        # get the state of the 2 secs
        if connection == Sec.HOR_CONNECTED:
            return secA.e & secB.w
        elif connection == Sec.VER_CONNECTED:
            return secA.s & secB.n
        else:
            return Sec.BLOCKED

    @property
    def pos(self) -> tuple:
        return (self.info.x, self.info.y)
    
    def __int__(self) -> int:
        return sum(self.get())
    
    def __repr__(self) -> str:
        return f'Sec{self.info.id}'
