from py_sass import SM_SASS
from . import _config as sp
from ._instr_cubin_db_proxy import Db_BinaryData_Proxy
from .sm_cubin_lib import SM_CuBin_Lib

"""
This file contains abstraction classes for the head and tail bits of a real kernel.
This is also the place where one would add more advanced stuff to do with those bits.

Check out sm_cubin_file.py for a sample.

ELF cheatsheet:
https://gist.github.com/x0nu11byt3/bcb35c3de461e5fb66173071a2379779

Some info about regs per thread:
https://forums.developer.nvidia.com/t/number-of-registers/8450

Additional info to add:
- registers per thread
- total number of registers
"""

class SM_CuBin_Kernel_Head:
    def __init__(self, sass:SM_SASS, words:list, bits:bytes, end_of_config:int, begin_of_sass:int):
        wl = sass.sm.details.ARCHITECTURE.WORD_SIZE
        # If the word length is not 64 we are in a different quantum reality
        if wl != 64: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        # 'words' is a list of lists of hex values, each 8 bits long => one word is 8 entries long
        bb_len = (len(words)*int(wl/8))
        # 'begin_of_sass' is calculated directly based on the binary data. If this one is the same
        # then 'end_of_config' is also correct
        if not bb_len == begin_of_sass: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # list of words of the head of the cubin
        self.__words = words
        # Binary index pointing to the end of the configuration part of the head.
        # => each binary head is a bit of data, followed by a range of zero words that padds the
        #    instructions to the correct place
        self.__end_of_config = end_of_config
        self.__bits = bits[:bb_len]

        # self.__bits is a byte array where each entry is 8 bits long
        if not len(self.__bits) % int(wl/8) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

    @property
    def words(self): return self.__words
    @property
    def bits(self): return self.__bits

    def to_db(self) -> Db_BinaryData_Proxy:
        return Db_BinaryData_Proxy.create(Db_BinaryData_Proxy.Type_CubinHead, 1, self.__bits, 'The beginning of the Cuda kernel bits up until the instruction bit start')


class SM_CuBin_Kernel_Tail:
    def __init__(self, sass:SM_SASS, words:list, bits:bytes):
        wl = sass.sm.details.ARCHITECTURE.WORD_SIZE
        # If the word length is not 64 we are in a different quantum reality
        if wl != 64: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # 'words' is a list of lists of hex values, each 8 bits long => one word is 8 entries long
        bb_len = (len(words)*int(wl/8))

        # List of words with the tail end of the cubin
        # NOTE: 'words' generally stars with a range of zero words that padd the end of the instructions
        self.__words = words
        self.__bits = bits[-bb_len:]

        if not len(self.__bits) % int(wl/8) == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)

    @property
    def words(self): return self.__words
    @property
    def bits(self): return self.__bits

    def to_db(self) -> Db_BinaryData_Proxy:
        return Db_BinaryData_Proxy.create(Db_BinaryData_Proxy.Type_CubinTail, 3, self.__bits, 'The end of the Cuda kernel from the end of the instructions to the end of the Cuda kernel')