
import os
import json
from datetime import date


pathfile = os.path.normpath(os.path.dirname(
    os.path.abspath(__file__)) + os.sep)
pathfile = os.path.abspath(os.path.join(pathfile, '..'))
pathfile = os.path.abspath(os.path.join(pathfile, '..'))
pathfile = pathfile+"/files/"


def saveJSON(folder, name, data, PathDate: date = None):
    if PathDate:
        PathSave = pathfile+folder+"/"+str(PathDate.year)
        if not os.path.isdir(PathSave):
            os.mkdir(PathSave)
        PathSave = PathSave+"/"+str(PathDate.month)
        if not os.path.exists(PathSave):
            os.mkdir(PathSave)
        folder = folder+"/"+str(PathDate.year)+"/"+str(PathDate.month)

    try:
        file = open(pathfile+folder+"/"+name+'.json', 'w')
        json.dump(data, file)
        file.close()
    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)
        return False

    return True


def getJSON(folder, name, PathDate=None):
    if PathDate:
        folder = folder+"/"+str(PathDate.year)+"/"+str(PathDate.month)
    try:
        f = open(pathfile+folder+"/"+name+'.json',)
        data = json.load(f)
        f.close()
        return data
    except Exception as e:
        print(type(e).__name__, __file__, e.__traceback__.tb_lineno)
        return False
