import ntpath

def get_standard_number(df):
    data = []
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