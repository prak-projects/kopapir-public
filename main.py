'''
Kőpapír

A projekt bemutatói, és oktatási célból jött létre. Az MIT Licensz feltételei szerint publikálható (lsd.: LICENSE).

(c) 2022
Preil Ákos [preil@prak.hu]
Komlósi Ádám [komlosi@prak.hu]
Talabér Levente [levi@prak.hu]
Csuhaj Zsolt
Google (mediapipe modul az Apache 2.0 alatt)
'''
from Tracker import Tracker
from Log import Log
from Eszkozok import Eszkozok
from Idozito import Idozito
import pygame as pg
from Kivetelek import *
import random


# Fatális hiba esetén
LOG = Log()
def crash(e):
    LOG.logInfo(3, "Hiba: " + str(e))
    pg.quit()
    exit()

class JatekAblak:
    def __init__(self):
        self.KEPERNYOMERET = pg.display.Info()
        self.ABLAKMERET = (self.KEPERNYOMERET.current_w, self.KEPERNYOMERET.current_h)
        self.ABLAK = pg.display.set_mode((self.ABLAKMERET[0], self.ABLAKMERET[1]))
        self.ORA = pg.time.Clock()
        self.START_IDO = pg.time.get_ticks()
        pg.display.set_caption("Kőpapír")

class JatekFolyamat:
    def __init__(self):
        self.rot = 0
        # Log inicializáció
        self.LOG = LOG
        # PyGame inicializáció
        pg.init()
        # Tracker inicializáció
        self.TRACKER = Tracker()
        # Játékablak-vezérlő
        self.JATEKABLAK = JatekAblak()
        # Eszközök betöltés
        self.ESZKOZOK = Eszkozok({
            "ABLAKMERET": self.JATEKABLAK.ABLAKMERET
        })
        pg.display.set_icon(self.ESZKOZOK.ESZKOZOK["logo"]["obj"].obj)
        # Játékállapotok
        self.K_JATEKALLAPOTOK = (
            # Fontos a sorrendbe rendezés
            "varakozas",
            "var_visszasz",
            "jatek",
            "vegeredmeny"
        )
        self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[0]
        self.VISSZASZAMLALOK = {
            "var_marad": Idozito(2), # várakozik, hogy miután egy kéz látható-e ott marad e x ideig
            "var_kpo": Idozito(3), # visszaszámol a k.p.o kezdetéig (3-2-1)
            "var_eredmeny": Idozito(2), # kimutatja az eredményt x ideig
            "mutat_kamera": Idozito(2) # mutatja a kamerát a helyes eredményhez
        }
        self.K_VEGEREDMENYEK = {
            0: "Győzelem",
            1: "Vesztettél",
            2: "Döntetlen"
        }
        self.VEGEREDMENYEK = {
            "nyert": 0, #0,1
            "valasztasok": [0,0]
        }
        self.GEP_DONTES = 0
        # Indítás
        self.LOG.logInfo(0, "Folyamat elindult\nKőpapír 2022 - Preil Ákos, Talabér Levente, Komlósi Ádám, Csuhaj Zsolt")
        self.startFolyamat()

    # végeredmény módosítása
    def s_vegeredmeny(self, eredmeny):
        self.VEGEREDMENYEK["nyert"] = eredmeny["nyert"]
        self.VEGEREDMENYEK["valasztasok"] = eredmeny["valasztasok"]
    
    def s_uj_jatek(self):
        self.VEGEREDMENYEK["nyert"] = 0
        self.VEGEREDMENYEK["valasztasok"] = [0,0]
    
    # nyerés eldöntése
    def nyeres(self, kez_gep, kez_jatekos):
        nyero_parok={1:2, 2:3, 3:1} # x üti y
        if kez_jatekos != 0:
            if kez_gep != kez_jatekos:
                if nyero_parok[kez_gep] == kez_jatekos:
                    return 1
                else:
                    return 0
            else:
                return 2
        else:
            return 1

    # Rajzolás
    def rajzol(self):
        ESZKOZOK = self.ESZKOZOK.ESZKOZOK
        # automatikus render
        IGNOR_RENDER = ["kez_"] # ignorált eszközök
        for i in ESZKOZOK.keys():
            for j in IGNOR_RENDER:
                if j not in i:
                    if ESZKOZOK[i]["obj"].lathato == True:
                        if (ESZKOZOK[i]["obj"].ism["x"] or ESZKOZOK[i]["obj"].ism["y"]) > 0:
                            for k in range(ESZKOZOK[i]["obj"].ism["x"]):
                                for v in range(ESZKOZOK[i]["obj"].ism["y"]):
                                    self.JATEKABLAK.ABLAK.blit(
                                        ESZKOZOK[i]["obj"].obj, 
                                        ((ESZKOZOK[i]["obj"].pozicio[0])+(k*ESZKOZOK[i]["obj"].meret[0]), (ESZKOZOK[i]["obj"].pozicio[1])+(v*ESZKOZOK[i]["obj"].meret[1]))
                                    )
                        else:
                            self.JATEKABLAK.ABLAK.blit(ESZKOZOK[i]["obj"].obj, (ESZKOZOK[i]["obj"].pozicio[0], ESZKOZOK[i]["obj"].pozicio[1]))
        # Manuális rajzolás
        # kezek
        kezek = self.ESZKOZOK.KEZEK
        # játékos
        jatekos_kez_str = str(self.TRACKER.statusz) if self.VEGEREDMENYEK["valasztasok"][1] == 0 else str(self.VEGEREDMENYEK["valasztasok"][1])
        self.JATEKABLAK.ABLAK.blit(pg.transform.rotate(ESZKOZOK["kez_"+jatekos_kez_str]["obj"].obj, -90), (
            ESZKOZOK["doboz"]["obj"].pozicio[0]-(ESZKOZOK["kez_0"]["obj"].obj.get_height())/4,
            (self.JATEKABLAK.ABLAKMERET[1]-ESZKOZOK["doboz"]["obj"].meret[1])/1.2
        ))
        # gép
        gep_kez_str = str(self.VEGEREDMENYEK["valasztasok"][0])
        self.JATEKABLAK.ABLAK.blit(pg.transform.flip(pg.transform.rotate(ESZKOZOK["kez_"+gep_kez_str]["obj"].obj, -90), True, False), (
            self.JATEKABLAK.ABLAKMERET[0]-ESZKOZOK["kez_0"]["obj"].obj.get_height()-ESZKOZOK["doboz"]["obj"].pozicio[0]+(ESZKOZOK["kez_0"]["obj"].obj.get_height())/4,
            (self.JATEKABLAK.ABLAKMERET[1]-ESZKOZOK["doboz"]["obj"].meret[1])/1.2
        ))        
        # letterbox rect
        pg.draw.rect(
            self.JATEKABLAK.ABLAK, 
            (20,20,20), 
            pg.Rect(0, 0, (self.JATEKABLAK.ABLAKMERET[0]-ESZKOZOK["doboz"]["obj"].meret[0])/2, self.JATEKABLAK.ABLAKMERET[1])
        )
        pg.draw.rect(
            self.JATEKABLAK.ABLAK, 
            (20,20,20), 
            pg.Rect(self.JATEKABLAK.ABLAKMERET[0]-((self.JATEKABLAK.ABLAKMERET[0]-ESZKOZOK["doboz"]["obj"].meret[0])/2), 0, (self.JATEKABLAK.ABLAKMERET[0]-ESZKOZOK["doboz"]["obj"].meret[0])/2, self.JATEKABLAK.ABLAKMERET[1])
        )
        

    def rajzol_szoveg(self, szoveg, szin=(200,200,200), poz=[0,0], center=False, selfMinus = {"x": False, "y": False}):
        txt = self.ESZKOZOK.JATEK_BT.render(szoveg, False, szin)
        txt_sh = self.ESZKOZOK.JATEK_BT.render(szoveg, False, (5,5,5))
        if center == True:
            poz = [((self.JATEKABLAK.ABLAKMERET[0]-txt.get_width())/2), ((self.JATEKABLAK.ABLAKMERET[1]-txt.get_height())/2)]
        if selfMinus["x"] != False or selfMinus["y"] != False:
            if selfMinus["x"] == True:
                poz[0] = poz[0]-txt.get_width()
            elif selfMinus["y"] == True:
                poz[1] = poz[1]-txt.get_height()
        self.JATEKABLAK.ABLAK.blit(txt_sh, (poz[0]+2, poz[1]+2))
        self.JATEKABLAK.ABLAK.blit(txt, poz)
        


    # Main
    def startFolyamat(self):
        while True:
            # Tracker update
            try:
                self.TRACKER.frissit()
            except NincsKamera:
                crash("Nincs kamerakép")
            except FrameDrop:
                self.LOG.logInfo(2, "Képkocka elejtve")
            # Események keresése
            for esemeny in pg.event.get():
                if esemeny.type == pg.QUIT:
                    # Kilépés
                    self.LOG.logInfo(0, "Folyamatok bezárása")
                    pg.quit()
                    exit()

            # Játéktér rajzolása
            self.rajzol()
            # Ha kéz nem látható
            if self.TRACKER.kameraStill is not None:
                image = self.TRACKER.kameraStill
                kam_kep = pg.image.frombuffer(image.tostring(), image.shape[1::-1], "BGR")
                kam_kep = pg.transform.scale(kam_kep, (kam_kep.get_width()/2,kam_kep.get_height()/2))
                kam_kep = pg.transform.flip(kam_kep, True, False)
                self.JATEKABLAK.ABLAK.blit(kam_kep, (self.ESZKOZOK.ESZKOZOK["doboz"]["obj"].pozicio[0],(self.JATEKABLAK.ABLAKMERET[1]-kam_kep.get_height())))
                if self.TRACKER.statusz == 0:
                    self.VISSZASZAMLALOK["mutat_kamera"].s_start(pg.time.get_ticks())
                    self.rajzol_szoveg("Nincs kéz", szin=(229,185,150), poz=[self.ESZKOZOK.ESZKOZOK["doboz"]["obj"].pozicio[0],self.JATEKABLAK.ABLAKMERET[1]], selfMinus = {"x": False, "y": True})

            # Játékállapot frissítése
            if (self.JATEKALLAPOT == self.K_JATEKALLAPOTOK[0]):
                # kezdő állapot
                if (self.TRACKER.statusz != 0):
                    # amennyiben kéz találva lett
                    self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[1]
                    self.VISSZASZAMLALOK["var_marad"].s_start(pg.time.get_ticks())
                else:
                    self.rajzol_szoveg("A kezdéshez mutasd fel egyik kezedet", center=True)
            elif (self.JATEKALLAPOT == self.K_JATEKALLAPOTOK[1]):
                if self.VISSZASZAMLALOK["var_marad"].lejart() == False:
                    if self.TRACKER.statusz == 0:
                        # ha a talált kéz eltűnik
                        self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[0]
                else:
                    # ha a talált kéz marad
                    if self.TRACKER.statusz == 3:
                        self.VISSZASZAMLALOK["var_kpo"].s_start(pg.time.get_ticks())
                        self.GEP_DONTES = random.randint(1,len(self.K_VEGEREDMENYEK))
                        self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[2]
                    else:
                        self.rajzol_szoveg("Mutass ollót a folytatáshoz", center=True)
            elif (self.JATEKALLAPOT == self.K_JATEKALLAPOTOK[2]):
                # játék kezdete visszaszámlálás
                if self.VISSZASZAMLALOK["var_kpo"].lejart() == True:
                    # ha a kő papír olló visszaszámlálás véget ért
                    valasztasok = [self.GEP_DONTES, self.TRACKER.statusz]
                    self.s_vegeredmeny({
                        "nyert": self.nyeres(valasztasok[0], valasztasok[1]),
                        "valasztasok": [valasztasok[0], valasztasok[1]]
                    })
                    self.VISSZASZAMLALOK["var_eredmeny"].s_start(pg.time.get_ticks())
                    self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[3]
                else:
                    ido = (self.VISSZASZAMLALOK["var_kpo"].ido//1000) - int(self.VISSZASZAMLALOK["var_kpo"].maradek_ido())
                    self.rajzol_szoveg(["Mutass egy alakzatot", "2", "3"][ido-1], center=True)
            elif (self.JATEKALLAPOT == self.K_JATEKALLAPOTOK[3]):
                if self.VISSZASZAMLALOK["var_eredmeny"].lejart() == True:
                    self.VISSZASZAMLALOK["var_marad"].s_start(pg.time.get_ticks())
                    self.s_uj_jatek()
                    self.JATEKALLAPOT = self.K_JATEKALLAPOTOK[1] 
                else:
                    self.rajzol_szoveg(self.K_VEGEREDMENYEK[self.VEGEREDMENYEK["nyert"]], center=True)
            pg.display.flip()

if __name__ == "__main__":
    _JatekFolyamat = JatekFolyamat()