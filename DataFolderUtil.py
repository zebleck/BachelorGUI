import os
import shutil
import glob
import re

def getFiles(path):
    old_path = os.getcwd()
    os.chdir(path)

    data = glob.glob('.\\*.exp') + glob.glob('data\*.exp')
    blanks = glob.glob('.\\*blk*.exp') + glob.glob('blank\*blk*.exp')
    yhasu = glob.glob('.\\*yhasU.exp') + glob.glob('yhas_u\*yhasU.exp')
    yhasth = glob.glob('.\\*yhasTh.exp') + glob.glob('yhas_th\*yhasTh.exp')
    hf = glob.glob('.\\*hf*.exp') + glob.glob('hf\*hf*.exp')

    files = {'data': data, 'blank': blanks, 'yhasth': yhasth, 'yhasu': yhasu, 'hf': hf}

    os.chdir(old_path)

    findStandardNumber(path)

    return files

def findStandardNumber(path):
    old_path = os.getcwd()
    os.chdir(path)

    data = re.split(r'\D+', ''.join(glob.glob('.\\*.exp') + glob.glob('data\*.exp')))

    os.chdir(old_path)
    return max(set(data), key=data.count)

def createDataFolders(path):
    old_path = os.getcwd()
    os.chdir(path)

    if os.path.exists('blank') == False:
        os.mkdir('blank')
    if os.path.exists('data') == False:
        os.mkdir('data')
    if os.path.exists('yhas_th') == False:
        os.mkdir('yhas_th')
    if os.path.exists('yhas_u') == False:
        os.mkdir('yhas_u')
    if os.path.exists('hf') == False:
        os.mkdir('hf')

    # blanks
    blanks = glob.glob('.\\*blk*.exp')
    for b in blanks:
        shutil.move(b, 'blank')
    # yhas_u
    yhasu = glob.glob('.\\*yhasU.exp')
    for u in yhasu:
        shutil.move(u, 'yhas_u')
    # yhas_th
    yhasth = glob.glob('.\\*yhasTh.exp')
    for t in yhasth:
        shutil.move(t, 'yhas_th')
    # hf
    hf = glob.glob('.\\*hf*.exp')
    for h in hf:
        shutil.move(h, 'hf')
    # data
    datar = glob.glob('.\\*.exp')
    for d in datar:
        shutil.move(d, 'data')

    os.chdir(old_path)