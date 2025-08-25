from ._tt_terms import TT_List, TT_Accessor, TT_Ext, TT_Default

class TT_Term:
    """
    Helper class for SASS_Class parser
    To parse the unknown text in sm_xx_instructions.txt, we need some very
    general expression of a token. This class is able to represent all types
    of token combinations and print them such that the output matches the parsed
    input string.

    Later on, all of these generalized tokens will be transmuted into somehing more
    specific (that is what all other classes in this file are for)
    """
    def __init__(self, tt:str, val):
        self.tt = tt
        self.ops = None
        self.val = val
        self.attr = []
        self.ext = []
        self.default = []
        self.star = None
        self.alias = None
        self.unknown_def = None
        # something like this: /LOOnly(LO)@:hilo
        #  => hilo alias does not appear in encoding
        self.is_at_alias = False
        # for default values that look like this: F32.F32/PRINT
        # there is only this specific case
        self.default_has_print = False
        # for things like this:
        # C:srcConst[UImm(5/0*):constBank]* [SImm(17)*:immConstOffset]
        # or this
        # A:srcAttr[Register:Ra]
        self.access_func = None

    def add_unknown(self, unknown_def):
        self.unknown_def = unknown_def

    def add_op(self, ops):
        self.ops = ops

    def add_attr(self, attr):
        if not attr.tt == TT_List.tt():
            raise Exception("Attempt to attach non-list type attribute to function")
        if not self.tt == TT_Accessor.tt():
            raise Exception("Attempt to attach attribute to non-access_func")
        self.attr.append(attr)

    @property
    def has_attr(self):
        return self.attr != []
    
    @property
    def has_star(self):
        return self.star != None

    def add_ext(self, ext):
        self.ext.extend(ext)

    def add_default(self, default):
        self.default.extend(default)

    def add_star(self, star):
        self.star = star

    def add_access_func(self, func):
        self.access_func = func

    def add_alias(self, alias):
        self.alias = alias

    def set_is_at_alias(self):
        self.is_at_alias = True

    def set_default_has_print(self):
        self.default_has_print = True

    def __str__(self):
        res = ''
        if self.tt == '$':
            res += '$( { '
            for i in self.val:
                res += str(i) + " "
            res += '} )$'
            return res
        elif self.tt == TT_Ext.tt(): res += '/'
        if self.ops:
            for o in self.ops:
                res += "[" + o.val + "]"
        if isinstance(self.val, str):
            res += self.val
        elif isinstance(self.val, int):
            res += str(self.val)
        else:
            res += '['
            for ind, i in enumerate(self.val):
                res += str(i)
                if ind < len(self.val)-1:
                    res += '+'
            res += ']'
        if self.access_func:
            res += ':' + str(self.access_func)
        if self.attr:
            for ind, i in enumerate(self.attr):
                res += str(i)
                if ind < len(self.attr)-1:
                    if self.star: res += '*'
        if self.tt == TT_Default.tt():
            if self.unknown_def:
                res += '[->unkown:' + self.unknown_def + ']'
        if self.default:
            res += "("
            for ind,d in enumerate(self.default):
                res += str(d)
                if ind < len(self.default)-1:
                    res += '/' 
                if d.default_has_print:
                    res += '/PRINT'
            res += ")"
        if not self.attr and self.star: res += self.star
        if self.alias:
            if not self.is_at_alias:
                res += ":" + self.alias
            else:
                res += "@:" + self.alias
        if self.ext:
            for ee in self.ext:
                # res += " " + str(ee)
                res += str(ee)
        return res 
