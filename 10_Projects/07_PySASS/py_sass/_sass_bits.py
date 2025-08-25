from __future__ import annotations
import typing
import copy
import math
import operator as oo
from . import _config as sp
from warnings import warn

##########################################################################
# This one is DEPRECATED! Use sass_values.SASS_Bits !!
warn(f"The module {__name__} is deprecated. Use py_sass_ext.SASS_Bits instead!", DeprecationWarning, stacklevel=2)
##########################################################################

class SASS_Bits_SignError(Exception):
    def __init__(self, message): super().__init__(message)
class SASS_Bits_AssembleError(Exception):
    def __init__(self, message): super().__init__(message)

class SASS_Bits:
    TT_CONVERTIBLE = set([oo.mul, oo.add, oo.sub, oo.eq, oo.le, oo.ge, oo.lt, oo.gt, oo.floordiv, oo.ne])
    """
    This one covers integers as bits with two's complement, variable number
    of bits and capped overflow:
    for bit_len = 3: 100 => -4 but 4 = 011+1 == 0 because of overflow 
    """
    def __init__(self, bits:typing.Tuple[int], bit_len:int=0, signed:bool=True):
        if not isinstance(bits, tuple): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(signed, bool): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if bit_len == 0: bit_len = len(bits)
        elif bit_len < len(bits): raise ValueError("Value must be tuple of at least bit_len length")
        if not all([i==1 or i==0 for i in bits]): raise ValueError("Value must be tuple with only 0 and 1")
        self.bits = ((bit_len-len(bits))*(0,)) + bits
        self.bit_len = bit_len
        self.signed = signed
        if self.bit_len < 2 and self.signed: raise SASS_Bits_SignError("One bit signed value not allowed")
        self.__hash = int(self)

    def __copy__(self):
        new = self.__new__(self.__class__)
        # no need for copies, all types are immutable anyways
        new.bits = self.bits
        new.bit_len = self.bit_len 
        new.signed = self.signed
        new.__hash = self.__hash
        return new

    @staticmethod
    def from_int(val:SASS_Bits|int, bit_len:int=0, signed:int=-1):
        """
        Create SASS_Bits from integer.
        If bit_len > 1 => signed.
        If bit_len == 1 => unsigned
        If bit_len == 0 => automatic (as many bits as needed to hold the result)
        If bit_len < 0 => interpret bit_len as positive number and use bit_len = max(abs(bit_len), len(bin(val)[2:]))
                          (at least bit_len but if val requires more bits, than that's fine)
        If signed == -1 => automatic: if val < 0 => signed otherwise unsigned
        If signed == 0  => unsigned (throw exception if not possible)
        IF signed == 1  => signed
        """
        if not isinstance(val, int):
            if isinstance(val, SASS_Bits): 
                if bit_len != 0 or signed!=-1: raise Exception(sp.CONST__ERROR_ILLEGAL)
                return val.__copy__()
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(signed, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not signed in [-1,0,1]: raise ValueError("signed must be a value in {-1,0,1}")
        if bit_len == 1 and signed == 1: raise SASS_Bits_SignError("Signed representation requires at least 2 bits!")
        is_neg = val < 0
        val_b = bin(val)[(3 if is_neg else 2):]
        val_signed = False
        if is_neg:
            if signed == -1: val_signed = True
            elif signed == 0: raise SASS_Bits_SignError("Can't create unsigned bits for negative value")
            elif signed == 1: val_signed = True
        else:
            if signed == 1: val_signed = True
            else: val_signed = False
        req_bit_len = len(val_b) + (1 if val_signed else 0)
        if bit_len == 0: bit_len = req_bit_len
        elif bit_len < 0: bit_len = max(abs(bit_len), req_bit_len)
        if req_bit_len > bit_len: raise ValueError("Insufficient bit_len {0} for value {1}".format(bit_len, val))
        val_b = val_b.zfill(bit_len)
        res = SASS_Bits(tuple(int(i) for i in val_b), bit_len, val_signed) # type: ignore
        if is_neg: res = res.at_negate()
        return res
    def to_dict(self):
        return {'bits': self.bits, 'bit_len': self.bit_len, 'signed': self.signed}
    def serialize(self):
        # l = 0
        # return l.to_bytes() + self.bit_len.to_bytes() + bytes(self.bits) + self.signed.to_bytes()
        # return "{0},{1},{2}".format(int(self), self.bit_len, self.signed)
        resi = 0
        for i,b in enumerate(reversed(self.bits)): resi += b<<i
        # if not self.bits == tuple(map(int, bin(resi)[2:].zfill(self.bit_len))):
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # if not ((self.bit_len & 0b11111111) << 8) >> 8 == self.bit_len:
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # if not self.signed & 0b11111111 == self.signed:
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        bb = (((self.bit_len & 0b11111111) << 8) | (self.signed & 0b11111111))
        # if not bb>>8 == self.bit_len:
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        # if not bb&0b11111111 == self.signed:
        #     raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return "{0},{1}".format(bb, resi)
    @staticmethod
    def deserialize(vals:str):
        l,b = [int(i) for i in vals.split(',')]
        bit_len = l>>8
        signed = bool(l & 0b11111111)
        return SASS_Bits(tuple(map(int, bin(b)[2:].zfill(bit_len))), bit_len, signed) # type: ignore
            
    @staticmethod
    def from_dict(dd:dict):
        if not 'bits' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'bit_len' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not 'signed' in dd: raise Exception(sp.CONST__ERROR_ILLEGAL)
        bits = dd['bits']
        bit_len = dd['bit_len']
        signed = dd['signed']
        if not isinstance(bits, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not all(isinstance(b, int) for b in bits): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(bit_len, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(signed, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        return SASS_Bits(tuple(bits), bit_len, signed)
    def pretty(self):
        return "{0}{1}:{2}b".format(int(self),'S' if self.signed else 'U',self.bit_len)
    # def bit_str(self):
    #     return "".join(str(i) for i in self.bits)
    def __str__(self):
        return self.pretty()
    def __bool__(self):
        if int(self) != 0: return True
        else: return False
    def __int__(self):
        if self.bit_len < 2 and self.signed: raise SASS_Bits_SignError("One bit signed value not allowed")
        val = sum([b<<ind for ind,b in enumerate(reversed(self.bits)) if b])
        if self.signed and (val & (1 << (self.bit_len - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << self.bit_len) # compute negative value
        return val # return positive value as is
    # def __eq__(self, other:SASS_Bits):
    #     if not isinstance(other, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     if not (other.signed == self.signed): raise SASS_Bits_SignError("Signedness must be the same for operands")
    #     if self.signed:
    #         return all([i==j for i,j in zip(reversed(self.bits[1:]), reversed(other.bits[1:]))]) and self.bits[0] == other.bits[0]
    #     else:
    #         return all([i==j for i,j in zip(reversed(self.bits), reversed(other.bits))])
    # def copy_with_new_value(self, new_val:int):
    #     """
    #     Try to create a new SASS_Bits instance with the same properties but a new value.
    #     It will succeed, if 'new_val' can be projected onto the current SASS_Bits properties
    #     bit_len and signed.

    #     For example, an unsigned SASS_Bits instance can't be updated with a negative new value.
    #     """
    #     if not isinstance(new_val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     try:
    #         return SASS_Bits.from_int(new_val, self.bit_len, 1 if self.signed else 0)
    #     except ValueError: return None
    #     except SASS_Bits_SignError: return None
    def assemble(self, instr_bits:typing.List[int], enc_inds:typing.Tuple[int], sm_nr:int):
        if not isinstance(instr_bits,list): raise ValueError("Invalid type for enc_bits")
        if not isinstance(enc_inds,tuple): raise ValueError("Invalid type for enc_inds")
        if not isinstance(sm_nr, int): raise Exception("Invalid type for sm_nr")

        # Assembling strategy:
        #  1. split the incomming bits into packs of 32 front to back
        #  2. split the encoding indices into packs of 32 front to back
        #  3. write each pack of 32 in sequence bitwise back-to-front into the target bits

        # For example:
        #  - if we have a 64 bit value:
        #     - split it into 2x 32
        #     - if we only have 32 encoding bits, we only pick the first 32 bits and ignore the rest
        #  - if we have a 5 bit value
        #     - split it into 1x 32 bits (still only 5 bits)
        #     - encode back to front using the encoding indices
        #     - if we have fewer encoding indices than bits, we ignore the remaining bits
        #       NOTE: all registers only select values that fit. The interesting cases are with the SASS_Range
        #
        #  Required results:
        # We need to cover the usecases:
        #  1. we have 64 bits but only want to keep the leading 32 bits
        #  2. we have a register with X<32 bits and B<X bits encoding space
        #  3. we have an immediate value with X<=32 bits and B<X bits encoding space
        #  4. we have an immediate value with 32<X<=64 bits and 32<=B<X encoding space
        #  5. we have an immediate value with 32<X<=64 bits and B<32 encoding space
        #  6. we have X<=32 bits values and more than X encoding space
        #  7. we have 32<X<=64 bits values and more than X encoding space
        # Case 1 induces encoding in 32 bits packages
        # Case 2 and 3 induce encoding back to front
        # Cases 1,2 and 3 thus induce requirement to encode front to back in 32 bits packs
        # and encode each pack back to front.
        # Case 4 induces the requirement that we pack front-to-back: fill the first 32 bits
        # back-to-front, then fill the second 32 bits back-to-front:
        #  38 bits: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXX
        #           BBBBBBBB|BBBBBBBB|BBBBBBBB|BBBBBBBB 32 encoding inds
        #
        #   Case 4: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX 32-bit-pack 1
        #           BBBBBBBB|BBBBBBBB|BBBBBBBB|BBBBBBBB 32 encoding inds
        #                                            <- (back-to-front)
        #           00000000|00000000|00000000|00XXXXXX 32-bit-pack 2
        #           --------|--------|--------|----BBBB remaining encoding inds
        #                                            <- (back-to-front)
        #
        #                                              
        #  38 bits: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXX
        #           BBBBBBBB|BBBBBB 14 encoding inds
        #   Case 5: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX 32-bit-pack 1
        #           --------|--------|--BBBBBB|BBBBBBBB 14 encoding inds
        #                                            <- (back-to-front)
        #           00000000|00000000|00000000|00XXXXXX 32-bit-pack 2
        #           --------|--------|--------|-------- no remaining encoding inds
        #                                            <- (back-to-front)
        #
        #
        #  64 bits: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX 64-bits (2x32 bits)
        #           BBBBBBBB|BBBBBBBB|BBBBBBBB|BBBBBBBB 32 encoding inds
        #
        #   Case 1: XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX 32-bit-pack 1
        #           BBBBBBBB|BBBBBBBB|BBBBBBBB|BBBBBBBB 32 encoding inds
        #                                            <- (back-to-front)
        #           XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX 32-bit-pack 1
        #           --------|--------|--------|-------- no remaining encoding inds
        #                                            <- (back-to-front)
        #
        #                                             
        #   8 bits: XXXXXXXX 8-bit pack
        #           BBBBB 5 encoding inds
        #
        # Case 2,3: 00000000|00000000|00000000|XXXXXXXX 32-bit pack filled back-to-front
        #           --------|--------|--------|---BBBBB 5 encoding inds
        #                                            <- (back-to-front)
        #
        # Case 6,7: have to be excluded using bit casts => always X >= B
        
        # Case 6,7
        if self.bit_len < len(enc_inds): self = self.cast(len(enc_inds))

        if len(self.bits) > 64 or len(enc_inds) > 64: raise Exception(sp.CONST__ERROR_UNEXPECTED) # assume, we never have more than 64 bits...

        w1 = [i for i in self.bits[:32]]
        l_w1 = len(w1)
        w1 = (32-l_w1)*[0] + w1
        e1 = enc_inds[:l_w1]
        if not len(w1) == 32: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        w2 = [i for i in self.bits[32:64]]
        l_w2 = len(w2)
        w2 = (32-l_w2)*[0] + w2
        e2 = enc_inds[l_w1:l_w2]
        if not len(w2) == 32: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if not len(enc_inds) >= self.bit_len:
            pass

        i_w1 = [(i-1,e-1) for i,e in zip(range(len(w1),0,-1), range(len(e1),0,-1))]
        i_w2 = [(i-1,e-1) for i,e in zip(range(len(w2),0,-1), range(len(e2),0,-1))]

        if not (len(e1) + len(e2) == len(enc_inds)): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not (l_w1 + l_w2 == len(self.bits)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        for ii,bb in i_w1: instr_bits[e1[bb]] = w1[ii]
        for ii,bb in i_w2: instr_bits[e2[bb]] = w2[ii]
        return instr_bits

        # # if not len(enc_inds) >= self.bit_len: raise SASS_Bits_AssembleError("Not enough encoding bits")
        # # make sure to fill up missing zeros if we have more encoding bits available than
        # # we have actual bits
        # bits = tuple(abs(self.bit_len-len(enc_inds))*[0]) + self.bits
        # for i,b in zip(enc_inds, bits): instr_bits[i] = b
        # return instr_bits
    def as_unsigned(self) -> SASS_Bits:
        """
        Interpret the UNCHANGED bits in SASS_Bits as 'unsigned'. Meaning
        1101 with bit_len = 4 goes from being -3 to 13.
        """
        new = copy.copy(self)
        new.signed = False
        return new
    def as_signed(self) -> SASS_Bits:
        """
        Interpret the UNCHANGED bits in SASS_Bits as 'signed'. Meaning
        1101 with bit_len = 4 goes from being 13 to -3.
        """
        if self.bit_len == 1: raise SASS_Bits_SignError("Signed value with only 1 bit is not allowed")
        new = copy.copy(self)
        new.signed = True
        return new
    def to_unsigned(self) -> SASS_Bits:
        """
        Change bit representation to unsigned.
        Negative numbers can't be converted to unsigned. Use at_negate first.
        This will shorten the bit representation by one bit.
        """
        if self.bits[0] == 1: raise SASS_Bits_SignError("Can't convert negative number to unsigned representation. Use at_negate first!")
        new = copy.copy(self)
        new.signed = False
        new.bits = new.bits[1:]
        new.bit_len -= 1
        return new
    def to_signed(self) -> SASS_Bits:
        """
        Change bit representation to signed.
        This will extend the bit representation by one bit.
        """
        new = copy.copy(self)
        new.signed = True
        new.bits = (0,) + new.bits
        new.bit_len += 1
        return new
    # def widen_to_bit_len(self, new_bit_len:int):
    #     """
    #     If signed:
    #     Equivalent of bits = bits << (new_bit_len - bit_len - 1)
    #     only shift for bit_len_dif-1, because the last bit is the signed one that doesn't
    #     change the value
        
    #     Else If unsigned:
    #     Equivalent of bits = bits << (new_bit_len - bit_len)
    #     we don't have a signed bit => shift the full amount
    #     """
    #     if not isinstance(new_bit_len, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     new = copy.copy(self)
    #     if self.signed: 
    #         new.bits = new.bits + (new_bit_len - self.bit_len - 1)*(0,)
    #     else:
    #         new.bits = new.bits + (new_bit_len - self.bit_len)*(0,)
    #     new.bit_len = new_bit_len
    #     return new
    def cast(self, new_bit_len:int) -> SASS_Bits:
        """
        Cast the current bits into a new format that is new_bit_len long.
         - If new_bit_len > bit_len
            - If signed     => fill up with msb
            - If not signed => fill up with msb
         - If new_bit_len < bit_len
            - If signed
               - If val < 0: take abs val, then empty to new_bit_len-1 bits, take the negative value of that
               - If val >= 0: empty to new_bit_len-1, return [0] + those bits
            - If not signed => take new_bit_len bits
         - If new_bit_len == bit_len: return a copy of the current one
        """
        new = copy.copy(self)
        if new_bit_len > self.bit_len:
            if self.signed:
                new.bits = tuple((new_bit_len - new.bit_len) * [new.bits[0]]) + new.bits
                new.bit_len = new_bit_len
            else:
                new.bits = tuple((new_bit_len - new.bit_len) * [0]) + new.bits
                new.bit_len = new_bit_len
        elif new_bit_len < self.bit_len:
            if self.signed:
                new = abs(new) # shave off signed msb
                new.bits = new.bits[-(new_bit_len - 1):]
                if self.bits[0] == 1:
                    new.bit_len = new_bit_len - 1
                    new = -new
                else:
                    new.bit_len = new_bit_len
                    new.bits = tuple([0]) + new.bits
            else:
                new.bits = new.bits[-new_bit_len:]
                new.bit_len = new_bit_len
        if not (len(new.bits) == new_bit_len): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return new
            
    def multiply(self, val:int) -> SASS_Bits:
        """
        Emulate the MULTIPLY thing in the definition of the SASS that occurs sometimes in the
        encodings.
        Like "TidB = tid MULTIPLY 4 SCALE 4;"

        This is a left-shift by log2(val) bits without changing the bit length.
        """
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not val % 2 == 0: raise ValueError("Invalid argument")
        if val <= 0: raise ValueError("Invalid argument")
        shift = int(math.log(val,2))
        if self.signed and self.bits[0] == 1:
            new = abs(self) # this will shave off the signed bit
            new.bits = new.bits[shift:] + tuple(shift*[0])
            new = -new # this will add back the signed bit
        else:
            new = copy.copy(self)
            new.bits = new.bits[shift:] + tuple(shift*[0])
        return new
    def scale(self, val) -> SASS_Bits:
        """
        Emulate the SCALE thing in the definition of the SASS that occurs sometimes in the
        encodings.
        Like "TidB = tid MULTIPLY 4 SCALE 4;"

        This is a right-shift by log2(val) bits without changing the bit length.
        """
        if not isinstance(val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not val % 2 == 0: raise ValueError("Invalid argument")
        if val <= 0: raise ValueError("Invalid argument")
        shift = int(math.log(val,2))
        if self.signed and self.bits[0] == 1:
            new = abs(self) # this will shave off the signed bit
            new.bits = tuple(shift*[0]) + new.bits[:-shift]
            # new.bit_len = len(new.bits)
            new = -new # this will add back the signed bit
        else:
            new = copy.copy(self)
            new.bits = tuple(shift*[0]) + new.bits[:-shift]
            # new.bit_len = len(new.bits)
        return new
    # def flex_multiply(self, val:int) -> SASS_Bits:
    #     """
    #     The same as multiply just with no restrictions in bit lengths
    #     """
    #     if not isinstance(val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     if not val % 2 == 0: raise ValueError("Invalid argument")
    #     if val <= 0: raise ValueError("Invalid argument")
    #     shift = int(math.log(val,2))
    #     if self.signed and self.bits[0] == 1:
    #         new_val = int(self.at_abs() << shift)
    #         new = SASS_Bits.from_int(new_val)
    #         new = -new
    #     else:
    #         new_val = int(self << shift)
    #         new = SASS_Bits.from_int(new_val)
    #     return new
    # def flex_scale(self, val) -> SASS_Bits:
    #     """
    #     The same as scale just with no restrictions in bit lengths
    #     """
    #     if not isinstance(val, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     if not val % 2 == 0: raise ValueError("Invalid argument")
    #     if val <= 0: raise ValueError("Invalid argument")
    #     shift = int(math.log(val,2))
    #     if self.signed and self.bits[0] == 1:
    #         new_val = int(self.at_abs() >> shift)
    #         new = SASS_Bits.from_int(new_val)
    #         new = -new
    #     else:
    #         new_val = int(self >> shift)
    #         new = SASS_Bits.from_int(new_val)
    #     return new
    # def msb(self, num_msb_bit:int):
    #     if not isinstance(num_msb_bit, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     new = copy.copy(self)
    #     new.bit_len = num_msb_bit
    #     new.bits = self.bits[:num_msb_bit]
    #     return new
    def at_negate(self) -> SASS_Bits:
        """Two's complement. Unsigned ones can't be negated => throw an exception if attempted"""
        if not self.signed: raise SASS_Bits_SignError("Unsigned one can't be negated")
        inv = tuple((i+1)%2 for i in self.bits)
        m = divmod(inv[-1]+1,2)
        res = [m[1]]
        new = copy.copy(self)
        [(m := divmod(inv[i]+m[0],2), res.insert(0, m[1]))  for i in range(-2,-self.bit_len,-1)]
        res.insert(0,inv[0])
        new.bits = tuple(res) 
        return new
    # def at_invert(self) -> SASS_Bits:
    #     """Flip each bit regardless of signed or not and positive or negative"""

    #     return SASS_Bits(tuple((i+1)%2 for i in self.bits), self.bit_len, self.signed) 
    # def at_abs(self) -> SASS_Bits:
    #     """If signed and negative, two's complement else return a copy of the original."""
    #     if not self.signed or self.bits[0] == 0: return copy.copy(self)
    #     return self.at_negate()
    # def at_sign(self) -> int:
    #     """If msb == 1, return 0, else 1"""
    #     if (not self.signed) or self.bits[0] == 0: return 1
    #     else: return 0

    def __add__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) + int(other))
        else: return SASS_Bits.from_int(int(self) + int(other), -max(self.bit_len, other.bit_len))
    def __sub__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) - int(other))
        else: return SASS_Bits.from_int(int(self) - int(other), -max(self.bit_len, other.bit_len))
    def __mul__(self, other:SASS_Bits|int|bool):
        if any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): return SASS_Bits.from_int(int(self) * int(other), -self.bit_len)
        elif isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) * int(other), -self.bit_len)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __matmul__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) * int(other))
        else: return SASS_Bits.from_int(int(self) * int(other), -max(self.bit_len, other.bit_len))
    def __truediv__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        raise Exception("Not supported")
    def __floordiv__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) // int(other))
        else: return SASS_Bits.from_int(int(self) // int(other), -max(self.bit_len, other.bit_len))
    def __mod__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, int) or isinstance(other, bool): return SASS_Bits.from_int(int(self) % int(other))
        else: return SASS_Bits.from_int(int(self) % int(other), -max(self.bit_len, other.bit_len))
    def __divmod__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        raise Exception("Not supported")
    def __pow__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        raise Exception("Not supported")
    # ==> unused!
    # def __lshift__(self, other:SASS_Bits|int|bool):
    #     if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     return SASS_Bits.from_int(int(self) << int(other), -max(self.bit_len, other.bit_len))
    # ==> unused!
    # def __rshift__(self, other:SASS_Bits|int|bool):
    #     if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
    #     return SASS_Bits.from_int(int(self) >> int(other), -max(self.bit_len, other.bit_len))
    def __and__(self, other:SASS_Bits):
        """bitwise & ('and' uses the __bool__ first then applies 'and' to the result)"""
        if not isinstance(other, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        req_bit_len = max(self.bit_len, other.bit_len)
        a = max(0, other.bit_len - self.bit_len)*(0,) + self.bits
        b = max(0, self.bit_len - other.bit_len)*(0,) + other.bits
        new_bits = tuple(i & j for i,j in zip(a,b))
        new = self.__new__(self.__class__)
        new.bits = new_bits
        new.signed = self.signed or other.signed
        new.bit_len = req_bit_len
        return new
    def __xor__(self, other:SASS_Bits):
        """bitwise ^"""
        if not isinstance(other, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        req_bit_len = max(self.bit_len, other.bit_len)
        a = max(0, other.bit_len - self.bit_len)*(0,) + self.bits
        b = max(0, self.bit_len - other.bit_len)*(0,) + other.bits
        new_bits = tuple(i ^ j for i,j in zip(a,b))
        new = self.__new__(self.__class__)
        new.bits = new_bits
        new.signed = self.signed or other.signed
        new.bit_len = req_bit_len
        return new
    def __or__(self, other:SASS_Bits):
        """bitwise | ('or' uses the __bool__ first then applies 'or' to the result)"""
        if not isinstance(other, SASS_Bits): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        req_bit_len = max(self.bit_len, other.bit_len)
        a = max(0, other.bit_len - self.bit_len)*(0,) + self.bits
        b = max(0, self.bit_len - other.bit_len)*(0,) + other.bits
        new_bits = tuple(i | j for i,j in zip(a,b))
        new = self.__new__(self.__class__)
        new.bits = new_bits
        new.signed = self.signed or other.signed
        new.bit_len = req_bit_len
        return new
    def __neg__(self):
        if self.signed:
            # keep the result signed (at least as many bits as we got going in)
            return SASS_Bits.from_int(-int(self), -self.bit_len)
        else:
            # not signed => add a bit if we go negative
            val = int(self)
            if val > 0: return SASS_Bits.from_int(-val, -(self.bit_len+1))
            else: raise Exception(sp.CONST__ERROR_ILLEGAL) # try to go positive with an unsigned value
    def __pos__(self):
        return self
    def __abs__(self):
        return SASS_Bits.from_int(abs(int(self)), -(self.bit_len-1))
    def __lshift__(self, num:int):
        """
        Bitwise left-shift by keeping signed/unsigned properties while increasing
        bit_len to match if necessary
        """
        if not any([isinstance(num, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        new = copy.copy(self)
        new.bits = self.bits + int(num)*(0,)
        new.bit_len = max(len(new.bits), self.bit_len)
        return new
    def __rshift__(self, num:int):
        """
        Bitwise right-shift by keeping signed/unsigned properties while also keeping
        bit_len the same. For example: 4 >> 1 == 2, -4 >> 1 == -66 (Note: this is different
        from the regular Python >>. For the equivalent Python >> for negative numbers,
        use int(-(SASS_Bits.from_int(-4, bit_len=8).at_abs() >> 1)))
        """
        if not any([isinstance(num, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        new = copy.copy(self)
        offs = 1 if new.signed else 0
        new.bits = tuple((self.bits[:offs] + int(num)*(0,) + self.bits[offs:])[:new.bit_len])
        return new
    def __lt__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) < int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) < int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __le__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) <= int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) <= int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __eq__(self, other:SASS_Bits|int|bool): # type: ignore
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) == int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) == int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __ne__(self, other:SASS_Bits|int|bool): # type: ignore
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) != int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) != int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __gt__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) > int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) > int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __ge__(self, other:SASS_Bits|int|bool):
        if not any([isinstance(other, tt) for tt in TT_DUAL_ARIT_OP]): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if isinstance(other, SASS_Bits): return int(self) >= int(other)
        elif isinstance(other, int) or isinstance(other, bool): return int(self) >= int(other)
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    def __hash__(self):
        # hashing based on bits would just be a tiny bit too much
        return self.__hash
    
if not 'TT_DUAL_ARIT_OP' in locals(): TT_DUAL_ARIT_OP = [SASS_Bits, bool, int]
if not 'TT_UNARY_OP' in locals(): TT_UNARY_OP = [SASS_Bits, bool]
if not 'TT_DUAL_BIT_OP' in locals(): TT_DUAL_BIT_OP = [SASS_Bits]

if __name__ == '__main__':
    ###########################################################################################
    # Tests
    ###########################################################################################
    SIGN_P = 1
    SIGN_N = 0

    tt0 = SASS_Bits.from_int(8, bit_len=8)
    print(tt0)
    int(tt0)

    print("cast: ", end='')
    tt0 = SASS_Bits.from_int(8, bit_len=8)
    tt1 = tt0.cast(16)
    assert(int(tt0) == int(tt1))
    assert(tt1.bit_len == 16)

    print("cast: ", end='')
    tt0 = SASS_Bits.from_int(8, bit_len=8, signed=1)
    tt1 = tt0.cast(16)
    assert(int(tt0) == int(tt1))
    assert(tt1.bit_len == 16)

    tt0 = SASS_Bits.from_int(-8, bit_len=8)
    tt1 = tt0.cast(16)
    assert(int(tt0) == int(tt1))
    assert(tt1.bit_len == 16)

    tt0 = SASS_Bits.from_int(int('0b111',2), bit_len=8, signed=1)
    tt1 = tt0.cast(4)
    assert(int(tt0) == int(tt1))
    assert(tt1.bit_len == 4)
    
    tt0 = SASS_Bits.from_int(-int('0b111',2), bit_len=8, signed=1)
    tt1 = tt0.cast(4)
    assert(int(tt0) == int(tt1))
    assert(tt1.bit_len == 4)

    tt0 = SASS_Bits.from_int(int('0b1111',2), bit_len=8, signed=1)
    tt1 = tt0.cast(4)
    assert(int('0b111',2) == int(tt1))
    assert(tt1.bit_len == 4)

    tt0 = SASS_Bits.from_int(int('0b1111',2), bit_len=8, signed=0)
    tt1 = tt0.cast(4)
    assert(int('0b1111',2) == int(tt1))
    assert(tt1.bit_len == 4)

    tt0 = SASS_Bits.from_int(-int('0b1111',2), bit_len=8, signed=1)
    tt1 = tt0.cast(4)
    assert(-int('0b111',2) == int(tt1))
    assert(tt1.bit_len == 4)
    print('ok')

    print("scale/multiply: ", end='')
    tt0 = SASS_Bits.from_int(8, bit_len=8)
    tt1 = tt0.scale(4)
    assert(int(tt0)//4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(8)
    tt1 = tt0.multiply(4)
    assert(0 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(8, bit_len=8)
    tt1 = tt0.multiply(4)
    assert(int(tt0)*4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(-8, bit_len=8)
    tt1 = tt0.multiply(4)
    assert(int(tt0)*4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(-8, bit_len=8)
    tt1 = tt0.scale(4)
    assert(int(tt0)//4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(8, bit_len=8)
    tt1 = tt0.multiply(4)
    assert(int(tt0)*4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(9, bit_len=8)
    tt1 = tt0.multiply(32)
    assert(int('00100000',2) == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(-9, bit_len=8)
    tt1 = tt0.multiply(32)
    assert(-int('00100000',2) == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)

    tt0 = SASS_Bits.from_int(-8, bit_len=8)
    tt1 = tt0.multiply(4)
    assert(int(tt0)*4 == int(tt1))
    assert(tt0.bit_len == tt1.bit_len)
    print('ok')

    print("Operators: ", end='')
    tt0 = SASS_Bits.from_int(0, bit_len=8)    
    tt7 = SASS_Bits.from_int(7, bit_len=8)
    tt5 = SASS_Bits.from_int(5, bit_len=8)
    tt8 = SASS_Bits.from_int(8, bit_len=8)
    tt4 = SASS_Bits.from_int(4, bit_len=8)
    ttm4 = SASS_Bits.from_int(-4, bit_len=8)

    # NOTE: this returns whoever is responsible for the result:
    # For this one, bla is a bool because False is the deciding factor
    bla = SASS_Bits.from_int(1) and False
    # For this one, bla is a SASS_Bits because it is the deciding factor
    bla = SASS_Bits.from_int(0) and True

    assert(bool(tt0 and tt7) == False)
    assert(bool(SASS_Bits.from_int(0) and True) == False)
    assert(bool(tt0 or tt7) == True)
    assert(bool(not tt0) == True)
    assert(bool(not tt7) == False)
    assert(-int(tt7) == int(-tt7))
    assert(int(tt7) == int(+tt7))
    assert(int(tt7 @ tt5) == 35)
    assert(int(tt7 @ ttm4) == -28)
    assert(int(tt7 * 5) == 35)
    assert(int(tt7 * SASS_Bits.from_int(5)) == 35)
    assert(int(tt7 * -4) == -28)
    assert(int(tt7 * SASS_Bits.from_int(-4)) == -28)
    assert(int(tt5 - tt7) == -2)
    assert(int(tt7 + tt5) == 12)
    assert(int(tt8 % tt5) == 3)
    assert(int(tt8 % tt4) == 0)
    assert(int(abs(ttm4)) == 4)
    assert(int(tt8 & tt5) == 0)
    assert(int(tt8 | tt5) == 13)
    assert(int(tt8 ^ tt4) == 12)
    assert(int(tt4 << 1) == 8)
    assert(int(tt4 >> 1) == 2)
    assert(int(ttm4 >> 1) == -66)
    assert(int(ttm4 << 1) == -8)
    print('ok')

    print('False value: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits((2,0,1), bit_len=3, signed=True) # type: ignore
    except ValueError:
        has_ex = True
    assert(has_ex)
    print('ok')

    print('Too long value: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits((1,0,0,1), bit_len=3, signed=True) # type: ignore
    except ValueError:
        has_ex = True
    assert(has_ex)
    print('ok')

    print('Bit size 1: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits((0,), bit_len=1, signed=True)
    except SASS_Bits_SignError:
        has_ex = True
    assert(has_ex)

    b1 = SASS_Bits((0,), bit_len=1, signed=False)
    # has_ex = False
    # try:
    #     b2 = b1.at_negate()
    # except SASS_Bits_SignError:
    #     has_ex = True
    # assert(has_ex)

    has_ex = False
    try:
        b2 = b1.as_signed()
    except SASS_Bits_SignError:
        has_ex = True
    assert(has_ex)
    
    # assert(SASS_Bits((0,), bit_len=1, signed=False).at_sign() == SIGN_P)
    # assert(SASS_Bits((1,), bit_len=1, signed=False).at_sign() == SIGN_P)
    assert(int(SASS_Bits((1,), bit_len=1, signed=False)) == 1)
    assert(int(SASS_Bits((0,), bit_len=1, signed=False)) == 0)

    print('ok')

    print('from_int: ', end='')
    v = SASS_Bits.from_int(0)
    assert(v.bit_len == 1)
    assert(v.signed == False)
    assert(int(v) == 0)
    v = SASS_Bits.from_int(1)
    assert(v.bit_len == 1)
    assert(v.signed == False)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(-1)
    assert(v.bit_len == 2)
    assert(v.signed == True)
    assert(int(v) == -1)
    v = SASS_Bits.from_int(1, bit_len=8, signed=1)
    assert(v.bit_len == 8)
    assert(v.signed == True)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(1, bit_len=8, signed=0)
    assert(v.bit_len == 8)
    assert(v.signed == False)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(1, signed=1)
    assert(v.bit_len == 2)
    assert(v.signed == True)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(1, signed=0)
    assert(v.bit_len == 1)
    assert(v.signed == False)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(-1, signed=1)
    assert(v.bit_len == 2)
    assert(v.signed == True)
    assert(int(v) == -1)
    v = SASS_Bits.from_int(1, bit_len=8, signed=0).to_signed()
    assert(v.bit_len == 9)
    assert(v.signed == True)
    assert(int(v) == 1)
    v = SASS_Bits.from_int(1, bit_len=8, signed=1).to_unsigned()
    assert(v.bit_len == 7)
    assert(v.signed == False)
    assert(int(v) == 1)

    has_ex = False
    try:
        v = SASS_Bits.from_int(1, bit_len=1, signed=1)
    except SASS_Bits_SignError:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(1, bit_len=1, signed=2)
    except ValueError:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(-1, signed=0)
    except SASS_Bits_SignError:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(-1).to_unsigned()
    except SASS_Bits_SignError:
        has_ex = True
    assert(has_ex)

    print('ok')
    print('assembly: ', end='')
    enc_bits = [0,0,0,0,0,0,0,0,0,0,0,0]
    enc_inds = (2,3,4)
    has_ex = False
    # try:
    #     res = SASS_Bits.from_int(7, 4, signed=0).assemble(enc_bits, enc_inds, 50)
    # except SASS_Bits_AssembleError:
    #     has_ex = True
    # assert(has_ex)
    
    # try:
    #     res = SASS_Bits.from_int(7, 3, signed=-1).assemble(enc_bits, enc_inds, 50)
    # except SASS_Bits_AssembleError:
    #     has_ex = True
    # assert(has_ex)

    res = SASS_Bits.from_int(7, 3, signed=0).assemble(enc_bits, enc_inds, 50) # type: ignore
    assert(res == [0,0,1,1,1,0,0,0,0,0,0,0])
    print('ok')

    # test bit sizes larger than 1
    bit_len = [2, 3, 5, 8, 12, 16, 17]
    perc = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.0, 1.1]
    print("bits|"+' unsigned '+'|' + " |"+'  signed  '+'|')
    for bl in bit_len:
        print(str(bl).zfill(2), ": ", end='')
        # unsigned
        mm = 2**bl
        p_ind = 0
        for r in range(0, mm):
            b = tuple(int(i) for i in bin(r)[2:].zfill(bl))
            s = SASS_Bits(b, len(b)) # type: ignore

            assert(int(s.as_unsigned()) == r)
            # assert(int(s.as_unsigned().at_abs()) == r)
            # assert(s.as_unsigned().at_sign() == SIGN_P)

            while r >= perc[p_ind]*(mm-1):
                p_ind += 1
                print('=',end='')

        # signed
        print('   ', end='')
        mm = 2**(bl-1)
        p_ind = 0
        for r in range(0, mm):
            b = tuple(int(i) for i in bin(r)[2:].zfill(bl))
            s = SASS_Bits(b, len(b)) # type: ignore

            assert(int(s) == r)

            # if r==0: assert(int(s.at_negate()) == -2**(bl-1))
            # else: assert(int(s.at_negate()) == -r)

            # assert(int(s.at_abs()) == r)
            # assert(int(s.at_negate().at_abs()) == r)
            # assert(s.at_sign() == SIGN_P)
            # assert(s.at_negate().at_sign() == SIGN_N)

            while r >= perc[p_ind]*(mm-1):
                p_ind += 1
                print('=',end='')
        print("  ok")
            