from __future__ import annotations
import random
import math
import typing
import sys
import itertools as itt
from . import _config as sp
from ._sass_bits import SASS_Bits
from warnings import warn

##########################################################################
# This one is DEPRECATED! Use py_sass_ext.SASS_Range !!
warn(f"The module {__name__} is deprecated. Use py_sass_ext.SASS_Range instead!", DeprecationWarning, stacklevel=2)
##########################################################################

class SASS_Range_Iter:
    def __init__(self, count:int, ii:typing.Iterator[SASS_Bits]):
        self.__count = count
        self.__iter = ii
    @property
    def count(self) -> int: return self.__count
    @property
    def iter(self) -> typing.Iterator[SASS_Bits]: return self.__iter

class SASS_Range:
    """
    This one is used to represent larger ranges in the instructions operands. For example
    functions like UImm(20/0) that reprensent a range of 20 bit.

    It is a replacement of the regular Python 'set' that is used for the smaller ranges.
    """
    def __init__(self, min_val:int, max_val:int, bit_len:int, signed:int, bit_mask:int|None):
        if not isinstance(min_val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(max_val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(signed, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_mask, int|None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        self.__min_val = min_val
        self.__max_val = max_val
        self.__bit_len = bit_len
        self.__signed = signed
        self.__bit_mask = bit_mask
        if bit_mask is not None: self.__bit_mask_bits = tuple(int(i) for i in bin(bit_mask)[2:])
        else: self.__bit_mask_bits = tuple()
        bb = len(bin(max_val)[2:])
        if not signed and bb > bit_len: raise Exception(sp.CONST__ERROR_ILLEGAL)
        elif signed and bb > bit_len-1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __str__(self) -> str: 
        return "[{0}, {1}]{2}{3}b{4}".format(self.__min_val, self.__max_val, 'S' if self.__signed else 'U', self.__bit_len, str(self.__bit_mask) + 'M' if self.__bit_mask is not None else '')
    def __iter__(self) -> SASS_Range:
        self.__iter = self.sample_iter(0).iter
        return self
    def __next__(self) -> SASS_Bits:
        return next(self.__iter)
    def __bool__(self) -> bool: 
        return not self.empty()
    def __max__(self) -> int: 
        return self.__max_val
    def __min__(self) -> int: 
        return self.__min_val
    def __eq__(self, other:SASS_Range) -> bool: # type: ignore
        if not isinstance(other, SASS_Range): return False
        return \
            self.__max_val == other.__max_val and \
            self.__min_val == other.__min_val and \
            self.__bit_len == other.__bit_len and \
            self.__signed == other.__signed and \
            self.__bit_mask == other.__bit_mask
    def __len__(self) -> int:
        s = self.size()
        if s > sys.maxsize: s = sys.maxsize
        return s
    
    def add_bit_mask(self, bit_mask:int) -> SASS_Range:
        self.__bit_mask = bit_mask
        self.__bit_mask_bits = tuple(int(i) for i in bin(bit_mask)[2:])
        return self
    
    def size(self) -> int: return self.__max_val - self.__min_val
    def bit_len(self) -> int: return self.__bit_len
    def empty(self) -> bool: return self.__max_val - self.__min_val == 0
    def to_dict(self) -> dict: 
        return {'min_val': self.__min_val, 'max_val': self.__max_val, 'bit_len': self.__bit_len, 'signed': self.__signed, 'bit_mask': self.__bit_mask}
    def serialize(self):
        # s = "1,{0},{1},{2},{3},{4}".format(self.__min_val, self.__max_val, self.__bit_len, self.__signed, 0 if self.__bit_mask is None else self.__bit_mask)
        min_val = self.__min_val
        max_val = self.__max_val
        bit_len = self.__bit_len
        signed = self.__signed
        bit_mask = self.__bit_mask if self.__bit_mask is not None else 0
        return "{0},{1},{2},{3},{4}".format(min_val, max_val, bit_len, signed, bit_mask)
    @staticmethod
    def deserialize(vals:str):
        """
        Get the next three comma separated numbers in the iterator and return a SASS_Bits
        """
        vals_i = [int(i) for i in vals.split(',')]
        if vals_i[-1] == 0: vals_i[-1] = None # type: ignore
        return SASS_Range(*vals_i)
    def deserialize2(vals:str): # type: ignore
        """
        Get the next three comma separated numbers in the iterator and return a SASS_Bits
        """
        vals_i = [int(i) for i in vals.split(',')]
        return vals_i[2:]
    @staticmethod
    def from_dict(dd:dict) -> SASS_Range:
        if not 'min_val' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'max_val' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'bit_len' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'signed' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'bit_mask' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        min_val = dd['min_val']
        max_val = dd['max_val']
        bit_len = dd['bit_len']
        signed = dd['signed']
        bit_mask = dd['bit_mask']
        if not isinstance(min_val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(max_val, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(signed, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not signed in [0,1]: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(bit_mask, int|None): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Range(min_val, max_val, bit_len, signed, bit_mask)
    
    def sample_iter(self, count:int=0) -> SASS_Range_Iter:
        # TODO: this one assumes that all bitmasks start from the bottom and are
        # dense...
        if self.__bit_mask is not None:
            bl = math.ceil(math.log2(self.__bit_mask))
            from_ = abs(self.__min_val) >> bl
            to = abs(self.__max_val) >> bl
            if self.__min_val < 0: from_ *= -1
            if self.__max_val < 0: to *= 1
        else:
            bl = None
            from_ = abs(self.__min_val)
            to = abs(self.__max_val)
            if self.__min_val < 0: from_ *= -1
            if self.__max_val < 0: to *= 1

        if count > 0: step = math.ceil((to - from_) / count)
        else: 
            step = 1
            count = to - from_

        if self.__bit_mask is not None: rr = (SASS_Bits.from_int(i<<bl, bit_len=self.__bit_len, signed=self.__signed) for i in range(from_, to-step, step)) # type: ignore
        else: rr = (SASS_Bits.from_int(i, bit_len=self.__bit_len, signed=self.__signed) for i in range(from_, to-step, step))
        
        if self.__bit_mask is not None: 
            end_val = (abs(self.__max_val) >> bl) << bl # type: ignore
            if self.__max_val < 0: end_val *= -1
        else: end_val = self.__max_val
        
        rr2 = itt.chain(rr, [SASS_Bits.from_int(end_val, bit_len=self.__bit_len, signed=self.__signed)]) # make sure the largest value is included
        return SASS_Range_Iter(count, rr2)
    
    def pick(self) -> SASS_Bits:
        # This one is a bit complicated because we want the result to be evenly distributed.
        # Thus, we have to first generate all bits without the bits that will be 0 because of a
        # potential bit mask and also without the signed bit and then add them later.
        # The reason for this is, that we want to enable proper Monte Carlo testing. With that,
        # if the random samples are not evenly distributed, it breaks everything.

        s = [sp.RANDOM__SEED_1, sp.RANDOM__SEED_2, sp.RANDOM__SEED_3, sp.RANDOM__SEED_4]
        random.seed(s[random.randint(0,len(s)-1)] + random.randint(-9999, 9999))
        # val = random.randrange(self.__min_val, self.__max_val+1)
        # if we have a bit mask, we discard the length of the bits of the bit mask
        bm = 0
        if self.__bit_mask is not None:
            bm = sum(self.__bit_mask_bits)
        bl = self.__bit_len
        # if the range is signed, we need one bit as signed bit
        if self.__signed == 1: bl -= 1
        bit_val = random.getrandbits(bl - bm)
        if self.__min_val < 0:
            # calculate the max negative value based on the bit restrictions bl-bm
            # and subtract it => center random value
            # NOTE: the signed bit (that we have if we have a neg min_val) is responsible
            # for negative and positive values => no need to divide m_min by 2.
            m_min = int((2**(bl-bm)-1))
            bit_val -= m_min
        bits:SASS_Bits = SASS_Bits.from_int(bit_val, bit_len=(self.__bit_len - bm), signed=self.__signed)
        # now we have a value made up of the right number of bits
        # => apply the bit mask if we have one
        if bm > 0:
            # generate a list that includes the bit mask bits
            target = self.__bit_len*[0]
            source = bits.bits
            # source = (1,1,1,1,1,1,1,1,1,1,1,1,1,1) # test case
            btmask = self.__bit_mask_bits
            # btmask = (1,0,1,0,0,0,0) # test case
            # goal = (1,1,1,1,1,1,1,1,1,0,1,0,1,1,1,1) # test case
            bm_ind = len(btmask)-1
            sr_ind = len(source)-1
            tr_ind = len(target)-1
            if not (sr_ind + 1 + bm == self.__bit_len): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not (bm_ind <= sr_ind): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            while bm_ind > 0:
                if btmask[bm_ind] == 0:
                    # if the bitmask is 0, take the value of the source, otherwise leave the target value 0
                    target[tr_ind] = source[sr_ind]
                    sr_ind -= 1
                bm_ind -= 1
                tr_ind -= 1
            # move the index in the target to the next one
            tr_ind -= 1
            if not (tr_ind == len(target) - len(btmask)-1): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            if not (sr_ind == tr_ind): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # transfer the rest
            target[:(tr_ind+1)] = source[:(sr_ind+1)]

            bits = SASS_Bits(tuple(target), bit_len=self.__bit_len, signed= True if self.__signed==1 else False) # type: ignore
            if not int(bits) & self.__bit_mask == 0: raise Exception(sp.CONST__ERROR_UNEXPECTED) # type: ignore
        return bits
    
    def intersection(self, other:set|SASS_Range) -> set|SASS_Range:
        if isinstance(other, set):
            # If the other one is a set, assume that we have a small amount of values. Convert this one to a 
            # normal set too. Iterate the set
            if self.__bit_mask is not None:
                rr = set(i & self.__bit_mask for i in range(self.__min_val, self.__max_val+1))
            else:
                rr = set(range(self.__min_val, self.__max_val+1))
            result = rr.intersection(other)
            return result
        elif isinstance(other, SASS_Range):
            if not self.__signed == other.__signed: raise Exception(sp.CONST__ERROR_ILLEGAL)
            new_max = min(self.__max_val, other.__max_val)
            new_min = max(self.__min_val, other.__min_val)
            new_bit_len = len(bin(abs(new_max))[2:])
            if new_min >= new_max: return SASS_Range(0, 0, 1, 0) # type: ignore
            if self.__signed: new_bit_len += 1
            if self.__bit_mask is not None and other.__bit_mask is not None: new_bit_mask = self.__bit_mask | other.__bit_mask
            elif self.__bit_mask is not None: new_bit_mask = self.__bit_mask
            elif other.__bit_mask is not None: new_bit_mask = other.__bit_mask
            else: new_bit_mask = None
            return SASS_Range(new_min, new_max, new_bit_len, self.__signed, bit_mask=new_bit_mask)
            # We assume that we don't really have non-continuous sets
            # raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        