import os
import pygame as pg
from Kivetelek import *
from Log import Log

class Eszkoz():
    def __init__(self, obj):
        self.obj = obj
        self.meret = (self.obj.get_width(), self.obj.get_height())
        self.pozicio = (500,500)
        self.lathato = True
        # Ismétlődés x,y tengelyen adott alkalommal (tiling)
        self.ism = {
            "x": 0,
            "y": 0
        }
        
    def u_meret(self):
        self.meret = (self.obj.get_width(), self.obj.get_height())
    
    def s_ism(self, ism):
        self.ism.update({"x": ism["x"], "y": ism["y"]})

    def s_meret_arany(self, meret):
        self.obj = pg.transform.scale(self.obj, (self.obj.get_width()/meret, self.obj.get_height()/meret))
        self.u_meret()
    
    def s_meret(self, meret):
        self.obj = pg.transform.scale(self.obj, (meret[0], meret[1]))
        self.u_meret()

    def s_poz(self, poz):
        self.pozicio = (poz[0], poz[1])

    def g_forgat(self, szog):
        rot_obj = pg.transform.rotate(self.obj, szog)
        rot_obj_rect = rot_obj.get_rect(center=self.obj.get_rect(center=(self.pozicio[0], self.pozicio[1])).center)
        return [rot_obj, rot_obj_rect]


class Eszkozok:
    def __init__(self, param):
        self.ESZKOZOK_UTVONAL = os.path.dirname(os.path.realpath(__file__)) + '/assets/'
        self.HELYES_KITERJESZTES = ["png", "ttf"]
        self.INGN_FAJLOK = ["bg0", "bg2"]
        self.LOG = Log()
        self.ESZKOZOK = {}
        self.KEZEK = {}
        self.JATEK_BT = pg.font.SysFont('Comic Sans MS', 30)
        # Paraméterek
        self.PARAM = param
        self.EszkozokBetolt()
        self.EszkozMeretezes()
    
    # Méretezések
    def EszkozMeretezes(self):
        # Méretek lekérése
        alap_meretek = {}
        for i in self.ESZKOZOK.keys():
            alap_meretek.update({i: self.ESZKOZOK[i]["obj"].meret})
        # Méretezési arány viszonyítva egy adott eszköz méretéhez
        ABLAKMERET = self.PARAM["ABLAKMERET"] # 0: x; 1: y
        ARANY = ((alap_meretek["doboz"][0]/ABLAKMERET[0])*1.25)
        for i in alap_meretek.keys():
            self.ESZKOZOK[i]["obj"].s_meret_arany(ARANY)
        # Explicit méretezés
        self.explicitMeretezes()
        
    # Explicit méretezés
    def explicitMeretezes(self):
        for i in self.ESZKOZOK.keys():
            if "kez_" in i:
                # kezek méretezése
                self.KEZEK.update({i: self.ESZKOZOK[i]["obj"]})
                self.ESZKOZOK[i]["obj"].s_meret(
                    (self.ESZKOZOK[i]["obj"].meret[0]/1.3, self.ESZKOZOK[i]["obj"].meret[1]/1.3)
                )
        # logo
        self.ESZKOZOK["logo"]["obj"].lathato = False
        # pipa, x
        self.ESZKOZOK["pipa"]["obj"].lathato = False # pipa
        self.ESZKOZOK["nemjo"]["obj"].lathato = False # x
        # doboz
        self.ESZKOZOK["doboz"]["obj"].pozicio = (
            (self.PARAM["ABLAKMERET"][0]-self.ESZKOZOK["doboz"]["obj"].meret[0])//2,
            (self.PARAM["ABLAKMERET"][1]-self.ESZKOZOK["doboz"]["obj"].meret[1]),
        )
        # háttér
        self.ESZKOZOK["bg1"]["obj"].s_ism({"x": 5, "y": 5})
        self.ESZKOZOK["bg1"]["obj"].s_poz([self.ESZKOZOK["doboz"]["obj"].pozicio[0], 0])
        self.ESZKOZOK["bg1"]["obj"].s_meret(
            (self.ESZKOZOK["doboz"]["obj"].meret[0]/5,self.ESZKOZOK["doboz"]["obj"].meret[0]/5)
        )
        # lámpabúra
        self.ESZKOZOK["lampa_bura"]["obj"].s_meret_arany(4)
        self.ESZKOZOK["lampa_bura"]["obj"].s_poz([
            (self.PARAM["ABLAKMERET"][0]-self.ESZKOZOK["lampa_bura"]["obj"].meret[0])//2,
            0
        ])
        # lámpa égő
        self.ESZKOZOK["lampa_feny"]["obj"].s_meret(
            (
                self.ESZKOZOK["doboz"]["obj"].meret[0]-((self.ESZKOZOK["doboz"]["obj"].meret[0])//3), 
                (self.PARAM["ABLAKMERET"][1]-self.ESZKOZOK["doboz"]["obj"].meret[1]-self.ESZKOZOK["lampa_bura"]["obj"].meret[1])
            )
        )
        self.ESZKOZOK["lampa_feny"]["obj"].s_poz([
            (self.PARAM["ABLAKMERET"][0]-self.ESZKOZOK["lampa_feny"]["obj"].meret[0])//2,
            (self.ESZKOZOK["lampa_bura"]["obj"].meret[1])
        ])
    
    # Betöltés
    def ujEszkoz(self, adat):
        self.ESZKOZOK.update({
            adat["fajlnev"]: {
                "obj": adat["obj"],
                "tipus": adat["tipus"]
            }
        })

    def EszkozokBetolt(self):
        fajlok = []
        szamlalo = {
            "nem_betoltott": 0,
            "betoltott": 0
        }
        for i in os.listdir(self.ESZKOZOK_UTVONAL):
            fajlnev = i.split('.')
            if len(fajlnev) > 1:
                szamlalo["nem_betoltott"] += 1
                if fajlnev[-1] in self.HELYES_KITERJESZTES and " " not in fajlnev[0]:
                    if (fajlnev[-1] == self.HELYES_KITERJESZTES[0]):
                        eszkoz_obj = Eszkoz(pg.image.load(self.ESZKOZOK_UTVONAL + "/" + i))
                    elif (fajlnev[-1] == self.HELYES_KITERJESZTES[1]):
                        self.JATEK_BT = pg.font.Font(self.ESZKOZOK_UTVONAL + "/" + i, 50)
                    if (fajlnev[0] not in self.INGN_FAJLOK):
                        szamlalo["betoltott"] += 1
                        self.ujEszkoz({
                            "fajlnev": fajlnev[0],
                            "obj": eszkoz_obj,
                            "tipus": type(eszkoz_obj)
                        })

        self.LOG.logInfo(0, "Eszköz betöltő: " + str(szamlalo["betoltott"]) + "/" + str(szamlalo["nem_betoltott"]) + " betöltve. Eszközlista: " + str(self.ESZKOZOK).replace(" ", "\n"))
    
    def masolEszkoz(self, alap, cel):
        # Eszköz másolása x névről y névre
        self.ESZKOZOK[cel] = self.ESZKOZOK[alap]
    
    def g_obj(self, obj):
        return self.ESZKOZOK[obj]["obj"]