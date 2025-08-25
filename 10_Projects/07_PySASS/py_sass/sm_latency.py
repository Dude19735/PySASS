import re
import os
import typing
import tabulate
import itertools as itt
from . import _config as sp
from ._sass_expression import SASS_Expr
from .sass_class import Iterator
from .sass_class import SASS_Class
from .sm_cu import SM_Cu

class SM_HELPERS:
    @staticmethod
    def line_parser(sets_str:str, outer_dict:dict):
        ii:Iterator = Iterator(sets_str)
        entry = []
        sets = []
        while True:
            c = next(ii, False)
            if not c: break
            if c in [' ', '\n']: continue
            if c in ['=',';']:
                cur = "".join(entry)
                sets.append(cur)
                entry = []
            else: entry.append(c)

        return sets

class SM_LAT_BASE:
    def __init__(self, sm:int, tt:str):
        self.__sm = sm
        self.__tt = tt
    
    @property
    def sm(self): return self.__sm
    @property
    def tt(self): return self.__tt

class OPERATION_SETS(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        sets = SM_HELPERS.line_parser("".join(lines), outer_dict)

        eval_sets = {}
        for i in range(0, len(sets), 2):
            e = SASS_Expr(sets[i+1], {}, {}, {}, {}, {})
            e.finalize({}, outer_dict)
            eval_sets[sets[i]] = e
            outer_dict[sets[i]] = e

        self.__sets = dict()
        for k in eval_sets:
            self.__sets[k] = eval_sets[k]({})

    @property
    def sets(self): return self.__sets

    def __str__(self):
        return "{0}\n   {1}".format(self.tt, "\n   ".join("{0} = {1}".format(k,v) for k,v in self.sets.items()))

class CONNECTOR_SETS(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        pl = [SM_HELPERS.line_parser(l, outer_dict) for l in lines]
        for h,l in pl:
            lt = l.split('+')
            if not CONNECTOR_SETS.__name__ in outer_dict[stage]:
                outer_dict[stage][CONNECTOR_SETS.__name__] = dict()    
            outer_dict[stage][CONNECTOR_SETS.__name__][h] = lt

class BIT_SETS(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        if len(lines) > 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        name, values = SM_HELPERS.line_parser(lines[0], outer_dict)
        values = {v for v in values[1:-1].split(',')}
        values = set(itt.chain.from_iterable([k for k in sm_cu.details.REGISTERS.Test if k.startswith(bb)] for bb in values)) # type: ignore

        self.__name = name
        self.__values = values
        outer_dict[self.__name] = self

    @property
    def name(self): return self.__name
    @property
    def values(self): return self.__values

    def __str__(self):
        return "{0}\n   {1}".format(self.tt, "{0} = {1}".format(self.name, self.values))

class RESOURCE(SM_LAT_BASE):
    @staticmethod
    def parse_head(head_str:str):
        name = ""
        default = ""
        bits = ""

        ii = Iterator(head_str)
        entry = []
        has_bits = False
        while True:
            c = next(ii, False)
            if c == False: break
            if c == '(':
                if has_bits:
                    bits = "".join(entry)
                else:
                    name = "".join(entry)    
                entry = []
            elif c == ':':
                has_bits = True
                name = "".join(entry)
                entry = []
            elif c == ')':
                default = "".join(entry)
                entry = []
            else: entry.append(c)
        if name == "":
            name = "".join(entry)    
            entry = []
        return (name, bits, default)
    
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        
        default_anti = None
        default_output = None
        name = None
        bits = None
        default = None
        values = None
        self.__ordered_zero = sp.SM_LATENCY__ORDERED_ZERO_VAL
        self.__special_connectors = set()

        for l in lines:
            if l.startswith('DEF'):
                if l.startswith('DEFAULT_ANTI'):
                    default_anti = l.split('=')[-1].strip(';')
                    if default_anti == 'ORDERED_ZERO': default_anti = self.__ordered_zero
                    elif default_anti.startswith('HARD'): default_anti = int(default_anti.split('(')[-1][:-1])
                    else: default_anti = int(default_anti)

                elif l.startswith('DEFAULT_OUTPUT'):
                    default_output = l.split('=')[-1].strip(';')
                    if default_output == '-': default_output = None
                    elif default_output == 'ORDERED_ZERO': default_output = self.__ordered_zero
                    elif default_output.startswith('HARD'): default_output = int(default_output.split('(')[-1][:-1])
                    else: default_output = int(default_output)

            else:
                ll = SM_HELPERS.line_parser(l, outer_dict)
                name, bits, default = RESOURCE.parse_head(ll[0])
                if len(ll) == 2:
                    tail = SASS_Expr(ll[1], {}, {}, {}, {}, {})
                    tail.finalize({}, outer_dict)
                    values = tail({})
                if bits != "":
                    if not bits in outer_dict: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    
        self.__default_anti = default_anti
        self.__default_output = default_output
        self.__name = name
        self.__bits = bits
        self.__default = default
        self.__values = values

        if stage not in outer_dict: outer_dict[stage] = dict()
        outer_dict[stage][self.__name] = self

        self.__connector_names = dict()

    @property
    def default_anti(self): return self.__default_anti
    @property
    def default_output(self): return self.__default_output
    @property
    def name(self): return self.__name
    @property
    def bits(self): return self.__bits
    @property
    def default(self): return self.__default
    @property
    def values(self): return self.__values
    @property
    def ordered_zero(self): return self.__ordered_zero
    @property
    def connector_names(self): return self.__connector_names
    @property
    def special_connectors(self): return self.__special_connectors

    def __str__(self):
        res = []
        if self.name: res.append(self.name)
        if self.bits: res.extend([" : ", self.bits])
        if self.default: res.extend(["(", self.default, ")"])
        if self.values: res.append(" = {0}".format(self.values))
        rr = "".join(res)
        if rr: 
            rr += ';'
            res = [rr]
        if self.default_anti is not None: res.append("DEFAULT_ANTI = {0};".format(self.default_anti))
        else: res.append("DEFAULT_ANTI = -;")
        if self.default_output is not None: res.append("DEFAULT_OUTPUT = {0};".format(self.default_output))
        else: res.append("DEFAULT_OUTPUT = -;")

        resources = "{0}\n   {1}".format(self.tt, "\n   ".join(res))

        res = []
        for k,n in self.__connector_names.items():
            res.append("{0} = {1}".format(k, n))
        
        connectors = "{0}\n   {1}".format('CONNECTOR NAMES({0})'.format(self.name), "\n   ".join(res))

        return "{0}\n{1}".format(resources, connectors)
    
    def add_connector_name(self, name:str, connectors:set):
        if name == 'all_connectors':
            self.__connector_names[name] = {c:self.values for c in connectors}
        else:
            # Kick this one out, it's not being used anywhere
            if name == 'sBoard': 
                self.__connector_names[name] = set()
                return
            elif name in ['PR_PRED', 'PR_CC', 'UPR_UPRED']:
                self.__special_connectors.add(name)
                if not 'all_connectors' in self.connector_names: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                self.__connector_names[name] = {c:connectors for c in self.connector_names['all_connectors'].keys()}
            else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

class CONNECTOR_NAMES(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        
        pl = [SM_HELPERS.line_parser(l, outer_dict)[0] for l in lines]
        for l in pl:
            head, resource_name = l.split(':')
            if not resource_name in outer_dict[stage]: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            resource:RESOURCE = outer_dict[stage][resource_name]

            if head.endswith('}'):
                name, connectors = head[:-1].split('{')
                connectors = set(i for i in connectors.split(',') if i)
            else:
                name = 'all_connectors'
                connectors = set(i for i in head.split(',') if i)
            resource.add_connector_name(name, connectors)

class CONNECTOR_CONDITIONS(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        self.__conditions = sp.SM_LATENCY__CONNECTOR_CONDITIONS[sm]
        outer_dict[CONNECTOR_CONDITIONS.__name__] = self.__conditions

    @property
    def conditions(self): return self.__conditions

    def __str__(self):
        return "{0}\n   {1}".format(self.tt, "\n   ".join([k + " : " + str(v) for k,v in self.conditions.items()]))

class TABLE_RC:
    def __init__(self, col_str:str, resource:RESOURCE, outer_dict:dict):
        head, params = col_str.split('`')
        
        params = params.strip('{').strip('}')
        head = head.split('[')
        if len(head) == 2:
            head_set = head[0]
            head_condition = head[1].strip(']')
            if head_condition.startswith('?'):
                head_condition = head_condition[1:] + "==1"
            
            if head_condition in outer_dict[CONNECTOR_CONDITIONS.__name__]:
                head_condition = outer_dict[CONNECTOR_CONDITIONS.__name__][head_condition]    
            else:
                head_condition = SASS_Expr(head_condition, {}, {}, {}, {}, {})
        elif len(head) == 1:
            head_set = head[0]
            head_condition = None
        else: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        params = [[pp.strip() for pp in p.split('@')] for p in params.split(',')]
        mods = {m[0] : outer_dict[CONNECTOR_CONDITIONS.__name__][m[1]] for m in params if len(m) == 2}
        params = {p[0] for p in params}
        all_params = dict()
        capital_input = []
        for param in params:
            if param in resource.special_connectors:
                capital_input.append(param)
                for p,v in resource.connector_names[param].items():
                    all_params[p] = v
            elif param == 'sBoard':
                all_params[param] = resource.connector_names[param]
            else:
                all_params[param] = resource.connector_names['all_connectors'][param]
        
        self.__head_set = head_set
        self.__head_condition = head_condition
        self.__all_params = all_params
        self.__mods = mods
        self.__capital_input = ",".join(capital_input)
        self.__resource = resource

    @property
    def head_set(self): return self.__head_set
    @property
    def head_condition(self): return self.__head_condition
    @property
    def all_params(self): return self.__all_params
    @property
    def mods(self): return self.__mods
    @property
    def resource(self): return self.__resource
    @property
    def capital_input(self): return "({0})".format(self.__capital_input) if self.__capital_input else ""

    def __str__(self):
        return "{0}{1}[{2}]`{{{3}}}".format(self.head_set, "{0}".format(self.__capital_input) if self.__capital_input else "", self.head_condition, self.all_params)
    
    def match(self, aliases:set):
        return aliases.intersection(self.all_params)

class TABLE(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        if lines[0].startswith('#80102'):
            self.__table_name = lines[0].split('_')[-1]
            lines = lines[1:]
        else: self.__table_name = '[NAMELESS]'
        
        c = "\n".join(lines)
        hw_input, c = [i.strip() for i in c.split(':',1)]
        hw_name = hw_input.strip('(').strip(')')

        if not hw_name in outer_dict[stage]:
            real_hw_name, bits = hw_name.split('|')
            hw_name = real_hw_name.strip()
            bits = bits.strip()
            if not hw_name in outer_dict[stage]:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            self.__resource = outer_dict[stage][hw_name]
        else:
            self.__resource = outer_dict[stage][hw_name]
        
        nl = "\\s*=\\s*[\n]*{"
        ss = [(m.start(), m.end()) for m in re.finditer(nl, c)]
        if len(ss) != 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        head = c[:(ss[0][0])].strip()
        body = c[ss[0][1]:].strip()
        body = body.strip('{').strip('};')
        
        def get_cc(c:str, resource:RESOURCE, outer_dict:dict) -> typing.List[TABLE_RC]:
            if CONNECTOR_SETS.__name__ in outer_dict[stage]:
                if c in outer_dict[stage][CONNECTOR_SETS.__name__]:
                    connector_sets = outer_dict[stage][CONNECTOR_SETS.__name__][c]
                    return [TABLE_RC(cc, resource, outer_dict) for cc in connector_sets]
                
            return [TABLE_RC(c, resource, outer_dict)]
            
        cols = [get_cc(c, self.__resource, outer_dict) for c in head.split('\n')]
        body = [i for i in body.split('\n') if i]
        body = [[bb.strip() for bb in b.split(':')] for b in body]
        rows = []
        vals = []
        for r,b in body:
            rows.append(get_cc(r, self.__resource, outer_dict))
            vv = []
            for i in b.split():
                if i == sp.SM_LATENCY__ORDERED_ZERO:
                    if not hw_name in outer_dict[stage]: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    resource:RESOURCE = outer_dict[stage][hw_name]
                    vv.append(resource.ordered_zero)
                else: vv.append(int(i))
            vals.append(vv)

        # extend to cover number of columns
        if not len(vals[0]) == len(cols):
            if not all(len(v) == 1 for v in vals): raise Exception(sp.CONST__ERROR_UNEXPECTED)
            vals = [len(cols)*v for v in vals]

        # do row/col assignment for values
        vals_rc = dict()
        counter = 0
        for vv,r in zip(vals, rows):
            for v,c in zip(vv, cols):
                pp = list(itt.product([(x.head_set, x) for x in r], [(y.head_set, y) for y in c]))
                for p in pp:
                    vals_rc[(p[0][1], p[1][1])] = {'v':v, 'r':p[0][0], 'c':p[1][0]}
                    counter += 1

        if not counter == len(vals_rc): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        self.__hw_name = hw_name
        self.__cols = cols
        self.__rows = rows
        self.__vals = vals
        self.__vals_rc = vals_rc

    @property 
    def table_name(self): return self.__table_name
    @property
    def hw_name(self): return self.__hw_name
    @property
    def resource(self): return self.__resource
    @property
    def cols(self): return self.__cols
    @property
    def rows(self): return self.__rows
    @property
    def vals(self): return self.__vals
    @property
    def vals_rc(self): return self.__vals_rc

    def match(self, sets:set, aliases:set, t_type:str):
        m = [{
            'table' : self.table_name,
            'input' : self.hw_name,
            'val' : i['v'],
            'r' : i['r'],
            'rp': set(rc[0].all_params),
            'capr' : rc[0].capital_input,
            'ri' : rc[0].match(aliases),
            'c' : i['c'],
            'cp' : set(rc[1].all_params),
            'capc' : rc[1].capital_input,
            'ci' : rc[1].match(aliases),
            't' : t_type
            } for rc,i in self.vals_rc.items() if (i['r'] in sets and i['c'] in sets)]
        
        for mm in m:
            mm['mcount'] = int(len(mm['ri']) > 0) + int(len(mm['ci']) > 0)

        return m

    def __str__(self):
        res = []
        res.append(self.tt)
        res.append("({0}) : {1}".format(self.hw_name, self.cols[0]))
        indent = "   "
        n_indent = 1
        for c in self.cols[1:]:
            res.append("{0}{1}".format(n_indent*indent,c))
            n_indent += 1
        res[-1] += " = "
        res.append("{")
        for r,v in zip(self.rows, self.vals):
            res.append("{0}{1} : {2}".format(indent, r, " ".join(str(i) for i in v)))
        res.append("};")
        return "\n".join(res)

class PIPELINE(SM_LAT_BASE):
    def __init__(self, sm_cu:SM_Cu, sm:int, tt:str, lines:list, outer_dict:dict, stage:str):
        super().__init__(sm, tt)
        resource = dict()
        operation = dict()
        ind=0
        for ind,l in enumerate(lines):
            if l == 'OPERATION PIPELINE RESOURCES': break
            rr = l.split(':')
            resource[rr[0].strip()] = int(rr[1].strip().strip(';'))
        ind2=0
        for ind2,l in enumerate(lines[(ind+1):]):
            rr = l.split(':')
            operation[rr[0].strip()] = rr[1].strip().strip(';')

        if not (ind + 1 + ind2 + 1 == len(lines)): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        self.__resource = resource
        self.__operation = operation
        
    @property
    def resource(self): return self.__resource
    @property
    def operation(self): return self.__operation

    def __str__(self):
        res = [self.tt]
        res.append("   " +  "\n   ".join(k + " : " + str(v) + ";" for k,v in self.resource.items()))
        res.append("OPERATION PIPELINE RESOURCES")
        res.append("   " +  "\n   ".join(k + " : " + str(v) + ";" for k,v in self.operation.items()))
        return "\n".join(res)

class SM_Latency:
    __PARTS = {
        "BIT SETS": BIT_SETS,
        "OPERATION SETS": OPERATION_SETS,
        "CONNECTOR SETS": CONNECTOR_SETS,
        "RESOURCE": RESOURCE,
        "HARD RESOURCE": RESOURCE,
        "CONNECTOR NAME": CONNECTOR_NAMES,
        "CONNECTOR NAMES": CONNECTOR_NAMES,
        "CONNECTOR CONDITIONS": CONNECTOR_CONDITIONS,
        sp.SM_LATENCY__TABLE_OUTPUT: TABLE,
        sp.SM_LATENCY__TABLE_TRUE: TABLE,
        sp.SM_LATENCY__TABLE_ANTI: TABLE,
        "PIPELINE RESOURCE": PIPELINE
    }

    __COMMENTS = {
        "BIT SETS": "% These are masks for some Test registers (Currently not really used)",
        "OPERATION SETS": "% Instruction classes pipeliens and opcodes",
        "CONNECTOR SETS": "% N/A",
        "RESOURCE": "% These are register value names",
        "HARD RESOURCE": "% These are register value names",
        "CONNECTOR NAME": "% These are names of aliases",
        "CONNECTOR NAMES": "% These are names of aliases",
        "CONNECTOR CONDITIONS": "% These are used from ._config.py",
        "TABLE_OUTPUT": "% Output to Output map (Rd, Rd2... to Rd, Rd2...)",
        "TABLE_TRUE": "% Input to Output map (Ra, Rb, Rc... to Rd, Rd2...)",
        "TABLE_ANTI": "% Output to Input map (Rd, Rd2... to Ra, Rb, Rc...)",
        "PIPELINE RESOURCE": "% Pipeline resources"
    }

    def __init__(self, sm:int, sm_cu:SM_Cu):
        location = os.path.dirname(os.path.realpath(__file__))
        path = location + '/DocumentSASS'
        doc = path + "/sm_{0}_latencies.txt.in".format(sm)

        outer_dict:dict = dict()
        lines = []
        with open(doc, 'r') as f: lines = f.readlines()
        if not lines: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # Remove the comment lines
        cur = ""
        op_sets = {}
        rr = re.compile("^#74205_[A-Z]+[0-9]+$")
        for line in lines:
            if not line.startswith('%'): 
                l = line.strip()
                if not l: continue
                if rr.match(l):
                    cur = l.split('_')[-1]
                    op_sets[cur] = []
                else: 
                    op_sets[cur].append(l)

        content = dict()
        for s,c in op_sets.items():
            line_inds = []
            content[s] = dict()
            ind=0
            for ind,cc in enumerate(c):
                if cc in SM_Latency.__PARTS: line_inds.append(ind)
            line_inds.append(ind+1)
            for f,t in zip(line_inds[:-1], line_inds[1:]):
                cc = c[f]
                part = SM_Latency.__PARTS[cc](sm_cu, sm, cc, c[(f+1):t], outer_dict, s)
                # Don't store the connector names. They are added to their respective resources.
                # The reason for this weird split is that it's not sure if all connector names immediately
                # follow their resource definitions.
                if cc in {'CONNECTOR NAME', 'CONNECTOR NAMES'}: continue
                if not cc in content[s]: content[s][cc] = []
                content[s][cc].append(part)
            pass
        
        res = []
        for k,v in outer_dict.items():
            if isinstance(v, SASS_Expr): res.append(v({}))

        # Make sure all the pipes and opcodes of the current sm are somewhere in the latencies as well
        # NOTE: there are non-existing pipes and opcodes in the latency files. This appears to be yet another neglected area.
        latency_set = set(itt.chain.from_iterable(res))
        if len(sm_cu.latency_set.difference(latency_set)) > 0: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        i_tt = itt.chain.from_iterable
        self.__op_sets = dict(i_tt([i for i in s.sets.items()] for s in i_tt(i_tt([ content[c][cc] for cc in content[c] if c.startswith('STAGE') and cc == 'OPERATION SETS'] for c in content))))
        self.__content = content

        tt = sp.SM_LATENCY__TABLE_TRUE
        self.__table_true = list(i_tt(s[tt] if tt in s else [] for s in self.content.values()))
        tt = sp.SM_LATENCY__TABLE_OUTPUT
        self.__table_output = list(i_tt(s[tt] if tt in s else [] for s in self.content.values()))
        tt = sp.SM_LATENCY__TABLE_ANTI
        self.__table_anti = list(i_tt(s[tt] if tt in s else [] for s in self.content.values()))
    
    @property
    def content(self): return self.__content
    @property
    def op_sets(self): return self.__op_sets
    @property
    def tables_true(self): return self.__table_true
    @property
    def tables_output(self): return self.__table_output
    @property
    def tables_anti(self): return self.__table_anti

    def match(self, instr_class:SASS_Class):
        sets = []
        pipe = instr_class.OPCODES['pipes'][0]['i']
        instr = instr_class.OPCODES['opcode']['i']
        for s,v in self.op_sets.items():
            if (pipe in v or instr in v):
                sets.append(s)

        # [print("{0}\nr={1}, c={2}\n, alias={3}\n".format(t[0],t[1],t[2], aliases)) for t in ttm]

        opa = instr_class.get_operand_alias()
        matches = []
        m = [t.match(set(sets), opa, 'T') for t in self.tables_true]
        for mm in m: 
            if mm:
                matches.append(mm)
        m = [t.match(set(sets), opa, 'F') for t in self.tables_output]
        for mm in m:
            if mm:
                matches.append(mm)
        m = [t.match(set(sets), opa, 'A') for t in self.tables_anti]
        for mm in m: 
            if mm: matches.append(mm)

        matches = list(itt.chain.from_iterable(matches))
        
        return {'c': instr_class, 'opa': opa, 'm': matches}

    def __str__(self):
        res = []
        for s,v in self.__content.items():
            res.append("% =========================================================")
            res.append("#74205_{0}".format(s))
            res.append("% =========================================================")
            for tt,vv in v.items():
                for vvv in vv:
                    res.append(self.__COMMENTS[tt])
                    cur = "{0}\n".format(str(vvv))
                    res.append(cur)
        return "\n".join(res)
    
    @staticmethod
    def matches_to_str(matches:dict, condition:typing.Callable, remove_quotes:bool=True):
        m = matches['m']
        entries = [["[{0}]".format(t['t']), 
                t['input'], t['table'], 
                t['r'] + t['capr'] + str(t['rp']),
                t['c'] + t['capc'] + str(t['cp']), 
                "{0}[x]{1}".format(t['ri'] if t['ri'] else '{}', t['ci'] if t['ci'] else '{}'), 
                t['val']] 
            for t in m if condition(t['mcount'])]
        
        if remove_quotes: entries = [[ii.replace("'", "") if isinstance(ii, str) else ii for ii in i] for i in entries]
        if entries: return str(tabulate.tabulate([["Type", "Input", "Table", "Row", "Col", "Cross", "Val"]] + entries, headers="firstrow"))
        else: return ""

    @staticmethod
    def matches_to_table(matches:dict, condition:typing.Callable):
        m = matches['m']
        entries = [["[{0}]".format(t['t']), 
                t['input'], t['table'], 
                t['r'] + t['capr'] + str(t['rp']),
                t['c'] + t['capc'] + str(t['cp']), 
                "{0}[x]{1}".format(t['ri'] if t['ri'] else '{}', t['ci'] if t['ci'] else '{}'), 
                t['val']] 
            for t in m if condition(t['mcount'])]
        
        if entries: return [["Type", "Input", "Table", "Row", "Col", "Cross", "Val"]] + entries
        else: return []

    @staticmethod
    def matches_to_file(filename:str, matches_dicts:list, condition1:typing.Callable, condition2:typing.Callable):
        with open(filename, 'w') as f:
            for matches in matches_dicts:
                class_ = matches['c']
                opa = matches['opa']
                m = matches['m']

                if not condition1(sum(int(t['mcount'] == 2) for t in m)): continue
                    
                entries_str = SM_Latency.matches_to_str(m, condition2)
                
                if not entries_str: continue
                f.write("===========================================================================================================================================\n{0}: {1}\n".format(class_.class_name, opa))
                f.write("\n")
                f.write(str(class_.FORMAT))
                f.write("\n\n")
                f.write(entries_str)
                f.write('\n')

# if __name__ == '__main__':
#     sms = [50,52,53,60,61,62,70,72,75,80,86,90,100,120]
#     sms = [50]
#     for sm in sms:
#         print("= {0} =======================================".format(sm))
#         s = SM_Latency(50)
#         print(s)
