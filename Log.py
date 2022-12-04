'''
Kőpapir hibalogger
'''
import os
from datetime import datetime

class Log:
    def __init__(self):
        self.tipusok = {
            0: "INFO",
            1: "WARN",
            2: "ERR",
            3: "CRASH"
        }
        self.logFajlUtvonal = os.path.dirname(os.path.realpath(__file__)) + '/log/log.txt'
        self.logInfo(0, "Folyamat indul")

    def logInfo(self, tipus, info):
        date = datetime.now().strftime("%H:%M:%S")
        adat = "[" + self.tipusok[tipus] + "] ("+date+") " + str(info)
        print(adat)
        try:
            with open(self.logFajlUtvonal, "a+", encoding="utf-8") as logFajl:
                logFajl.writelines([adat+"\n"])
        except Exception as e:
            print("log fájl nem írható: " + str(e))