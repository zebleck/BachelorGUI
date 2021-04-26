import ntpath


def get_standard_number(df):
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


def maybeMakeNumber(s):
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
    return list(map(maybeMakeNumber, l))
