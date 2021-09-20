from datetime import datetime
import ntpath
import json
import pandas as pd
import os
import numpy as np
import xlrd
from PyQt5.QtGui import QFontMetrics


def load_constants(path):
    with open(path, 'r') as file:
        constants = json.loads(file.read().replace('\n', ''))
    fileName = path_leaf(path)
    if 'coral' in fileName:
        constants['type'] = 'coral'
    elif 'stalag' in fileName:
        constants['type'] = 'stalag'
    else:
        constants['type'] = 'stalag'
    return constants

def load_json(path):
    with open(path, 'r') as file:
        _dict = json.loads(file.read().replace('\n', ''))
    return _dict
    
    
def load_ratios(path):
    folder_data = os.path.join(path, 'data')
    if os.path.isdir(folder_data):
        list_data = os.listdir(folder_data)
        names_data = np.sort(np.array(list_data))

        rbook = xlrd.open_workbook(os.path.join(path, 'Ratios.xlsx'))

        sheet = rbook.sheet_by_name('Ratios')

        ratios_dict = {}

        for col in range(1, sheet.ncols):
            key = sheet.cell(0, col).value
            ratios_dict[key] = []
            
            for row in range(1, sheet.nrows):
                try:
                    ratios_dict[key].append(float(sheet.cell(row, col).value))
                except:
                    ratios_dict[key].append(sheet.cell(row, col).value)
        
        ratios = pd.DataFrame(ratios_dict, index=names_data)
    
        return ratios


def get_standard_number_from_df(df):
    if 'Lab. #' in df:
        data = list(df['Lab. #'])
    elif 'Lab.Nr.' in df:
        data = list(df['Lab.Nr.'])
    else:
        return None
    return max(set(data), key=data.count)


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_dates(path):
    dates = []

    old_path = os.getcwd()

    folder_data = os.path.join(path, 'data')
    list_data = os.listdir(folder_data)
    names_data = np.sort(np.array(list_data))

    for i in range(len(names_data)):
        os.chdir(folder_data)
        cc = pd.read_table(names_data[i], sep='\t')  # read in files from Neptune software
        raw = pd.DataFrame(cc)

        dates.append(raw.iloc[1, 0].replace('Date: ', ''))

    os.chdir(old_path)

    return dates


def maybe_make_number(s):
    """Returns a string 's' into a integer if possible, a float if needed or
    returns it as is.
    Used to convert lab numbers from string to int but handle exceptions (like '9799-4')"""

    # handle None, "", 0
    if not s:
        return s
    try:
        f = float(s)
        i = int(f)
        return i if f == i else f
    except ValueError:
        return s


def try_convert_to_int(l):
    return list(map(maybe_make_number, l))


def save_array(arr, path, name):
    with open(os.path.join(path, name + '.txt'), 'w') as file:
        for line in arr:
            file.write(str(line) + '\n')


def openFileItem(path, item):
    itemPath = os.path.join(path, item.text())
    if os.path.isfile(itemPath):
        os.system("notepad.exe {}".format(itemPath))


def keyByValue(_dict, value):
    return dict(zip(_dict.values(), _dict.keys()))[value]


def sortableTimestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def setHeight(edit, nRows):
    RowHeight = QFontMetrics(edit.font()).lineSpacing()
    edit.setFixedHeight(nRows * RowHeight)