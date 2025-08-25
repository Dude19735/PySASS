import os
import typing
from py_sass import SM_SASS
from py_sass import SASS_Class
from py_sass_ext import BitVector
from . import _config as sp
from ._instr_cubin import Instr_CuBin
from ._instr_cubin_db_proxy import Db_Binary_Proxy
from .sm_cubin_kernel import SM_CuBin_Kernel
from .sm_cubin_file import SM_CuBin_File
from .sm_cubin_db import SM_Cubin_DB

"""
This file contains all methods necessary to create instructions, assemble them to
bits, create one ficticious kernel, decode that kernel and go back to class_names and
Instr_CuBin_Repr.

At the bottom are three test methods that showcase the correct use.
"""

class Instr_CuBin_Test:
    ##############################################################################################
    ##############################################################################################
    ###                                   Test Cubin decode                                    ###
    ##############################################################################################
    ##############################################################################################
    @staticmethod
    def test_cubin_decode(sass:SM_SASS, source:str):
        sm_nr:int = sass.sm_nr
        
        print("[SM {0}] Decode Cubin...".format(sm_nr))
        source_cubin = SM_CuBin_File(sass, source)
        
        print("[SM {0}] Cubin to DB...".format(sm_nr))
        full:Db_Binary_Proxy = SM_Cubin_DB.file_to_db(sass, source_cubin)
        
        print("[SM {0}] Persist DB...".format(sm_nr))
        db_con = SM_Cubin_DB.persist_bins([full])
        print("[SM {0}] DB to compressed stream...".format(sm_nr))
        b_stream:bytes = SM_Cubin_DB.db_con_to_mem(db_con)
        print("[SM {0}] Compressed stream to db...".format(sm_nr))
        db_con2 = SM_Cubin_DB.db_mem_to_con(b_stream)
        print("[SM {0}] Store DB to file...".format(sm_nr))
        SM_Cubin_DB.db_con_to_file(db_con2, 'test_db.db')
        print("[SM {0}] === Success! === ".format(sm_nr))

    ##############################################################################################
    ##############################################################################################
    ###                                   Test kernel decode                                   ###
    ##############################################################################################
    ##############################################################################################
    @staticmethod
    def test_instr_decode(sass:SM_SASS, bb:typing.List[BitVector], tt:typing.List[str], single_class:bool, p_step=250):
        sm_nr:int = sass.sm_nr
        classes_ = sass.sm.classes_dict
        m_lenc = max([len(k) for k in classes_.keys()])
        ljust_val = m_lenc + 4 + 4 + 6 + 8

        dec_res = SM_CuBin_Kernel.decode_kernel(sass, [bb], ['test'], ['0x00'], tt)
        print("[SM {0}] Class assignment test...".format(sm_nr))
        res = tt == dec_res[0]['class_names']
        if not res: raise Exception(sp.CONST__ERROR_UNEXPECTED)
        
        all_kernel = []
        kk=dict()
        for ind,(kk,koh) in enumerate(zip(dec_res, len(dec_res)*['0x00'])):
            print(100*" ", "\r", "  [{0}: {1}/{2}]".format(kk['kernel_name'], 0, len(kk['class_names'])), end='\r')
            all_kernel.append(SM_CuBin_Kernel(str(ind), sm_nr, sass, kk, '0x42', koh, head_only=False, verbose=True))
        if kk == dict(): raise Exception(sp.CONST__ERROR_UNEXPECTED)
        print(100*" ", "\r", "  [{0}: {1}/{2}]".format(kk['kernel_name'], len(all_kernel), len(kk['class_names'])))
        
        print("[SM {0}] Create DB Proxy...".format(sm_nr))
        db:Db_Binary_Proxy = SM_Cubin_DB.kernel_list_to_db_test(sass, all_kernel)
        
        print("[SM {0}] Persist DB...".format(sm_nr))
        db_con = db_con = SM_Cubin_DB.persist_bins([db])
        print("[SM {0}] DB to compressed stream...".format(sm_nr))
        b_stream:bytes = SM_Cubin_DB.db_con_to_mem(db_con)
        print("[SM {0}] Compressed stream to db...".format(sm_nr))
        db_con2 = SM_Cubin_DB.db_mem_to_con(b_stream)
        print("[SM {0}] Store DB to file...".format(sm_nr))
        SM_Cubin_DB.db_con_to_file(db_con2, 'test_db.db')
        print("[SM {0}] === Success! ===".format(sm_nr))

    ##############################################################################################
    ##############################################################################################
    ###                          Test regular instruction generation                           ###
    ##############################################################################################
    ##############################################################################################
    @staticmethod
    def test_instr_enc(sass:SM_SASS, enc_count:int, single_class:bool, single_class_name:str, p_step=250):
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(enc_count, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if single_class and not (isinstance(single_class_name, str) and len(single_class_name) > 0): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(p_step, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not p_step >= 1: raise Exception(sp.CONST__ERROR_ILLEGAL)

        classes_ = sass.sm.classes_dict
        sm_nr = sass.sm_nr

        m_lenc = max([len(k) for k in classes_.keys()])
        ljust_val = m_lenc + 4 + 4 + 6 + 8
        msg = "[SM {0}]-[{1}/{2}] {3}:"

        # Create binary vectors (full length, 128 or 88 bit length)
        bv = []
        tt = []
        for ind,class_name in enumerate(classes_.keys()):
            if single_class and class_name != single_class_name: continue
            mm = msg.format(sm_nr, str(ind+1).rjust(4), str(len(classes_)).rjust(4), class_name).ljust(ljust_val)
            if not sass.encdom.instr_exists(class_name): 
                print(mm + "N/C",flush=True)
                continue

            for ec in range(0, enc_count):
                enc_vals = sass.encdom.pick(class_name)
                bv.append(Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals, check_conditions=False))
                tt.append(class_name)
                if ec%p_step==0:
                    print(mm + "[{0}/{1}]".format(str(ec+1).rjust(4), str(enc_count).rjust(4)), end='\r', flush=True)
            print(mm + "\r{0}[{1}/{2}]".format(mm, str(enc_count).rjust(4), str(enc_count).rjust(4)), flush=True)

        if sm_nr < 70 and len(bv)%3 != 0:
            bf_instr_len = (3-len(bv)%3)
            print("[SM {0}] Back-filling {1} nop instructions...".format(sm_nr, bf_instr_len))
            nop_class_name = Instr_CuBin.get_nop(sass)
            for i in range(0, bf_instr_len):
                enc_vals = sass.encdom.pick(nop_class_name)
                bv.append(Instr_CuBin.instr_assemble_to_bv(sass, nop_class_name, enc_vals, check_conditions=False))
                tt.append(nop_class_name)

        # Create 64 bit binary vectors (final binary encoding)
        bb = Instr_CuBin.instr_bv_list_to_bwords(sass, bv)

        # To store to an exec file, call instr_bwords_to_bytes on each binary word

        Instr_CuBin_Test.test_instr_decode(sass, bb, tt, single_class, p_step)

    ##############################################################################################
    ##############################################################################################
    ###                          Test fixed enc_vals instr generation                          ###
    ##############################################################################################
    ##############################################################################################
    @staticmethod
    def test_instr_enc_iter(sass:SM_SASS, single_class:bool, single_class_name:str, p_step=250):
        if not isinstance(sass, SM_SASS): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(single_class, bool): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if single_class and not isinstance(single_class_name, str): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not isinstance(p_step, int): raise Exception(sp.CONST__ERROR_ILLEGAL)
        if not p_step >= 1: raise Exception(sp.CONST__ERROR_ILLEGAL)

        # raise Exception("This test is not up-to-date")

        classes_ = sass.sm.classes_dict
        sm_nr = int(sass.sm.details.SM_XX.split('_')[1])

        m_lenc = max([len(k) for k in classes_.keys()])
        ljust_val = m_lenc + 4 + 4 + 6 + 8

        # Create binary vectors (full length, 128 or 88 bit length)
        msg = "[SM {0}]-[{1}/{2}] {3}:"
        bv = []
        tt = []
        for ind,class_name in enumerate(classes_.keys()):
            if single_class and class_name != single_class_name: continue
            mm = msg.format(sm_nr, str(ind+1).rjust(4), str(len(classes_)).rjust(4), class_name).ljust(ljust_val)
            if not sass.encdom.instr_exists(class_name): 
                print(mm + "N/C",flush=True)
                continue

            class_:SASS_Class
            class_ = classes_[class_name]
            ncp = SASS_Class.get_non_const_preds(class_)
            if ncp:
                ncp_res = sass.encdom.fix(class_name, ncp)
                enc_count = len(ncp_res)

                for ec,enc_vals in enumerate(sass.encdom.fixed_iter(class_name)):
                    bv.append(Instr_CuBin.instr_assemble_to_bv(sass, class_name, i))
                    tt.append(class_name)
                    if ec%p_step==0:
                        print(mm + "[{0}/{1}]".format(str(ec+1).rjust(4), str(enc_count).rjust(4)), end='\r', flush=True)
            else:
                enc_count = 1
                for ec in range(0, enc_count):
                    enc_vals = sass.encdom.pick(class_name)
                    bv.append(Instr_CuBin.instr_assemble_to_bv(sass, class_name, enc_vals))
                    tt.append(class_name)
                    if ec%p_step==0:
                        print(mm + "[{0}/{1}]".format(str(ec+1).rjust(4), str(enc_count).rjust(4)), end='\r', flush=True)
            print(mm + "\r{0}[{1}/{2}]".format(mm, str(enc_count).rjust(4), str(enc_count).rjust(4)), flush=True)

        if sm_nr < 70 and len(bv)%3 != 0:
            bf_instr_len = (3-len(bv)%3)
            print("[SM {0}] Back-filling {1} nop instructions...".format(sm_nr, bf_instr_len))
            nop_class_name = Instr_CuBin.get_nop(sass)
            for i in range(0, bf_instr_len):
                enc_vals = sass.encdom.pick(nop_class_name)
                bv.append(Instr_CuBin.instr_assemble_to_bv(sass, nop_class_name, enc_vals))
                tt.append(nop_class_name)

        # Create 64 bit binary vectors (final binary encoding)
        bb = Instr_CuBin.instr_bv_list_to_bwords(sass, bv)
        Instr_CuBin_Test.test_instr_decode(sass, bb, tt, single_class, p_step)
    