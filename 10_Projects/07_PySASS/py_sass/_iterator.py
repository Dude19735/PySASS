import itertools as itt

class Iterator:
    """
    This class contains an iterator that makes the current item accessible.
    """
    def __init__(self, obj:str):
        self.__iterator = itt.islice(obj, 0, None)
        self.__current = None
        self.__chr_counter = 0

    @property
    def current(self):
        """The item the iterator currently points at"""
        return self.__current
    
    @property
    def chr_counter(self):
        """The index of the current item"""
        return self.__chr_counter
    
    def __next__(self):
        """__next__ override"""
        self.__current = next(self.__iterator, False)
        self.__chr_counter += 1
        return self.__current