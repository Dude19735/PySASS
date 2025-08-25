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
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
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
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('5U:6b'),
            'reuse_src_a': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_b': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'reuse_src_c': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'rnd': SASS_Create_Utils.sass_bits_from_str('0U:2b'),               # keep 0=.RN
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

class SASS_KK__UIADD3_URsIUR_RIR:
    def __init__(self, kk_sm:KK_SM, target_ureg:tuple, src_ureg_neg:bool, src_ureg:tuple, src_imm:int, usched_info_reg:tuple, req=0b111111):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'uiadd3__URsIUR_RIR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Sb': SASS_Create_Utils.sass_bits_from_str('-712774222S:32b'),
            'UPg': SASS_Create_Utils.sass_bits_from_str('4U:3b'),
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'UPu': SASS_Create_Utils.sass_bits_from_str('6U:3b'),
            'UPv': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'URa': SASS_Create_Utils.sass_bits_from_str('46U:6b'),
            'URa@negate': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'URc': SASS_Create_Utils.sass_bits_from_str('30U:6b'),
            'URc@negate': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'URd': SASS_Create_Utils.sass_bits_from_str('42U:6b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('1U:5b'),
            
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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

class SASS_KK__isetp__RRR_RRR_noEX:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, Pu:tuple, Ra:tuple, icmp:tuple, Rb:tuple, fmt:tuple, usched_info_reg:tuple):
        """integer set predicate: Pu = (True if Ra [icmp] Rb else False)
        """
        # NOTE: this is actually not a noEX, but that one is not available on SM 75
        class_name = 'isetp__RRR_RRR'

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

        enc_vals = {
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # set by params
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('1U:1b'),        # set by params
            'Pr': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'Pr@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pp': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # PT, input from chaining, not used here, keep PT
            'Pp@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # don't negate
            'Pu': SASS_Create_Utils.sass_bits_from_str('4U:3b'),            # target set by params
            'Pv': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # PT
            'Ra': SASS_Create_Utils.sass_bits_from_str('39U:8b'),           # source Ra set by params
            'Rb': SASS_Create_Utils.sass_bits_from_str('37U:8b'),           # source Rb set by params
            'ex': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b'),       # keep 0
            'bop': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # AND for chaining, AND with PT is whatever is on the left of it
            'fmt': SASS_Create_Utils.sass_bits_from_str('0U:1b'),           # data type (like U32) set by params
            'icmp': SASS_Create_Utils.sass_bits_from_str('4U:3b'),          # compare, set by param
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

class SASS_KK__IADD3_NOIMM_RRR_RRR:
    def __init__(self, kk_sm:KK_SM, target_reg:tuple, negate_Ra:bool, src_Ra:tuple, negate_Rb:bool, src_Rb:tuple, negate_Rc:bool, src_Rc:tuple, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,4).class_name)
        class_name = 'iadd3_noimm__RRR_RRR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,2),0))

        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))

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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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

        if Rb_signed: srcfmt = kk_sm.regs.SRCFMT_U32_S32__S32__5
        else: srcfmt = kk_sm.regs.SRCFMT_U32_S32__U32__4
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

        class_name = 'stg_uniform__RaRZ'

        # location = os.path.dirname(os.path.realpath(__file__)) + '/variable_latency_instructions/binaries'
        # source = '{0}/template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)
        # print(src_cubin.get_instr(0,21).class_name)
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,21),0))

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'sem': SASS_Create_Utils.sass_bits_from_str('1U:2b'),
            'sco': SASS_Create_Utils.sass_bits_from_str('3U:2b'),
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'Ra_URc': SASS_Create_Utils.sass_bits_from_str('4U:6b'),
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('112S:24b'),
            'Rb': SASS_Create_Utils.sass_bits_from_str('30U:8b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('8U:6b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('0U:3b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('20U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(uniform_reg, 'Ra_URc', enc_vals)
        enc_vals = overwrite_helper(offset, 'Ra_offset', enc_vals)
        enc_vals = overwrite_helper(source_reg, 'Rb', enc_vals)
        enc_vals = overwrite_helper(rd, 'src_rel_sb', enc_vals)
        enc_vals = overwrite_helper(size, 'sz', enc_vals)
        enc_vals = overwrite_helper(req, 'req_bit_set', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        # Make stuff accessible
        self.enc_vals = enc_vals
        self.class_name = class_name

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

        # location = os.path.dirname(os.path.realpath(__file__)) + '/variable_latency_instructions/binaries'
        # source = '{0}/template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)
        # print(src_cubin.get_instr(0,3).class_name)
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,3),0))

        if not (0 <= RD and RD <= 7): raise Exception('Invalid param')
        if not (0 <= WR and WR <= 7): raise Exception('Invalid param')
        if RD == WR: raise Exception('Invalid param')
        if not (0 <= REQ and REQ <= 0b111111): raise Exception('Invalid param')

        # Ra, Ra_URb, Ra_offset
        # Rd
        # RD, WR
        # USCHED_INFO

        enc_vals = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),        # 0x0
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # 0x7
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),             # .E
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),           # .EN
            'sp2': SASS_Create_Utils.sass_bits_from_str('0U:2b'),           # .nosp2
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),            # .64
            'sem': SASS_Create_Utils.sass_bits_from_str('1U:2b'),           # .WEAK
            'sco': SASS_Create_Utils.sass_bits_from_str('3U:2b'),           # .SYS
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # .noprivate
            'Pu': SASS_Create_Utils.sass_bits_from_str('7U:3b'),            # 0x7
            'Rd': SASS_Create_Utils.sass_bits_from_str('32U:8b'),           # target register set by param
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),          # source register set by param
            'Ra_URb': SASS_Create_Utils.sass_bits_from_str('4U:6b'),        # source uniform register set by param
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('112S:24b'),  # source immediate value set by param
            'Pnz': SASS_Create_Utils.sass_bits_from_str('7U:3b'),           # 0x7
            'Pnz@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),       # 0x0
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),   # REQ set by param
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),    # RD set by param
            'dst_wr_sb': SASS_Create_Utils.sass_bits_from_str('2U:3b'),     # WR set by param
            'usched_info': SASS_Create_Utils.sass_bits_from_str('20U:5b'),  # USCHED_INFO set by param
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')        # 0x0
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

class SASS_KK__IMAD_RRC_RRC:
    def __init__(self, kk_sm:KK_SM, Rd:tuple, Ra:tuple, Rb:tuple, m_bank:int, m_bank_offset:int, usched_info_reg:tuple):
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,2).class_name)
        class_name = 'imad__RRC_RRC'
        # ww, enc_vals = kk_sm.get_enc_vals(class_name, {}, {})
        # print(SASS_Create_Utils.enc_vals_dict_to_init(enc_vals))
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }

        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name ], enc_vals, throw=True)
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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

class SASS_KK__MOV:
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
    def __init__(self, kk_sm:KK_SM, param_offset:int, param_reg:tuple, usched_info_reg:tuple):
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }
        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals__mov['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__mov['usched_info'] = usched_info_new

        Rd_val = param_reg[-1]
        Rd_old:SASS_Bits = enc_vals__mov['Rd']
        Rd_new:SASS_Bits = SASS_Bits.from_int(Rd_val, bit_len=Rd_old.bit_len, signed=Rd_old.signed)
        enc_vals__mov['Rd'] = Rd_new

        Sb_addr_val = param_offset
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
        # location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,1).class_name)
        class_name = 'uldc_const__RCR'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,1),0))
        enc_vals = {
            'UPg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'UPg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'URd': SASS_Create_Utils.sass_bits_from_str('4U:6b'), # target register like UR4 above
            'Sa_bank': SASS_Create_Utils.sass_bits_from_str('0U:5b'),
            'Sa_addr': SASS_Create_Utils.sass_bits_from_str('280S:17b'),
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('5U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }
        enc_vals = overwrite_helper(usched_info_reg, 'usched_info', enc_vals)
        enc_vals = overwrite_helper(uniform_reg, 'URd', enc_vals)
        enc_vals = overwrite_helper(m_offset, 'Sa_addr', enc_vals)
        enc_vals = overwrite_helper(size, 'sz', enc_vals)

        Instr_CuBin.check_expr_conditions(kk_sm.sass.sm.classes_dict[class_name], enc_vals, throw=True)
        self.enc_vals = enc_vals
        self.class_name = class_name


class SASS_KK__STG:
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
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
        # src_cubin = SM_CuBin_File(kk_sm.sass, source)

        # print(src_cubin.get_instr(0,5).class_name)
        class_name__stg = 'stg_uniform__RaRZ'
        # print(SASS_Create_Utils.enc_vals_to_init(src_cubin.get_instr(0,5),0))
        enc_vals__stg = {
            'Pg@not': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Pg': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'e': SASS_Create_Utils.sass_bits_from_str('1U:1b'),
            'cop': SASS_Create_Utils.sass_bits_from_str('1U:3b'),
            'sz': SASS_Create_Utils.sass_bits_from_str('5U:3b'),
            'sem': SASS_Create_Utils.sass_bits_from_str('1U:2b'),
            'sco': SASS_Create_Utils.sass_bits_from_str('3U:2b'),
            'private': SASS_Create_Utils.sass_bits_from_str('0U:1b'),
            'Ra': SASS_Create_Utils.sass_bits_from_str('255U:8b'),
            'Ra_URc': SASS_Create_Utils.sass_bits_from_str('4U:6b'), # target register (like UR4)
            'Ra_offset': SASS_Create_Utils.sass_bits_from_str('0S:24b'), # target offset, like 0x0 for entry 1 or 0x8 for entry 2 etc
            'Rb': SASS_Create_Utils.sass_bits_from_str('2U:8b'), # source register (the same one that appears in the CS2R instr)
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('0U:6b'),
            'src_rel_sb': SASS_Create_Utils.sass_bits_from_str('7U:3b'),
            'usched_info': SASS_Create_Utils.sass_bits_from_str('17U:5b'),
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
        }
        usched_info = usched_info_reg[-1]
        usched_info_old:SASS_Bits = enc_vals__stg['usched_info']
        usched_info_new:SASS_Bits = SASS_Bits.from_int(usched_info, bit_len=usched_info_old.bit_len, signed=usched_info_old.signed)
        enc_vals__stg['usched_info'] = usched_info_new

        Ra_URc_val = uniform_reg[-1]
        Ra_URc_old:SASS_Bits = enc_vals__stg['Ra_URc']
        Ra_URc_new:SASS_Bits = SASS_Bits.from_int(Ra_URc_val, bit_len=Ra_URc_old.bit_len, signed=Ra_URc_old.signed)
        enc_vals__stg['Ra_URc'] = Ra_URc_new

        # Ra_val = target_reg[-1]
        # Ra_old:SASS_Bits = enc_vals__stg['Ra']
        # Ra_new:SASS_Bits = SASS_Bits.from_int(Ra_val, bit_len=Ra_old.bit_len, signed=Ra_old.signed)
        # enc_vals__stg['Ra'] = Ra_new

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
    def __init__(self, kk_sm:KK_SM, target_reg:tuple, usched_info_reg:tuple, req:int=0, clk=True, special_reg:tuple|None=None):
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

        if clk:
            SRa =kk_sm.regs.SpecialRegister__SR_CLOCKLO__80
        else:
            if special_reg is None: raise Exception(sp.CONST__ERROR_ILLEGAL)
            SRa = special_reg

        # For example, this is the value of SR_CLOCKLO that is already in the enc_vals
        # SRa =kk_sm.regs.SpecialRegister__SR_CLOCKLO__80

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

class SASS_KK__BRA:
    def __init__(self, kk_sm:KK_SM, pred_invert:bool, pred:tuple, Pp_invert:bool, Pp:tuple, imm_val:int, usched_info_reg:tuple):
        class_name = 'bra_'

        # raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

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
            'req_bit_set': SASS_Create_Utils.sass_bits_from_str('37U:6b'),
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
        # source = '{0}/k.x.template_{1}'.format(location, kk_sm.sm_nr)
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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
            'batch_t': SASS_Create_Utils.sass_bits_from_str('0U:3b')
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
    # Use the filename to get the architecture to keep it consistent
    sm_nr = int(__file__.split('.py')[0].split('_')[-1])
    kk_sm = KK_SM(sm_nr, ip='127.0.0.1', port=8180, webload=True, load_encdom=True)

    usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1
    SASS_KK__Empty(kk_sm, usched_info_reg=usched_info_reg)
    target_reg = kk_sm.regs.Register__R4__4
    SASS_KK__CS2R(kk_sm, target_reg=target_reg, usched_info_reg=usched_info_reg)
    param_reg = kk_sm.regs.Register__R2__2
    SASS_KK__MOV(kk_sm, param_offset=0x168, param_reg=param_reg, usched_info_reg=usched_info_reg)
    SASS_KK__MOVImm(kk_sm, exec_pred_inv=False, exec_pred=kk_sm.regs.Predicate__P0__0, target_reg=target_reg, imm_val=0x5, usched_info_reg=usched_info_reg)
    uniform_reg = kk_sm.regs.UniformRegister__UR4__4
    SASS_KK__ULDC(kk_sm, uniform_reg=uniform_reg, m_offset=0x168, usched_info_reg=usched_info_reg)
    SASS_KK__STG(kk_sm, uniform_reg=uniform_reg, target_reg=param_reg, target_offset = 0x0, source_reg=target_reg, usched_info_reg=usched_info_reg)
    SASS_KK__NOP(kk_sm)
    # SASS_KK__IMAD_RRC_RRC(kk_sm)
    # SASS_KK__IMAD_RRsI_RRI(kk_sm)
    SASS_KK__IMAD_RRC_RRC(kk_sm, kk_sm.regs.Register__R2__2, kk_sm.regs.Register__RZ__255, kk_sm.regs.Register__RZ__255, 0x0, 0x168, usched_info_reg)
    SASS_KK__STG_RaRZ(kk_sm, uniform_reg=kk_sm.regs.UniformRegister__UR4__4, offset=0x0, source_reg=kk_sm.regs.Register__R4__4, usched_info_reg=usched_info_reg)
    ui_rd:tuple = kk_sm.regs.Register__R2__2
    SASS_KK__ldg_uniform_RaRZ(kk_sm, Rd=ui_rd, Ra=kk_sm.regs.Register__RZ__255, Ra_URb=kk_sm.regs.UniformRegister__UR2__2,ra_offset = 0x8,RD=0x7,WR=0x0,REQ=0b000001,USCHED_INFO=usched_info_reg)

    SASS_KK__i2f__Rb_32b(kk_sm, Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                              Rd=kk_sm.regs.Register__R10__10, dst_fsize=32,
                              Rb_signed=False,
                              Rb=kk_sm.regs.Register__R12__12,
                              usched_info_reg=usched_info_reg)

    SASS_KK__IADD3_NOIMM_RRR_RRR(kk_sm,
                                    target_reg=kk_sm.regs.Register__R12__12,
                                    negate_Ra=False, src_Ra=kk_sm.regs.Register__R14__14,
                                    negate_Rb=False, src_Rb=kk_sm.regs.Register__RZ__255,
                                    negate_Rc=False, src_Rc=kk_sm.regs.Register__RZ__255,
                                    usched_info_reg=usched_info_reg)

    SASS_KK__IADD3_IMM_RsIR_RIR(kk_sm,
                                target_reg=kk_sm.regs.Register__R4__4,
                                negate_Ra=False,
                                Ra=kk_sm.regs.Register__R5__5,
                                src_imm=0x1,
                                negate_Rc=False,
                                Rc=kk_sm.regs.Register__R7__7,
                                usched_info_reg=usched_info_reg)

    SASS_KK__isetp__RRR_RRR_noEX(kk_sm,
                                 pred_invert=False, pred=kk_sm.regs.Predicate__PT__7,
                                 Pu=kk_sm.regs.Predicate__P0__0,
                                 Ra=kk_sm.regs.Register__R2__2,
                                 icmp=kk_sm.regs.ICmpAll__GE__6,
                                 Rb=kk_sm.regs.Register__R4__4,
                                 fmt=kk_sm.regs.FMT__U32__0,
                                 usched_info_reg=usched_info_reg)
    
    SASS_KK__dadd__RRR_RR(kk_sm,
                           Pg_negate=False, Pg=kk_sm.regs.Predicate__PT__7,
                           Rd=kk_sm.regs.Register__R2__2,
                           Ra_reuse=False, Ra_absolute=False, Ra_negate=False, Ra=kk_sm.regs.Register__R4__4,
                           Rc_reuse=False, Rc_absolute=False, Rc_negate=False, Rc=kk_sm.regs.Register__R6__6,
                           usched_info_reg=usched_info_reg, req=0x1
                           )

    # t_location = os.path.dirname(os.path.realpath(__file__)) + '/templates'
    # target = '{0}/k.183instr.template_{1}'.format(t_location, kk_sm.sm_nr)
    # source = '{0}/k.x.template_{1}'.format(t_location, kk_sm.sm_nr)
    # modified = '{0}/mod.template_{1}'.format(t_location, kk_sm.sm_nr)
    # target_cubin = SM_CuBin_File(kk_sm.sass, target)
    # source_cubin = SM_CuBin_File(kk_sm.sass, source)


    # # cash values
    # usched_info_reg=kk_sm.regs.USCHED_INFO__WAIT1_END_GROUP__1

    # # override all instructions with a nop
    # nop = SASS_KK__NOP(kk_sm)
    # for i in range(0, len(target_cubin[0])):
    #     target_cubin.create_instr(0, i, nop.class_name__nop, nop.enc_vals__nop)
    # # for i in range(0, len(source_cubin[0])):
    # #     target_cubin.replace_instr(0, i, source_cubin.get_instr(0, i))
    # # target_cubin.to_exec(modified)

    # # exit(0)
    # i=0
    # # add the first of three empty kernel instructions
    # empty = SASS_KK__Empty(kk_sm, usched_info_reg=usched_info_reg)
    # target_cubin.create_instr(0, i, empty.class_name__mov, empty.enc_vals__mov)
    # i+=1

    # # add immediate value 5 to target register R4
    # # mov = SASS_KK__MOV(kk_sm, param_offset=0x168, param_reg=kk_sm.regs.Register__R2__2, usched_info_reg=usched_info_reg)
    # # target_cubin.create_instr(0, i, mov.class_name__mov, mov.enc_vals__mov)
    # # i+=1
    # # target_cubin.replace_instr(0, i, source_cubin.get_instr(0, 2))
    # # i+=1

    # # add parameter to register R2
    # mov_imm = SASS_KK__MOVImm(kk_sm, target_reg=kk_sm.regs.Register__R4__4, imm_val=42, usched_info_reg=usched_info_reg)
    # target_cubin.create_instr(0, i, mov_imm.class_name, mov_imm.enc_vals)
    # i+=1
    # # target_cubin.replace_instr(0, i, source_cubin.get_instr(0, 4))
    # # i+=1

    # # add move back instructions using UR4
    # uldc = SASS_KK__ULDC(kk_sm, uniform_reg=kk_sm.regs.UniformRegister__UR4__4, offset=0x168, usched_info_reg=usched_info_reg)
    # target_cubin.create_instr(0, i, uldc.class_name, uldc.enc_vals)
    # i+=1
    # # mov_imm = SASS_KK__MOVImm(kk_sm, target_reg=kk_sm.regs.Register__R3__3, imm_val=0x0, usched_info_reg=usched_info_reg)
    # # target_cubin.create_instr(0, i, mov_imm.class_name, mov_imm.enc_vals)
    # # i+=1
    # stg = SASS_KK__STG(kk_sm, uniform_reg=kk_sm.regs.UniformRegister__UR4__4, target_reg=kk_sm.regs.Register__R2__2, target_offset=0x0, source_reg=kk_sm.regs.Register__R4__4, usched_info_reg=usched_info_reg)
    # target_cubin.create_instr(0, i, stg.class_name__stg, stg.enc_vals__stg)
    # i+=1

    # # add the last two empty kernel instructions
    # target_cubin.create_instr(0, i, empty.class_name__exit, empty.enc_vals__exit)
    # i+=1
    # target_cubin.create_instr(0, i, empty.class_name__bra, empty.enc_vals__bra)
    # i+=1

    # target_cubin.to_exec(modified)


    print("Finished")
