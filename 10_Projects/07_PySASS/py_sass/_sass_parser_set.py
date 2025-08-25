import itertools as itt
from ._sass_util import SASS_Util as su

class SASS_Parser_Set:
    """
    This one is part of the instructions.txt parser.
    
    Stuff that is between [ ... ]

    The result is a nested set where all the entries are down-converted
    to the closest type
    """

    @staticmethod
    def parse(lines_iter:itt.islice):
        result = set()
        entry = []
        while True:
            i = next(lines_iter, False)
            if not i: break

            if i == '[': 
                ret = SASS_Parser_Set.parse(lines_iter)
                result.add(ret)
            elif i == ']':
                val = su.try_convert("".join(entry))
                if val != '': result.add(val)
                break
            elif i == ',':
                val = su.try_convert("".join(entry))
                if val != '': result.add(val)
                entry = []
            else:
                entry.append(i)
        return result
    
if __name__ == '__main__':
    pass
