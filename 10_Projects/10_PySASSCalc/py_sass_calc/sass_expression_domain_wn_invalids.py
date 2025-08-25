import os
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass_ext import SASS_Enc_Dom
import _config as sp

class SASS_Expr_Domain_Wn_Invalids:
    """
    Some registers have a name like INVALID...
    We have to remove them from the valid domains to make instructions individually
    decodable.

    This script was used to try some decoding scheme which turned out not to work. It is outdated now but kept for reference.
    """

    @staticmethod
    def wn_invalids(sm:int):
        if not isinstance(sm, int): raise Exception(sp.CONST__ERROR_UNEXPECTED)

        sass_path = os.path.dirname(os.path.realpath(__file__)) + "/DocumentSASS"
        d_path = sass_path + "/sm_{0}_domains_wn_invalids.pickle"

        sass = SM_SASS(sm)
        # sedom = SASS_Enc_Dom(sm, load_invalids=True)

        classes_ = sass.sm.classes_dict

        msg = "[SM {0}]-[{1}/{2}] {3}:"
        m_lenc = max([len(k) for k in classes_.keys()])
        ljust_val = m_lenc + 4 + 4 + 6 + 8
        class_names = classes_.keys()
        for ind,class_name in enumerate(class_names):
            mm = msg.format(sm, str(ind+1).rjust(4), str(len(class_names)).rjust(4), class_name).ljust(ljust_val)
            if not sedom.instr_exists(class_name):
                print(mm + "N/C",flush=True)
                continue
            
            dom = sedom.idom(class_name)
            class_:SASS_Class
            class_ = classes_[class_name]
            opc_mod = class_.opc_mod
            reg_mod = class_.reg_mod

            if (not opc_mod['invalid']) and (not reg_mod['invalid']):
                print(mm + "No invalids",flush=True)
                continue

            if class_name != 'ATOM':
                continue

            dom_wn = []
            for d in dom:
                for k,v in opc_mod['invalid'].items():
                    if not k in d: continue
                    pass
                for k,v in reg_mod['invalid'].items():
                    if not k in d: continue
                    pass

        # print("|SM_{0}: Dump encoding domains to pickle...".format(sm),end='')
        # with open(d_path.format(sm), 'wb') as f:
        #     pickle.dump(class_encode_domains, f, pickle.HIGHEST_PROTOCOL)
        # print('ok')

# safeguard
if __name__ == '__main__':
    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]

    for sm in sms: 
        SASS_Expr_Domain_Wn_Invalids.wn_invalids(sm)
