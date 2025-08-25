from py_sass_ext import SASS_Bits
from py_sass_ext import SASS_Range
from py_sass_ext import SASS_Enc_Dom
from py_sass_ext import BitVector
from py_sass_ext import IntVector
import pickle
import typing
import sys
import os

# a = SASS_Bits((1,0,1,0,0), 5, False)
# b = SASS_Bits((1,0,1,0,0), 5, False)

# print(a.bit_len())
# print(a.bits())

def test_range(r:SASS_Range, r_size:int):
    size = r.size()
    if(size != r_size): raise Exception("Unexpected")
    found = set()
    for i in range(0, 100000):
        val = r.pick()
        validate = val in r
        if not validate: raise Exception("Unexpected")
        found.add(int(val))
        if(len(found) == size): break
    
    if not len(found) == size: raise Exception("Unexpected")

def test_range_iter():
    r = SASS_Range(1,0,2,0,0)
    for i in range(5): print(r.pick())
    print("=v=")
    for b in r: print(b)
    print("=^=")
    for i in range(5): print(r.pick())
    print("=v=")
    for b in r: print(b)

def test_range_sized_iter():
    r = SASS_Range(1,0,10,0,0)
    a = set()
    print("=v=")
    for b in r.sized_iter(2):
        a.add(b)
        print(b)
    if len(a) != 2: raise Exception("Unexpected")
    print("=*=")
    a = set()
    for b in r.sized_iter(8): 
        a.add(b)
        print(b)
    if len(a) != 8: raise Exception("Unexpected")
    print("=^=")

    x = r
    pass

def test_sass_bits():
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
    tt7s = SASS_Bits.from_int(7, bit_len=8, signed=1)
    tt5 = SASS_Bits.from_int(5, bit_len=8)
    tt5s = SASS_Bits.from_int(5, bit_len=8, signed=1)
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
    assert(int(tt7s @ ttm4) == -28)
    assert(int(tt7 @ ttm4) == -28)
    assert(int(tt7 * 5) == 35)
    assert(int(tt7 * SASS_Bits.from_int(5)) == 35)
    assert(int(tt7s * -4) == -28)
    assert(int(tt7 * -4) == -28)
    assert(int(tt7s * SASS_Bits.from_int(-4)) == -28)
    assert(int(tt7 * SASS_Bits.from_int(-4)) == -28)
    assert(int(tt5s - tt7s) == -2)
    assert(int(tt5 - tt7s) == -2)
    assert(int(tt5s - tt7) == -2)
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

    
    y = int(tt7 * -4)
    SASS_Bits.enable_warnings()
    z = int(tt7 * -4)
    SASS_Bits.disable_warnings()
    w = int(tt7 * -4)
    # assert(int(ttm4 >> 1) == -66)
    # assert(int(ttm4 << 1) == -8)
    print('ok')

    b1 = SASS_Bits((1,0,1), bit_len=3, signed=True)
    ll = [
        SASS_Bits((0,0,0), bit_len=3, signed=False),
        SASS_Bits((0,0,1), bit_len=3, signed=False),
        SASS_Bits((0,1,0), bit_len=3, signed=False),
        SASS_Bits((0,1,1), bit_len=3, signed=False),
        SASS_Bits((1,0,0), bit_len=3, signed=False),
        SASS_Bits((1,0,1), bit_len=3, signed=False),
        SASS_Bits((1,1,0), bit_len=3, signed=False),
        SASS_Bits((1,1,1), bit_len=3, signed=False)
    ]

    ss = set(ll)
    
    ll_p = pickle.dumps(ll, pickle.HIGHEST_PROTOCOL)
    ll_up = pickle.loads(ll_p)
    assert(all(i==j for i,j in zip(ll, ll_up)))

    print('False value: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits([2,0,1], bit_len=3, signed=True)
    except:
        has_ex = True
    assert(has_ex)
    print('ok')

    print('Too long value: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits((1,0,0,1), bit_len=3, signed=True)
    except:
        has_ex = True
    assert(has_ex)
    print('ok')

    print('Bit size 1: ',end='')
    has_ex = False
    try:
        b1 = SASS_Bits((0,), bit_len=1, signed=True)
    except:
        has_ex = True
    assert(has_ex)

    b1 = SASS_Bits((0,), bit_len=1, signed=False)
    has_ex = False
    try:
        b2 = b1.at_negate()
    except:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        b2 = b1.as_signed()
    except:
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
    except:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(1, bit_len=1, signed=2)
    except:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(-1, signed=0)
    except:
        has_ex = True
    assert(has_ex)

    has_ex = False
    try:
        v = SASS_Bits.from_int(-1).to_unsigned()
    except:
        has_ex = True
    assert(has_ex)

    print('ok')
    print('assembly: ', end='')
    enc_bits = [0,0,0,0,0,0,0,0,0,0,0,0]
    enc_inds = (2,3,4)

    res = SASS_Bits.from_int(7, 3, signed=0).assemble(enc_bits, enc_inds, 50)
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
            s = SASS_Bits(b, len(b))

            while r >= perc[p_ind]*(mm-1):
                p_ind += 1
                print('=',end='')

        # signed
        print('   ', end='')
        mm = 2**(bl-1)
        p_ind = 0
        for r in range(0, mm):
            b = tuple(int(i) for i in bin(r)[2:].zfill(bl))
            s = SASS_Bits(b, len(b))

            assert(int(s) == r)

            while r >= perc[p_ind]*(mm-1):
                p_ind += 1
                print('=',end='')
        print("  ok")

def test_sets(sign:int):
    l = []
    for i in range(0, 10):
        l.append(SASS_Bits.from_int(i))

    s = set()
    for i in l:
        s.add(i)

    rr1 = SASS_Range(range_min=1, range_max=0, bit_len=8, signed=sign, bit_mask=3)
    res:typing.Set[SASS_Bits]|SASS_Range
    res = rr1.intersection(s)
    expected = set({0,4,8})
    assert(all(int(i) in expected for i in res) and all(r in res for r in expected))

    rr2 = SASS_Range(1, 0, 8, sign, 3)
    rr3 = rr1.intersection(rr2)
    assert(len(rr2) == len(rr1))
    assert(len(rr1) == len(rr3))
    assert(rr1 == rr2)
    assert(rr1 == rr3)
    mres = set()
    for val in rr3:
        assert(val in rr3)
        assert(val in rr1)
        assert(val in rr2)
        mres.add(val)

    for val in rr3:
        assert(val in rr3)
        mres.remove(val)
    assert(len(mres) == 0)
    


if __name__ == '__main__':
    ###########################################################################################
    # Tests SASS_Range
    ###########################################################################################
    test_range(SASS_Range(1,0,8,0,0), 256)
    test_range(SASS_Range(1,0,8,0,3), 64)
    test_range(SASS_Range(1,0,10,0,42), 128)
    test_range(SASS_Range(1,0,8,1,0), 256)
    test_range(SASS_Range(1,0,8,1,3), 64)
    test_range(SASS_Range(1,0,10,1,42), 128)

    test_range_iter()
    test_range_sized_iter()
    test_sets(sign=0)

    r = SASS_Range(0,65535,17,1,3)

    pass

    ###########################################################################################
    # Tests SASS_Bits
    ###########################################################################################
    test_sass_bits()

    ###########################################################################################
    # Tests EncDom
    ###########################################################################################
    # SASS_Enc_Dom.enable_compare_output()
    
    # location = "/".join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-3])
    # pp_1 = location + "/DocumentSASS/sm_{0}_domains.lz4"
    # enc_dom_1 = SASS_Enc_Dom(pp_1.format(50), show_progress=True)

    # key_values = {"E": {0, 1}, "LDInteger": {0, 1, 2, 3, 4, 5, 6, 7}}
    # fixed_res = enc_dom_1.fix("LD", key_values)
    # for i in enc_dom_1.fixed_iter("LD"):
    #     print(i)
    # pass

    # pp_2 = location + "/DocumentSASS/sm_{0}_domains.lz4"
    # enc_dom_2 = SASS_Enc_Dom(pp_2.format(90), show_progress=True)

    pass