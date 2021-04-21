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

def willFilesBeMoved(path):
    old_path = os.getcwd()
    os.chdir(path)

    if len(glob.glob('.\\*.exp')+glob.glob('.\\*blk*.exp')+glob.glob('.\\*yhasU.exp')+glob.glob('.\\*yhasTh.exp')+glob.glob('.\\*hf*.exp')) > 0:
        os.chdir(old_path)
        return True
    else:
        os.chdir(old_path)
        return False

def willFilesBeDeleted(path):
    old_path = os.getcwd()
    os.chdir(path)

    if len(glob.glob('.\\*.TDT')+glob.glob('.\\*.dat')+glob.glob('.\\*.log')+glob.glob('.\\*.ini')+glob.glob('.\\*.TXT')) > 0:
        os.chdir(old_path)
        return True
    else:
        os.chdir(old_path)
        return False

def findStandardNumber(path):
    old_path = os.getcwd()
    os.chdir(path)

    data = re.split(r'\D+', ''.join(glob.glob('.\\*.exp') + glob.glob('data\*.exp')))

    os.chdir(old_path)

    maxN = max(set(data), key=data.count)
    if maxN == '' or data.count(maxN) == 1:
        return None
    else:
        return max(set(data), key=data.count)

def getLabNrsFromList(filenameList):
    labNrs = re.split(r'\d+(?!\.)\D{1}', ''.join(filenameList))[1:]
    # remove ''
    labNrs = [val for val in labNrs if val != '']

    # remove '.exp'
    for i, nr in enumerate(labNrs):
        if '.exp' in nr:
            labNrs[i] = int(nr.replace('.exp', ''))
    return labNrs

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

def removeUnnecessaryFiles(path):
    old_path = os.getcwd()
    os.chdir(path)

    files = glob.glob('.\\*.TDT')+glob.glob('.\\*.dat')+glob.glob('.\\*.log')+glob.glob('.\\*.ini')+glob.glob('.\\*.TXT')
    for file in files:
        os.remove(file)

    os.chdir(old_path)

'''
    used for debugging
    specifically investigation of uncorrected age being lower than corrected age in some cases
'''

def writeList(path, filename, list):
    with open(os.path.join(path, filename), 'w') as file:
        for list_count, sub_list in enumerate(list):
            for i, item in enumerate(sub_list):
                file.write('{}'.format(item))
                if i < len(sub_list)-1:
                    file.write(',')
            if list_count < len(list)-1:
                file.write('\n')
        file.close()

def writeLineByLine(path, filename, list):
    with open(os.path.join(path, filename), 'w') as file:
        for element in list:
            file.write('{}\n'.format(element))
        file.close()