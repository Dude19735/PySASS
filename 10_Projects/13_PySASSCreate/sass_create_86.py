import os
import _config as sp
from py_sass_ext import SASS_Bits
from py_cubin import SM_CuBin_File
from py_cubin import Instr_CuBin
from py_cubin import Instr_CuBin_Repr
from kk_sm import KK_SM
from sass_create_utils import SASS_Create_Utils

def overwrite_helper(val:tuple|int|bool, val_str:str, enc_vals:dict):
    if isinstance(val, tuple): v = val[-1]
    elif isinstance(val, int): v = val
    elif isinstance(val, bool): v = int(val)
    else: raise Exception(sp.CONST__ERROR_ILLEGAL)
    v_old:SASS_Bits = enc_vals[val_str]
    v_new:SASS_Bits = SASS_Bits.from_int(v, bit_len=v_old.bit_len, signed=v_old.signed)
    enc_vals[val_str] = v_new
    return enc_vals

class SASS_KK__f2f_f64_upconvert__R_R32_R_RRR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, 
                 Rd:tuple,
                 Rb_negate:bool, Rb_absolute:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = 'f2f_f64_upconvert__R_R32_R_RRR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Rb': SASS_Create_Utils.sass_bits_from_str('37U:8b'),           # set by param
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('38U:8b'),           # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # set by param
            'dstfmt.srcfmt': SASS_Create_Utils.sass_bits_from_str('19U:5b'),# keep 19, only 32 to 64 available, which is 19
            'ftz': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0, .noftz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0, .RN
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # set by param
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__i2f__Rb_32b:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, 
                 Rd:tuple, dst_fsize:int,
                 Rb_signed:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = 'i2f__Rb_32b'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        if not dst_fsize in (16, 32): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if Rb_signed: srcfmt = kk_sm.regs.SRCFMT__S32__5
        else: srcfmt = kk_sm.regs.SRCFMT__U32__4
        if dst_fsize == 16: dstfmt = kk_sm.regs.DSTFMT_F16_F32__F16__1
        else: dstfmt = kk_sm.regs.DSTFMT_F16_F32__F32__2

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('32U:8b'),           # set by param
            'dstfmt': SASS_Create_Utils.sass_bits_from_str('3U:2b'),        # F16 or F32, set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0, .RN (also the default)
            'Rb': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'srcfmt': SASS_Create_Utils.sass_bits_from_str('5U:3b'),        # SRCFMT "U32"=4 , "S32"=5; => set by flag
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(dstfmt, 'dstfmt', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(srcfmt, 'srcfmt', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__i2f_Rd64__Rb_32b:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, Rd:tuple, Rb_signed:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = 'i2f_Rd64__Rb_32b'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        if Rb_signed: srcfmt = kk_sm.regs.SRCFMT__S32__5
        else: srcfmt = kk_sm.regs.SRCFMT__U32__4

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('32U:8b'),           # set by param
            'dstfmt': SASS_Create_Utils.sass_bits_from_str('3U:2b'),        # Float64, has "F64"=3 only => leave untouched
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0, .RN (also the default)
            'Rb': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'srcfmt': SASS_Create_Utils.sass_bits_from_str('5U:3b'),        # SRCFMT "U32"=4 , "S32"=5; => set by flag
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(srcfmt, 'srcfmt', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__mufu__RRR_RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 mufuop:tuple,
                 Rd:tuple,
                 Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, rd:int=0x0, wr:int=0x0):
        class_name = 'mufu__RRR_RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'mufuop': SASS_Create_Utils.sass_bits_from_str('4U:4b'),        # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('50U:8b'),           # set by param
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Rb': SASS_Create_Utils.sass_bits_from_str('44U:8b'),           # set by param
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')    # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(mufuop, 'mufuop', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__dmul__RRR_RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0, rd:int=0x7, wr:int=0x7):
        class_name = 'dmul__RRR_RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('42U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('42U:8b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('4U:3b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('57U:6b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__fmul__RRR_RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = 'fmul__RRR_RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('37U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('38U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('31U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('53U:6b'),  
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'scale': SASS_Create_Utils.sass_bits_from_str('4U:3b'),         # keep 4=.noscale
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__mov__RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Rb_reuse:bool, Rb:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = 'mov__RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'PixMaskU04': SASS_Create_Utils.sass_bits_from_str('15U:4b'),   # pixel mask, keep 15 to get all bits
            'Rb': SASS_Create_Utils.sass_bits_from_str('34U:8b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('41U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('22U:6b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')        
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__fadd__RRR_RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = 'fadd__RRR_RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('37U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'ftz': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.noftz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('28U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__dadd__RRR_RR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = 'dadd__RRR_RR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('44U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('39U:6b'),  # REQ
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('4U:3b'),    # RD
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # WR
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__f2i_Rd64__Rb_64b:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, Rd:tuple,
                 Rb_absolute:bool, Rb_negate:bool, Rb:tuple, signed:bool,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        """
        Float to int, signed or unsigned
        DSTFMT_U64_S64 "U64"=6 , "S64"=7;
        """
        if signed: dst_format = kk_sm.regs.DSTFMT_U64_S64__S64__7
        else: dst_format = kk_sm.regs.DSTFMT_U64_S64__U64__6
        class_name = 'f2i_Rd64__Rb_64b'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('50U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('36U:8b'),           
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('6U:3b'),     # WR
            'dstfmt': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # DSTFMT_U64_S64
            'ftz': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.noftz
            'ntz': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nontz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('12U:6b'),  # REQ
            'rnd': SASS_Create_Utils.sass_bits_from_str('3U:2b'),           # keep 3 = .TRUNC
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('2U:3b'),    # RD
            'srcfmt': SASS_Create_Utils.sass_bits_from_str('3U:2b'),        # keep 3=.F64 only
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')    
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(dst_format, 'dstfmt', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__i2f_Rd64__IU_32b:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple, Rd:tuple, Sb:int,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        """
        32 bit int to 64 bit float
        """
        class_name = 'i2f_Rd64__IU_32b'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),
            'Sb': SASS_Create_Utils.sass_bits_from_str('610812097S:32b'), 
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('6U:3b'),     
            'dstfmt': SASS_Create_Utils.sass_bits_from_str('3U:2b'),        # destination format: keep 6 for F64 only
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('47U:6b'),  # REQ
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('3U:3b'),    # read barrier
            'srcfmt': SASS_Create_Utils.sass_bits_from_str('4U:3b'),        # source format: keep 4 for U32 only
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Sb, 'Sb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__i2f__IU_32b:
    """
    32 bit int to 16 or 32 bit float.
    dst_format: 16 or 32
    """
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple, Sb:int,
                 dst_format:int,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        
        if dst_format == 16: dst_format = kk_sm.regs.DSTFMT_F16_F32__F16__1
        elif dst_format == 32: dst_format = kk_sm.regs.DSTFMT_F16_F32__F32__2
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        class_name = 'i2f__IU_32b'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('45U:8b'),
            'Sb': SASS_Create_Utils.sass_bits_from_str('1S:32b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('2U:3b'),     # write barrier
            'dstfmt': SASS_Create_Utils.sass_bits_from_str('1U:2b'),        # destination format
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('34U:6b'),  # REQ
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('5U:3b'),    # read barrier
            'srcfmt': SASS_Create_Utils.sass_bits_from_str('5U:3b'),        # keep 4 = .U32 only
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Sb, 'Sb', enc_vals)
        enc_vals = overwrite_helper(dst_format, 'dstfmt', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__dfma__RCxR_RCxR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb_absolute:bool, Sb_negate:bool, Sb_offset:int, URb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RCxR_RCxR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),        # set by param
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'fmz': SASS_Create_Utils.sass_bits_from_str('1U:2b'),           # keep 0=.nofmz
            'rnd': SASS_Create_Utils.sass_bits_from_str('2U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat

            'Rd': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # set by param

            'Ra': SASS_Create_Utils.sass_bits_from_str('46U:8b'),           # set by param
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param

            'Sb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Sb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Sb_offset': SASS_Create_Utils.sass_bits_from_str('26578U:16b'),# set by param
            'URb': SASS_Create_Utils.sass_bits_from_str('34U:6b'),          # set by param

            'Rc': SASS_Create_Utils.sass_bits_from_str('30U:8b'),           # set by param
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('28U:6b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),    # set by param
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param

            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')        # keep 0
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_absolute, 'Sb@absolute', enc_vals)
        enc_vals = overwrite_helper(Sb_negate, 'Sb@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_offset, 'Sb_offset', enc_vals)
        enc_vals = overwrite_helper(URb, 'URb', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RsIR_RIR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb:int,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RsIR_RIR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            # Predicate configuration
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            
            # Extensions
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'), # keep 0=.nofmz
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'), # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'), # keep 0=.nosat
            # Destination register
            'Rd': SASS_Create_Utils.sass_bits_from_str('33U:8b'),           
            # Source register 1
            'Ra': SASS_Create_Utils.sass_bits_from_str('36U:8b'),           
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   
            # Source immediate value
            'Sb': SASS_Create_Utils.sass_bits_from_str('-1425045178S:32b'),
            # Source register 3
            'Rc': SASS_Create_Utils.sass_bits_from_str('30U:8b'),        
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),  
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            # Cache and barriers
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('5U:6b'),
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'), 
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b'),
            # Keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }

        # Overwrite predicate configuration
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        # Overwrite destination register
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        # Overwrite source register 1
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        # Overwrite source immediate value
        enc_vals = overwrite_helper(Sb, 'Sb', enc_vals)
        # Overwrite source register 3
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        # Overwrite cache bits and barriers
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        # Check if the new configuration is valid
        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], 
                                          enc_vals, throw=True)
        
        self.class_name = class_name
        self.enc_vals = enc_vals
        
class SASS_KK__dfma__RRC_RRC:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc_absolute:bool, Sc_negate:bool, Sc_addr:int, Sc_bank:int,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RRC_RRC"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('46U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('45U:8b'),
            'Sc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc_addr': SASS_Create_Utils.sass_bits_from_str('57404S:17b'),
            'Sc_bank': SASS_Create_Utils.sass_bits_from_str('7U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_absolute, 'Sc@absolute', enc_vals)
        enc_vals = overwrite_helper(Sc_negate, 'Sc@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_bank, 'Sc_bank', enc_vals)
        enc_vals = overwrite_helper(Sc_addr, 'Sc_addr', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RRCx_RRCx:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc_absolute:bool, Sc_negate:bool, Sc_offset:int, URc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RRCx_RRCx"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('43U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('45U:8b'),
            'Sc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Sc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc_offset': SASS_Create_Utils.sass_bits_from_str('61936U:16b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('44U:6b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('62U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param      
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_absolute, 'Sc@absolute', enc_vals)
        enc_vals = overwrite_helper(Sc_negate, 'Sc@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_offset, 'Sc_offset', enc_vals)
        enc_vals = overwrite_helper(URc, 'URc', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RRsI_RRI:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc:int,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RRsI_RRI"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('43U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('44U:8b'),
            'Sc': SASS_Create_Utils.sass_bits_from_str('-1993637945S:32b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('16U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc, 'Sc', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RRR_RRR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RRR_RRR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('34U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('42U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('5U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RRU_RRU:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 URc_absolute:bool, URc_negate:bool, URc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RRU_RRU"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('41U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('34U:8b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('39U:6b'),
            'URc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('24U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(URc, 'URc', enc_vals)
        enc_vals = overwrite_helper(URc_absolute, 'URc@absolute', enc_vals)
        enc_vals = overwrite_helper(URc_negate, 'URc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__dfma__RUR_RUR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 URb_absolute:bool, URb_negate:bool, URb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RUR_RUR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('44U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),
            'URb': SASS_Create_Utils.sass_bits_from_str('47U:6b'),
            'URb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('36U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(URb, 'URb', enc_vals)
        enc_vals = overwrite_helper(URb_absolute, 'URb@absolute', enc_vals)
        enc_vals = overwrite_helper(URb_negate, 'URb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__dfma__RCR_RCR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb_absolute:bool, Sb_negate:bool, Sb_addr:int, Sb_bank:int,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0, wr:int=0x7, rd:int=0x7):
        class_name = "dfma__RCR_RCR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Ra': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Rc': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # set by param
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'Sb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Sb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Sb_addr': SASS_Create_Utils.sass_bits_from_str('84S:17b'),     # set by param
            'Sb_bank': SASS_Create_Utils.sass_bits_from_str('27U:5b'),      # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0 = .RN
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),  # set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),     # set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b')     # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_absolute, 'Sb@absolute', enc_vals)
        enc_vals = overwrite_helper(Sb_negate, 'Sb@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_bank, 'Sb_bank', enc_vals)
        enc_vals = overwrite_helper(Sb_addr, 'Sb_addr', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__ffma__RCxR_RCxR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb_absolute:bool, Sb_negate:bool, Sb_offset:int, URb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RCxR_RCxR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),        # set by param
            'Ra': SASS_Create_Utils.sass_bits_from_str('46U:8b'),           # set by param
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rc': SASS_Create_Utils.sass_bits_from_str('30U:8b'),           # set by param
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # set by param
            'Sb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Sb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Sb_offset': SASS_Create_Utils.sass_bits_from_str('26578U:16b'),# set by param
            'URb': SASS_Create_Utils.sass_bits_from_str('34U:6b'),          # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('1U:2b'),           # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('28U:6b'),  # set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('2U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_absolute, 'Sb@absolute', enc_vals)
        enc_vals = overwrite_helper(Sb_negate, 'Sb@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_offset, 'Sb_offset', enc_vals)
        enc_vals = overwrite_helper(URb, 'URb', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RIR_RIR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb:int,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RIR_RIR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Ra': SASS_Create_Utils.sass_bits_from_str('36U:8b'),           # set by param
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Rc': SASS_Create_Utils.sass_bits_from_str('30U:8b'),           # set by param
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('33U:8b'),           # set by param
            'Sb': SASS_Create_Utils.sass_bits_from_str('-1425045178S:32b'), # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('5U:6b'),   # set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')    # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sb, 'Sb', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RRC_RRC:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc_absolute:bool, Sc_negate:bool, Sc_addr:int, Sc_bank:int,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RRC_RRC"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('46U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('45U:8b'),
            'Sc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc_addr': SASS_Create_Utils.sass_bits_from_str('57404S:17b'),
            'Sc_bank': SASS_Create_Utils.sass_bits_from_str('7U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_absolute, 'Sc@absolute', enc_vals)
        enc_vals = overwrite_helper(Sc_negate, 'Sc@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_bank, 'Sc_bank', enc_vals)
        enc_vals = overwrite_helper(Sc_addr, 'Sc_addr', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RRCx_RRCx:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc_absolute:bool, Sc_negate:bool, Sc_offset:int, URc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RRCx_RRCx"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('43U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('45U:8b'),
            'Sc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Sc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc_offset': SASS_Create_Utils.sass_bits_from_str('61936U:16b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('44U:6b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('62U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')       
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_absolute, 'Sc@absolute', enc_vals)
        enc_vals = overwrite_helper(Sc_negate, 'Sc@negate', enc_vals)
        enc_vals = overwrite_helper(Sc_offset, 'Sc_offset', enc_vals)
        enc_vals = overwrite_helper(URc, 'URc', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RRI_RRI:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Sc:int,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RRI_RRI"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('43U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('44U:8b'),
            'Sc': SASS_Create_Utils.sass_bits_from_str('-1993637945S:32b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('16U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sc, 'Sc', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RRR_RRR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RRR_RRR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('34U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('42U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('5U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),               # keep 0=.nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RRU_RRU:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Rb_reuse:bool, Rb_absolute:bool, Rb_negate:bool, Rb:tuple,
                 URc_absolute:bool, URc_negate:bool, URc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RRU_RRU"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('41U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'Rb@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('34U:8b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('39U:6b'),
            'URc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('24U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rb_reuse, 'reuse_src_b', enc_vals)
        enc_vals = overwrite_helper(Rb, 'Rb', enc_vals)
        enc_vals = overwrite_helper(Rb_absolute, 'Rb@absolute', enc_vals)
        enc_vals = overwrite_helper(Rb_negate, 'Rb@negate', enc_vals)
        enc_vals = overwrite_helper(URc, 'URc', enc_vals)
        enc_vals = overwrite_helper(URc_absolute, 'URc@absolute', enc_vals)
        enc_vals = overwrite_helper(URc_negate, 'URc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals
class SASS_KK__ffma__RUR_RUR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 URb_absolute:bool, URb_negate:bool, URb:tuple,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RUR_RUR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('48U:8b'),
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('44U:8b'),
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),
            'URb': SASS_Create_Utils.sass_bits_from_str('47U:6b'),
            'URb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('36U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(URb, 'URb', enc_vals)
        enc_vals = overwrite_helper(URb_absolute, 'URb@absolute', enc_vals)
        enc_vals = overwrite_helper(URb_negate, 'URb@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__ffma__RCR_RCR:
    def __init__(self, kk_sm:KK_SM,
                 Pg_negate:bool, Pg:tuple,
                 Rd:tuple,
                 Ra_reuse:bool, Ra_absolute:bool, Ra_negate:bool, Ra:tuple,
                 Sb_absolute:bool, Sb_negate:bool, Sb_addr:int, Sb_bank:int,
                 Rc_reuse:bool, Rc_absolute:bool, Rc_negate:bool, Rc:tuple,
                 usched_info_reg:tuple, req:int=0):
        class_name = "ffma__RCR_RCR"
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by param
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # set by param
            'Ra': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'Ra@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # set by param
            'Rc': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # set by param
            'Rc@absolute': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('40U:8b'),           # set by param
            'Sb@absolute': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'Sb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # set by param
            'Sb_addr': SASS_Create_Utils.sass_bits_from_str('84S:17b'),     # set by param
            'Sb_bank': SASS_Create_Utils.sass_bits_from_str('27U:5b'),      # set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'fmz': SASS_Create_Utils.sass_bits_from_str('2U:2b'),           # keep 0, nofmz
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('1U:1b'),   # set by param
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # keep 0 = .RN
            'sat': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # keep 0 = .nosat
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        enc_vals = overwrite_helper(Pg, 'Pg', enc_vals)
        enc_vals = overwrite_helper(Pg_negate, 'Pg@not', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)
        enc_vals = overwrite_helper(Ra, 'Ra', enc_vals)
        enc_vals = overwrite_helper(Ra_reuse, 'reuse_src_a', enc_vals)
        enc_vals = overwrite_helper(Ra_absolute, 'Ra@absolute', enc_vals)
        enc_vals = overwrite_helper(Ra_negate, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_absolute, 'Sb@absolute', enc_vals)
        enc_vals = overwrite_helper(Sb_negate, 'Sb@negate', enc_vals)
        enc_vals = overwrite_helper(Sb_bank, 'Sb_bank', enc_vals)
        enc_vals = overwrite_helper(Sb_addr, 'Sb_addr', enc_vals)
        enc_vals = overwrite_helper(Rc_reuse, 'reuse_src_c', enc_vals)
        enc_vals = overwrite_helper(Rc, 'Rc', enc_vals)
        enc_vals = overwrite_helper(Rc_absolute, 'Rc@absolute', enc_vals)
        enc_vals = overwrite_helper(Rc_negate, 'Rc@negate', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__ldg_uniform_RaRZ:
    def __init__(self, kk_sm:KK_SM, Rd:tuple, Ra:tuple, Ra_URb:tuple, ra_offset:int, RD:int, WR:int, REQ:int, USCHED_INFO:tuple, size=64):
        class_name = "ldg_uniform__RaRZ"

        if size == 128:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__128__6
        elif size == 64:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__64__5
        elif size == 32:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__32__4
        elif size == 16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__U16__2
        elif size == -16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__S16__3
        elif size == 8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__U8__0
        elif size == -8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__S8__1
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        if not (0 <= RD and RD <= 7): raise Exception('Invalid param')
        if not (0 <= WR and WR <= 7): raise Exception('Invalid param')
        # if RD == WR: raise Exception('Invalid param')
        if not (0 <= REQ and REQ <= 0b111111): raise Exception('Invalid param')

        # Ra, Ra_URb, Ra_offset
        # Rd
        # RD, WR
        # USCHED_INFO

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # 0x7
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),    # 0x0
            'Pnz': SASS_Create_Utils.sass_bits_from_str('7U:3b'),       # 0x7
            'Pnz@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # 0x0
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # 0x7
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),      # source base register set by param
            'Ra_URb': SASS_Create_Utils.sass_bits_from_str('32U:6b'),   # source base uniform register set by param
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('1286168S:24b'), # Set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('8U:8b'),        # target register set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),   # 0x0
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),       # .EN
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'), # WR set by param
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),         # .E
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),   # 0x0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'), # REQ set by param
            'sem': SASS_Create_Utils.sass_bits_from_str('3U:2b'),
            'sco': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'sp2': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # .nosp2
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'), # RD set by param
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),        # .64
            'usched_info': SASS_Create_Utils.sass_bits_from_str('5U:5b') # USCHED_INFO set by param
        }

        usched_info = USCHED_INFO[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new
        
        Rd_val = Rd[-1]
        Rd_val_old:SASS_Bits = enc_vals['Rd']
        Rd_val_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_val_old.bit_len, signed=Rd_val_old.signed)
        enc_vals['Rd'] = Rd_val_new

        Ra_val = Ra[-1]
        Ra_val_old:SASS_Bits = enc_vals['Ra']
        Ra_val_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_val_old.bit_len, signed=Ra_val_old.signed)
        enc_vals['Ra'] = Ra_val_new

        Ra_URb_val = Ra_URb[-1]
        Ra_URb_val_old:SASS_Bits = enc_vals['Ra_URb']
        Ra_URb_val_new:SASS_Bits = SASS_Bits.from_int(Ra_URb_val, bit_len=Ra_URb_val_old.bit_len, signed=Ra_URb_val_old.signed)
        enc_vals['Ra_URb'] = Ra_URb_val_new

        Ra_offset_old:SASS_Bits = enc_vals['Ra_offset']
        Ra_offset_new:SASS_Bits = SASS_Bits.from_int(ra_offset, bit_len=Ra_offset_old.bit_len, signed=Ra_offset_old.signed)
        enc_vals['Ra_offset'] = Ra_offset_new

        WR_old:SASS_Bits = enc_vals['dst_wr_sb']
        WR_new:SASS_Bits = SASS_Bits.from_int(WR, bit_len=WR_old.bit_len, signed=WR_old.signed)
        enc_vals['dst_wr_sb'] = WR_new

        RD_old:SASS_Bits = enc_vals['src_rel_sb']
        RD_new:SASS_Bits = SASS_Bits.from_int(RD, bit_len=RD_old.bit_len, signed=RD_old.signed)
        enc_vals['src_rel_sb'] = RD_new

        REQ_old:SASS_Bits = enc_vals['req_bit_set']
        REQ_new:SASS_Bits = SASS_Bits.from_int(REQ, bit_len=REQ_old.bit_len, signed=REQ_old.signed)
        enc_vals['req_bit_set'] = REQ_new

        enc_vals = overwrite_helper(size, 'sz', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__IADD3_NOIMM_RUR_RUR:
    def __init__(self, 
                 kk_sm:KK_SM, dest_reg:tuple, 
                 src_reg1_neg:bool, 
                 src_reg1:tuple, 
                 src_ureg2_neg:bool, 
                 src_ureg2:tuple, 
                 usched_info_reg:tuple):
        class_name = 'iadd3_noimm__RUR_RUR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('10U:8b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('0U:8b'),
            'URb': SASS_Create_Utils.sass_bits_from_str('9U:6b'),
            'URb@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('20U:5b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(dest_reg, 'Rd', enc_vals)
        enc_vals = overwrite_helper(src_reg1_neg, 'Ra@negate', enc_vals)
        enc_vals = overwrite_helper(src_reg1, 'Ra', enc_vals)
        enc_vals = overwrite_helper(src_ureg2_neg, 'URb@negate', enc_vals)
        enc_vals = overwrite_helper(src_ureg2, 'URb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__ULDC_CONST_RCR:
    def __init__(self, kk_sm:KK_SM, u_dest_reg:tuple, sz:tuple, m_bank:int, m_bank_addr:int, usched_info_reg:tuple):
        class_name = 'uldc_const__RCR'
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'UPg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('4U:3b'),
            'URd': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'Sa_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'Sa_addr': SASS_Create_Utils.sass_bits_from_str('352S:17b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('18U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(m_bank, 'Sa_bank', enc_vals)
        enc_vals = overwrite_helper(m_bank_addr, 'Sa_addr', enc_vals)
        enc_vals = overwrite_helper(u_dest_reg, 'URd', enc_vals)
        enc_vals = overwrite_helper(sz, 'sz', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.class_name = class_name
        self.enc_vals = enc_vals

class SASS_KK__imul__RRR_RRR:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, dest_reg:tuple, Ra:tuple, Rb:tuple, fmt:tuple, usched_info_reg:tuple):
        class_name = 'imul__RRR_RRR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('1U:3b'),            # predicate, set by params
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),        # invert (or not) predicate, set by params
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # source reg A, set by params
            'Rb': SASS_Create_Utils.sass_bits_from_str('47U:8b'),           # source reg B, set by params
            'Rd': SASS_Create_Utils.sass_bits_from_str('38U:8b'),           # destination reg, set by params
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # set to 0
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # type U32, S32
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # set to 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),  # Wait for nothing (63 == 0b111111)
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by params
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at_not = int(pred_invert)
        Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
        enc_vals['Pg@not'] = Pg_at_not_new

        Pg = pred[-1]
        Pg_old:SASS_Bits = enc_vals['Pg']
        Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
        enc_vals['Pg'] = Pg_new

        Rd = dest_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        Ra_val = Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        Rb_val = Rb[-1]
        Rb_old:SASS_Bits = enc_vals['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals['Rb'] = Rb_new

        fmt_val = fmt[-1]
        fmt_old:SASS_Bits = enc_vals['fmt']
        fmt_new:SASS_Bits = SASS_Bits.from_int(fmt_val, bit_len=fmt_old.bit_len, signed=fmt_old.signed)
        enc_vals['fmt'] = fmt_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__imul__RsIR_RIR:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, dest_reg:tuple, Ra:tuple, imm_val:int, fmt:tuple, usched_info_reg:tuple):
        class_name = 'imul__RsIR_RIR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('5U:3b'),            # predicate
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # invert (or not) predicate
            'Ra': SASS_Create_Utils.sass_bits_from_str('30U:8b'),           # source register, set by param
            'Rd': SASS_Create_Utils.sass_bits_from_str('39U:8b'),           # dest register, set by param
            'Sb': SASS_Create_Utils.sass_bits_from_str('-1803945533S:32b'), # immediate value, set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # set to 0
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # data type, set py param
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # set to 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),  # wait for nothing
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set by param
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at_not = int(pred_invert)
        Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
        enc_vals['Pg@not'] = Pg_at_not_new

        Pg = pred[-1]
        Pg_old:SASS_Bits = enc_vals['Pg']
        Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
        enc_vals['Pg'] = Pg_new

        Rd = dest_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        Ra_val = Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        val = imm_val
        Sb_old:SASS_Bits = enc_vals['Sb']
        Sb_new:SASS_Bits = SASS_Bits.from_int(val, bit_len=Sb_old.bit_len, signed=Sb_old.signed)
        enc_vals['Sb'] = Sb_new

        fmt_val = fmt[-1]
        fmt_old:SASS_Bits = enc_vals['fmt']
        fmt_new:SASS_Bits = SASS_Bits.from_int(fmt_val, bit_len=fmt_old.bit_len, signed=fmt_old.signed)
        enc_vals['fmt'] = fmt_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__isetp__RRR_RRR_noEX:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, Pu:tuple, Ra:tuple, icmp:tuple, Rb:tuple, fmt:tuple, usched_info_reg:tuple):
        """integer set predicate: Pu = (True if Ra [icmp] Rb else False)
        """
        class_name = 'isetp__RRR_RRR_noEX'
        
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by params
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),        # set by params
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # PT, input from chaining, not used here, keep PT
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # don't negate
            'Pu': SASS_Create_Utils.sass_bits_from_str('4U:3b'),            # target set by params
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # PT
            'Ra': SASS_Create_Utils.sass_bits_from_str('39U:8b'),           # source Ra set by params
            'Rb': SASS_Create_Utils.sass_bits_from_str('37U:8b'),           # source Rb set by params
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # AND for chaining, AND with PT is whatever is on the left of it
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # data type (like U32) set by params
            'icmp': SASS_Create_Utils.sass_bits_from_str('4U:3b'),          # compare, set by param
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),  # wait for nothing
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # overwritten by params
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at_not = int(pred_invert)
        Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
        enc_vals['Pg@not'] = Pg_at_not_new

        Pg = pred[-1]
        Pg_old:SASS_Bits = enc_vals['Pg']
        Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
        enc_vals['Pg'] = Pg_new

        Pu_val = Pu[-1]
        Pu_old:SASS_Bits = enc_vals['Pu']
        Pu_new:SASS_Bits = SASS_Bits.from_int(Pu_val, bit_len=Pu_old.bit_len, signed=Pu_old.signed)
        enc_vals['Pu'] = Pu_new

        Ra_val = Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        icmp_val = icmp[-1]
        icmp_old:SASS_Bits = enc_vals['icmp']
        icmp_new:SASS_Bits = SASS_Bits.from_int(icmp_val, bit_len=icmp_old.bit_len, signed=icmp_old.signed)
        enc_vals['icmp'] = icmp_new

        Rb_val = Rb[-1]
        Rb_old:SASS_Bits = enc_vals['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals['Rb'] = Rb_new

        fmt_val = fmt[-1]
        fmt_old:SASS_Bits = enc_vals['fmt']
        fmt_new:SASS_Bits = SASS_Bits.from_int(fmt_val, bit_len=fmt_old.bit_len, signed=fmt_old.signed)
        enc_vals['fmt'] = fmt_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__isetp_simple__RUR_RUR_noEX:
    def __init__(self):
        class_name = 'isetp_simple__RUR_RUR_noEX'
        enc_vals = {

        }


class SASS_KK__ISETP_RUR_RUR_NOEX:
    def __init__(self, kk_sm:KK_SM, target_Pu:tuple, aux_pred:tuple, Ra:tuple, URb:tuple, comp_op:tuple, f_type:tuple, bop_op:tuple, pred_invert:bool, pred:tuple, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'isetp__RUR_RUR_noEX'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        # FORMAT PREDICATE @[!]Predicate(PT):Pg
        # Opcode /ICmpAll:icmp /FMT(S32):fmt /Bop:bop
        #     Predicate:Pu
        #     ,Predicate:Pv
        #     ,Register:Ra /REUSE(noreuse):reuse_src_a
        #     ,UniformRegister:URb
        #     ,[!]Predicate:Pp
        # $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$
        # $( { ? USCHED_INFO(DRAIN):usched_info } )$
        # $( { ? BATCH_T(NOP):batch_t } )$
        # $( { ? PM_PRED(PMN):pm_pred } )$

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'icmp': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URb': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('13U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pu_val = target_Pu[-1]
        Pu_old:SASS_Bits = enc_vals['Pu']
        Pu_new:SASS_Bits = SASS_Bits.from_int(Pu_val, bit_len=Pu_old.bit_len, signed=Pu_old.signed)
        enc_vals['Pu'] = Pu_new

        Pv = aux_pred[-1]
        Pv_old:SASS_Bits = enc_vals['Pv']
        Pv_new:SASS_Bits = SASS_Bits.from_int(Pv, bit_len=Pv_old.bit_len, signed=Pv_old.signed)
        enc_vals['Pv'] = Pv_new

        Ra_val = Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        URb_val = URb[-1]
        URb_old:SASS_Bits = enc_vals['URb']
        URb_new:SASS_Bits = SASS_Bits.from_int(URb_val, bit_len=URb_old.bit_len, signed=URb_old.signed)
        enc_vals['URb'] = URb_new

        icmp = comp_op[-1]
        icmp_old:SASS_Bits = enc_vals['icmp']
        icmp_new:SASS_Bits = SASS_Bits.from_int(icmp, bit_len=icmp_old.bit_len, signed=icmp_old.signed)
        enc_vals['icmp'] = icmp_new

        bop = bop_op[-1]
        bop_old:SASS_Bits = enc_vals['bop']
        bop_new:SASS_Bits = SASS_Bits.from_int(bop, bit_len=bop_old.bit_len, signed=bop_old.signed)
        enc_vals['bop'] = bop_new

        fmt = f_type[-1]
        fmt_old:SASS_Bits = enc_vals['fmt']
        fmt_new:SASS_Bits = SASS_Bits.from_int(fmt, bit_len=fmt_old.bit_len, signed=fmt_old.signed)
        enc_vals['fmt'] = fmt_new

        Pp_at_not = int(pred_invert)
        Pp_at_not_old:SASS_Bits = enc_vals['Pp@not']
        Pp_at_not_new:SASS_Bits = SASS_Bits.from_int(Pp_at_not, bit_len=Pp_at_not_old.bit_len, signed=Pp_at_not_old.signed)
        enc_vals['Pp@not'] = Pp_at_not_new

        Pp = pred[-1]
        Pp_old:SASS_Bits = enc_vals['Pp']
        Pp_new:SASS_Bits = SASS_Bits.from_int(Pp, bit_len=Pp_old.bit_len, signed=Pp_old.signed)
        enc_vals['Pp'] = Pp_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__IADD3_NOIMM_RRR_RRR:
    def __init__(self, kk_sm:KK_SM, target_reg:tuple, negate_Ra:bool, src_Ra:tuple, negate_Rb:bool, src_Rb:tuple, negate_Rc:bool, src_Rc:tuple, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'iadd3_noimm__RRR_RRR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('24U:8b'),
            'Pu': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('2U:8b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('4U:8b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Rd = target_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        Ra_neg = int(negate_Ra)
        Ra_neg_old:SASS_Bits = enc_vals['Ra@negate']
        Ra_neg_new:SASS_Bits = SASS_Bits.from_int(Ra_neg, bit_len=Ra_neg_old.bit_len, signed=Ra_neg_old.signed)
        enc_vals['Ra@negate'] = Ra_neg_new

        Ra = src_Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        Rb_neg = int(negate_Rb)
        Rb_neg_old:SASS_Bits = enc_vals['Rb@negate']
        Rb_neg_new:SASS_Bits = SASS_Bits.from_int(Rb_neg, bit_len=Rb_neg_old.bit_len, signed=Rb_neg_old.signed)
        enc_vals['Rb@negate'] = Rb_neg_new

        Rb = src_Rb[-1]
        Rb_old:SASS_Bits = enc_vals['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals['Rb'] = Rb_new

        Rc_neg = int(negate_Rc)
        Rc_neg_old:SASS_Bits = enc_vals['Rc@negate']
        Rc_neg_new:SASS_Bits = SASS_Bits.from_int(Rc_neg, bit_len=Rc_neg_old.bit_len, signed=Rc_neg_old.signed)
        enc_vals['Rc@negate'] = Rc_neg_new

        Rc = src_Rc[-1]
        Rc_old:SASS_Bits = enc_vals['Rc']
        Rc_new:SASS_Bits = SASS_Bits.from_int(Rc, bit_len=Rc_old.bit_len, signed=Rc_old.signed)
        enc_vals['Rc'] = Rc_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__IADD3_IMM_RsIR_RIR:
    def __init__(self, kk_sm:KK_SM, target_reg:tuple, negate_Ra:bool, Ra:tuple, src_imm:int, negate_Rc:bool, Rc:tuple, usched_info_reg:tuple, req:int=0x0):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'iadd3_imm__RsIR_RIR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # predicate, set to PT
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # negate predicate, set to False
            'Rd': SASS_Create_Utils.sass_bits_from_str('33U:8b'),           # target reg, set by param
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set to PT
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set to PT
            'Ra': SASS_Create_Utils.sass_bits_from_str('33U:8b'),           # source reg Ra, set by param
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'Ra@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),     # negate source Ra, set by param
            'Sb': SASS_Create_Utils.sass_bits_from_str('899591266S:32b'),   # source imm val, set by param
            'Rc': SASS_Create_Utils.sass_bits_from_str('46U:8b'),           # source reg Rc, set by param
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # noreuse
            'Rc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),     # negate Rc, set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),  # wait for nothing
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')    # set by param
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        val = target_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(val, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        Ra_neg = int(negate_Ra)
        Ra_neg_old:SASS_Bits = enc_vals['Ra@negate']
        Ra_neg_new:SASS_Bits = SASS_Bits.from_int(Ra_neg, bit_len=Ra_neg_old.bit_len, signed=Ra_neg_old.signed)
        enc_vals['Ra@negate'] = Ra_neg_new

        val = Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        val = src_imm
        Sb_old:SASS_Bits = enc_vals['Sb']
        Sb_new:SASS_Bits = SASS_Bits.from_int(val, bit_len=Sb_old.bit_len, signed=Sb_old.signed)
        enc_vals['Sb'] = Sb_new

        Rc_neg = int(negate_Rc)
        Rc_neg_old:SASS_Bits = enc_vals['Rc@negate']
        Rc_neg_new:SASS_Bits = SASS_Bits.from_int(Rc_neg, bit_len=Rc_neg_old.bit_len, signed=Rc_neg_old.signed)
        enc_vals['Rc@negate'] = Rc_neg_new

        val = Rc[-1]
        Rc_old:SASS_Bits = enc_vals['Rc']
        Rc_new:SASS_Bits = SASS_Bits.from_int(val, bit_len=Rc_old.bit_len, signed=Rc_old.signed)
        enc_vals['Rc'] = Rc_new

        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__UIADD3_URsIUR_RIR:
    def __init__(self, kk_sm:KK_SM, target_ureg:tuple, src_ureg_neg:bool, src_ureg:tuple, src_imm:int, usched_info_reg:tuple, req=0b111111):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'uiadd3__URsIUR_RIR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        enc_vals = {
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'UPg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'URd': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'UPu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'UPv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'URa': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'URa@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sb': SASS_Create_Utils.sass_bits_from_str('10S:32b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('63U:6b'),
            'URc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('6U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        URd = target_ureg[-1]
        URd_old:SASS_Bits = enc_vals['URd']
        URd_new:SASS_Bits = SASS_Bits.from_int(URd, bit_len=URd_old.bit_len, signed=URd_old.signed)
        enc_vals['URd'] = URd_new

        URa_neg = int(src_ureg_neg)
        URa_neg_old:SASS_Bits = enc_vals['URa@negate']
        URa_neg_new:SASS_Bits = SASS_Bits.from_int(URa_neg, bit_len=URa_neg_old.bit_len, signed=URa_neg_old.signed)
        enc_vals['URa@negate'] = URa_neg_new

        URa = src_ureg[-1]
        URa_old:SASS_Bits = enc_vals['URa']
        URa_new:SASS_Bits = SASS_Bits.from_int(URa, bit_len=URa_old.bit_len, signed=URa_old.signed)
        enc_vals['URa'] = URa_new

        Sb = src_imm
        Sb_old:SASS_Bits = enc_vals['Sb']
        Sb_new:SASS_Bits = SASS_Bits.from_int(Sb, bit_len=Sb_old.bit_len, signed=Sb_old.signed)
        enc_vals['Sb'] = Sb_new

        REQ_old:SASS_Bits = enc_vals['req_bit_set']
        REQ_new:SASS_Bits = SASS_Bits.from_int(req, bit_len=REQ_old.bit_len, signed=REQ_old.signed)
        enc_vals['req_bit_set'] = REQ_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__SEL_RRR_RRR:
    def __init__(self, kk_sm:KK_SM, target_reg:tuple, reg1:tuple, reg2:tuple, pred_invert:bool, pred:tuple, usched_info_reg:tuple):
        class_name = 'sel__RRR_RRR'
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('0U:8b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('13U:8b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('134U:8b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Rd = target_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        Ra = reg1[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        Rb = reg2[-1]
        Rb_old:SASS_Bits = enc_vals['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals['Rb'] = Rb_new

        Pp_at_not = int(pred_invert)
        Pp_at_not_old:SASS_Bits = enc_vals['Pp@not']
        Pp_at_not_new:SASS_Bits = SASS_Bits.from_int(Pp_at_not, bit_len=Pp_at_not_old.bit_len, signed=Pp_at_not_old.signed)
        enc_vals['Pp@not'] = Pp_at_not_new

        Pp = pred[-1]
        Pp_old:SASS_Bits = enc_vals['Pp']
        Pp_new:SASS_Bits = SASS_Bits.from_int(Pp, bit_len=Pp_old.bit_len, signed=Pp_old.signed)
        enc_vals['Pp'] = Pp_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__ISETP_RCR_RCR:
    def __init__(self, kk_sm:KK_SM, target_pred:tuple, aux_pred:tuple, reg:tuple, m_bank:int, m_bank_addr:int, comp_op:tuple, f_type:tuple, bop_op:tuple, pred_invert:bool, pred:tuple, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'isetp__RCR_RCR_noEX'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'icmp': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sb_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'Sb_addr': SASS_Create_Utils.sass_bits_from_str('352S:17b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('13U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pu = target_pred[-1]
        Pu_old:SASS_Bits = enc_vals['Pu']
        Pu_new:SASS_Bits = SASS_Bits.from_int(Pu, bit_len=Pu_old.bit_len, signed=Pu_old.signed)
        enc_vals['Pu'] = Pu_new

        Pv = aux_pred[-1]
        Pv_old:SASS_Bits = enc_vals['Pv']
        Pv_new:SASS_Bits = SASS_Bits.from_int(Pv, bit_len=Pv_old.bit_len, signed=Pv_old.signed)
        enc_vals['Pv'] = Pv_new

        Ra = reg[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        Sb_bank = m_bank
        Sb_bank_old:SASS_Bits = enc_vals['Sb_bank']
        Sb_bank_new:SASS_Bits = SASS_Bits.from_int(Sb_bank, bit_len=Sb_bank_old.bit_len, signed=Sb_bank_old.signed)
        enc_vals['Sb_bank'] = Sb_bank_new

        Sb_addr = m_bank_addr
        Sb_addr_old:SASS_Bits = enc_vals['Sb_addr']
        Sb_addr_new:SASS_Bits = SASS_Bits.from_int(Sb_addr, bit_len=Sb_addr_old.bit_len, signed=Sb_addr_old.signed)
        enc_vals['Sb_addr'] = Sb_addr_new

        icmp = comp_op[-1]
        icmp_old:SASS_Bits = enc_vals['icmp']
        icmp_new:SASS_Bits = SASS_Bits.from_int(icmp, bit_len=icmp_old.bit_len, signed=icmp_old.signed)
        enc_vals['icmp'] = icmp_new

        bop = bop_op[-1]
        bop_old:SASS_Bits = enc_vals['bop']
        bop_new:SASS_Bits = SASS_Bits.from_int(bop, bit_len=bop_old.bit_len, signed=bop_old.signed)
        enc_vals['bop'] = bop_new

        fmt = f_type[-1]
        fmt_old:SASS_Bits = enc_vals['fmt']
        fmt_new:SASS_Bits = SASS_Bits.from_int(fmt, bit_len=fmt_old.bit_len, signed=fmt_old.signed)
        enc_vals['fmt'] = fmt_new

        Pp_at_not = int(pred_invert)
        Pp_at_not_old:SASS_Bits = enc_vals['Pp@not']
        Pp_at_not_new:SASS_Bits = SASS_Bits.from_int(Pp_at_not, bit_len=Pp_at_not_old.bit_len, signed=Pp_at_not_old.signed)
        enc_vals['Pp@not'] = Pp_at_not_new

        Pp = pred[-1]
        Pp_old:SASS_Bits = enc_vals['Pp']
        Pp_new:SASS_Bits = SASS_Bits.from_int(Pp, bit_len=Pp_old.bit_len, signed=Pp_old.signed)
        enc_vals['Pp'] = Pp_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals__isetp = enc_vals
        self.class_name__isetp = class_name

class SASS_KK__uisetp__URsIUR_URIR:
    def __init__(self, kk_sm:KK_SM, negate_upred:bool, upred:tuple, target_UPu:tuple, src_URa:tuple, icmp:tuple, fmt:tuple, src_imm_val:int, usched_info_reg:tuple):
        """integer set predicate: UPu = (True if URa [icmp] imm_val else False) using data type fmp
        """
        class_name = 'uisetp__URsIUR_URIR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'UPg': SASS_Create_Utils.sass_bits_from_str('4U:3b'),           # upred, set by param
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),       # negate upred, set by param
            'UPu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           # output predicate, set by param
            'UPv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           # space filler, set to UPT
            'URa': SASS_Create_Utils.sass_bits_from_str('41U:6b'),          # input register, set by param
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # used data type, set by param
            'icmp': SASS_Create_Utils.sass_bits_from_str('2U:3b'),          # compare operation, set by param
            'Sb': SASS_Create_Utils.sass_bits_from_str('-21S:32b'),          # compared immediate value
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # chaining operation, set to AND
            'UPp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           # chaining input predicate, set to UPT
            'UPp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # chaining input predicate negation, set to false
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # wait for nothing
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b')    # set by param
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(upred, 'UPg', enc_vals)
        enc_vals = overwrite_helper(negate_upred, 'UPg@not', enc_vals)
        enc_vals = overwrite_helper(target_UPu, 'UPu', enc_vals)
        enc_vals = overwrite_helper(src_URa, 'URa', enc_vals)
        enc_vals = overwrite_helper(icmp, 'icmp', enc_vals)
        enc_vals = overwrite_helper(fmt, 'fmt', enc_vals)
        enc_vals = overwrite_helper(src_imm_val, 'Sb', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__ISETP_RsIR_RIR:
    def __init__(self, kk_sm:KK_SM, target_pred:tuple, aux_pred:tuple, reg:tuple, imm:int, comp_op:tuple, fmt:tuple, bop_op:tuple, invert_Pp:bool, Pp:tuple, usched_info_reg:tuple):
        class_name = 'isetp__RsIR_RIR_noEX'
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        # @[!]Pg ISETP [!]Pu [!]Pv Ra SImm:Sb [!]Pp
        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # predicate
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),    # negate predicate
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('19U:8b'),
            'Sb': SASS_Create_Utils.sass_bits_from_str('365444356S:32b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'icmp': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # negate chaining input predicate
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),    # chaining input predicate
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(target_pred, 'Pu', enc_vals)
        enc_vals = overwrite_helper(aux_pred, 'Pv', enc_vals)
        enc_vals = overwrite_helper(reg, 'Ra', enc_vals)
        enc_vals = overwrite_helper(imm, 'Sb', enc_vals)
        enc_vals = overwrite_helper(comp_op, 'icmp', enc_vals)
        enc_vals = overwrite_helper(bop_op, 'bop', enc_vals)
        enc_vals = overwrite_helper(fmt, 'fmt', enc_vals)
        enc_vals = overwrite_helper(invert_Pp, 'Pp@not', enc_vals)
        enc_vals = overwrite_helper(Pp, 'Pp', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__imad__RRU_RRU:
    """multiply-add

    Calculate: Rd = Ra*Rb + URc
    """
    def __init__(self, kk_sm:KK_SM, invert_Pg:bool, Pg:tuple, Rd:tuple, Ra:tuple, Rb:tuple, negate_URc:bool, URc:tuple, usched_info_reg:tuple, reuse_a:bool=False, reuse_b:bool=False):
        class_name = 'imad__RRU_RRU'
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        # FORMAT PREDICATE @[!]Predicate(PT):Pg
        # Opcode /LOOnly(LO):wide /FMT(S32):fmt
        #     Register:Rd
        #     ,Register:Ra /REUSE(noreuse):reuse_src_a
        #     ,Register:Rb /REUSE(noreuse):reuse_src_b
        #     ,[-]UniformRegister:URc
        # $( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$
        # $( { ? USCHED_INFO(DRAIN):usched_info } )$
        # $( { ? BATCH_T(NOP):batch_t } )$
        # $( { ? PM_PRED(PMN):pm_pred } )$

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('1U:3b'), # replace
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'), # replace
            'Ra': SASS_Create_Utils.sass_bits_from_str('243U:8b'), # replace
            'Rb': SASS_Create_Utils.sass_bits_from_str('130U:8b'), # replace
            'Rd': SASS_Create_Utils.sass_bits_from_str('126U:8b'), # replace
            'URc': SASS_Create_Utils.sass_bits_from_str('37U:6b'), # replace
            'URc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'), # replace
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b') # replace
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        invert_Pg_val = int(invert_Pg)
        invert_Pg_val_old:SASS_Bits = enc_vals['Pg@not']
        invert_Pg_val_new:SASS_Bits = SASS_Bits.from_int(invert_Pg_val, bit_len=invert_Pg_val_old.bit_len, signed=invert_Pg_val_old.signed)
        enc_vals['Pg@not'] = invert_Pg_val_new

        Pg_val = Pg[-1]
        Pg_val_old:SASS_Bits = enc_vals['Pg']
        Pg_val_new:SASS_Bits = SASS_Bits.from_int(Pg_val, bit_len=Pg_val_old.bit_len, signed=Pg_val_old.signed)
        enc_vals['Pg'] = Pg_val_new

        Rd_val = Rd[-1]
        Rd_val_old:SASS_Bits = enc_vals['Rd']
        Rd_val_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_val_old.bit_len, signed=Rd_val_old.signed)
        enc_vals['Rd'] = Rd_val_new

        Ra_val = Ra[-1]
        Ra_val_old:SASS_Bits = enc_vals['Ra']
        Ra_val_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_val_old.bit_len, signed=Ra_val_old.signed)
        enc_vals['Ra'] = Ra_val_new

        Rb_val = Rb[-1]
        Rb_val_old:SASS_Bits = enc_vals['Rb']
        Rb_val_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_val_old.bit_len, signed=Rb_val_old.signed)
        enc_vals['Rb'] = Rb_val_new

        negate_URc_val = int(negate_URc)
        negate_URc_val_old:SASS_Bits = enc_vals['URc@negate']
        negate_URc_val_new:SASS_Bits = SASS_Bits.from_int(negate_URc_val, bit_len=negate_URc_val_old.bit_len, signed=negate_URc_val_old.signed)
        enc_vals['URc@negate'] = negate_URc_val_new

        URc_val = URc[-1]
        URc_val_old:SASS_Bits = enc_vals['URc']
        URc_val_new:SASS_Bits = SASS_Bits.from_int(URc_val, bit_len=URc_val_old.bit_len, signed=URc_val_old.signed)
        enc_vals['URc'] = URc_val_new

        reuse_a_val = int(reuse_a)
        reuse_a_val_old:SASS_Bits = enc_vals['reuse_src_a']
        reuse_a_val_new:SASS_Bits = SASS_Bits.from_int(reuse_a_val, bit_len=reuse_a_val_old.bit_len, signed=reuse_a_val_old.signed)
        enc_vals['reuse_src_a'] = reuse_a_val_new

        reuse_b_val = int(reuse_b)
        reuse_b_val_old:SASS_Bits = enc_vals['reuse_src_b']
        reuse_b_val_new:SASS_Bits = SASS_Bits.from_int(reuse_b_val, bit_len=reuse_b_val_old.bit_len, signed=reuse_b_val_old.signed)
        enc_vals['reuse_src_b'] = reuse_b_val_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__IMAD_RRsI_RRI:
    def __init__(self, kk_sm:KK_SM, Rd:tuple, Ra:tuple, Rb:tuple, imm_val:int, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'imad__RRsI_RRI'
        # print(src_cubin.get_instr(0,4).all_enc_vals[0])
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('5U:8b'), # target register
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'), # source register 1
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('255U:8b'), # source register 2
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc': SASS_Create_Utils.sass_bits_from_str('0S:32b'), # immediate value
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Rd_val = Rd[-1]
        Rd_val_old:SASS_Bits = enc_vals['Rd']
        Rd_val_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_val_old.bit_len, signed=Rd_val_old.signed)
        enc_vals['Rd'] = Rd_val_new

        Ra_val = Ra[-1]
        Ra_val_old:SASS_Bits = enc_vals['Ra']
        Ra_val_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_val_old.bit_len, signed=Ra_val_old.signed)
        enc_vals['Ra'] = Ra_val_new

        Rb_val = Rb[-1]
        Rb_val_old:SASS_Bits = enc_vals['Rb']
        Rb_val_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_val_old.bit_len, signed=Rb_val_old.signed)
        enc_vals['Rb'] = Rb_val_new

        Sc_old:SASS_Bits = enc_vals['Sc']
        Sb_new:SASS_Bits = SASS_Bits.from_int(imm_val, bit_len=Sc_old.bit_len, signed=Sc_old.signed)
        enc_vals['Sc'] = Sb_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals__imad_imm = enc_vals
        self.class_name__imad_imm = class_name

class SASS_KK__IMAD_RRC_RRC:
    def __init__(self, kk_sm:KK_SM, Rd:tuple, Ra:tuple, Rb:tuple, m_bank:int, m_bank_offset:int, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,2).class_name)
        class_name = 'imad__RRC_RRC'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('3U:8b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Sc_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'Sc_addr': SASS_Create_Utils.sass_bits_from_str('364S:17b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }
        
        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Rd_val = Rd[-1]
        Rd_val_old:SASS_Bits = enc_vals['Rd']
        Rd_val_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_val_old.bit_len, signed=Rd_val_old.signed)
        enc_vals['Rd'] = Rd_val_new

        Ra_val = Ra[-1]
        Ra_val_old:SASS_Bits = enc_vals['Ra']
        Ra_val_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_val_old.bit_len, signed=Ra_val_old.signed)
        enc_vals['Ra'] = Ra_val_new

        Rb_val = Rb[-1]
        Rb_val_old:SASS_Bits = enc_vals['Rb']
        Rb_val_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_val_old.bit_len, signed=Rb_val_old.signed)
        enc_vals['Rb'] = Rb_val_new

        Sc_bank_old:SASS_Bits = enc_vals['Sc_bank']
        Sc_bank_new:SASS_Bits = SASS_Bits.from_int(m_bank, bit_len=Sc_bank_old.bit_len, signed=Sc_bank_old.signed)
        enc_vals['Sc_bank'] = Sc_bank_new

        Sc_addr_old:SASS_Bits = enc_vals['Sc_addr']
        Sc_addr_new:SASS_Bits = SASS_Bits.from_int(m_bank_offset, bit_len=Sc_addr_old.bit_len, signed=Sc_addr_old.signed)
        enc_vals['Sc_addr'] = Sc_addr_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__NOP:
    def __init__(self, kk_sm:KK_SM, usched_info_reg=None):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        if usched_info_reg is None: usched_info_reg = kk_sm.regs.USCHED_INFO__DRAIN__0

        # print(src_cubin.get_instr(0,3).class_name)
        class_name = 'nop_'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,3),0))
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name ], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__umov__UR:
    def __init__(self, kk_sm:KK_SM, negate_upred:bool, upred:tuple, target_ureg:tuple, source_ureg:tuple, usched_info_reg:tuple):
        class_name = 'umov__UR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'UPg': SASS_Create_Utils.sass_bits_from_str('2U:3b'),           # predicate, set by param
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # negate predicate, set py param
            'URb': SASS_Create_Utils.sass_bits_from_str('31U:6b'),          # source ureg, set by param
            'URd': SASS_Create_Utils.sass_bits_from_str('45U:6b'),          # destination ureg, set py param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # wait for nothing
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set py param
        }

        enc_vals = overwrite_helper(negate_upred, 'UPg@not', enc_vals)
        enc_vals = overwrite_helper(upred, 'UPg', enc_vals)
        enc_vals = overwrite_helper(target_ureg, 'URd', enc_vals)
        enc_vals = overwrite_helper(source_ureg, 'URb', enc_vals)
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__UMOVImm:
    def __init__(self, kk_sm:KK_SM, negate_upred:bool, upred:tuple, target_ureg:tuple, imm_val:int, usched_info_reg:tuple):
        class_name = 'umov__UI'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Sb': SASS_Create_Utils.sass_bits_from_str('1U:32b'),           # value, set by param
            'UPg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           # set by param
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # set by param
            'URd': SASS_Create_Utils.sass_bits_from_str('63U:6b'),          # target, set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),  # wait for nothing
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')    # set by param
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        UPg_at = int(negate_upred)
        UPg_at_old:SASS_Bits = enc_vals['UPg@not']
        UPg_at_new:SASS_Bits = SASS_Bits.from_int(UPg_at, bit_len=UPg_at_old.bit_len, signed=UPg_at_old.signed)
        enc_vals['UPg@not'] = UPg_at_new

        UPg_val = upred[-1]
        UPg_val_old:SASS_Bits = enc_vals['UPg']
        UPg_val_new:SASS_Bits = SASS_Bits.from_int(UPg_val, bit_len=UPg_val_old.bit_len, signed=UPg_val_old.signed)
        enc_vals['UPg'] = UPg_val_new

        URd_val = target_ureg[-1]
        URd_val_old:SASS_Bits = enc_vals['URd']
        URd_val_new:SASS_Bits = SASS_Bits.from_int(URd_val, bit_len=URd_val_old.bit_len, signed=URd_val_old.signed)
        enc_vals['URd'] = URd_val_new

        Sb_old:SASS_Bits = enc_vals['Sb']
        Sb_new:SASS_Bits = SASS_Bits.from_int(imm_val, bit_len=Sb_old.bit_len, signed=Sb_old.signed)
        enc_vals['Sb'] = Sb_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__MOVImm:
    def __init__(self, kk_sm:KK_SM, exec_pred_inv:bool, exec_pred:tuple, target_reg:tuple, imm_val:int, usched_info_reg:tuple, req:int=0x0):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,3).class_name)
        class_name = 'mov__RI'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,3),0))
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('4U:8b'), # this is the destination register
            'Sb': SASS_Create_Utils.sass_bits_from_str('5U:32b'), # this is the immediate value
            'PixMaskU04': SASS_Create_Utils.sass_bits_from_str('15U:4b'), # this one is always 0xf
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at = int(exec_pred_inv)
        Pg_at_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_new:SASS_Bits = SASS_Bits.from_int(Pg_at, bit_len=Pg_at_old.bit_len, signed=Pg_at_old.signed)
        enc_vals['Pg@not'] = Pg_at_new

        Pg_val = exec_pred[-1]
        Pg_val_old:SASS_Bits = enc_vals['Pg']
        Pg_val_new:SASS_Bits = SASS_Bits.from_int(Pg_val, bit_len=Pg_val_old.bit_len, signed=Pg_val_old.signed)
        enc_vals['Pg'] = Pg_val_new

        Rd_val = target_reg[-1]
        Rd_val_old:SASS_Bits = enc_vals['Rd']
        Rd_val_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_val_old.bit_len, signed=Rd_val_old.signed)
        enc_vals['Rd'] = Rd_val_new

        Sb_old:SASS_Bits = enc_vals['Sb']
        Sb_new:SASS_Bits = SASS_Bits.from_int(imm_val, bit_len=Sb_old.bit_len, signed=Sb_old.signed)
        enc_vals['Sb'] = Sb_new

        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__MOV_Rc:
    """
    Move ptr of input param to register. For example, param_offset = 0x160 for param 1, 0x168 for param 2 (if it's an 8 byte val)
    etc.
    param_reg = R2 (for example) will hold the address ptr

    For example:
    Class: mov__RC
    U0: @PT [MOV] R2, Sb[UImm(0x0)][SImm(0x168)], UImm(0xf)
        $REQ:[{'BITSET'}]=0x0, $USCHED_INFO:[{'W2', 'trans2'}]=0x12, $BATCH_T:[{'NOP'}]=0x0, $PM_PRED:[{'PMN'}]=0x0, $RD:[{'UImm'}]=0x7, $WR:[{'UImm'}]=0x7
        [0x630]: SM[86], ENCW[128], INSTR[0xfe40000000f0000005a0000027a02]
        Move [Movement Instructions]
    """
    def __init__(self, kk_sm:KK_SM, Sb_bank:int, Sb_addr:int, Rd:tuple, usched_info_reg:tuple):
        # print(src_cubin.get_instr(0,3).class_name)
        class_name__mov = 'mov__RC'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,3),0))
        enc_vals__mov = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('2U:8b'), # target register, the one that will hold the ptr to the variable/ptr
            'Sb_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'), # mem bank index (for input params it's 0x0)
            'Sb_addr': SASS_Create_Utils.sass_bits_from_str('352S:17b'), # mem bank offset (for input params it starts at 0x160 and increases aligned with var size, like 8 for a ptr, 4 for an int, etc)
            'PixMaskU04': SASS_Create_Utils.sass_bits_from_str('15U:4b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }
        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals__mov['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__mov['usched_info'] = usched_info_new

        Rd_val = Rd[-1]
        Rd_old:SASS_Bits = enc_vals__mov['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals__mov['Rd'] = Rd_new

        Sb_bank_val = Sb_bank
        Sb_bank_old:SASS_Bits = enc_vals__mov['Sb_bank']
        Sb_bank_new:SASS_Bits = SASS_Bits.from_int(Sb_bank_val, bit_len=Sb_bank_old.bit_len, signed=Sb_bank_old.signed)
        enc_vals__mov['Sb_bank'] = Sb_bank_new

        Sb_addr_val = Sb_addr
        Sb_addr_old:SASS_Bits = enc_vals__mov['Sb_addr']
        Sb_addr_new:SASS_Bits = SASS_Bits.from_int(Sb_addr_val, bit_len=Sb_addr_old.bit_len, signed=Sb_addr_old.signed)
        enc_vals__mov['Sb_addr'] = Sb_addr_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name__mov], enc_vals__mov, throw=True)
        self.enc_vals = enc_vals__mov
        self.class_name = class_name__mov

class SASS_KK__ULDC:
    """
    This one produces something like this:
      Class: uldc_const__RCR
      U0: @PT [ULDC]/64 UR4, Sa[UImm(0x0)][SImm(0x118)]
          $REQ:[{'BITSET'}]=0x0, $USCHED_INFO:[{'W5EG', 'WAIT5_END_GROUP'}]=0x5, $BATCH_T:[{'NOP'}]=0x0, $PM_PRED:[{'PMN'}]=0x0, $RD:[{'UImm'}]=0x7, $WR:[{'UImm'}]=0x7
          [0x610]: SM[86], ENCW[128], INSTR[0xfca0000000a000000460000047ab9]
          Load from Constant Memory into a Uniform Register [Uniform Datapath Instructions]
    """
    def __init__(self, kk_sm:KK_SM, uniform_reg:tuple, m_offset:int, usched_info_reg:tuple, size:int=64):
        if size == 64:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__64__5
        elif size == 32:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__32__4
        elif size == 16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__U16__2
        elif size == -16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__S16__3
        elif size == 8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__U8__0
        elif size == -8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64__S8__1
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)
        
        # print(src_cubin.get_instr(0,1).class_name)
        class_name = 'uldc_const__RCR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,1),0))
        enc_vals = {
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # keep 0
            'UPg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),            # "U8"=0 , "S8"=1 , "U16"=2 , "S16"=3, "32"=4 , "64"=5
            'URd': SASS_Create_Utils.sass_bits_from_str('4U:6b'),           # target register like UR4 above
            'Sa_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),       # keep 0
            'Sa_addr': SASS_Create_Utils.sass_bits_from_str('280S:17b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # Wait for no one
            'usched_info': SASS_Create_Utils.sass_bits_from_str('5U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')        # keep 0
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(uniform_reg, 'URd', enc_vals)
        enc_vals = overwrite_helper(m_offset, 'Sa_addr', enc_vals)
        enc_vals = overwrite_helper(size, 'sz', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__stg__sImmOffset:
    def __init__(self, kk_sm:KK_SM, offset_Ra:tuple, ra_offset:int, Rb:tuple, usched_info_reg:tuple, req:int=0b111111, rd:int=0x7):
        class_name = 'stg__sImmOffset'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),                # predicate PT
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),            # don't negate predicate
            'Ra': SASS_Create_Utils.sass_bits_from_str('32U:8b'),               # address register, set by param
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('-6670312S:24b'), # offset immediate value, set by param
            'Rb': SASS_Create_Utils.sass_bits_from_str('40U:8b'),               # source register, set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),           # set to 0
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),               # 1 == .EN
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),                 # 1 == .E
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # set to 0
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # 0 = .noprivate
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),      # req, set by param
            'sco': SASS_Create_Utils.sass_bits_from_str('3U:3b'),               # 5 = .SYS
            'sem': SASS_Create_Utils.sass_bits_from_str('3U:2b'),               # 3 = .MMIO
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),        # RD barrier, set by param
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),                # 5 = .64
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')        # set by param
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Ra_val = offset_Ra[-1]
        Ra_old:SASS_Bits = enc_vals['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals['Ra'] = Ra_new

        Ra_offset_val = ra_offset
        Ra_offset_old:SASS_Bits = enc_vals['Ra_offset']
        Ra_offset_new:SASS_Bits = SASS_Bits.from_int(Ra_offset_val, bit_len=Ra_offset_old.bit_len, signed=Ra_offset_old.signed)
        enc_vals['Ra_offset'] = Ra_offset_new

        Rb_val = Rb[-1]
        Rb_old:SASS_Bits = enc_vals['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals['Rb'] = Rb_new

        req_bits_old = enc_vals['req_bit_set']
        req_bits_new:SASS_Bits = SASS_Bits.from_int(req, bit_len=req_bits_old.bit_len, signed=req_bits_old.signed)
        enc_vals['req_bit_set'] = req_bits_new

        rd_old = enc_vals['src_rel_sb']
        rd_new:SASS_Bits = SASS_Bits.from_int(rd, bit_len=rd_old.bit_len, signed=rd_old.signed)
        enc_vals['src_rel_sb'] = rd_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__STG_RaRZ:
    def __init__(self, kk_sm:KK_SM, uniform_reg:tuple, offset:int, source_reg:tuple, usched_info_reg:tuple, rd:int=0x7, req:int=0x0, size:int=64):
        if size == 128:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__128__6
        elif size == 64:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__64__5
        elif size == 32:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__32__4
        elif size == 16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__U16__2
        elif size == -16:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__S16__3
        elif size == 8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__U8__0
        elif size == -8:
            size = kk_sm.regs.SZ_U8_S8_U16_S16_32_64_128__S8__1
        else: raise Exception(sp.CONST__ERROR_ILLEGAL)

        # print(src_cubin.get_instr(0,1).class_name)
        class_name = 'stg_uniform__RaRZ'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,1),0))
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),      # "U8"=0, "S8"=1, "U16"=2, "S16"=3, "32"=4, "64"=5, "128"=6
            'sem': SASS_Create_Utils.sass_bits_from_str('3U:2b'),     # "CONSTANT"=0 , "WEAK"=1 , "STRONG"=2 , "MMIO"=3;
            'sco': SASS_Create_Utils.sass_bits_from_str('5U:3b'),     # "nosco"=0 , "CTA"=1 , "SM"=2 , "VC"=3 , "GPU"=4 , "SYS"=5;
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'), # "noprivate"=0 , "PRIVATE"=1
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'Ra_URc': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('0S:24b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('2U:8b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(uniform_reg, 'Ra_URc', enc_vals)
        enc_vals = overwrite_helper(offset, 'Ra_offset', enc_vals)
        enc_vals = overwrite_helper(source_reg, 'Rb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(size, 'sz', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        # Make stuff accessible---
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__STG_memdesc_Ra64:
    """
    Class: stg_memdesc__Ra64
    U0: @PT [STG]/E/EN/64/WEAK/nosco/noprivate/noexp_desc memoryDescriptor[UR4][R2/64, SImm(0x0)], R4
        $REQ:[{'BITSET'}]=0x0, $RD:[{'UImm'}]=0x7, $USCHED_INFO:[{'W1', 'trans1'}]=0x11, $BATCH_T:[{'NOP'}]=0x0, $PM_PRED:[{'PMN'}]=0x0, $WR:[{'UImm'}]=0x7
        C[51:51]=0x1
        [0x650]: SM[86], ENCW[128], INSTR[0xfe2000c101b040000000402007986]
        Store to Global Memory [Load/Store Instructions]
    """
    def __init__(self, kk_sm:KK_SM, uniform_reg:tuple, target_reg:tuple, target_offset:int, source_reg:tuple, usched_info_reg:tuple):
        ##############################################################################################
        # NOTE: leave the comments for reference => some template for how to construct these objects 
        # and get rid of the templates afterwards...
        # NOTE: Check out SASS_KK_CSR2 for a probably cleanest example
        ##############################################################################################

        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.cs2r.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,5).class_name)

        class_name__stg = 'stg_memdesc__Ra64'
        enc_vals__stg = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'sem': SASS_Create_Utils.sass_bits_from_str('1U:2b'),
            'sco': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'e_desc': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra_URc': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('2U:8b'),
            'input_reg_sz_64_dist': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('0S:24b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('4U:8b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals__stg['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__stg['usched_info'] = usched_info_new

        Ra_URc_val = uniform_reg[-1]
        Ra_URc_old:SASS_Bits = enc_vals__stg['Ra_URc']
        Ra_URc_new:SASS_Bits = SASS_Bits.from_int(Ra_URc_val, bit_len=Ra_URc_old.bit_len, signed=Ra_URc_old.signed)
        enc_vals__stg['Ra_URc'] = Ra_URc_new

        Ra_val = target_reg[-1]
        Ra_old:SASS_Bits = enc_vals__stg['Ra']
        Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        enc_vals__stg['Ra'] = Ra_new

        Ra_offset_val = target_offset
        Ra_offset_old:SASS_Bits = enc_vals__stg['Ra_offset']
        Ra_offset_new:SASS_Bits = SASS_Bits.from_int(Ra_offset_val, bit_len=Ra_offset_old.bit_len, signed=Ra_offset_old.signed)
        enc_vals__stg['Ra_offset'] = Ra_offset_new

        Rb_val = source_reg[-1]
        Rb_old:SASS_Bits = enc_vals__stg['Rb']
        Rb_new:SASS_Bits = SASS_Bits.from_int(Rb_val, bit_len=Rb_old.bit_len, signed=Rb_old.signed)
        enc_vals__stg['Rb'] = Rb_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name__stg], enc_vals__stg, throw=True)
        # Make stuff accessible
        self.enc_vals = enc_vals__stg
        self.class_name = class_name__stg

class SASS_KK__CS2R:
    def __init__(self, 
                 kk_sm:KK_SM, 
                 target_reg:tuple, 
                 usched_info_reg:tuple, 
                 req:int=0,
                 clk=True,
                 special_reg:tuple|None=None):
        ##############################################################################################
        # NOTE: leave the comments for reference => some template for how to construct these objects 
        # and get rid of the templates afterwards...
        ##############################################################################################
        # This is the location for some template
        # Create a template with the required instruction and follow the procedure outlined by the comments
        # to create an instruction template

        # It is also possible to use kk_sm.sass.encdom but that one requires potentially an enormous
        # amount of RAM. For very targeted instruction generation, this approach is better.

        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.cs2r.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,2).class_name)
        class_name = 'cs2r_'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))
        # This is some generic encoding like it frequently occcurs inside a cubin
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('4U:8b'), # target register
            'SRa': SASS_Create_Utils.sass_bits_from_str('80U:8b'), # special register source
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('18U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        # Replace some values with other ones
        # This is a tuple: the first two entries are the path, the last one is the value
        # For example: ('Register', 'R4', 4)
        # This one could come from the outside too...
        Rd = target_reg[-1]
        Rd_old:SASS_Bits = enc_vals['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals['Rd'] = Rd_new

        # For example, this is the value of SR_CLOCKLO that is already in the enc_vals
        if clk:
            SRa =kk_sm.regs.SpecialRegister__SR_CLOCKLO__80
        else:
            if special_reg is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
            SRa = special_reg

        usched_info_old = enc_vals['usched_info']
        usched_info = usched_info_reg[-1]
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        req_bits_old = enc_vals['req_bit_set']
        req_bits_new:SASS_Bits = SASS_Bits.from_int(req, bit_len=req_bits_old.bit_len, signed=req_bits_old.signed)
        enc_vals['req_bit_set'] = req_bits_new

        enc_vals = overwrite_helper(SRa, 'SRa', enc_vals)

        # Make sure that we didn't write crap into the instruction
        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__EXIT:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, Pp_invert:bool, Pp:tuple, usched_info_reg:tuple):
        class_name = 'exit_'
        # enc_vals_exit = exit_instr.all_enc_vals[0]
        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'mode': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'no_atexit': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('21U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at_not = int(pred_invert)
        Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
        enc_vals['Pg@not'] = Pg_at_not_new

        Pg = pred[-1]
        Pg_old:SASS_Bits = enc_vals['Pg']
        Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
        enc_vals['Pg'] = Pg_new

        Pp_at_not = int(Pp_invert)
        Pp_at_not_old:SASS_Bits = enc_vals['Pp@not']
        Pp_at_not_new:SASS_Bits = SASS_Bits.from_int(Pp_at_not, bit_len=Pp_at_not_old.bit_len, signed=Pp_at_not_old.signed)
        enc_vals['Pp@not'] = Pp_at_not_new

        Pp_val = Pp[-1]
        Pp_old:SASS_Bits = enc_vals['Pp']
        Pp_new:SASS_Bits = SASS_Bits.from_int(Pp_val, bit_len=Pp_old.bit_len, signed=Pp_old.signed)
        enc_vals['Pp'] = Pp_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

# class SASS_KK__r2p__RIR:
#     def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, usched_info_reg:tuple):
#         class_name = 'r2p__RIR'

#         ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
#         print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

#         enc_vals = {
#             'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
#             'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
#             'Ra': SASS_Create_Utils.sass_bits_from_str('36U:8b'),
#             'Sb': SASS_Create_Utils.sass_bits_from_str('-285402349U:32b'),
#             'a_bsel': SASS_Create_Utils.sass_bits_from_str('2U:2b'),        # 
#             'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
#             'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
#             'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # leep 0, nowait
#             'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),   # keep 0, noreuse
#             'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b')   # set py params
#         }

#         usched_info = usched_info_reg[-1]
#         usched_info_old:SASS_Bits = enc_vals['usched_info']
#         usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
#         enc_vals['usched_info'] = usched_info_new

#         Pg_at_not = int(pred_invert)
#         Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
#         Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
#         enc_vals['Pg@not'] = Pg_at_not_new

#         Pg = pred[-1]
#         Pg_old:SASS_Bits = enc_vals['Pg']
#         Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
#         enc_vals['Pg'] = Pg_new

#         Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

#         # Make stuff accessible
#         self.enc_vals = enc_vals
#         self.class_name = class_name

class SASS_KK__ldg__uImmOffset:
    def __init__(self, kk_sm:KK_SM, 
                 Ra_offset:int, Rd:tuple, usched_info_reg:tuple, 
                 wr:int=0x7, rd:int=0x7, req=0, 
                 ext:dict={'cop': '1U:3b', 'e': '1U:1b', 'private': '1U:1b', 'sco': '1U:3b', 'sem': '2U:2b', 'sp2': '3U:2b', 'sz': '4U:3b'}):
        class_name = 'ldg__uImmOffset'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        # All illegal combinations are in this table:
        # TABLES_mem_1_illegal_encodings(sem,sco,private)
        #    0 0 1 -> 1
        #    0 1 0 -> 2
        #    0 1 1 -> 3
        #    0 2 0 -> 9
        #    0 2 1 -> 11
        #    0 3 0 -> 13
        #    0 3 1 -> 14
        #    0 4 0 -> 15

        # All legal ones are in here
        # TABLES_mem_1(sem,sco,private)
        #    0 0 0 -> 4
        #    2 2 1 -> 4
        #    1 2 1 -> 4
        #    2 1 1 -> 4
        #    1 1 1 -> 4
        #    2 4 1 -> 6
        #    1 4 1 -> 6
        #    2 3 1 -> 6
        #    1 3 1 -> 6
        #    1 0 0 -> 0
        #    1 5 1 -> 0
        #    2 2 0 -> 5
        #    2 1 0 -> 5
        #    2 4 0 -> 7
        #    2 3 0 -> 7
        #    2 5 0 -> 10
        #    2 5 1 -> 10
        #    3 4 0 -> 8
        #    3 1 0 -> 8
        #    3 2 0 -> 8
        #    3 3 0 -> 8
        #    3 5 0 -> 12
        #(i) 0 0 1 -> 1
        #(i) 0 1 0 -> 2
        #(i) 0 1 1 -> 3
        #(i) 0 2 0 -> 9
        #(i) 0 2 1 -> 11
        #(i) 0 3 0 -> 13
        #(i) 0 3 1 -> 14
        #(i) 0 4 0 -> 15
        
        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # all predicates PT and not inverted
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        #  ...
            'Pnz': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           #  ...
            'Pnz@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       #  ...
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            #  ...
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # keep RZ
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('0U:24b'),    # set py param
            'Rd': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # set by param
            'cop': SASS_Create_Utils.sass_bits_from_str(ext['cop']), # "EF"=0 , "EN"=1 , "EL"=2 , "LU"=3 , "EU"=4 , "NA"=5
            'e': SASS_Create_Utils.sass_bits_from_str(ext['e']),             # "noe"=0 , "E"=1
            'sem': SASS_Create_Utils.sass_bits_from_str(ext['sem']),         # "CONSTANT"=0 , "WEAK"=1 , "STRONG"=2 , "MMIO"=3;
            'sco': SASS_Create_Utils.sass_bits_from_str(ext['sco']),         # "nosco"=0 , "CTA"=1 , "SM"=2 , "VC"=3 , "GPU"=4 , "SYS"=5;
            'private': SASS_Create_Utils.sass_bits_from_str(ext['private']), # "noprivate"=0 , "PRIVATE"=1;
            'sp2': SASS_Create_Utils.sass_bits_from_str(ext['sp2']),         # "nosp2"=0 , "LTC64B"=1 , "LTC128B"=2 , "LTC256B"=3
            'sz': SASS_Create_Utils.sass_bits_from_str(ext['sz']),           # "U8"=0 , "S8"=1 , "U16"=2 , "S16"=3 , "32"=4 , "64"=5 , "128"=6
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),     # WR, set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # RD, set by param
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # REQ, set by param
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),       # keep 0
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')    # set by param
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(wr, 'dst_wr_sb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)
        enc_vals = overwrite_helper(Ra_offset, 'Ra_offset', enc_vals)
        enc_vals = overwrite_helper(Rd, 'Rd', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__BRA:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, Pp_invert:bool, Pp:tuple, imm_val:int, usched_info_reg:tuple):
        class_name = 'bra_'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'cond': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'depth': SASS_Create_Utils.sass_bits_from_str('1U:2b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'sImm': SASS_Create_Utils.sass_bits_from_str('-791113152S:50b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b')
        }

        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals['usched_info'] = usched_info_new

        Pg_at_not = int(pred_invert)
        Pg_at_not_old:SASS_Bits = enc_vals['Pg@not']
        Pg_at_not_new:SASS_Bits = SASS_Bits.from_int(Pg_at_not, bit_len=Pg_at_not_old.bit_len, signed=Pg_at_not_old.signed)
        enc_vals['Pg@not'] = Pg_at_not_new

        Pg = pred[-1]
        Pg_old:SASS_Bits = enc_vals['Pg']
        Pg_new:SASS_Bits = SASS_Bits.from_int(Pg, bit_len=Pg_old.bit_len, signed=Pg_old.signed)
        enc_vals['Pg'] = Pg_new

        Pp_at_not = int(Pp_invert)
        Pp_at_not_old:SASS_Bits = enc_vals['Pp@not']
        Pp_at_not_new:SASS_Bits = SASS_Bits.from_int(Pp_at_not, bit_len=Pp_at_not_old.bit_len, signed=Pp_at_not_old.signed)
        enc_vals['Pp@not'] = Pp_at_not_new

        Pp_val = Pp[-1]
        Pp_old:SASS_Bits = enc_vals['Pp']
        Pp_new:SASS_Bits = SASS_Bits.from_int(Pp_val, bit_len=Pp_old.bit_len, signed=Pp_old.signed)
        enc_vals['Pp'] = Pp_new

        sImm = imm_val
        sImm_old:SASS_Bits = enc_vals['sImm']
        sImm_new:SASS_Bits = SASS_Bits.from_int(sImm, bit_len=sImm_old.bit_len, signed=sImm_old.signed)
        enc_vals['sImm'] = sImm_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)

        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

class SASS_KK__Empty:
    """
    This one contains all requirements to produce an empty kernel that does nothing.
    """
    def __init__(self, kk_sm:KK_SM, usched_info_reg:tuple):
        ##############################################################################################
        # NOTE: leave the comments for reference => some template for how to construct these objects 
        # and get rid of the templates afterwards...
        ##############################################################################################

        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.empty.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)
        
        # usched_info = src_cubin.valid_regs.USCHED_INFO__WAIT1_END_GROUP__1
        usched_info = usched_info_reg[-1]

        # mov_instr:Instr_CuBin_Repr = src_cubin.get_instr(0,0)
        # mov_instr_cl = mov_instr.class_name
        class_name__mov = 'mov__RC'
        # exit_instr:Instr_CuBin_Repr = src_cubin.get_instr(0,1)
        class_name__exit = 'exit_'
        # bra_instr:Instr_CuBin_Repr = src_cubin.get_instr(0,2)
        class_name__bra = 'bra_'

        # enc_vals_mov = mov_instr.all_enc_vals[0]
        enc_vals__mov = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Rd': SASS_Create_Utils.sass_bits_from_str('1U:8b'),
            'Sb_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'Sb_addr': SASS_Create_Utils.sass_bits_from_str('40S:17b'),
            'PixMaskU04': SASS_Create_Utils.sass_bits_from_str('15U:4b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('18U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }
        usched_info_old:SASS_Bits = enc_vals__mov['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__mov['usched_info'] = usched_info_new

        # enc_vals_exit = exit_instr.all_enc_vals[0]
        enc_vals__exit = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'mode': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'no_atexit': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('21U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }
        usched_info_old:SASS_Bits = enc_vals__exit['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__exit['usched_info'] = usched_info_new

        # enc_vals_bra = bra_instr.all_enc_vals[0]
        enc_vals__bra = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'depth': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'cond': SASS_Create_Utils.sass_bits_from_str('0U:2b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'sImm': SASS_Create_Utils.sass_bits_from_str('-16S:50b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'pm_pred': SASS_Create_Utils.sass_bits_from_str('0U:2b')
        }
        usched_info_old:SASS_Bits = enc_vals__bra['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__bra['usched_info'] = usched_info_new

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name__mov], enc_vals__mov, throw=True)
        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name__exit], enc_vals__exit, throw=True)
        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name__bra], enc_vals__bra, throw=True)

        # Make stuff accessible
        self.enc_vals__bra = enc_vals__bra
        self.class_name__bra = class_name__bra
        self.enc_vals__exit = enc_vals__exit
        self.class_name__exit = class_name__exit
        self.enc_vals__mov = enc_vals__mov
        self.class_name__mov = class_name__mov

if __name__ == '__main__':
    sm_nr = int(__file__.split('.py')[0].split('_')[-1])
    kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=True, load_encdom=True)
    
    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
    SASS_KK__Empty(kk_sm, usched_info_reg=usched_info_reg)
    target_reg = kk_sm.regs.Register__R4__4
    SASS_KK__CS2R(kk_sm, target_reg=target_reg, usched_info_reg=usched_info_reg)
    param_reg = kk_sm.regs.Register__R2__2
    SASS_KK__MOV_Rc(kk_sm, Sb_bank=0x0, Sb_addr=0x168, Rd=param_reg, usched_info_reg=usched_info_reg)
    SASS_KK__MOVImm(kk_sm, exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__PT__7, target_reg=target_reg, imm_val=0x5, usched_info_reg=usched_info_reg)
    SASS_KK__UMOVImm(kk_sm, negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7, target_ureg=kk_sm.regs.UniformRegister__UR2__2, imm_val=5, usched_info_reg=usched_info_reg)
    SASS_KK__umov__UR(kk_sm, negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7, target_ureg=kk_sm.regs.UniformRegister__UR2__2, source_ureg=kk_sm.regs.UniformRegister__UR4__4, usched_info_reg=usched_info_reg)
    uniform_reg = kk_sm.regs.UniformRegister__UR4__4
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg)
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg,
                  size=32)
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg,
                  size=16)
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg,
                  size=-16)
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg,
                  size=8)
    SASS_KK__ULDC(kk_sm, 
                  uniform_reg=uniform_reg, 
                  m_offset=0x118, 
                  usched_info_reg=usched_info_reg,
                  size=-8)
    SASS_KK__STG_memdesc_Ra64(kk_sm, uniform_reg=uniform_reg, target_reg=param_reg, target_offset = 0x0, source_reg=target_reg, usched_info_reg=usched_info_reg)
    SASS_KK__NOP(kk_sm)
    SASS_KK__IMAD_RRC_RRC(kk_sm, kk_sm.regs.Register__R2__2, kk_sm.regs.Register__RZ__255, kk_sm.regs.Register__RZ__255, 0x0, 0x168, usched_info_reg)
    SASS_KK__IMAD_RRsI_RRI(kk_sm, kk_sm.regs.Register__R2__2, kk_sm.regs.Register__RZ__255, kk_sm.regs.Register__RZ__255, 0x168, usched_info_reg)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=128)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=64)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=32)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=16)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=-16)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=8)
    SASS_KK__STG_RaRZ(kk_sm,
                      uniform_reg=kk_sm.regs.UniformRegister__UR4__4, 
                      offset=0x0, 
                      source_reg=kk_sm.regs.Register__R4__4, 
                      usched_info_reg=usched_info_reg, 
                      size=-8)
    SASS_KK__uisetp__URsIUR_URIR(kk_sm, 
                                 negate_upred=False, upred=kk_sm.regs.UniformPredicate__UPT__7,
                                 target_UPu=kk_sm.regs.UniformPredicate__UP0__0,
                                 src_URa=kk_sm.regs.UniformRegister__UR2__2, 
                                 icmp=kk_sm.regs.ICmpAll__GT__4, fmt=kk_sm.regs.FMT__S32__1,
                                 src_imm_val=10, usched_info_reg=usched_info_reg)
    SASS_KK__ISETP_RsIR_RIR(kk_sm, 
                            target_pred=kk_sm.regs.Predicate__P0__0, 
                            aux_pred=kk_sm.regs.Predicate__PT__7, 
                            reg=kk_sm.regs.Register__R4__4, 
                            imm=10, 
                            comp_op=kk_sm.regs.ICmpAll__EQ__2,
                            fmt=kk_sm.regs.FMT__S32__1,
                            bop_op=kk_sm.regs.Bop__AND__0, 
                            invert_Pp=False,
                            Pp=kk_sm.regs.Predicate__PT__7,
                            usched_info_reg=usched_info_reg)
    SASS_KK__ISETP_RCR_RCR(kk_sm, 
                            target_pred=kk_sm.regs.Predicate__P0__0, 
                            aux_pred=kk_sm.regs.Predicate__PT__7, 
                            reg=kk_sm.regs.Register__R4__4, 
                            m_bank=0x0,
                            m_bank_addr=0x160,
                            comp_op=kk_sm.regs.ICmpAll__EQ__2,
                            f_type=kk_sm.regs.FMT__S32__1,
                            bop_op=kk_sm.regs.Bop__AND__0, 
                            pred_invert=False,
                            pred=kk_sm.regs.Predicate__PT__7,
                            usched_info_reg=usched_info_reg)
    SASS_KK__SEL_RRR_RRR(kk_sm, 
                         target_reg=kk_sm.regs.Register__R5__5,
                         reg1=kk_sm.regs.Register__R3__3,
                         reg2=kk_sm.regs.Register__R4__4,
                         pred_invert=False,
                         pred=kk_sm.regs.Predicate__PT__7,
                         usched_info_reg=usched_info_reg)
    SASS_KK__EXIT(kk_sm, 
                  pred_invert=False, 
                  pred=kk_sm.regs.Predicate__PT__7, 
                  Pp_invert=False,
                  Pp=kk_sm.regs.Predicate__PT__7, 
                  usched_info_reg=usched_info_reg)

    SASS_KK__ULDC_CONST_RCR(kk_sm, 
                            u_dest_reg=kk_sm.regs.UniformRegister__UR0__0, 
                            sz=kk_sm.regs.SZ_32_64_128___32__4, 
                            m_bank=0x0, 
                            m_bank_addr=0x160, 
                            usched_info_reg=usched_info_reg)

    SASS_KK__ISETP_RUR_RUR_NOEX(kk_sm, 
                            target_Pu=kk_sm.regs.Predicate__P0__0,
                            aux_pred=kk_sm.regs.Predicate__PT__7, 
                            Ra=kk_sm.regs.Register__R4__4,
                            URb=kk_sm.regs.UniformRegister__UR1__1,
                            comp_op=kk_sm.regs.ICmpAll__EQ__2,
                            f_type=kk_sm.regs.FMT__S32__1,
                            bop_op=kk_sm.regs.Bop__AND__0, 
                            pred_invert=False,
                            pred=kk_sm.regs.Predicate__PT__7,
                            usched_info_reg=usched_info_reg)
    SASS_KK__ULDC_CONST_RCR(kk_sm, 
                            kk_sm.regs.UniformRegister__UR1__1, 
                            kk_sm.regs.SZ_32_64_128___32__4, 
                            m_bank=0x0, 
                            m_bank_addr= 0x160, 
                            usched_info_reg=usched_info_reg)
    SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm, 
                                target_reg=kk_sm.regs.Register__R4__4, 
                                negate_Ra=False,
                                Ra=kk_sm.regs.Register__R5__5, 
                                src_imm=0x1, 
                                negate_Rc=False,
                                Rc=kk_sm.regs.Register__R7__7,
                                usched_info_reg=usched_info_reg)
    SASS_KK__UIADD3_URsIUR_RIR(kk_sm, 
                               target_ureg=kk_sm.regs.UniformRegister__UR1__1,
                               src_ureg_neg=False, src_ureg=kk_sm.regs.UniformRegister__UR2__2,
                               src_imm=0x1, usched_info_reg=usched_info_reg)
    
    SASS_KK__IADD3_NOIMM_RUR_RUR(kk_sm, 
                                 dest_reg=kk_sm.regs.Register__R1__1,
                                 src_reg1_neg=False,
                                 src_reg1=kk_sm.regs.Register__R4__4,
                                 src_ureg2_neg=False,
                                 src_ureg2=kk_sm.regs.UniformRegister__UR1__1,
                                 usched_info_reg=usched_info_reg)
    
    SASS_KK__imad__RRU_RRU(kk_sm, 
                           invert_Pg=False, 
                           Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R4__4, 
                           Ra=kk_sm.regs.Register__R6__6, 
                           Rb=kk_sm.regs.Register__R8__8, 
                           negate_URc=False, 
                           URc=kk_sm.regs.UniformRegister__UR2__2,
                           usched_info_reg=usched_info_reg)
    
    ui_rd:tuple = kk_sm.regs.Register__R2__2
    SASS_KK__ldg_uniform_RaRZ(kk_sm, Rd=ui_rd, Ra=kk_sm.regs.Register__RZ__255, Ra_URb=kk_sm.regs.UniformRegister__UR2__2,ra_offset = 0x8,RD=0x7,WR=0x0,REQ=0b000001,USCHED_INFO=usched_info_reg)

    SASS_KK__BRA(kk_sm,
                 pred_invert=False, pred=kk_sm.regs.Predicate__PT__7,
                 Pp_invert=False, Pp=kk_sm.regs.Predicate__PT__7,
                 imm_val=-16,
                 usched_info_reg=usched_info_reg)
    
    SASS_KK__isetp__RRR_RRR_noEX(kk_sm, 
                                 pred_invert=False, pred=kk_sm.regs.Predicate__PT__7, 
                                 Pu=kk_sm.regs.Predicate__P0__0, 
                                 Ra=kk_sm.regs.Register__R2__2,
                                 icmp=kk_sm.regs.ICmpAll__GE__6,
                                 Rb=kk_sm.regs.Register__R4__4,
                                 fmt=kk_sm.regs.FMT__U32__0,
                                 usched_info_reg=usched_info_reg)
    
    SASS_KK__imul__RRR_RRR(kk_sm, 
                           pred_invert=False, pred=kk_sm.regs.Predicate__PT__7,
                           dest_reg=kk_sm.regs.Register__R2__2,
                           Ra=kk_sm.regs.Register__R4__4,
                           Rb=kk_sm.regs.Register__R6__6,
                           fmt=kk_sm.regs.FMT__U32__0,
                           usched_info_reg=usched_info_reg)
    
    SASS_KK__imul__RsIR_RIR(kk_sm, 
                           pred_invert=False, pred=kk_sm.regs.Predicate__PT__7,
                           dest_reg=kk_sm.regs.Register__R2__2,
                           Ra=kk_sm.regs.Register__R4__4,
                           imm_val=8,
                           fmt=kk_sm.regs.FMT__U32__0,
                           usched_info_reg=usched_info_reg)
    
    SASS_KK__stg__sImmOffset(kk_sm, 
                             offset_Ra=kk_sm.regs.Register__R2__2, ra_offset=0x4,
                             Rb=kk_sm.regs.Register__R4__4, 
                             usched_info_reg=usched_info_reg,
                             req=63, rd=0x7)
    
    SASS_KK__ldg__uImmOffset(kk_sm, Ra_offset=0x0, Rd=kk_sm.regs.Register__R2__2, usched_info_reg=usched_info_reg)

    SASS_KK__ffma__RCR_RCR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb_negate=False, Sb_absolute=False, Sb_bank=0, Sb_addr=0x160,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RCxR_RCxR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb_negate=False, Sb_absolute=False, Sb_offset=0x160, URb=kk_sm.regs.UniformRegister__UR4__4,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RIR_RIR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb=123,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RRC_RRC(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc_negate=False, Sc_absolute=False, Sc_bank=0, Sc_addr=0x160,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RRCx_RRCx(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc_negate=False, Sc_absolute=False, Sc_offset=0x160, URc=kk_sm.regs.UniformRegister__UR4__4,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RRI_RRI(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc=123,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RRR_RRR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R8__8,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RRU_RRU(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           URc_absolute=False, URc_negate=False, URc=kk_sm.regs.UniformRegister__UR8__8,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__ffma__RUR_RUR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           URb_absolute=False, URb_negate=False, URb=kk_sm.regs.UniformRegister__UR8__8,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    
    SASS_KK__dfma__RCR_RCR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb_negate=False, Sb_absolute=False, Sb_bank=0, Sb_addr=0x160,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RCxR_RCxR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb_negate=False, Sb_absolute=False, Sb_offset=0x160, URb=kk_sm.regs.UniformRegister__UR4__4,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RsIR_RIR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Sb=123,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RRC_RRC(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc_negate=False, Sc_absolute=False, Sc_bank=0, Sc_addr=0x160,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RRCx_RRCx(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc_negate=False, Sc_absolute=False, Sc_offset=0x160, URc=kk_sm.regs.UniformRegister__UR4__4,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RRsI_RRI(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Sc=123,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RRR_RRR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R8__8,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RRU_RRU(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           URc_absolute=False, URc_negate=False, URc=kk_sm.regs.UniformRegister__UR8__8,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__dfma__RUR_RUR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           URb_absolute=False, URb_negate=False, URb=kk_sm.regs.UniformRegister__UR8__8,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    SASS_KK__i2f__IU_32b(kk_sm,
                         Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                         Rd=kk_sm.regs.Register__R10__10, Sb=10,
                         dst_format=32, usched_info_reg=usched_info_reg
                         )
    SASS_KK__i2f_Rd64__IU_32b(kk_sm, Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7, 
                              Rd=kk_sm.regs.Register__R10__10,
                              Sb=15, 
                              usched_info_reg=usched_info_reg)
    
    SASS_KK__i2f_Rd64__Rb_32b(kk_sm, Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7, 
                              Rd=kk_sm.regs.Register__R10__10,
                              Rb_signed=False,
                              Rb=kk_sm.regs.Register__R12__12, 
                              usched_info_reg=usched_info_reg)

    SASS_KK__i2f__Rb_32b(kk_sm, Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7, 
                              Rd=kk_sm.regs.Register__R10__10, dst_fsize=32,
                              Rb_signed=False,
                              Rb=kk_sm.regs.Register__R12__12, 
                              usched_info_reg=usched_info_reg)

    SASS_KK__f2i_Rd64__Rb_64b(kk_sm, Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                              Rd=kk_sm.regs.Register__R10__10, 
                              Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R8__8,
                              signed=False, usched_info_reg=usched_info_reg)
    
    SASS_KK__dadd__RRR_RR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )
    
    SASS_KK__mov__RR(kk_sm,
                     Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                     Rd=kk_sm.regs.Register__R2__2,
                     Rb_reuse=False, Rb=kk_sm.regs.Register__R4__4,
                     usched_info_reg=usched_info_reg, req=0x1)
    
    SASS_KK__fadd__RRR_RR(kk_sm,
                          Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                          Rd=kk_sm.regs.Register__R2__2,
                          Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                          Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                          usched_info_reg=usched_info_reg, req=0x1)
    
    SASS_KK__fmul__RRR_RR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1)
    
    SASS_KK__dmul__RRR_RR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rb_reuse=False, Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1)
    
    SASS_KK__mufu__RRR_RR(kk_sm,
                          Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                          mufuop=kk_sm.regs.MUFU_OP__RCP__4,
                          Rd=kk_sm.regs.Register__R2__2,
                          Rb_absolute=False, Rb_negate=False, Rb=kk_sm.regs.Register__R6__6,
                          usched_info_reg=usched_info_reg, req=0x1)
    
    SASS_KK__f2f_f64_upconvert__R_R32_R_RRR(kk_sm,
                 Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7, 
                 Rd=kk_sm.regs.Register__R2__2,
                 Rb_negate=False, Rb_absolute=True, Rb=kk_sm.regs.Register__R4__4,
                 usched_info_reg=usched_info_reg, 
                 req=0x0, wr=0x7, rd=0x7)


    print("Finished")
