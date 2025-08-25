import operator
import typing
import itertools as itt
from . import _config as sp
from .sm_cu_details import SM_Cu_Details

class SASS_Expr_Domain_Contract:
    """
    This one takes care of constructing the least amount of sets that cover all possibilities. Check out the test case at the end
    to compare the naive version based on one single groupby and the more fancy one based on a recursively applied groupby.

    Since we test all possible cases for domains that are small enough, we get a list of dictionaries for which a given
    expression evaluates to True. For example
    s1 = [
        {'a':0, 'b':0, 'c':0},
        {'a':0, 'b':0, 'c':1},
        {'a':0, 'b':0, 'c':2},
        {'a':0, 'b':0, 'c':3},
        {'a':0, 'b':1, 'c':0},
        {'a':0, 'b':1, 'c':1},
        {'a':0, 'b':2, 'c':0},
        {'a':0, 'b':2, 'c':1},

        {'a':1, 'b':0, 'c':0},
        {'a':1, 'b':0, 'c':1},
        {'a':1, 'b':1, 'c':0},
        {'a':1, 'b':1, 'c':1},
        {'a':1, 'b':2, 'c':0},
        {'a':1, 'b':2, 'c':1},
    ]

    To prevent the domain representation to blow up in size, it is necessary to contract all of these into a representation that uses
    sets.

    The group_naive will produce the following.
    {'a': {0}, 'b': {0}, 'c': {0, 1, 2, 3}}
    {'a': {0}, 'b': {1}, 'c': {0, 1}}
    {'a': {0}, 'b': {2}, 'c': {0, 1}}
    {'a': {1}, 'b': {0}, 'c': {0, 1}}
    {'a': {1}, 'b': {1}, 'c': {0, 1}}
    {'a': {1}, 'b': {2}, 'c': {0, 1}}
    6 sets is better than 14, but NOTE that in the triples (a=0,b=1,c=0), (a=0,b=1,c=1), (a=0,b=2,c=0), (a=0,b=2,c=1)
    the values of a and c are independent of the value of b. Thus the respective sets {'a': {0}, 'b': {1}, 'c': {0, 1}} and 
    {'a': {0}, 'b': {2}, 'c': {0, 1}} which are the source for the 4 example triples, can be contracted to
    the set {'a': {0}, 'b': {1, 2}, 'c': {0, 1}}. The same is true for the three sets
    {'a': {1}, 'b': {0}, 'c': {0, 1}}
    {'a': {1}, 'b': {1}, 'c': {0, 1}}
    {'a': {1}, 'b': {2}, 'c': {0, 1}}
    where the choice of b is also independent of a and b and thus can be represented as {'a': {1}, 'b': {0, 1, 2}, 'c': {0, 1}}.

    The regular group method produces this result which has 3 sets instead of 6 at the cost of a bit of recursion. The maximal number of
    variables possible is 6 (based on exhaustive statistics on all expressions). Thus the recursion depth is limited.
    {'a': {0}, 'b': {0}, 'c': {0, 1, 2, 3}}
    {'a': {0}, 'b': {1, 2}, 'c': {0, 1}}
    {'a': {1}, 'b': {0, 1, 2}, 'c': {0, 1}}
    """

    @staticmethod
    def group_naive(okok):
        res_k = {}
        for k in okok[0].keys():
            res_k[k] = set()
        # collect all values for each alias in the result in the set, so that each value is unique
        for i in okok: 
            for k in res_k.keys(): res_k[k].add(i[k])
        # res_k contains a set for each alias with all values in all surviving possibilities out of itt.product. Sort them by their size
        # and get the aliases (keys) in ascending order into k_sorted
        asc_keys = sorted([(k, len(v)) for k,v in res_k.items()], key=operator.itemgetter(1))
        k_sorted = [k[0] for k in asc_keys]
        # we must apply the groupby to a sorted list of possibilities (okok). Sort the okok list of dictionaries according to the alias values
        s_okok = sorted(okok, key=operator.itemgetter(*k_sorted))
        gg = [list(g) for i,g in itt.groupby(s_okok, key=operator.itemgetter(*k_sorted[:-1]))]
        # gg now contains as few sets as can easily be obtained
        res = [{k: set(i[k] for i in ggg) for k in ggg[0]} for ggg in gg]

        return res
    
    @staticmethod
    def __group_rec(k_sorted, s_okok):
        k = k_sorted[0]
        if len(k_sorted) > 1:
            gg = []
            for i,g in itt.groupby(s_okok, key=operator.itemgetter(k)):
                rec,ok = SASS_Expr_Domain_Contract.__group_rec(k_sorted[1:], [dict(j for j in i.items() if j[0] != k) for i in list(g)])
                gg.append((i, rec))
        else:
            return [{k: set(itt.chain.from_iterable([i.values() for i in s_okok]))}],k

        # group by the result of the recursion (item 1), then take only the group element m[0] from each group
        pp = [(i,set(m[0] for m in g)) for i,g in itt.groupby(gg, key=operator.itemgetter(1))]
        # collect all elements with current key k into a set for the same group
        res = list(itt.chain.from_iterable([{k:n} | s for s in r] for r,n in pp))
        # return list(itt.chain.from_iterable(((s | {k: set([m[0] for m in g])}) for s in i) for i,g in itt.groupby(gg, key=operator.itemgetter(1))))
        return res,k

    @staticmethod
    def to_limit(details:SM_Cu_Details):
        raise Exception("Moved to py_sasscalc.SASS_Expr_Domain_Calc")

    @staticmethod
    def group(okok:typing.List[dict]):
        if not okok: return []

        res_k = {}
        for k in okok[0].keys():
            res_k[k] = set()
        # collect all values for each alias in the result in the set, so that each value is unique
        for i in okok: 
            for k in res_k.keys(): res_k[k].add(i[k])
        # res_k contains a set for each alias with all values in all surviving possibilities out of itt.product. Sort them by their size
        # and get the aliases (keys) in ascending order into k_sorted
        asc_keys = sorted([(k, len(v)) for k,v in res_k.items()], key=operator.itemgetter(1))
        k_sorted = [k[0] for k in asc_keys]
        # we must apply the groupby to a sorted list of possibilities (okok). Sort the okok list of dictionaries according to the alias values
        s_okok = sorted(okok, key=operator.itemgetter(*k_sorted))

        res,k = SASS_Expr_Domain_Contract.__group_rec(k_sorted, s_okok)

        # add 
        gg = [(i[k], ([(kk,i[kk]) for kk in i.keys() if not kk==k])) for i in res] # + [('rc',set([1,2]))])) for i in res]
        pp = []
        for i in gg:
            # print(i[0], [(kk, vv) for kk,vv in i[1]])
            ff = False
            for p in pp:
                if all([kk in p and vv == p[kk] for kk,vv in i[1]]):
                    if k in p: p[k] = p[k].union(i[0])
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    ff = True
                    break
            if ff: continue
            pp.append(dict(i[1]))
            pp[-1][k] = i[0]
        return pp
    
if __name__ == '__main__':
    s1 = [
        {'a':0, 'b':0, 'c':0},
        {'a':0, 'b':0, 'c':1},
        {'a':0, 'b':0, 'c':2},
        {'a':0, 'b':0, 'c':3},
        {'a':0, 'b':1, 'c':0},
        {'a':0, 'b':1, 'c':1},
        {'a':0, 'b':2, 'c':0},
        {'a':0, 'b':2, 'c':1},

        {'a':1, 'b':0, 'c':0},
        {'a':1, 'b':0, 'c':1},
        {'a':1, 'b':1, 'c':0},
        {'a':1, 'b':1, 'c':1},
        {'a':1, 'b':2, 'c':0},
        {'a':1, 'b':2, 'c':1},
    ]

    rr1 = SASS_Expr_Domain_Contract.group_naive(s1)
    print("rr1")
    [print(i) for i in rr1]
    print("rr2")
    rr2 = SASS_Expr_Domain_Contract.group(s1)
    [print(i) for i in rr2]

    ####################################################################3

    mi1 = 2
    ei1 = 0
    mi2 = 2
    ei2 = 0
    range_to = 10
    rz = range_to-1
    
    s3 = [{'ra':ra,'rb':rb} for ra,rb in itt.product(range(range_to), range(range_to)) if not ((((ra + int(ra == rz)) % mi1) == ei1) and (((rb + int(rb == rz)) % mi2) == ei2))]
    rr3 = SASS_Expr_Domain_Contract.group(s3)
    print("rr3")
    [print(i) for i in rr3]

