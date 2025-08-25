"""
This class contains a couple of methods that can be used to add cash bit definitions to instructions.

For example, an instruction class that doesn't have WR or RD definitions, meaning their value
is set as 0x7 in the ENCODINGS stage of the instruction class, can get a real, modifiable field with this.

The whole thing is basically useless because the mechanism doesn't work in real life (meaning, fixed-latency
instructions can't set barriers and non-fixed-latency instructions, that can set barriers, crash if one
tries to set a barrier that isn't supported.)
"""

from __future__ import annotations
from . import _config as sp
from ._sass_expression import SASS_Expr
from ._tt_instruction import TT_Instruction
from ._tt_term import TT_Term
from ._tt_terms import TT_Cash
from ._sass_class import _SASS_Class
from .sass_class import SASS_Class
from .sm_cu_details import SM_Cu_Details
from py_sass_ext import SASS_Bits
from warnings import warn

############################################################################
# This one is DEPRECATED! Don't use cash bit augmentation. It doesn't work!!
warn(f"The module {__name__} is deprecated. Don't use cash bit augmentation! It doesn't work!", DeprecationWarning, stacklevel=2)
############################################################################

class SASS_Class_Cash_Aug:
    @staticmethod
    def __get_tt_cash__dst_wr_sb(class_name:str, details:SM_Cu_Details) -> tuple[TT_Cash, str, SASS_Bits]:
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        dst_wr_sb_str = '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$'
        dst_wr_sb_tt:TT_Term = _SASS_Class.parse_cash_str(class_name, dst_wr_sb_str, details.as_dict())[0]
        dst_wr_sb = TT_Cash(class_name, dst_wr_sb_tt, details, added_later=True)
        return dst_wr_sb, 'dst_wr_sb', SASS_Bits.from_int(7, bit_len=3, signed=0)

    @staticmethod
    def __get_tt_cash__src_rel_sb(class_name:str, details:SM_Cu_Details) -> tuple[TT_Cash, str, SASS_Bits]:
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        src_rel_sb_str = '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$'
        src_rel_sb_tt:TT_Term = _SASS_Class.parse_cash_str(class_name, src_rel_sb_str, details.as_dict())[0]
        src_rel_sb = TT_Cash(class_name, src_rel_sb_tt, details, added_later=True)
        return src_rel_sb, 'src_rel_sb', SASS_Bits.from_int(7, bit_len=3, signed=0)
    
    @staticmethod
    def __get_tt_cash__req_bit_set(class_name:str, details:SM_Cu_Details) -> tuple[TT_Cash, str, SASS_Bits]:
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        req_bit_set_str = '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$'
        req_bit_set_tt:TT_Term = _SASS_Class.parse_cash_str(class_name, req_bit_set_str, details.as_dict())[0]
        src_rel_sb = TT_Cash(class_name, req_bit_set_tt, details, added_later=True)
        return src_rel_sb, 'req_bit_set', SASS_Bits.from_int(0, bit_len=6, signed=0)
    
    @staticmethod
    def __get_tt_cash__pm_pred(class_name:str, details:SM_Cu_Details) -> tuple[TT_Cash, str, SASS_Bits]:
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        pm_pred_str = '$( { ? PM_PRED(PMN):pm_pred } )$'
        pm_pred_tt:TT_Term = _SASS_Class.parse_cash_str(class_name, pm_pred_str, details.as_dict())[0]
        pm_pred = TT_Cash(class_name, pm_pred_tt, details, added_later=True)
        return pm_pred, 'pm_pred', SASS_Bits.from_int(7, bit_len=2, signed=0)

    @staticmethod
    def __replace_encoding(class_name:str, checks:dict, replacements:dict, format_tt:TT_Instruction, encodings:list, details:SM_Cu_Details):
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        if not isinstance(class_name, str): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(checks, dict): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(format_tt, TT_Instruction): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(encodings, list): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not isinstance(details, SM_Cu_Details): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if not (checks.keys() | replacements.keys() == checks.keys()): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        if 'dst_wr_sb' in checks and checks['dst_wr_sb'] != []:
            val, name, default = SASS_Class_Cash_Aug.__get_tt_cash__dst_wr_sb(class_name, details)
            format_tt.cashs.append(val)
            format_tt.eval[name] = val.values[-1].value
            expr = SASS_Expr(replacements['dst_wr_sb'], details.TABLES_DICT, details.CONSTANTS_DICT, details.REGISTERS_DICT, details.PARAMETERS_DICT, details.TABLES_INV_DICT)
            expr.finalize(format_tt.eval)
            encodings[checks['dst_wr_sb'][0]]['alias'] = expr
            encodings[checks['dst_wr_sb'][0]]['X'] = 'added by parser for consistency'
            format_tt.add_default_enc_vals(name, default)
        if 'req_bit_set' in checks and checks['req_bit_set'] != []:
            val, name, default = SASS_Class_Cash_Aug.__get_tt_cash__req_bit_set(class_name, details)
            format_tt.cashs.append(val)
            format_tt.eval[name] = val.values[-1].value
            expr = SASS_Expr(replacements['req_bit_set'], details.TABLES_DICT, details.CONSTANTS_DICT, details.REGISTERS_DICT, details.PARAMETERS_DICT, details.TABLES_INV_DICT)
            expr.finalize(format_tt.eval)
            encodings[checks['req_bit_set'][0]]['alias'] = expr
            encodings[checks['req_bit_set'][0]]['X'] = 'added by parser for consistency'
            format_tt.add_default_enc_vals(name, default)
        if 'src_rel_sb' in checks and checks['src_rel_sb'] != []:
            val, name, default = SASS_Class_Cash_Aug.__get_tt_cash__src_rel_sb(class_name, details)
            format_tt.cashs.append(val)
            format_tt.eval[name] = val.values[-1].value
            expr = SASS_Expr(replacements['src_rel_sb'], details.TABLES_DICT, details.CONSTANTS_DICT, details.REGISTERS_DICT, details.PARAMETERS_DICT, details.TABLES_INV_DICT)
            expr.finalize(format_tt.eval)
            encodings[checks['src_rel_sb'][0]]['alias'] = expr
            encodings[checks['src_rel_sb'][0]]['X'] = 'added by parser for consistency'
            format_tt.add_default_enc_vals(name, default)
        if 'pm_pred' in checks and checks['pm_pred'] != []:
            val, name, default = SASS_Class_Cash_Aug.__get_tt_cash__pm_pred(class_name, details)
            format_tt.cashs.append(val)
            format_tt.eval[name] = val.values[-1].value
            expr = SASS_Expr(replacements['pm_pred'], details.TABLES_DICT, details.CONSTANTS_DICT, details.REGISTERS_DICT, details.PARAMETERS_DICT, details.TABLES_INV_DICT)
            expr.finalize(format_tt.eval)
            encodings[checks['pm_pred'][0]]['alias'] = expr
            encodings[checks['pm_pred'][0]]['X'] = 'added by parser for consistency'
            format_tt.add_default_enc_vals(name, default)

    @staticmethod
    def augment_cashes(class_:SASS_Class, details:SM_Cu_Details):
        # !!! used for useless cash augmentation => not used anymore, but here for reference !!!
        sm_nr:int = int(details.SM_XX.split('_')[-1])
        format_tt:TT_Instruction = class_.FORMAT
        encodings:list = class_.ENCODING
        class_name:str = class_.class_name

        if 50 <= sm_nr and sm_nr <= 62:
            replacements = {
                'dst_wr_sb': 'VarLatOperandEnc(dst_wr_sb)',
                'req_bit_set': 'req_bit_set',
                'src_rel_sb': 'VarLatOperandEnc(src_rel_sb)'
            }

            checks = {
                'dst_wr_sb': [ind for ind,x in enumerate(encodings) if (x['code_name'].startswith('OEVarLatDest') or x['code_name'].endswith('dst_wr_sb')) and x['alias'].startswith_int()],
                'req_bit_set': [ind for ind,x in enumerate(encodings) if (x['code_name'].startswith('OEWaitOnSb') or x['code_name'].endswith('req_sb_bitset')) and x['alias'].startswith_int()],
                'src_rel_sb': [ind for ind,x in enumerate(encodings) if (x['code_name'].startswith('OEVarLatSrc') or x['code_name'].endswith('src_rel_sb')) and x['alias'].startswith_int()]
            }

            SASS_Class_Cash_Aug.__replace_encoding(class_name, checks, replacements, format_tt, encodings, details)
            # Must be 4 different sets of bits
            if len(format_tt.cashs) != 4: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        elif 70 <= sm_nr and sm_nr <= 80:
            replacements = {
                'dst_wr_sb': 'VarLatOperandEnc(dst_wr_sb)',
                'req_bit_set': 'req_bit_set',
                'src_rel_sb': 'VarLatOperandEnc(src_rel_sb)'
            }

            checks = {
                'dst_wr_sb': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_3_112_110_dst_wr_sb') and x['alias'].startswith_int()],
                'req_bit_set': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_6_121_116_req_bit_set') and x['alias'].startswith_int()],
                'src_rel_sb': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_3_115_113_src_rel_sb') and x['alias'].startswith_int()]
            }

            SASS_Class_Cash_Aug.__replace_encoding(class_name, checks, replacements, format_tt, encodings, details)
            # Must be 5 different sets of bits
            if len(format_tt.cashs) != 5: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
        elif 86 <= sm_nr and sm_nr <= 120:
            replacements = {
                'dst_wr_sb': 'VarLatOperandEnc(dst_wr_sb)',
                'req_bit_set': 'req_bit_set',
                'src_rel_sb': 'VarLatOperandEnc(src_rel_sb)',
                'pm_pred': 'pm_pred'
            }

            checks = {
                'dst_wr_sb': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_3_112_110_dst_wr_sb') and x['alias'].startswith_int()],
                'req_bit_set': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_6_121_116_req_bit_set') and x['alias'].startswith_int()],
                'src_rel_sb': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_3_115_113_src_rel_sb') and x['alias'].startswith_int()],
                'pm_pred': [ind for ind,x in enumerate(encodings) if x['code_name'].startswith('BITS_2_103_102_pm_pred') and x['alias'].startswith_int()]
            }

            SASS_Class_Cash_Aug.__replace_encoding(class_name, checks, replacements, format_tt, encodings, details)
            # Must be 5 different sets of bits
            if len(format_tt.cashs) != 6: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        else:
            # need to check the behaviour if a new architecture is added
            #  => check out SM_SASS.set_config_fieds for a guide on how to do that
            raise Exception(sp.CONST__ERROR_NOT_IMPLEMENTED)

        for x in format_tt.cashs:
            xx = str(x)
            if xx.find('WR')>=0:
                class_.__wr_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('RD')>=0:
                class_.__rd_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('WR_EARLY')>=0:
                class_.__wr_early_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('REQ')>=0:
                class_.__req_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('BATCH_T')>=0:
                class_.__batch_t_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('USCHED_INFO')>=0:
                class_.__usched_info_alias = str(x.values[-1].alias) # type: ignore
            elif xx.find('PM_PRED')>=0:
                class_.__pm_pred_alias = str(x.values[-1].alias) # type: ignore
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)