import os
import pickle
import termcolor
import typing
import json
import itertools as itt
import operator as op
from py_sass_ext import SASS_Enc_Dom
from py_sass_ext import BitVector
from . import _config as sp
from ._sass_expression_ops import Op_Defined, Op_Not
from ._sass_expression import SASS_Expr
from ._instr_enc_dec_gen import Instr_EncDec_Gen
from ._instr_enc_dec_lookup import Instr_EncDec_Lookup
if not sp.SWITCH__USE_TT_EXT:
    from ._tt_terms import TT_List, TT_Reg, TT_Func
else:
    from py_sass_ext import TT_List, TT_Reg, TT_Func
from .sass_class import SASS_Class
from .sass_class_props import SASS_Class_Props
from .sass_parser_iter import SASS_Parser_Iter
from .sm_cu import SM_Cu
from .sm_cu_props import SM_Cu_Props
from .sm_latency import SM_Latency
from .misc_lookup_db import LookupDB

class SM_SASS:
    """This class is the main abstraction for a compute capability.
    """    

    def __init__(self, sm:int, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False, web_crawl=False, collect_statistics=False):
        if web_crawl and sm < 75:
            print(termcolor.colored("Nvidia tends to change their website. At this point (18.08.2025) it seems that all SASS instruction documentation for SM prior to SM 75 (Turing) has been removed from their website. Thus, we cannot proceed with web crawing anymore for this SM!!", color='red', attrs=['bold']))
            print(termcolor.colored("Setting 'web_crawl' to False", color='green'))
            web_crawl=False

        location = os.path.dirname(os.path.realpath(__file__))
        log_path = location + '/DocumentSASS'
        path = location + '/DocumentSASS/sm_'
        name_s = '_instructions.txt'
        name = name_s + '.in'

        sm_xx = 'sm_{0}'.format(sm)
        instructions_txt = path + str(sm) + name
        instructions_pickle = instructions_txt + '.pickle'
        if not os.path.exists(instructions_pickle) and not reparse:
            print("{0} not available. Run parse step...".format(instructions_pickle))
            reparse = True
            
        if reparse:
            if not os.path.exists(instructions_txt):
                print(termcolor.colored("If this is the first time, run ", 'red') + termcolor.colored("py_sass_install_all", 'red',  attrs=['bold']) + termcolor.colored("!", 'red'))
                print()
                print(termcolor.colored("If this isn't the first run, check if DocumentSASS/instr.zip is unpacked.", 'red'))
                print(termcolor.colored("  If it isn't, unpack it and put all files in DocumentSASS/*", 'red'))
                print(termcolor.colored("  This should not happen, though...", 'red'))
                raise Exception(sp.CONST__ERROR_UNEXPECTED)

            result = SASS_Parser_Iter.parse(sm, instructions_txt)
            result['GLOBAL__ALL_ACCESSORS'] = sp.GLOBAL__ALL_ACCESSORS
            result['GLOBAL__ALL_FUNCTIONS'] = sp.GLOBAL__ALL_FUNCTIONS
            result['GLOBAL__ALL_NON_REGS'] = sp.GLOBAL__ALL_NON_REGS
            result['GLOBAL__ALL_REMAINDERS'] = sp.GLOBAL__ALL_REMAINDERS
            result['GLOBAL__ALL_DEFAULTS'] = sp.GLOBAL__ALL_DEFAULTS

            with open(instructions_pickle, 'wb') as f:
                pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)
            self.print_res(sm_xx, result)
        else:
            print("\nOpen {0}...".format(instructions_pickle), end='')
            with open(instructions_pickle, 'rb') as f:
                result = pickle.load(f)
                sp.GLOBAL__ALL_ACCESSORS = result['GLOBAL__ALL_ACCESSORS'] 
                sp.GLOBAL__ALL_FUNCTIONS = result['GLOBAL__ALL_FUNCTIONS'] 
                sp.GLOBAL__ALL_NON_REGS = result['GLOBAL__ALL_NON_REGS']  
                sp.GLOBAL__ALL_REMAINDERS = result['GLOBAL__ALL_REMAINDERS']
                sp.GLOBAL__ALL_DEFAULTS = result['GLOBAL__ALL_DEFAULTS']
            print("loaded {0} instruction classes".format(len(result['CLASS'].keys())))

        self.__sm:SM_Cu = SM_Cu(result, sm_xx, finalize=finalize, opcode_gen=opcode_gen, web_crawl=web_crawl, log_path=log_path)
        self.__sm_nr:int = sm
        self.__latencies:SM_Latency = SM_Latency(sm, self.__sm)

        # # match instruction classes to latency baseline
        # for instr_class in self.sm.classes_dict.values():
        #     # if instr_class.OPCODES['pipes'][0]['i'] == 'VMADmio_pipe':
        #     # if instr_class.OPCODES['pipes'][0]['i'] == 'P2Rfxu_pipe':
        #     pipe = instr_class.OPCODES['pipes'][0]['i']
        #     instr = instr_class.OPCODES['opcode']['i']
        #     # if (pipe in MATH_OPS or instr in MATH_OPS) and (pipe in FXU_OPS or instr in FXU_OPS):
        #     #     # print(instr_class.class_name, pipe, instr)
        #     #     pass
        #     lb = self.latencies.match(instr_class)

        lookup_p = log_path + "/sm_{0}_lookup.pickle".format(sm)
        if not os.path.exists(lookup_p) or lookup_gen:
            self.__lu = Instr_EncDec_Gen.lookup_gen(sm, self.__sm.classes_dict, self.__sm.opcode_multiples, self.__sm.all_instr_desc, self.__sm.details)
            with open(lookup_p, 'wb') as f:
                pickle.dump(self.__lu, f, pickle.HIGHEST_PROTOCOL)
            self.lu_to_md(log_path + "/sm_{0}_lu.autogen.md".format(sm))
        else:
            print("Open {0}...".format(lookup_p))
            self.__lu = Instr_EncDec_Gen.lookup_load(lookup_p)

        self.__props:SM_Cu_Props = SM_Cu_Props(self.__sm_nr, self.__latencies, self.__sm, self.__lu, sp.CONST__OUTPUT_TO_FILE)

        self.__encdom = None
        self.__encdom_type = "None"

        if sp.CONST__OUTPUT_TO_FILE: self.to_files()

        self.set_config_fieds()

        if collect_statistics:
            self.collect_stats()

        # Unreliable...
        # self.__others = self.get_others()

    @property
    def encdom(self): 
        if self.__encdom is None: raise Exception("EncDom is not loaded! Call [sm_sass].load_encdom first!")
        return self.__encdom
    @property
    def encdom_type(self): return self.__encdom_type
    @property
    def latencies(self): return self.__latencies
    @property
    def sm_nr(self): return self.__sm_nr
    @property
    def lu(self): return self.__lu
    @property
    def sm(self) -> SM_Cu: return self.__sm
    @property
    def props(self): return self.__props
    @property
    def lookup_db(self): return self.__lookup_db

    def set_config_fieds(self):
        self.max_config_fields_for_sm = max([len(c.FORMAT.cashs) for c in self.__sm.classes_dict.values()])
        
        # =========================================================================================
        # leave this comment as reminder and information
        # =========================================================================================
        # How to check for cash parts?
        no_wr = [c for c in self.sm.classes_dict.values() if not any(str(x).find('WR')>=0 for x in c.FORMAT.cashs)]
        no_rd_or_wr_early = [c for c in self.sm.classes_dict.values() if not any(str(x).find('RD')>=0 or str(x).find('WR_EARLY')>=0 for x in c.FORMAT.cashs)]
        no_req = [c for c in self.sm.classes_dict.values() if not any(str(x).find('REQ')>=0 for x in c.FORMAT.cashs)]
        no_usched_info = [c for c in self.sm.classes_dict.values() if not any(str(x).find('USCHED_INFO')>=0 for x in c.FORMAT.cashs)]
        no_batch_t = [c for c in self.sm.classes_dict.values() if not any(str(x).find('BATCH_T')>=0 for x in c.FORMAT.cashs)]
        no_pm_pred = [c for c in self.sm.classes_dict.values() if not any(str(x).find('PM_PRED')>=0 for x in c.FORMAT.cashs)]

        # Every instruction class for all SMs needs at least WR, RD/WR_EARLY, REQ and USCHED_INFO
        #  => NOPE, we don't do that anymore
        # if no_wr!=[] or no_rd_or_wr_early!=[] or no_req!=[] or no_usched_info!=[]: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        # =========================================================================================
        # leave this comment as reminder and information
        # =========================================================================================
        # Collect all cash definitions for each sm
        sp.GLOBAL__CASH_EXPR[self.sm_nr] = set(itt.chain.from_iterable({str(x) for x in c.FORMAT.cashs} for c in self.sm.classes_dict.values()))
        # Output:
        #   (50, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (52, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (53, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (60, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (61, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (62, {
        #           '$( { ? USCHED_INFO:usched_info } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', '$( { & REQ:req = BITSET(6/0x0000):req_sb_bitset } )$'})
        #   (70, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (72, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (75, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(W1/PRINT):usched_info } )$', '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (80, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (86, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { ? PM_PRED(PMN):pm_pred } )$', 
        #           '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(W1/PRINT):usched_info } )$', '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (90, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & WR_EARLY:wr_early = UImm(3/0x7):src_rel_sb } )$', '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$',
        #           '$( { ? PM_PRED(PMN):pm_pred } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (100, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & WR_EARLY:wr_early = UImm(3/0x7):src_rel_sb } )$', '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { ? PM_PRED(PMN):pm_pred } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})
        #   (120, {
        #           '$( { ? BATCH_T(NOP):batch_t } )$', 
        #           '$( { & WR:wr = UImm(3/0x7):dst_wr_sb } )$', 
        #           '$( { & WR_EARLY:wr_early = UImm(3/0x7):src_rel_sb } )$', '$( { & RD:rd = UImm(3/0x7):src_rel_sb } )$', 
        #           '$( { ? PM_PRED(PMN):pm_pred } )$', 
        #           '$( { & REQ:req = BITSET(6/0x0000):req_bit_set } )$', 
        #           '$( { ? USCHED_INFO(W1/PRINT):usched_info } )$', '$( { ? USCHED_INFO(DRAIN):usched_info } )$'})

        if self.__sm_nr >= 70:
            # =========================================================================================
            # leave this comment as reminder and information
            # =========================================================================================
            # Used to figure out which ones have which for the cashes
            # no_usched_info = any([any([c for e in c.ENCODING if set(e['alias'].get_alias_names()).intersection({'usched_info'}) == {}]) for c in self.sm.classes_dict.values()])
            # no_batch_t = any([any([c for e in c.ENCODING if set(e['alias'].get_alias_names()).intersection({'batch_t'}) == {}]) for c in self.sm.classes_dict.values()])
            # print()
            # print(sm)
            # for c in self.sm.classes_dict.values():
            #     if len(c.FORMAT.cashs) == self.max_config_fields_for_sm: 
            #         print(c.class_name)
            #         break
            # sp.GLOBAL__CASH_EXPR[self.sm_nr] = {
            #     'no_usched_info': 'True' if any([any([c for e in c.ENCODING if set(e['alias'].get_alias_names()).intersection({'usched_info'}) == {}]) for c in self.sm.classes_dict.values()]) else 'False',
            #     'no_batch_t': 'True' if any([any([c for e in c.ENCODING if set(e['alias'].get_alias_names()).intersection({'batch_t'}) == {}]) for c in self.sm.classes_dict.values()]) else 'False'
            # }
            # Output:
            #   (70, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (72, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (75, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (80, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (86, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (90, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (100, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            #   (120, {'no_usched_info': 'False', 'no_batch_t': 'False'})
            # => there are no instructions that don't have usched_info and batch_t

            # =========================================================================================
            # leave this comment as reminder and information
            # =========================================================================================
            # What are the names of the encodings for the cash bits?
            # sp.GLOBAL__CASH_EXPR_EXTRA[self.sm_nr] = {
            #     'req_bit_set': set(itt.chain.from_iterable([e['code_name'] for e in c.ENCODING if len(set(e['alias'].get_alias_names()).intersection({'req_bit_set'})) > 0] for c in self.sm.classes_dict.values())),
            #     'src_rel_sb': set(itt.chain.from_iterable([e['code_name'] for e in c.ENCODING if len(set(e['alias'].get_alias_names()).intersection({'src_rel_sb'})) > 0] for c in self.sm.classes_dict.values())),
            #     'dst_wr_sb': set(itt.chain.from_iterable([e['code_name'] for e in c.ENCODING if len(set(e['alias'].get_alias_names()).intersection({'dst_wr_sb'})) > 0] for c in self.sm.classes_dict.values())),
            #     'pm_pred': set(itt.chain.from_iterable([e['code_name'] for e in c.ENCODING if len(set(e['alias'].get_alias_names()).intersection({'pm_pred'})) > 0] for c in self.sm.classes_dict.values()))
            # }
            # Output
            #   (70, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': set()})
            #   (72, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': set()})
            #   (75, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': set()})
            #   (80, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': set()})
            #   (86, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': {'BITS_2_103_102_pm_pred'}})
            #   (90, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': {'BITS_2_103_102_pm_pred'}})
            #   (100, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': {'BITS_2_103_102_pm_pred'}})
            #   (120, {'req_bit_set': {'BITS_6_121_116_req_bit_set'}, 'src_rel_sb': {'BITS_3_115_113_src_rel_sb'}, 'dst_wr_sb': {'BITS_3_112_110_dst_wr_sb'}, 'pm_pred': {'BITS_2_103_102_pm_pred'}})
            # => the encoding of the existing cash bits is very consistend on SM70 to SM120
            
            # =========================================================================================
            # leave this comment as reminder and information
            # =========================================================================================
            # sp.GLOBAL__CASH_EXPR[self.sm_nr] = {
            #     'BITS_6_121_116_req_bit_set': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('BITS_6_121_116_req_bit_set')] for c in self.sm.classes_dict.values()])),
            #     'BITS_3_115_113_src_rel_sb': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('BITS_3_115_113_src_rel_sb')] for c in self.sm.classes_dict.values()])),
            #     'BITS_3_112_110_dst_wr_sb': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('BITS_3_112_110_dst_wr_sb')] for c in self.sm.classes_dict.values()])),
            #     'BITS_2_103_102_pm_pred': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('BITS_2_103_102_pm_pred')] for c in self.sm.classes_dict.values()]))
            # }
            # Output:
            #   (70, {'BITS_6_121_116_req_bit_set': {'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': set()})
            #   (72, {'BITS_6_121_116_req_bit_set': {'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': set()})
            #   (75, {'BITS_6_121_116_req_bit_set': {'0', 'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': set()})
            #   (80, {'BITS_6_121_116_req_bit_set': {'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': set()})
            #   (86, {'BITS_6_121_116_req_bit_set': {'0', 'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': {'pm_pred'}})
            #   (90, {'BITS_6_121_116_req_bit_set': {'0', 'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': {'pm_pred'}})
            #   (100, {'BITS_6_121_116_req_bit_set': {'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': {'pm_pred'}})
            #   (120, {'BITS_6_121_116_req_bit_set': {'0', 'req_bit_set'}, 'BITS_3_115_113_src_rel_sb': {'VarLatOperandEnc(src_rel_sb)', '7'}, 'BITS_3_112_110_dst_wr_sb': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'BITS_2_103_102_pm_pred': {'pm_pred'}})
            # Either we have a table lookup or set the value to a fixed integer that is either 0 for the req_bit_set or 7 for the others

            # These four are sometimes encoded as fixed values in the ENCODING stage and may have to be added in decoding post processing
            req_bit_set = [n for n in self.__sm.details.FUNIT.encoding.keys() if n.find('req_bit_set')>=0] # type: ignore
            if not len(req_bit_set) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            src_rel_sb = [n for n in self.__sm.details.FUNIT.encoding.keys() if n.find('src_rel_sb')>=0] # type: ignore
            if not len(src_rel_sb) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            dst_wr_sb = [n for n in self.__sm.details.FUNIT.encoding.keys() if n.find('dst_wr_sb')>=0] # type: ignore
            if not len(dst_wr_sb) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            pm_pred = [n for n in self.__sm.details.FUNIT.encoding.keys() if n.find('pm_pred')>=0] # type: ignore
            if self.__sm_nr >= 86 and not len(pm_pred) == 1: raise Exception(sp.CONST__ERROR_UNEXPECTED)

            # =========================================================================================
            # leave this comment as reminder and information
            # =========================================================================================
            # These two are never encoded as fixed values in the ENCODING stage
            # usched_info = [n for n in self.sm.details.FUNIT.encoding.keys() if n.find('usched_info')>=0]
            # batch_t = [n for n in self.sm.details.FUNIT.encoding.keys() if n.find('batch_t')>=0]

            # print(no_usched_info, no_batch_t, len(req_bit_set), len(src_rel_sb), len(dst_wr_sb), len(usched_info), len(batch_t), len(pm_pred))

            self.config_bits = {req_bit_set[0]:'req_bit_set', src_rel_sb[0]:'src_rel_sb', dst_wr_sb[0]:'dst_wr_sb'}
            if self.__sm_nr >= 86: self.config_bits[pm_pred[0]] = 'pm_pred'

            # on SM70++ all of them need BATCH_T as well
            if no_batch_t!=[]: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            # on SM86++ all of them also need a PM_PRED
            if self.__sm_nr >= 86 and no_pm_pred: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        else:
            # SMs 50 to 62 are fairly regular. There are some instruction classes that use other designations for the cash bits but they all have
            # a full set
            self.config_bits = {'OEUSchedInfo':'usched_info','OEWaitOnSb':'req_sb_bitset','OEVarLatDest':'dst_wr_sb','OEVarLatSrc':'src_rel_sb'}

            # =========================================================================================
            # leave this comment as reminder and information
            # =========================================================================================
            # The following two show that there are no SMs between 50 and 62 that don't have either an OE... style set of cash bits or one that looks for example like this:
            #   hfma2__v2_req_sb_bitset=req_sb_bitset
            #   hfma2__v2_src_rel_sb=VarLatOperandEnc(src_rel_sb)
            #   hfma2__v2_dst_wr_sb=VarLatOperandEnc(dst_wr_sb)
            #   hfma2__v2_usched_info=usched_info
            # meaning, "hfma2__v2" is the instruction class and the rest of the name is the cash bit designation.
            # sp.GLOBAL__CASH_EXPR[self.sm_nr] = {
            #     'OEUSchedInfo': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('OEUSchedInfo')] for c in self.sm.classes_dict.values()])),
            #     'OEWaitOnSb': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('OEWaitOnSb')] for c in self.sm.classes_dict.values()])),
            #     'OEVarLatDest': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('OEVarLatDest')] for c in self.sm.classes_dict.values()])),
            #     'OEVarLatSrc': set(itt.chain.from_iterable([[str(x['alias']) for x in c.ENCODING if x['code_name'].startswith('OEVarLatSrc')] for c in self.sm.classes_dict.values()]))
            # }
            # Output:
            #   (50, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            #   (52, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            #   (53, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            #   (60, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            #   (61, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            #   (62, {'OEVarLatDest': {'VarLatOperandEnc(dst_wr_sb)', '7'}, 'OEWaitOnSb': {'req_bit_set', 'req_sb_bitset'}, 'OEVarLatSrc': {'VarLatOperandEnc(src_rel_sb)', '7'}})
            # => we either have a fixed encoding to 7 or use a lookup table mechanism 

            # Are there any instruction classes that don't have either the regular OE... or the hfma2__... style cash bits encoding?
            # sp.GLOBAL__CASH_EXPR_EXTRA[self.sm_nr] = {
            #     'OEVarLatDest': {c.class_name for c in self.sm.classes_dict.values() if not any(x for x in c.ENCODING if x['code_name'].startswith('OEVarLatDest') or x['code_name'].endswith('dst_wr_sb'))},
            #     'OEUSchedInfo': {c.class_name for c in self.sm.classes_dict.values() if not any(x for x in c.ENCODING if x['code_name'].startswith('OEUSchedInfo') or x['code_name'].endswith('usched_info'))},
            #     'OEWaitOnSb': {c.class_name for c in self.sm.classes_dict.values() if not any(x for x in c.ENCODING if x['code_name'].startswith('OEWaitOnSb') or x['code_name'].endswith('req_sb_bitset'))},
            #     'OEVarLatSrc': {c.class_name for c in self.sm.classes_dict.values() if not any(x for x in c.ENCODING if x['code_name'].startswith('OEVarLatSrc') or x['code_name'].endswith('src_rel_sb'))}
            # }
            # Output:
            #   (50, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            #   (52, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            #   (53, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            #   (60, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            #   (61, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            #   (62, {'OEVarLatDest': set(), 'OEUSchedInfo': set(), 'OEWaitOnSb': set(), 'OEVarLatSrc': set()})
            # => there are non of those instructions

    def collect_stats(self):
        print("Collect statistics for SM_{0}...".format(self.__sm_nr))
        c:SASS_Class
        for class_name, c in self.__sm.classes_dict.items():
            expr:SASS_Expr
            for cond in c.CONDITIONS:
                expr = cond['expr']
                pat = expr.pattern
                if not expr.has_large_func:
                    if pat in sp.GLOBAL__EXPRESSIONS:
                        sp.GLOBAL__EXPRESSIONS[pat] += 1
                    else: 
                        sp.GLOBAL__EXPRESSIONS[pat] = 1
                        sp.GLOBAL__EXPRESSIONS_OLD_NEW_COR[pat] = expr.old_pattern
                else:
                    if pat in sp.GLOBAL__LARGE_FUNC_EXPRESSIONS: 
                        sp.GLOBAL__LARGE_FUNC_EXPRESSIONS[pat] += 1
                    else: 
                        sp.GLOBAL__LARGE_FUNC_EXPRESSIONS[pat] = 1
                        sp.GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR[pat] = expr.old_pattern
                    if pat in sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR: 
                        sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR[pat].append(class_name)
                    else: 
                        sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR[pat] = [class_name]
                        
                if pat in sp.GLOBAL__EXPRESSIONS_VAR_COUNT:
                    if not (pat == (Op_Defined.__name__,) or pat == (Op_Not.__name__, Op_Defined.__name__)) and sp.GLOBAL__EXPRESSIONS_VAR_COUNT[pat] != len(expr.get_alias_names()): raise Exception(sp.CONST__ERROR_UNEXPECTED)
                    sp.GLOBAL__EXPRESSIONS_LAST_SM[pat] = self.__sm.details.SM_XX
                else: 
                    sp.GLOBAL__EXPRESSIONS_VAR_COUNT[pat] = len(expr.get_alias_names())
                    sp.GLOBAL__EXPRESSIONS_EXAMPLE[pat] = str(expr)
                    sp.GLOBAL__EXPRESSIONS_FIRST_SM[pat] = self.__sm.details.SM_XX
                    sp.GLOBAL__EXPRESSIONS_FIRST_INSTR[pat] = class_name
                    sp.GLOBAL__EXPRESSIONS_LAST_SM[pat] = self.__sm.details.SM_XX

    def lu_to_md(self, path:str):
        if not path.endswith(".md"): path += ".md"
        with open(path, 'w') as f:
            for lu in self.__lu.values():
                f.write("### " + Instr_EncDec_Lookup.to_str(lu) + "\n")

    def lu_to_json(self):
        res = dict()
        for lu in self.__lu.values():
            x = Instr_EncDec_Lookup.to_json(lu)
            res.update(x)

        with open("lu_{0}.json".format(self.sm_nr), 'w') as f:
            json.dump(res, f, indent=4)

        pass

    def get_others(self):
        res = dict()
        for lu in self.__lu.values():
            x = Instr_EncDec_Lookup.get_others(lu)
            for k,v in x.items():
                if k in res: res[k].extend(v)
                else: res.update(x)
        return res

    def print_res(self, sm_xx:str, result:dict):
        print(sm_xx, len(result['CLASS'].keys()), " instruction classes")
        if 'aa' in result.keys(): print('attributes', result['aa'])
        if 'rr' in result.keys(): print('func', result['rr'])
        if 'rr_ext' in result.keys(): print('attributes ext', result['rr_ext'])
        if 'ud' in result.keys(): print('unknown defaults', result['ud'])

    def to_files(self):
        with open('sm_{0}_instructions.txt.out'.format(self.__sm_nr), 'w') as f:
            f.write(str(self.__sm))
        # with open('sm_{0}_latencies.txt.out'.format(self.sm_nr), 'w') as f:
        #     f.write(str(self.latencies))

    def load_encdom(self, show_progress=True):
        if self.__encdom is not None: 
            del self.__encdom
            self.__encdom = None
        location = os.path.dirname(os.path.realpath(__file__))
        lz4_path = location + '/DocumentSASS/'
        dom_name = "sm_{0}_domains.lz4"
        self.__encdom = SASS_Enc_Dom(lz4_path + dom_name.format(self.__sm_nr), show_progress=show_progress)
        self.__encdom_type = "large"

    def load_encdom_small(self, show_progress=True):
        if self.__encdom is not None: 
            del self.__encdom
            self.__encdom = None
        location = os.path.dirname(os.path.realpath(__file__))
        lz4_path = location + '/DocumentSASS/'
        dom_name = "sm_{0}_domains.small.lz4"
        self.__encdom = SASS_Enc_Dom(lz4_path + dom_name.format(self.__sm_nr), show_progress=show_progress)
        self.__encdom_type = "small"

    def remove_loaded_encdom(self):
        if self.__encdom is not None:
            del self.__encdom
            self.__encdom = None
        self.__encdom_type = 'None'

    def get_class_mem_access_patterns(self, class_:SASS_Class) -> typing.Tuple[typing.List[tuple], typing.List[set]]:
        props:SASS_Class_Props = class_.props
        local_group = list()
        for ll in props.list_rf_alias:
            args:dict = ll['a']
            v:str
            types = dict()
            types['Register'] = 0
            types['NonZeroRegister'] = 0
            types['ZeroRegister'] = 0
            types['NonZeroRegisterFAU'] = 0
            types['UniformRegister'] = 0
            types['NonZeroUniformRegister'] = 0
            types['ZeroUniformRegister'] = 0
            types['SImm'] = 0
            types['UImm'] = 0
            other_count = 0
            for k,v in args.items():
                if v == 'reg':
                    tt:TT_Reg = props.tt_regs[k]
                    if tt.value == 'Register': 
                        types['Register']+=1
                    elif tt.value == 'NonZeroRegister': 
                        types['NonZeroRegister']+=1
                    elif tt.value == 'ZeroRegister': 
                        types['ZeroRegister']+=1
                    elif tt.value == 'NonZeroRegisterFAU': 
                        types['NonZeroRegisterFAU']+=1
                    elif tt.value == 'UniformRegister': 
                        types['UniformRegister']+=1
                    elif tt.value == 'NonZeroUniformRegister': 
                        types['NonZeroUniformRegister']+=1
                    elif tt.value == 'ZeroUniformRegister': 
                        types['ZeroUniformRegister']+=1
                    else: 
                        raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                elif v == 'func':
                    tt:TT_Func = props.tt_funcs[k]
                    if tt.value == 'SImm': types['SImm']+=1
                    elif tt.value == 'UImm': types['UImm']+=1
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            if any(v > 1 for v in types.values()): 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            local_group.append((ll['type'], ll['tt'], tuple([k for k,v in types.items() if v > 0])))
            if len(local_group[-1][-1]) > 3:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
        return local_group, [set(i[-1]) for i in local_group]

    def get_mem_access_patterns(self) -> typing.Tuple[typing.List[typing.List[typing.Set]], typing.List[str]]:
        """This is an adapted variant of the test method 'test_instr_bits_to_class'. It returns
        all memory access patterns for the current SM.

        For example, for SM 86, it returns:
        * [
            [{'NonZeroRegister', 'SImm'}]
            [{'NonZeroRegister', 'UniformRegister', 'SImm'}]
            [{'NonZeroRegister', 'UniformRegister'}]
            [{'NonZeroRegister'}]
            [{'NonZeroUniformRegister', 'SImm'}]
            [{'Register', 'SImm'}]
            [{'Register', 'SImm'}, {'Register', 'UniformRegister', 'SImm'}]
            [{'Register', 'SImm'}, {'UniformRegister'}, {'Register', 'SImm'}]
            [{'Register', 'SImm'}, {'UniformRegister', 'ZeroRegister', 'SImm'}]
            [{'Register', 'UImm'}]
            [{'Register', 'UniformRegister', 'SImm'}]
            [{'Register', 'UniformRegister', 'SImm'}, {'Register', 'SImm'}]
            [{'Register', 'UniformRegister', 'SImm'}, {'UniformRegister'}, {'Register', 'SImm'}]
            [{'Register', 'UniformRegister', 'SImm'}, {'ZeroRegister', 'SImm'}]
            [{'UImm'}]
            [{'UImm'}, {'NonZeroRegister', 'SImm'}]
            [{'UImm'}, {'SImm'}]
            [{'UImm'}, {'UImm'}, {'SImm'}]
            [{'UImm'}, {'UniformRegister', 'SImm'}]
            [{'UImm'}, {'ZeroRegister', 'SImm'}]
            [{'UniformRegister', 'SImm'}]
            [{'UniformRegister', 'UImm'}]
            [{'UniformRegister'}]
            [{'UniformRegister'}, {'NonZeroRegister', 'SImm'}]
            [{'UniformRegister'}, {'Register', 'SImm'}]
            [{'UniformRegister'}, {'UImm'}]
            [{'UniformRegister'}, {'UImm'}, {'SImm'}]
            [{'UniformRegister'}, {'UniformRegister'}]
            [{'UniformRegister'}, {'ZeroRegister', 'UImm'}]
            [{'ZeroRegister', 'UImm'}]
            [{'UniformRegister', 'ZeroRegister', 'SImm'}]
            [{'UniformRegister', 'ZeroRegister'}]
            [{'UImm', 'ZeroUniformRegister'}]
          ]

        :return: a list with all memory access patterns consisting of sub-lists with sets of register categories and function types and a list sorted the same way with an example class for every category
        :rtype: list, list
        """
        class_:SASS_Class
        ff_prints = []
        for class_ in self.sm.classes_dict.values():
            local_group, local_pattern = self.get_class_mem_access_patterns(class_)
            if local_group:
                ff_prints.append((class_.class_name, local_group))

        analysis = sorted([[
            i[0],
            "-".join("{0}:{1}".format(ii[0],str(ii[1])) for ii in i[-1]), 
            "-".join("[{0}]".format(",".join(iii for iii in ii[-1])) for ii in i[-1])
        ] for i in ff_prints], key=lambda x:x[-1])
        gg = [(m,list(g)) for m,g in itt.groupby(analysis, key=lambda x:x[-1])]
        
        mem_access_fields = [[set(i[1:-1].split(',')) for i in ggg[0].split('-')] for ggg in gg]
        class_example = [ggg[1][0][0] for ggg in gg]
        
        return mem_access_fields, class_example

    @staticmethod
    def __tab_str(item, tab_len = 8):
        return ' '*(tab_len - len(str(item)))
    @staticmethod
    def __space_str(items, item, tab_len=8):
        res = ""
        for i in items: res += ' '*tab_len
        res += str(item)
        return res
    @staticmethod
    def __line_str(item, tab_len=8):
        return "{0}{1}".format(item, SM_SASS.__tab_str(item, tab_len=tab_len))
    @staticmethod
    def __stats(f:typing.TextIO, expr_dict:dict, expr_old_dict:dict):
        ge = expr_dict
        ge_old = expr_old_dict
        gev = sp.GLOBAL__EXPRESSIONS_VAR_COUNT
        gee = sp.GLOBAL__EXPRESSIONS_EXAMPLE
        gfs = sp.GLOBAL__EXPRESSIONS_FIRST_SM
        gls = sp.GLOBAL__EXPRESSIONS_LAST_SM
        gfi = sp.GLOBAL__EXPRESSIONS_FIRST_INSTR

        f.write("{0}{1}{2}{3}{4}\n".format(
            SM_SASS.__line_str('Num'),
            SM_SASS.__line_str('VarC'),
            SM_SASS.__line_str('f.Sm'),
            SM_SASS.__line_str('l.Sm'),
            'Pattern | Old Pattern | Example | First Class',
        ))

        res = sorted([(i[1], i[0], c) for i,c in zip(ge.items(),ge_old.values())], key=op.itemgetter(0), reverse=True)
        for i in res: f.write("{0}{1}{2}{3}{4}\n{5}\n{6}\n{7}\n".format(
            SM_SASS.__line_str(i[0]),
            SM_SASS.__line_str(gev[i[1]]),
            SM_SASS.__line_str(gfs[i[1]]),
            SM_SASS.__line_str(gls[i[1]]),
            i[1],
            '   ' + SM_SASS.__space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], i[2]),
            '   ' + SM_SASS.__space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], gee[i[1]]),
            '   ' + SM_SASS.__space_str([i[0], gev[i[1]], gfs[i[1]], gls[i[1]]], gfi[i[1]])
        ))
    @staticmethod
    def stats_to_file():
        # Now we can just write the statistics to a file
        print("Write statistics to file...")
        with open('expr_stats.autogen.txt','w') as f: SM_SASS.__stats(f, sp.GLOBAL__EXPRESSIONS, sp.GLOBAL__EXPRESSIONS_OLD_NEW_COR)
        with open('expr_stats_lf.autogen.txt','w') as f: SM_SASS.__stats(f, sp.GLOBAL__LARGE_FUNC_EXPRESSIONS, sp.GLOBAL__LARGE_FUNC_EXPRESSIONS_OLD_NEW_COR)
        with open('expr_stats_lf_instr.autogen.txt','w') as f:
            for i in sp.GLOBAL__EXPRESSIONS_ALL_RANGE_INSTR.items():
                f.write(str(i[0]) + "\n   " + sp.GLOBAL__EXPRESSIONS_EXAMPLE[i[0]] + "\n   " + str(i[1]) + "\n")

    @staticmethod
    def create_lookup_db(sm_nr_list:list):
        db = LookupDB()

        props_list = [
            {'p' : 'Latency Type', 'n' : 'Control - Fixed Latency',       'f' : SM_Cu_Props.__dict__['measure__control__fixed_lat'],    'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Control - Variable Latency',    'f' : SM_Cu_Props.__dict__['measure__control__vared_lat'],    'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Sync - Fixed Latency',          'f' : SM_Cu_Props.__dict__['measure__sync__fixed_lat'],       'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Sync - Variable Latency',       'f' : SM_Cu_Props.__dict__['measure__sync__vared_lat'],       'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Load/Store - Fixed Latency',    'f' : SM_Cu_Props.__dict__['measure__load_store__fixed_lat'], 'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Load/Store - Variable Latency', 'f' : SM_Cu_Props.__dict__['measure__load_store__vared_lat'], 'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Data - Fixed Latency',          'f' : SM_Cu_Props.__dict__['measure__data__fixed_lat'],       'o': SM_Cu_Props.__name__, 't' : 'cn_set'},
            {'p' : 'Latency Type', 'n' : 'Data - Variable Latency',       'f' : SM_Cu_Props.__dict__['measure__data__vared_lat'],       'o': SM_Cu_Props.__name__, 't' : 'cn_set'},

            {'p' : 'Flags',        'n' : '/REUSE',              'f' : SASS_Class_Props.__dict__['has_reuse'],               'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$WR',                 'f' : SASS_Class_Props.__dict__['cash_has__wr'],            'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$WR_EARLY',           'f' : SASS_Class_Props.__dict__['cash_has__wr_early'],      'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$RD',                 'f' : SASS_Class_Props.__dict__['cash_has__rd'],            'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$BATCH_T',            'f' : SASS_Class_Props.__dict__['cash_has__batch_t'],       'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$REQ',                'f' : SASS_Class_Props.__dict__['cash_has__req'],           'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$USCHED_INFO',        'f' : SASS_Class_Props.__dict__['cash_has__usched_info'],   'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : '$PM_PRED',            'f' : SASS_Class_Props.__dict__['cash_has__pm_pred'],       'o': SASS_Class_Props.__name__, 't' : 'TF' },
            {'p' : 'Flags',        'n' : 'Variable Predicates', 'f' : SASS_Class_Props.__dict__['has_variable_predicates'], 'o': SASS_Class_Props.__name__, 't' : 'TF' }
        ]

        db.create(props_list)

        for sm in sm_nr_list:
            sass = SM_SASS(sm)
            db.insert_sm_categories({v.category for v in sass.sm.all_instr_desc.values()})
            for c in sass.sm.classes_dict.values():
                if not c.props.opcode in sass.sm.all_instr_desc:
                    c_desc = None
                else: c_desc = sass.sm.all_instr_desc[c.props.opcode]
                db.insert_class(sass.sm_nr, sass.props, c_desc, c, props_list)

    @staticmethod
    def get_lookup_db() -> bytes:
        return LookupDB().get_serialized()

def test_instr_bits_to_class(instr_bits_l:list, sass:SM_SASS, target_classes:list=[]):
    """This one is the same as in py_cubin (py_cubin._instr_cubin.instr_bits_to_class) 
    and is meant for TESTING!

    Use this to debug instructions that don't immediately find a solution if the only thing
    available is a bit-code.

    :param instr_bits_l: list with BitVector containing the bits of a full instruction
    :type instr_bits_l: list
    :param sass: SM_SASS for the corresponding SM number (for example SM 86)
    :type sass: SM_SASS
    :param target_classes: a list with target instr_class names used for testing to compare if the input matches the required output, defaults to []
    :type target_classes: list, optional
    :raises Exception: if matching to an instruction class failed
    :return: list of instr_class.class_name containing the matches for the BitVectors inside the instr_bits_l list
    :rtype: list
    """
    if not isinstance(instr_bits_l, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if not isinstance(target_classes, list): raise Exception(sp.CONST__ERROR_ILLEGAL)
    if target_classes and len(target_classes) != len(instr_bits_l): raise Exception(sp.CONST__ERROR_ILLEGAL)

    encw = sass.sm.details.FUNIT.encoding_width # type: ignore
    sm = int(sass.sm.details.SM_XX.split('_')[1])
    res = []
    for i_ind, instr_bits in enumerate(instr_bits_l):
        if target_classes and i_ind%1000 == 0: print(100*" ",'\r', "[SM {0}]: Decode [{1}/{2}]".format(sm, i_ind, len(instr_bits_l)), end='\r', flush=True)
        if len(instr_bits) != encw: raise Exception(sp.CONST__ERROR_UNEXPECTED)

        m_found = False
        for m_ind, enc_ref in sass.sm.opcode_ref.items():
            mask_check = all(instr_bits[i]==0 for i in m_ind)
            if not mask_check: continue

            found = False
            for enc_ind, enc_bin in enc_ref.items():
                opc_bin = tuple(instr_bits[i] for i in enc_ind)
                if not opc_bin in enc_bin: continue
                if target_classes: tcn = target_classes[i_ind]
                else: tcn = None

                match, msg = Instr_EncDec_Lookup.get(sass.lu[opc_bin], instr_bits, tcn)
                if msg:
                    raise Exception("Decode Exception: {0}".format(msg))
                res.append(match)
                found = True
                break
            if found: 
                m_found = True
                break
        if not m_found: raise Exception(sp.CONST__ERROR_UNEXPECTED)
    if target_classes: print(100*" ",'\r', "[SM {0}]: Decode [{1}/{2}]".format(sm, len(instr_bits_l), len(instr_bits_l)))
    return res

def test_list_operands(sass:SM_SASS):
    """This is a test method only. It does a bit of statistics with the lists and attributes.

    For SM 50, it produces
        89:[UImm]-[SImm]
            Const_FFMA
            attr_2.0:[UImm(5/0*):constBank]-attr_2.1:[SImm(17)*:immConstOffset]
        23:[ZeroRegister,UImm]
            I_ALD
            attr_1.0:[ZeroRegister(RZ):Ra+UImm(10/0)*:uImm]
        22:[NonZeroRegister,SImm]
            ALD
            attr_1.0:[NonZeroRegister:Ra+SImm(11/0)*:sImm]
        17:[Register]
            IPA_1
            attr_1.0:[Register:Ra]
        3:[UImm]
            I_IPA_1
            attr_1.0:[UImm(10/0)*:uImm]
        2:[NonZeroRegister]
            ALD_PHYS
            attr_1.0:[NonZeroRegister:Ra]
        2:[UImm]-[NonZeroRegisterFAU,SImm]
            LDC
            attr_1.0:[UImm(5/0*):constBank]-attr_1.1:[NonZeroRegisterFAU:Ra+SImm(17/0)*:sImm]
        2:[UImm]-[Register,SImm]
            BRX_c
            attr_1.0:[UImm(5/0*):constBank]-attr_1.1:[Register(RZ):Ra+SImm(17/0)*:sImm]
        2:[UImm]-[ZeroRegister,SImm]
            I_LDC
            attr_1.0:[UImm(5/0*):constBank]-attr_1.1:[ZeroRegister(RZ):Ra+SImm(17)*:immConstOffset]

    The first one is the pattern, for example [UImm]-[SImm]. Then the first instruction class
    that pattern appears with the stringified version of it for that instruction class
    """
    class_:SASS_Class
    ff_prints = []
    for class_ in sass.sm.classes_dict.values():
        props:SASS_Class_Props = class_.props
        local_group = list()
        for ll in props.list_rf_alias:
            args:dict = ll['a']
            v:str
            types = dict()
            types['Register'] = 0
            types['NonZeroRegister'] = 0
            types['ZeroRegister'] = 0
            types['NonZeroRegisterFAU'] = 0
            types['UniformRegister'] = 0
            types['NonZeroUniformRegister'] = 0
            types['ZeroUniformRegister'] = 0
            types['SImm'] = 0
            types['UImm'] = 0
            other_count = 0
            for k,v in args.items():
                if v == 'reg':
                    tt:TT_Reg = props.tt_regs[k]
                    if tt.value == 'Register': 
                        types['Register']+=1
                    elif tt.value == 'NonZeroRegister': 
                        types['NonZeroRegister']+=1
                    elif tt.value == 'ZeroRegister': 
                        types['ZeroRegister']+=1
                    elif tt.value == 'NonZeroRegisterFAU': 
                        types['NonZeroRegisterFAU']+=1
                    elif tt.value == 'UniformRegister': 
                        types['UniformRegister']+=1
                    elif tt.value == 'NonZeroUniformRegister': 
                        types['NonZeroUniformRegister']+=1
                    elif tt.value == 'ZeroUniformRegister': 
                        types['ZeroUniformRegister']+=1
                    else: 
                        raise Exception(sp.CONST__ERROR_UNEXPECTED)
                
                elif v == 'func':
                    tt:TT_Func = props.tt_funcs[k]
                    if tt.value == 'SImm': types['SImm']+=1
                    elif tt.value == 'UImm': types['UImm']+=1
                    else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
                else: raise Exception(sp.CONST__ERROR_UNEXPECTED)
            
            if any(v > 1 for v in types.values()): 
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
            local_group.append((ll['type'], ll['tt'], tuple([k for k,v in types.items() if v > 0])))
            if len(local_group[-1][-1]) > 3:
                raise Exception(sp.CONST__ERROR_UNEXPECTED)
        if local_group:
            ff_prints.append((class_.class_name, local_group))
    pass

    analysis = sorted([[
        i[0],
        "-".join("{0}:{1}".format(ii[0],str(ii[1])) for ii in i[-1]), 
        "-".join("[{0}]".format(",".join(iii for iii in ii[-1])) for ii in i[-1])
    ] for i in ff_prints], key=lambda x:x[-1])
    gg = [(m,list(g)) for m,g in itt.groupby(analysis, key=lambda x:x[-1])]
    gg_sorted = sorted(gg, key=lambda x:len(x[1]), reverse=True)
    gg_sorted_str = "\n".join(["".join([str(len(i[1])).rjust(4), ":", i[0], "\n      ", i[1][0][0], "\n      ", i[1][0][1]]) for i in gg_sorted])
    
    mem_access_patterns = "\n".join([",".join([str(set(i[1:-1].split(','))) for i in ggg[0].split('-')]) for ggg in gg])
    
    with open("lst_attr_{0}.autogen.txt".format(sass.sm_nr), 'w') as f:
        f.write("All Access Patterns (Verbose Descrption)\n")
        f.write("========================================\n")
        f.write(gg_sorted_str)
        f.write('\n')
        f.write('\n')
        f.write("All Memory Access Patterns\n")
        f.write("==========================\n")
        f.write(mem_access_patterns)

if __name__ == '__main__' or True:
    def dict_to_str(dd:dict):
        return {k:(v if 
                   isinstance(v, str|int|float) 
                   else (dict_to_str(v) 
                         if isinstance(v, dict) 
                         else ([(vv if isinstance(vv, str|int|float) else dict_to_str(vv)) for vv in v] if isinstance(v, list) else "<py_sass.tt_terms.{0}..>".format(type(v).__name__)))) 
                for k,v in dd.items()}


    # print("Store to zip...")
    # path = 'DocumentSASS/sm_'
    # name = '_instructions.txt'
    # archive_name = 'DocumentSASS/instr.zip'
    # with zipfile.ZipFile(archive_name, 'w') as zz:
    #     for sm in [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90]:
    #         instructions_txt = path + str(sm) + name    
    #         zz.write(instructions_txt)

    # we only want to test the parser
    # sp.TEST__MOCK_INSTRUCTIONS = False
    sass = {}
    sms = [50, 52, 53, 60, 61, 62, 70, 72, 75, 80, 86, 90, 100, 120]
    # sms = [86, 90, 100, 120]
    # sms = [50]
    # import time
    # import gzip
    sp.GLOBAL__CASH_EXPR = dict()
    sp.GLOBAL__CASH_EXPR_EXTRA = dict()
    conditions_count = []
    for sm in sms:
        # t0 = time.time()
        sass = SM_SASS(sm, reparse=True, finalize=True, opcode_gen=True, lookup_gen=True, web_crawl=False, collect_statistics=False)
        # sass = SM_SASS(sm, reparse=False, finalize=False, opcode_gen=False, lookup_gen=False, web_crawl=False, collect_statistics=False)
        jj = sass.lu_to_json()
        pass

    SM_SASS.create_lookup_db(sms)
        # test_list_operands(sass)
        # for class_ in sass.sm.classes_dict.values():
        #     lcg, lcp = sass.get_class_mem_access_patterns(class_)
        #     print(lcp, class_.class_name)
        # sass.get_mem_access_patterns()
        # sass.load_encdom_small()
        # sass.to_files()
        # t1 = time.time()
        # ds = gzip.compress(pickle.dumps(sass))
        # t2 = time.time()
        # du = pickle.loads(gzip.decompress(ds))
        # t3 = time.time()
        # print(len(ds), t1-t0, t2-t1, t3-t2)

        # Instr_EncDec_Lookup.get(sass.lu[opc_bin], instr_bits, tcn)
        # instr_l = [BitVector([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1])]
        # res = test_instr_bits_to_class(instr_l, sass)

        # conditions_count.append(sum(len(v.CONDITIONS) for v in sass.sm.classes_dict.values()))

        # # Register lookup:
        # reg_lookup = {i:["{0}.{1}[{2}]".format(i,vv, ",".join([str(kkk) for kkk in kk])) for vv, kk in v.items()] for i,v in sass.sm.details.REGISTERS_DICT.items()}
        
        # # sample_class:SASS_Class = sass.sm.classes_dict[[c for c in sass.sm.classes_dict if 'add' in c][0]]
        # # sample_props:SASS_Class_Props = sample_class.props

        # [v.class_name for v in sass.sm.classes_dict.values() if any(isinstance(r, TT_List) and r.extensions for r in v.FORMAT.regs)]

        # stg1:SASS_Class = [sass.sm.classes_dict[i] for i in sass.sm.classes_dict if i.startswith('stg')][0]
        # stg1.props.list_rf_alias
        # instr_class:SASS_Class = sass.sm.classes_dict['dfma__RRC_RRC']
        # format_tt:TT_Instruction = instr_class.FORMAT
        # print(format_tt)

    # SM_SASS.stats_to_file()
    pass