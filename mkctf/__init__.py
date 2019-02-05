'''mkCTF package

Variables:
    __version__ {str} -- Package version
    __version_info__ {tuple} -- Package version
'''
__major__ = 2
__minor__ = 1
__patch__ = 1
__version_info__ = (__major__, __minor__, __patch__)
__version__ = f'{__major__}.{__minor__}.{__patch__}'
__banner__ = r"""
           _     ____ _____ _____
 _ __ ___ | | __/ ___|_   _|  ___|
| '_ ` _ \| |/ / |     | | | |_
| | | | | |   <| |___  | | |  _|
|_| |_| |_|_|\_\\____| |_| |_|    v{}

""".format(__version__)
