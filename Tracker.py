'''
Kőpapír tracker
'''

import cv2 as cv
import mediapipe as mp
import math
from Kivetelek import *

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

LANDMARKS_N = {
  # ujjbegyek
  "HUVELYK_4":4,
  "MUTATO_4":8,
  "KOZEPSO_4":12,
  "GYURUS_4":16,
  "KIS_4":20,
  # 3. szint
  "HUVELYK_3":2,
  "MUTATO_3":6,
  "KOZEPSO_3":10,
  "GYURUS_3":14,
  "KIS_3":18,
  # 0. szint
  "HUVELYK_0":2,
  "MUTATO_0":5,
  "KOZEPSO_0":9,
  "GYURUS_0":13,
  "KIS_0":17,
  # Csukló
  "CSUKLO_0": 0,
}

def tavolsag(x,y):
    # Távolság számítása 2 pont között
    return math.sqrt((x[1]-x[0])**2 + (y[1] - y[0])**2)

class Tracker:
    def __init__(self):
        self.MP_HANDS = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.2, min_tracking_confidence=0.5, max_num_hands=1)
        self.KAMERA = cv.VideoCapture(1)
        self.STATUSZ_KONYVTAR = {
            0: "Nincs kéz",
            1: "Papír",
            2: "Kő",
            3: "Olló"
        }
        self.statusz = 0
        self.kameraStill = False

    def frissit(self):
        if (self.KAMERA):
            res, kameraKep = self.KAMERA.read()
            if not res:
                raise FrameDrop
            kameraKep.flags.writeable = False
            dimenziok = {}
            kezAdatok = self.MP_HANDS.process(kameraKep)
            if kezAdatok:
                koordinatak = kezAdatok.multi_hand_world_landmarks
                if koordinatak is not None:
                    for i in LANDMARKS_N.keys():
                        dimenziok.update({
                            i: tavolsag(
                                (koordinatak[0].landmark[LANDMARKS_N[i]].x, koordinatak[0].landmark[LANDMARKS_N["CSUKLO_0"]].x),
                                (koordinatak[0].landmark[LANDMARKS_N[i]].y, koordinatak[0].landmark[LANDMARKS_N["CSUKLO_0"]].y)
                            )
                        })
                if len(dimenziok) > 0:
                    if (dimenziok["MUTATO_3"] > dimenziok["MUTATO_4"]):
                        self.statusz = 2
                    else:
                        if (dimenziok["GYURUS_4"] < dimenziok["GYURUS_3"]):
                            self.statusz = 3
                        else:
                            self.statusz = 1
                else:
                    self.statusz = 0
                if kezAdatok.multi_hand_landmarks:
                    for hand_landmarks in kezAdatok.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            kameraKep,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style())
                self.kameraStill = kameraKep
        else:
            raise NincsKamera