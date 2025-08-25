import requests
import re
import json
import typing
import os
import pickle
import itertools as itt
from . import _config as sp
from .sm_cu_details import SM_Cu_Details
from .sass_class import SASS_Class
from .sass_class_cash_aug import SASS_Class_Cash_Aug

class SM_XX_Instr_Desc:
    """
    One entry from the nvidia SASS website
    One entry kind of looks like this:
        DADD:           FP64 Add  [Floating Point Instructions]
    """
    PRINT_LEN = 15
    def __init__(self, instr=None, category=None, desc=None):
        if not instr: instr = 'N/A'
        if not category: category = 'N/A'
        if not desc: desc = ''

        self.__instr:str = instr
        self.__category:str = category
        self.__desc:str = desc

    @property
    def instr(self) -> str: 
        """Contains the instruction code of the current instruction class.

        For example
        * IMAD, I2F, IADD
        
        :return: the opcode string of the current instruction class or "N/A" if the code is not available
        :rtype: str
        """        
        return self.__instr
    @property
    def desc(self) -> str:
        """Contains the Nvidia description of the current insturction or "N/A" if the descrption is not available.

        NOTE: the descriptions for all instruction classes with the same opcode string are the same.

        :return: a description of the current instruction.
        :rtype: str
        """        
        return self.__desc
    @property
    def category(self) -> str: 
        """Contains the Nvidia instruction class category for the current instruction or "N/A" if the description is not available.

        For example
        * floating point instruction
        * control instruction

        NOTE: the descriptions for all instruction classes with the same opcode string are the same.
        
        :return: the instruction category for the current instruction class or "N/A" if it's not available
        :rtype: str
        """        
        return self.__category

    def __str__(self) -> str: return "{0}:{1}{2} [{3}]".format(self.__instr, (self.PRINT_LEN-len(self.__instr) if self.__instr is not None else 0)*' ', self.__desc, self.__category)
    def doc(self) -> str: return "{0} [{1}]".format(self.__desc, self.__category)

class SM_Cu:
    URL_BASE = 'https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html'
    URL = {
        'sm_50' : '#maxwell-and-pascal-instruction-set',
        'sm_52' : '#maxwell-and-pascal-instruction-set',
        'sm_53' : '#maxwell-and-pascal-instruction-set',
        'sm_60' : '#maxwell-and-pascal-instruction-set',
        'sm_61' : '#maxwell-and-pascal-instruction-set',
        'sm_62' : '#maxwell-and-pascal-instruction-set',
        'sm_70' : '#volta-instruction-set',
        'sm_72' : '#volta-instruction-set',
        'sm_75' : '#turing-instruction-set',
        'sm_80' : '#nvidia-ampere-gpu-and-ada-instruction-set',
        'sm_86' : '#nvidia-ampere-gpu-and-ada-instruction-set',
        'sm_90' : '#hopper-instruction-set',
        'sm_100': '#blackwell-instruction-set',
        'sm_120': '#blackwell-instruction-set'
    }

    def __init__(self, results:dict, sm_xx:str, finalize, opcode_gen, web_crawl, log_path):
        self.details = SM_Cu_Details(results, sm_xx)
        if not log_path.endswith('/'): log_path += '/'
        self.log_path = log_path

        fn_class = self.log_path + sm_xx + '_classes_' + '.pickle'
        fn_skipped_class = self.log_path + sm_xx + '_skipped_classes_' + '.pickle'
        fn_opc_refs = self.log_path + sm_xx + '_opc_refs_' + '.pickle'
        web_crawl_json_name = log_path + sm_xx + '_instr_desc' + '.json'
        fn_skiped = log_path + sm_xx + '_skipped.autogen' + '.txt'

        # if we don't have finalize=True but don't have the required pickle, flip finalize to true
        if not os.path.exists(fn_class) and not finalize:
            print("{0} not available. Apply finalize step..".format(fn_class))
            finalize = True

        # #################################################################################
        # Generate or load instruction classes
        if not finalize:
            print('Open {0}...'.format(fn_class))
            with open(fn_class, 'rb') as f: class_ = pickle.load(f)
            print('Open {0}...'.format(fn_skipped_class))
            with open(fn_skipped_class, 'rb') as f: skiped_classes = pickle.load(f)
            all_class_names = list(results['CLASS'].keys())
        else:
            class_ = dict()
            skiped_classes = dict()
            print('Set class parsing results to attr...')
            # for param in results['CLASS'].keys(): setattr(self, "class__" + param, results['CLASS'][param])
            all_class_names = list(results['CLASS'].keys())

            msg = 'Finalize classes...' + ('(gen mock instr)' if sp.TEST__MOCK_INSTRUCTIONS else '')
            print('|' + msg + (100-len(msg)-2)*' ' + '|')
            progr_v = (len(all_class_names) / 50)
            progr_n = 0
            def pb(ind:int, progr_v, progr_n):
                pn = ind // progr_v
                if pn > progr_n: 
                    while progr_n < pn:
                        print(2*'=',end='', flush=True)
                        progr_n += 1
                return progr_n

            self.mock_sass_bits = []
            self.mock_sass_classes = []
            if os.path.exists(log_path + "{0}_non_sat.json".format(sm_xx)):
                with open(log_path + "{0}_non_sat.json".format(sm_xx), 'r') as f:
                    non_sat_class_names = json.load(f)
            else: non_sat_class_names = []
                          
            for ind, class_name in enumerate(all_class_names):
                sass_class = results['CLASS'][class_name]
                if class_name in class_.keys(): raise Exception('Double definition of class {0}'.format(class_name))
                ccc = SASS_Class(class_name, sass_class, self.details)

                # ===============================================================================================
                # Keep for reference
                # ===============================================================================================
                # This adds missing cash bit definitions in the FORMAT of the instruction class.
                # The functionality was experimental and it's useless in the real world because
                # the instructions don't work that way (see comments inside the class for info)
                # SASS_Class_Cash_Aug.augment_cashes(ccc, self.details)

                if ccc.deprecated_by_nvidia:
                    ccc.set_deprecated_reason("Deprecated ny Nvidia")
                    skiped_classes[class_name] = ccc
                elif class_name in non_sat_class_names:
                    ccc.set_deprecated_reason("Not satisfiable CONDITIONS")
                    skiped_classes[class_name] = ccc
                else: class_[class_name] = ccc
                
                progr_n = pb(ind, progr_v, progr_n)
            print('==')

            if skiped_classes:
                with open(fn_skiped, 'w') as f:
                    for i in skiped_classes.items():
                        dc:SASS_Class = i[1]
                        print("Skipped", i[0], ": ", dc.deprecated_reason)
                        f.write("{0}: {1}\n".format(i[0], dc.deprecated_reason))
                    print(flush=True)

            with open(fn_class, 'wb') as f: pickle.dump(class_, f, pickle.HIGHEST_PROTOCOL)
            with open(fn_skipped_class, 'wb') as f: pickle.dump(skiped_classes, f, pickle.HIGHEST_PROTOCOL)

        self.__all_class_names:typing.List[str] = all_class_names
        self.__class:typing.Dict[str, SASS_Class] = class_
        self.__skipped_classes:typing.Dict[str, SASS_Class] = skiped_classes
        self.__class_pipes:typing.Dict[str, typing.List[SASS_Class]] = {}
        c:SASS_Class
        for c in self.__class.values():
            sets = c.props.lat_set
            for s in sets:
                if not s in self.__class_pipes: self.__class_pipes[s] = [c]
                else: self.__class_pipes[s].append(c)

        # #################################################################################
        # Construct set containing pipe and opcode for the latency match
        self.latency_set = set(itt.chain.from_iterable(c.OPCODES['set'] for c in self.__class.values()))

        # #################################################################################
        # Generate or load instruction descriptions
        all_instr_codes = set([i.OPCODES['opcode']['i'] for i in self.__class.values()])
        if web_crawl:
            print("Webcrawl {0} from Nvidia's website...".format(sm_xx))
            instr_descs = dict()
            instr_descs['_comment'] = 'N/C: instr in txt but not on web, N/A: instr on web but not in txt'
            instr_descs.update(self.__web_scrape(sm_xx, all_instr_codes))
            jj = json.dumps(instr_descs, indent=4)
            with open(web_crawl_json_name, 'w') as f: f.write(jj)
        else:
            if not os.path.exists(web_crawl_json_name): raise Exception(sp.CONST__ERROR_ILLEGAL)
            print("Open {0}...".format(web_crawl_json_name))
            with open(web_crawl_json_name, 'r') as f: instr_descs = json.load(f)
            
        self.all_instr_desc = self.instr_descs_to_obj(sm_xx, instr_descs)

        if not os.path.exists(fn_opc_refs) and not opcode_gen:
            print("{0} not available. Apply opcode_gen step..".format(fn_class))
            opcode_gen = True

        # #################################################################################
        # Generate or load opcode lookup table
        opcode_ref = {}
        opcode_multiples = {}
        if opcode_gen:
            cc:SASS_Class
            class_count = 0
            print("Create Opcode lookup...")
            for cc in self.__class.values():
                k1 = tuple(ind for ind,i in enumerate(cc.funit_mask) if i==0)
                k2 = cc.get_opcode_encoding()[0]
                k3 = cc.get_opcode_bin()
                if k1 in opcode_ref:
                    if k2 in opcode_ref[k1]: opcode_ref[k1][k2].append(k3)
                    else: opcode_ref[k1][k2] = [k3]
                else:
                    opcode_ref[k1] = dict()
                    opcode_ref[k1][k2] = [k3]

                if k3 in opcode_multiples: opcode_multiples[k3].append(cc.class_name)
                else: opcode_multiples[k3] = [cc.class_name]
                class_count += 1

            if not class_count == len(self.__class): raise Exception(sp.CONST__ERROR_UNEXPECTED)

            self.opcode_ref = dict((k, dict((vk, set(vi)) for vk,vi in sorted(v.items(), key=lambda x: len(x[0]), reverse=True))) for k,v in sorted(opcode_ref.items(), key=lambda x: len(x[0]), reverse=True))
            self.opcode_multiples = dict((k,v) for k,v in sorted(opcode_multiples.items(), key=lambda x: len(x[1]), reverse=True))

            with open(fn_opc_refs, 'wb') as f: pickle.dump({'opcode_ref': self.opcode_ref, 'opcode_mult': self.opcode_multiples}, f, pickle.HIGHEST_PROTOCOL)
        else:
            print('Open {0}...'.format(fn_opc_refs))
            with open(fn_opc_refs, 'rb') as f: 
                x = pickle.load(f)
                self.opcode_ref = x['opcode_ref']
                self.opcode_multiples = x['opcode_mult']

    @property
    def class_pipes(self) -> typing.Dict[str, typing.List[SASS_Class]]: return self.__class_pipes
    @property
    def classes_dict(self) -> typing.Dict[str, SASS_Class]: return self.__class
    @property
    def all_class_names(self) -> typing.List[str]: return self.__all_class_names
    @property
    def skipped_classes(self) -> typing.Dict[str, SASS_Class]: return self.__skipped_classes

    def get_from_all_classes(self, class_name):
        if class_name in self.__class: return self.__class[class_name]
        return self.__skipped_classes[class_name]

    def classes_info(self): return [(i[0],"".join(str(i) for i in i[1].get_opcode_bin()), i[1]) for i in self.__class.items()]

    def __str__(self):
        res = []
        for c in self.__class.values():
            res.append(str(c))
        return "\n".join(res)

    def __web_scrape(self, sm_xx, available_instr:set):
        response = requests.get(self.URL_BASE)
        to_find = 'class="headerlink" href="{0}"'.format(self.URL[sm_xx])
        ind = [m.end(0) for m in re.finditer(to_find, response.text)][-1]
        specs = response.text[ind:]

#         head_str = """
# <thead>
# <tr class="row-odd">
# <th class="head"><p>Opcode</p></th>
# <th class="head"><p>Description</p></th>
# </tr>
# </thead>
# """
        head_str = '<thead>\r\n<tr class="row-odd"><th class="head"><p>Opcode</p></th>\r\n<th class="head"><p>Description</p></th>\r\n</tr>\r\n</thead>\r\n'
        head_ind = specs.find(head_str)
        if head_ind < 0:
            raise Exception("Head not found for {0}".format(self.URL[sm_xx]))
        
        body = specs[(head_ind+len(head_str)):]

        if not body.startswith('<tbody>'):
            raise Exception("Body not found for {0}".format(self.URL[sm_xx]))

        end_ind = body.find('</tbody>')
        sass_table = body[len('<tbody>'):end_ind]
        end_strong = '</strong>'

        start_strong = '<p><strong>'
        end_strong = '</strong></p>'
        categories = [i.split(end_strong) for i in sass_table.split(start_strong)[1:]]

        start_inds = [[m.end(0) for m in re.finditer('<td><p>', ll[1])] for ll in categories]
        end_inds = [[m.start(0) for m in re.finditer('</p></td>', ll[1])] for ll in categories]
        instr_descs = [[[cc[0], (s,e), cc[1][s:e]] for s,e in zip(s_i, e_i)] for s_i, e_i, cc in zip(start_inds, end_inds, categories)]

        covered = set()
        res = dict()
        for dd in instr_descs:
            for j in range(0, len(dd), 2):
                # print(dd[j], dd[j+1])
                if dd[j][2]:
                    covered.add(dd[j][2])
                    if dd[j][2] in available_instr:
                        res[dd[j][2]] = {'instr': dd[j][2], 'category': dd[j][0], 'desc': dd[j+1][2]}
                    else:
                        res[dd[j][2]] = {'instr': dd[j][2], 'category': 'N/A', 'desc': 'N/A'}

        for dd in available_instr:
            if not dd in covered:
                res[dd] = {'instr': dd, 'category': 'N/C', 'desc': 'N/C'}
        return res

    def instr_descs_to_obj(self, sm_xx, instr_descs):
        all_instr_desc = dict()
        with open(self.log_path + sm_xx + ".log",'w') as f:
            dd = [d for i,d in instr_descs.items() if not i=='_comment']
            for d in dd:
                if d['desc'] != 'N/C':
                    all_instr_desc[d['instr']] = SM_XX_Instr_Desc(d['instr'], d['category'], d['desc'])
                    f.write(str(all_instr_desc[d['instr']]) + "\n")
            for d in dd:
                if d['desc'] == 'N/C':
                    f.write('Instruction {0} not on web for {1}\n'.format(d['instr'], sm_xx))
        
        return all_instr_desc
