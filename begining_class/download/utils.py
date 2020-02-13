import os


def get_name(path):
    """
    path/to/abc.tif ---> return: abc
    """
    name_file = os.path.basename(path)
    name=name_file.split('.')[0]
    return name

def make_dest_path(path, suffix):
    """
    EX:
    'path/abc.tif' + suffix '-any.tif' ---> return: 'path/abc-any.tif'
    """
    dir_name = os.path.dirname(path)
    file_name = get_name(path)
    dest_path = dir_name + '/' + file_name + suffix
    return dest_path

