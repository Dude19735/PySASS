import itertools as itt

class SASS_Parser_Condition:
    """
    This one is part of the instructions.txt parser.

    This one parses things of the shape like
    ... MAIN_KEY
        SUB_KEY_1 : VAL_1
        ...
        SUB_KEY_N : VAL_N

    The result is a dictionary of shape
    { MAIN_KEY : { SUB_KEY_1 : VAL_1, ..., SUB_KEY_N : VAL_N }}
    """

    @staticmethod
    def parse(lines_iter:itt.islice, local_res:dict):
        result = {}
        entry = []
        name = ""
        state = 0
        while True:
            i = next(lines_iter, False)
            if not i: break

            if state == 0 and i == '\n':
                state = 1
                name = "".join(entry)
                entry = []
            elif state == 1 and i == '\n':
                nn = "".join(entry)
                vals = [x.strip() for x in nn.split(':')]
                if not len(vals) == 2:
                    break
                result[vals[0]] = vals[1]
                entry = []
            else:
                entry.append(i)
        
        return vals[0], {name : result} # type: ignore
    
if __name__ == '__main__':
    examples = """
   CONDITION TYPES
      ILLEGAL_INSTR_ENCODING_ERROR : ERROR
      OOR_REG_ERROR : ERROR
      MISALIGNED_REG_ERROR : ERROR
      INVALID_CONST_ADDR_ERROR : ERROR
      MISALIGNED_ADDR_ERROR : ERROR
      UNPREDICTABLE_BEHAVIOR_ERROR : ERROR
      PC_MISALIGNED_ERROR : ERROR
      ILLEGAL_INSTR_ENCODING_WARNING : WARNING
      OOR_REG_WARNING : WARNING
      MISALIGNED_REG_WARNING : WARNING
      INVALID_CONST_ADDR_WARNING : WARNING
      MISALIGNED_ADDR_WARNING : WARNING
      UNPREDICTABLE_BEHAVIOR_WARNING : WARNING
      ILLEGAL_INSTR_ENCODING_INFO : INFO
      OOR_REG_INFO : INFO
      MISALIGNED_REG_INFO : INFO
      INVALID_CONST_ADDR_INFO : INFO
      MISALIGNED_ADDR_INFO : INFO
      UNPREDICTABLE_BEHAVIOR_INFO : INFO
      ILLEGAL_INSTR_ENCODING_SASS_ONLY_ERROR : ERROR
      INVALID_CONST_ADDR_SASS_ONLY_ERROR : ERROR
PARAMETERS
    MAX_REG_COUNT = 255
    SHADER_TYPE = 0
    MAX_CONST_BANK = 17
"""
    result = {}
    lines_iter = itt.islice(examples, 0, None)
    entry = []
    while True:
        c = next(lines_iter, False)
        if not c: break

        if c in (' ', '\n'):
            nn = "".join(entry).strip()
            while nn != '':
                if nn == "CONDITION":
                    nn, res = SASS_Parser_Condition.parse(lines_iter, result)
                    result.update(res)
                    entry = []
                else:
                    nn = ''
        else:
            entry.append(c)
            

    pass