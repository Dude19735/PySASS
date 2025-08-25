import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_List:
    """
    This one is part of the instruction.txt parser
    Stuff that is between { ... }

    The result is a nested list where all the entries are down-converted
    to the closest type
    """

    @staticmethod
    def parse(lines_iter:itt.islice):
        # if lines_str.startswidth({') => enter here
        # start {' count with 1
        # example:
        #   { "R_CUDA_32", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
        # return as soon as the { ... }' pairs count hits 0
        # return python tuple with all entries

        result = []
        entry = []
        while True:
            i = next(lines_iter, False)
            if not i: break

            if i == '{': 
                ret = SASS_Parser_List.parse(lines_iter)
                result.append(ret)
            elif i == '}':
                val = su.try_convert("".join(entry))
                if val != '': result.append(val)
                break
            elif i == ',':
                val = su.try_convert("".join(entry))
                if val != '': result.append(val)
                entry = []
            else:
                entry.append(i)
        return result
    
if __name__ == '__main__':
    examples = """
  { '&' REQ:req '=' BITSET(6/0x0000):req_sb_bitset }
  { "R_CUDA_NONE", 0, False, False, 0,0, { { 0, 0} } }
  { "R_CUDA_32", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_64", 0xffffffffffffffff, False, False, 0,0, { { 0, 64} } }
  { "R_CUDA_G32", "R_CUDA_G32", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_G64", "R_CUDA_G64", 0xffffffffffffffff, False, False, 0,0, { { 0, 64} } }
  { "R_CUDA_ABS32_26", 0xffffffffffffffff, False, False, 0,0, { { 26, 32} } }
  { "R_CUDA_TEX_HEADER_INDEX", 0xffffffffffffffff, False, False, False, 0,0, { { 0, 20} } }
  { "R_CUDA_SAMP_HEADER_INDEX", 0xffffffffffffffff, False, False, False, 0,0, { { 20, 12} } }
  { "R_CUDA_SURF_HW_DESC", 4, 0, 32 }
  { "R_CUDA_SURF_HW_SW_DESC", 5, 0, 32 }
  { "R_CUDA_ABS32_LO_26", 0x00000000ffffffff, False, False, 0,0, { { 26, 32} } }
  { "R_CUDA_ABS32_HI_26", 0xffffffff00000000, False, False, 0,0, { { 26, 32} } }
  { "R_CUDA_ABS32_23", 0xffffffffffffffff, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_ABS32_LO_23", 0x00000000ffffffff, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_ABS32_HI_23", 0xffffffff00000000, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_ABS24_26", 0xffffffffffffffff, False, False, 0,0, { { 26, 24} } }
  { "R_CUDA_ABS24_23", 0xffffffffffffffff, False, False, 0,0, { { 23, 24} } }
  { "R_CUDA_ABS16_26", 0xffffffffffffffff, False, False, 0,0, { { 26, 16} } }
  { "R_CUDA_ABS16_23", 0xffffffffffffffff, False, False, 0,0, { { 23, 16} } }
  { "R_CUDA_TEX_SLOT", 0xffffffffffffffff, False, False, 0,0, { { 32, 8} } }
  { "R_CUDA_SAMP_SLOT", 0xffffffffffffffff, False, False, 0,0, { { 40, 5} } }
  { "R_CUDA_SURF_SLOT", 0xffffffffffffffff, False, False, 0,0, { { 26, 6} } }
  { "R_CUDA_TEX_BINDLESSOFF13_32", 0xffffffffffffffff, False, False, 0,2, { { 32, 13} } }
  { "R_CUDA_TEX_BINDLESSOFF13_47", 0xffffffffffffffff, False, False, 0,2, { { 47, 13} } }
  { "R_CUDA_CONST_FIELD19_28", 0xffffffffffffffff, "ConstBankAddress2", False, False, 0,0, { { 28, 18},',
  { 26, 1} } }
  { "R_CUDA_CONST_FIELD19_23", 0xffffffffffffffff, "ConstBankAddress2", False, False, 0,0, { { 23, 19} } }
  { "R_CUDA_TEX_SLOT9_49", 0xffffffffffffffff, False, False, 0,0, { { 49, 9} } }
  { "R_CUDA_6_31", 0xffffffffffffffff, False, False, 0,0, { { 31, 6} } }
  { "R_CUDA_2_47", 0xffffffffffffffff, False, False, 0,0, { { 47, 2} } }
  { "R_CUDA_TEX_BINDLESSOFF13_41", 0xffffffffffffffff, False, False, 0,2, { { 41, 13} } }
  { "R_CUDA_TEX_BINDLESSOFF13_45", 0xffffffffffffffff, False, False, 0,2, { { 45, 13} } }
  { "R_CUDA_FUNC_DESC32_23", "fdesc", 0xffffffffffffffff, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_FUNC_DESC32_LO_23", "fdesc", 0x00000000ffffffff, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_FUNC_DESC32_HI_23", "fdesc", 0xffffffff00000000, False, False, 0,0, { { 23, 32} } }
  { "R_CUDA_FUNC_DESC_32", "R_CUDA_FUNC_DESC_32", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_FUNC_DESC_64", "R_CUDA_FUNC_DESC_64", 0xffffffffffffffff, False, False, 0,0, { { 0, 64} } }
  { "R_CUDA_CONST_FIELD21_26", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 26, 21} } }
  { "R_CUDA_QUERY_DESC21_37", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 37, 21} } }
  { "R_CUDA_CONST_FIELD19_26", 0xffffffffffffffff, "ConstBankAddress2", False, False, 0,0, { { 26, 19} } }
  { "R_CUDA_CONST_FIELD21_23", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 23, 21} } }
  { "R_CUDA_PCREL_IMM24_26", 0xffffffffffffffff, True, False, 0,0, { { 26, 24} } }
  { "R_CUDA_PCREL_IMM24_23", 0xffffffffffffffff, True, False, 0,0, { { 23, 24} } }
  { "R_CUDA_ABS32_20", 0xffffffffffffffff, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_ABS32_LO_20", 0x00000000ffffffff, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_ABS32_HI_20", 0xffffffff00000000, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_ABS24_20", 0xffffffffffffffff, False, False, 0,0, { { 20, 24} } }
  { "R_CUDA_ABS16_20", 0xffffffffffffffff, False, False, 0,0, { { 20, 16} } }
  { "R_CUDA_FUNC_DESC32_20", "fdesc", 0xffffffffffffffff, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_FUNC_DESC32_LO_20", "fdesc", 0x00000000ffffffff, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_FUNC_DESC32_HI_20", "fdesc", 0xffffffff00000000, False, False, 0,0, { { 20, 32} } }
  { "R_CUDA_CONST_FIELD19_20", 0xffffffffffffffff, "ConstBankAddress2", False, False, 0,0, { { 20, 19} } }
  { "R_CUDA_BINDLESSOFF13_36", 0xffffffffffffffff, False, False, 0,2, { { 36, 13} } }
  { "R_CUDA_SURF_HEADER_INDEX", "R_CUDA_SURF_HEADER_INDEX", 0xffffffffffffffff, False, False, False, 0,0, { { 0, 20} } }
  { "R_CUDA_INSTRUCTION64", 17, 0, 64 }
  { "R_CUDA_CONST_FIELD21_20", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 20, 21} } }
  { "R_CUDA_ABS32_32", 0xffffffffffffffff, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_ABS32_LO_32", 0x00000000ffffffff, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_ABS32_HI_32", 0xffffffff00000000, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_ABS47_34", 0xffffffffffffffff, False, False, 0,2, { { 34, 47} } }
  { "R_CUDA_ABS16_32", 0xffffffffffffffff, False, False, 0,0, { { 32, 16} } }
  { "R_CUDA_ABS24_32", 0xffffffffffffffff, False, False, 0,0, { { 32, 24} } }
  { "R_CUDA_FUNC_DESC32_32", "fdesc", 0xffffffffffffffff, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_FUNC_DESC32_LO_32", "fdesc", 0x00000000ffffffff, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_FUNC_DESC32_HI_32", "fdesc", 0xffffffff00000000, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_CONST_FIELD19_40", 0xffffffffffffffff, "ConstBankAddress2", False, False, 0,0, { { 40, 19} } }
  { "R_CUDA_BINDLESSOFF14_40", 0xffffffffffffffff, False, False, 0,2, { { 40, 14} } }
  { "R_CUDA_CONST_FIELD21_38", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 38, 21} } }
  { "R_CUDA_INSTRUCTION128", 17, 0, 128 }
  { "R_CUDA_YIELD_OPCODE9_0", 18, 0, 9 }
  { "R_CUDA_YIELD_CLEAR_PRED4_87", 19, 87, 4 }
  { "R_CUDA_32_LO", 0x00000000ffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_32_HI", 0xffffffff00000000, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_UNUSED_CLEAR32", "R_CUDA_UNUSED_CLEAR32", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_UNUSED_CLEAR64", "R_CUDA_UNUSED_CLEAR64", 0xffffffffffffffff, False, False, 0,0, { { 0, 64} } }
  { "R_CUDA_ABS24_40", 0xffffffffffffffff, False, False, 0,0, { { 40, 24} } }
  { "R_CUDA_ABS55_16_34", 0xffffffffffffffff, False, False, 0,2, { { 16, 8}, { 34, 47} } }
  { "R_CUDA_8_0", 0x00000000000000ff, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_8", 0x000000000000ff00, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_16", 0x0000000000ff0000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_24", 0x00000000ff000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_32", 0x000000ff00000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_40", 0x0000ff0000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_48", 0x00ff000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_8_56", 0xff00000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_0", "R_CUDA_G8_0", 0x00000000000000ff, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_8", "R_CUDA_G8_8", 0x000000000000ff00, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_16", "R_CUDA_G8_16", 0x0000000000ff0000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_24", "R_CUDA_G8_24", 0x00000000ff000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_32", "R_CUDA_G8_32", 0x000000ff00000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_40", "R_CUDA_G8_40", 0x0000ff0000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_48", "R_CUDA_G8_48", 0x00ff000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_G8_56", "R_CUDA_G8_56", 0xff00000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_0", "fdesc", 0x00000000000000ff, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_8", "fdesc", 0x000000000000ff00, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_16", "fdesc", 0x0000000000ff0000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_24", "fdesc", 0x00000000ff000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_32", "fdesc", 0x000000ff00000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_40", "fdesc", 0x0000ff0000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_48", "fdesc", 0x00ff000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_FUNC_DESC_8_56", "fdesc", 0xff00000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_ABS20_44", 0xffffffffffffffff, False, False, 0,0, { { 44, 20} } }
  { "R_CUDA_SAMP_HEADER_INDEX_0", 0xffffffffffffffff, False, False, False, 0,0, { { 0, 12} } }
  { "R_CUDA_UNIFIED", "unified", 0xffffffffffffffff, False, False, 0,0, { { 0, 64} } }
  { "R_CUDA_UNIFIED_32", "unified", 0xffffffffffffffff, False, False, 0,0, { { 0, 32} } }
  { "R_CUDA_UNIFIED_8_0 ", "unified", 0x00000000000000ff, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_8 ", "unified", 0x000000000000ff00, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_16", "unified", 0x0000000000ff0000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_24", "unified", 0x00000000ff000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_32", "unified", 0x000000ff00000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_40", "unified", 0x0000ff0000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_48", "unified", 0x00ff000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED_8_56", "unified", 0xff00000000000000, False, False, 0,0, { { 0, 8} } }
  { "R_CUDA_UNIFIED32_LO_32", "unified", 0x00000000ffffffff, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_UNIFIED32_HI_32", "unified", 0xffffffff00000000, False, False, 0,0, { { 32, 32} } }
  { "R_CUDA_ABS56_16_34", 0xffffffffffffffff, False, False, 0,2, { { 16, 8}, { 34, 48} } }
  { "R_CUDA_CONST_FIELD22_37", 0xffffffffffffffff, "ConstBankAddress0", False, False, 0,0, { { 37, 22} } }
    """

    result = []
    lines_iter = itt.islice(examples, 0, None)
    while True:
        c = next(lines_iter, False)
        if not c: break

        if c =='{': 
            res = SASS_Parser_List.parse(lines_iter)
            result.append(res)

    pass