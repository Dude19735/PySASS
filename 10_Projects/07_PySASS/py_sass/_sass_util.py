import typing

class SASS_Util:
    """
    This one contains all kinds of converters and stuff that are used all over the place.
    """

    @staticmethod
    def try_convert(val, convert_hex=False, convert_bin=False, convert_split_bin=False, replace_quotes=False):
        """
        convert_hex: if True, convert terms like '0xFF' to corresponding integer
        convert_bin: if True, convert terms like '0b1001' to corresponding integer
        convert_split_bin: if True, convert terms like '0b1_1001_0' to integer corresponding to '0b110010'

        This method is used extremely often.
        """
        if isinstance(val, int) or isinstance(val, float):
            return val
        
        if not any([isinstance(val, i) for i in [str, bool]]):
            return val
        
        if replace_quotes:
            val = val.replace('"','')
        else:
            val = val.strip()
        # if we have a string => remove the quotes because it will be a string regardless
        val = val.strip('"')

        if val == 'nan': return val
        elif val == 'NaN': return val
        elif val == 'NAN': return val

        try:
            return int(val)
        except ValueError:
            pass
        if convert_hex and isinstance(val, str) and val.startswith('0x'):
            try:
                return int(val, 16)
            except ValueError:
                pass
        if convert_bin and isinstance(val, str) and val.startswith('0b'):
            if convert_split_bin:
                val = val.replace('_','')
            try:
                vv = int(val, 2)
                # in one instance, we have 0b01_1 things
                # in this case, just return the string
                v = val.split('_')
                if len(v) == 2:
                    return val
                return vv
            except ValueError:
                pass
        try:
            return float(val)
        except ValueError:
            pass
        if val == 'True': return True
        if val == 'False': return False

        return val

    @staticmethod
    def as_bits(bstr:str, x, y):
        ll = ['1' if i=='X' else '0' for i in bstr]
        llb = ["".join((ll[i], ll[i+1], ll[i+2], ll[i+3], ll[i+4], ll[i+5], ll[i+6], ll[i+7])) for i in range(0, len(ll)-8, 8)]
        as_str = "".join(llb)
        as_8bit_str = llb
        as_int = [int(bb, 2) for bb in as_8bit_str]
        as_bytes = [bb.to_bytes() for bb in as_int]
        as_bytes_str = b"".join(as_bytes)

        return { # actual
            "bit_str128": as_str,
            "bit_str8": as_8bit_str,
            "int_list8": as_int,
            "bytes_list": as_bytes,
            "bytes_str25": as_bytes_str
        }
        # return np.array([1 if i=='X' else 0 for i in bstr.strip("\"")], dtype=np.bool)

    @staticmethod
    def as_sequence(seq:str):
        # Pref(A1..B1)=(A2..B2), for example SR(0..255)=(0..255)
        part = seq.split('=')
        prefix, pseqs = part[0][:-1].split('(')

        pseq = pseqs.split('..')
        seql = list(range(int(pseq[0]), int(pseq[1])))

        seqrs = part[1][1:-1]
        seqrsp = seqrs.split('..')
        seqr = list(range(int(seqrsp[0]), int(seqrsp[1])))

        return prefix, dict(zip([prefix + str(s) for s in seql], seqr))

    @staticmethod
    def as_tuple(ll:list):
        ll2 = []
        for i in ll:
            ll2.append(SASS_Util.try_convert(i))
        return tuple(ll2)

    @staticmethod
    def as_2_list(ll:list, ):
        ll2 = []
        for i in range(1,len(ll),2):
            ll2.append((SASS_Util.try_convert(ll[i-1]), SASS_Util.try_convert(ll[i])))
        return ll2

    @staticmethod
    def as_dict(ll:list, ff:typing.Callable, convert_hex=False, convert_bin=False):
        ll2 = []
        for i in range(1,len(ll),2):
            ll2.append((ll[i-1].strip('*').strip(), ff(ll[i], convert_hex, convert_bin)))
        return dict(ll2)

    @staticmethod
    def update_dict(new:dict, into:dict):
        # TODO: maybe change this mechanism to make sure all values are preserved
        # NOTE: there may be keys inside 'new' that are already inside of 'into'
        #       but at this point, we really don't care...
        
        # new_kk = list(new.keys())
        # old_kk = list(into.keys())
        # overlap = [k1 for k1 in old_kk if k1 in new_kk]
        # if overlap:
        #     for o in overlap:
        #         if into[o] != new[o]:
        #             into[o] = [into[o]] + [new[o]]
        # return into
        into.update(new)
        return into
