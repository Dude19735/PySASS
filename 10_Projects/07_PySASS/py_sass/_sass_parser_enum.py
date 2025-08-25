import itertools as itt
from ._sass_util import SASS_Util as su
from . import _config as sp

class SASS_Parser_Enum:
    """
    This one is part of the instructions.txt parser.

    This one covers all the ones that enumerate stuff
    """

    @staticmethod 
    def parse_expression(xx:str, enum_counter:int, local_res:dict):
        # in the special case
        # USCHED_INFO
        #   OFF_DECK_DRAIN=0,
        #   DRAIN *= 0, ...
        # we have no idea what the *= stands for. In all txt files, this
        # only appears with the DRAIN and nowhere else => just ignore it ^^
        if xx.find('DRAIN *') >= 0:
            xx = xx.replace('DRAIN *', 'DRAIN')
        expr = [x.strip() for x in xx.split('=') if x.strip()]
        if len(expr) == 2:
            res = SASS_Parser_Enum.parse_assignment(expr, local_res)
            vals = res.values()
            if isinstance(next(iter(vals)), int):
                enum_counter = max(res.values())+1 # type: ignore
            return res, enum_counter, [(i[0],i[1]) for i in res.items()]

        expr = [x.strip() for x in expr[0].split('+') if x.strip()]
        if len(expr) > 1 or (len(expr) == 1 and xx.strip().startswith('=')):
            result = dict(itt.chain.from_iterable([list(local_res[i].items()) for i in expr]))
            return result, enum_counter, [(i[0],i[1]) for i in result.items()]

        res = SASS_Parser_Enum.parse_side(expr[0], local_res)
        res_expr = []
        if isinstance(res, list):
            rr = {}
            for i in res:
                rr[i] = enum_counter
                res_expr.append((i, enum_counter))
                enum_counter += 1
            result = rr
        else:
            result = {res : enum_counter}
            res_expr.append((res, enum_counter))
            enum_counter += 1
        return result, enum_counter, res_expr


    @staticmethod
    def parse_assignment(assignment:list, local_res:dict):
        lside = SASS_Parser_Enum.parse_side(assignment[0], local_res)
        rside = SASS_Parser_Enum.parse_side(assignment[1], local_res)
        if isinstance(lside, list):
            return dict(zip(lside, rside)) # type: ignore
        else:
            return { lside : rside }

    @staticmethod
    def parse_side(side:str, local_res:dict):
        xx = side.split('..')
        if len(xx) == 2:
            return SASS_Parser_Enum.parse_sequence(xx, local_res)
        else:
            return su.try_convert(side, convert_hex=True, convert_bin=True)

    @staticmethod
    def parse_sequence(seq:list, local_res:dict):
        xx0  = seq[0].split('(')
        xx1 = seq[1].strip(')')
        prefix = ""
        if len(xx0) == 2:
            prefix = xx0[0]
        from_s = int(xx0[-1])
        to_s = int(xx1)

        seqr = list(range(from_s, to_s+1))
        if prefix:
            return [prefix + str(s) for s in seqr]
        return seqr

    @staticmethod
    def parse(lines_iter:itt.islice, local_res:dict):
        result = {}
        entry = []
        entries = []
        enum_counter = 0
        while True:
            i = next(lines_iter, False)
            if not i: break

            if i == ';':
                entries.append("".join(entry).strip())
                entry = []
                break
            elif i == ',':
                entries.append("".join(entry).strip())
                entry = []
            else:
                entry.append(i)

        res_entries = []
        for e in entries:
            res, enum_counter, res_e_entries = SASS_Parser_Enum.parse_expression(e, enum_counter, local_res)
            result = su.update_dict(res, result) 
            res_entries.extend(res_e_entries)

        inter = [(i,[gg[1] for gg in g]) for i,g in itt.groupby(res_entries, key=lambda x: x[0])]
        rr = {}
        for i in inter:
            if i[0] not in rr:
                rr[i[0]] = set()
            for b in i[1]:
                if isinstance(b, int):
                    rr[i[0]].add(b)
                elif isinstance(b, str):
                    rr[i[0]].add(su.try_convert(b, convert_bin=True, convert_hex=True, convert_split_bin=True))
                elif isinstance(b, set):
                    rr[i[0]] = rr[i[0]].union(b)
                else:
                    raise Exception(sp.CONST__ERROR_UNEXPECTED)

        if len(rr) != len(result):
            raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return '', rr

if __name__ == '__main__':
    with open('./py_sass/enum_example.txt','r') as f:
        examples = f.read()

    tt = {
        "ARCHITECTURE": None, 
        "PARAMETERS": None, 
        "CONSTANTS": None, 
        "REGISTERS": SASS_Parser_Enum.parse, 
        "TABLES": None, 
        "NOP_ENCODING": None, 
        "ALTERNATE CLASS": None, 
        "CLASS": None
    }

    result = {}
    local_result = {}
    lines_iter = itt.islice(examples, 0, None)
    entry = []
    ff = None
    cur_nn = ''
    while True:
        c = next(lines_iter, False)
        if not c:
            if cur_nn and local_result:
                result[cur_nn] = local_result
                local_result = {} 
            break

        if c in (' ', '\n'):
            nn = "".join(entry).strip()
            while nn:
                if nn in tt.keys():
                    ff = tt[nn]
                    if cur_nn:
                        result[cur_nn] = local_result
                        local_result = {}
                    cur_nn = nn
                    nn = ''
                    entry = []
                elif nn and ff:
                    new_nn, res = ff(lines_iter, local_result)
                    local_result = su.update_dict({nn: res}, local_result)
                    nn = new_nn
                    entry = []
                else:
                    nn = ''
        else:
            entry.append(c)
            

    pass