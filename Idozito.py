import pygame as pg
class Idozito:
    def __init__(self, ido = 0):
        self.start = pg.time.get_ticks()
        self.ido = 1000*ido if ido > 0 else 0 # az időzítő ideje (eddig számol)

    def s_start(self, start_tick):
        self.start = int(start_tick)
    
    def lejart(self):
        if ((pg.time.get_ticks() - self.start) > self.ido):
            return True
        else:
            return False

    def maradek_ido(self, ms = False):
        adat = (pg.time.get_ticks() - self.start)
        return str(adat//1000) if ms == False else str(adat)